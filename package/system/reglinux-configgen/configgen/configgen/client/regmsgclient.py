import contextlib
import pathlib
import socket
import struct

# Default socket path for regmsgd
DEFAULT_SOCKET_PATH = "/var/run/regmsgd.sock"


def parse_regmsg_response(response: str) -> tuple[bool, str]:
    """Parse regmsg response and return (success, content).

    Args:
        response: Raw response from regmsg (with OK/ERR prefix)

    Returns:
        Tuple of (success flag, content)

    """
    if response.startswith("OK "):
        return True, response[3:]  # Remove "OK " prefix
    if response.startswith("ERR "):
        return False, response[4:]  # Remove "ERR " prefix
    if response == "OK":
        return True, ""  # Empty content after "OK"
    if response == "ERR":
        return False, ""  # Empty content after "ERR"
    # Handle response without prefix (could be legacy format)
    return True, response


class RegMsgClient:
    """Client for communication with regmsgd service using Unix sockets.

    Optimized for embedded systems with focus on memory efficiency,
    performance, and robustness.
    """

    def __init__(
        self,
        address: str = DEFAULT_SOCKET_PATH,
        timeout: int = 5000,
    ):
        """Initialize the RegMsg client.

        Args:
            address: Unix socket path for regmsgd
            timeout: Timeout in milliseconds for send/receive operations

        """
        self.address = address
        self.timeout = timeout
        self.socket: socket.socket | None = None
        self._connected = False

    def connect(self) -> None:
        """Establish connection with regmsgd service."""
        if self._connected:
            return

        # Create socket with proper error handling
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Set timeout in seconds (socket timeout is in seconds, not milliseconds)
        sock.settimeout(self.timeout / 1000.0)

        try:
            sock.connect(self.address)
            # Close previous socket if exists (cleanup)
            if self.socket is not None:
                with contextlib.suppress(OSError):
                    self.socket.close()
            self.socket = sock
            self._connected = True
        except OSError as e:
            # Clean up socket if connection fails
            with contextlib.suppress(OSError):
                sock.close()
            raise RuntimeError(
                f"Failed to connect to regmsgd at {self.address}: {e!s}",
            ) from e

    def disconnect(self) -> None:
        """Close connection with regmsgd service."""
        if self.socket is not None:
            with contextlib.suppress(OSError):
                self.socket.close()
            self.socket = None

        self._connected = False

    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self.socket is not None

    def is_socket_available(self) -> bool:
        """Check if the socket file exists without connecting.

        This can be used to check if the regmsgd service is likely running.

        Returns:
            True if the socket file exists, False otherwise

        """
        return pathlib.Path(self.address).exists()

    def set_timeout(self, timeout: int) -> None:
        """Update the timeout value for the current connection.

        Args:
            timeout: New timeout value in milliseconds

        """
        self.timeout = timeout
        if self.socket is not None:
            self.socket.settimeout(timeout / 1000.0)

    def send_message(self, message: str) -> str:
        """Send a message to regmsgd and return the response.

        Args:
            message: Message to be sent

        Returns:
            Response from regmsgd service

        Raises:
            RuntimeError: If not connected or communication error occurs

        """
        if not self.is_connected():
            raise RuntimeError("Client is not connected. Call connect() first.")

        if self.socket is None:
            raise RuntimeError("Socket is None, cannot send/receive message")

        try:
            # Encode the message to bytes
            message_bytes = message.encode("utf-8")
            msg_length = len(message_bytes)

            # Send message length (4-byte big-endian integer) and message in one operation
            # Using struct.pack for better performance than to_bytes
            length_bytes = struct.pack("!I", msg_length)
            self.socket.sendall(length_bytes + message_bytes)

            # Receive response length (4-byte big-endian integer)
            length_bytes = self._recv_all(4)
            response_length = struct.unpack("!I", length_bytes)[0]

            # Receive the actual response
            response_bytes = self._recv_all(response_length)
            return response_bytes.decode("utf-8")
        except TimeoutError:
            raise RuntimeError(
                f"Timeout in communication with regmsgd (>{self.timeout}ms)",
            ) from None
        except OSError as e:
            raise RuntimeError(f"Error in communication with regmsgd: {e!s}") from e
        except UnicodeDecodeError:
            raise RuntimeError(
                "Invalid response format: non-UTF-8 data received",
            ) from None
        except struct.error:
            raise RuntimeError("Invalid response length format") from None
        except Exception as e:
            raise RuntimeError(f"Unexpected error sending message: {e!s}") from e

    def _recv_all(self, length: int) -> bytes:
        """Receive exactly 'length' bytes from the socket.

        Optimized for embedded systems to minimize memory allocations.
        """
        if length <= 0:
            return b""

        if self.socket is None:
            raise RuntimeError("Socket is None, cannot receive data")

        buffer = bytearray(length)
        view = memoryview(buffer)
        bytes_received = 0

        while bytes_received < length:
            chunk_size = self.socket.recv_into(view[bytes_received:])
            if chunk_size == 0:
                raise RuntimeError("Connection closed while receiving data")
            bytes_received += chunk_size

        return bytes(buffer)

    def __enter__(self):
        """Enable usage as context manager."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: object | None,
    ) -> None:
        """Ensure connection is closed when exiting context manager."""
        self.disconnect()


# Compatibility functions to maintain original interface
# Global client instance (optional; could also be kept inside a class)
_client: RegMsgClient | None = None


def regmsg_connect(
    address: str = DEFAULT_SOCKET_PATH,
    timeout: int = 5000,
) -> RegMsgClient:
    """Compatibility function to connect to regmsgd.

    Args:
        address: Unix socket path for regmsgd
        timeout: Timeout in milliseconds for operations

    Returns:
        RegMsgClient instance ready for use

    """
    global _client
    _client = RegMsgClient(address, timeout)
    _client.connect()

    return _client


def regmsg_send_message(message: str, timeout: int = 5000) -> str:
    """Compatibility function to send message to regmsgd.

    Args:
        message: Message to be sent
        timeout: Timeout in milliseconds for operations (optional)

    Returns:
        Response from regmsgd service

    """
    global _client

    # If already connected globally, use existing client
    if _client is not None and _client.is_connected():
        # Update timeout if needed and if different from current timeout
        if _client.socket is not None:
            _client.socket.settimeout(timeout / 1000.0)
        # Also update the client's timeout value for consistency
        _client.timeout = timeout
        return _client.send_message(message)
    # If no global connection exists, create temporarily
    with RegMsgClient(timeout=timeout) as client:
        return client.send_message(message)


def regmsg_disconnect() -> None:
    """Compatibility function to disconnect from regmsgd."""
    global _client

    if _client is not None:
        _client.disconnect()
        _client = None


@contextlib.contextmanager
def regmsg_client(address: str = DEFAULT_SOCKET_PATH, timeout: int = 5000):
    """Context manager for safe usage of regmsg client.

    Args:
        address: Unix socket path for regmsgd
        timeout: Timeout in milliseconds for operations

    """
    client = RegMsgClient(address, timeout)
    try:
        client.connect()
        yield client
    finally:
        client.disconnect()
