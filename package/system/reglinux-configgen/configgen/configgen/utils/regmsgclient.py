import contextlib
from typing import Any

import zmq
import zmq.error


class RegMsgClient:
    """
    Client for communication with regmsgd service using ZeroMQ.

    This class provides a more robust and safe interface for communicating
    with the regmsgd daemon, with enhanced error handling and connection
    management features.
    """

    def __init__(
        self, address: str = "ipc:///var/run/regmsgd.sock", timeout: int = 5000
    ):
        """
        Initialize the RegMsg client.

        Args:
            address: IPC socket address for regmsgd
            timeout: Timeout in milliseconds for send/receive operations
        """
        self.address = address
        self.timeout = timeout
        self.context: zmq.Context[Any] | None = None
        self.socket: zmq.Socket[Any] | None = None
        self._connected = False

    def connect(self) -> None:
        """Establish connection with regmsgd service."""
        if self._connected:
            return

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)

        # Additional safety check to ensure socket exists before use
        if self.socket is None:
            raise RuntimeError("Socket is None after context creation")

        # Configure timeout to avoid indefinite hangs
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.socket.setsockopt(zmq.SNDTIMEO, self.timeout)

        self.socket.connect(self.address)
        self._connected = True

    def disconnect(self) -> None:
        """Close connection with regmsgd service."""
        if self.socket is not None:
            try:
                self.socket.close()
            except zmq.error.Again:
                # Ignore errors during closing
                pass
            except AttributeError:
                # Handle case where socket is None during close attempt
                pass
            self.socket = None

        if self.context is not None:
            try:
                self.context.term()
            except zmq.error.Again:
                # Ignore errors during termination
                pass
            except AttributeError:
                # Handle case where context is None during term attempt
                pass
            self.context = None

        self._connected = False

    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self.socket is not None and self.context is not None

    def send_message(self, message: str) -> str:
        """
        Send a message to regmsgd and return the response.

        Args:
            message: Message to be sent

        Returns:
            Response from regmsgd service

        Raises:
            RuntimeError: If not connected or communication error occurs
        """
        if not self.is_connected():
            raise RuntimeError("Client is not connected. Call connect() first.")

        # Additional safety check to ensure socket exists before use
        if self.socket is None:
            raise RuntimeError("Socket is None, cannot send/receive message")

        try:
            self.socket.send_string(message)
            reply = self.socket.recv_string()
            return reply
        except zmq.Again:
            raise RuntimeError(
                f"Timeout in communication with regmsgd (>{self.timeout}ms)"
            )
        except zmq.error.ZMQError as e:
            raise RuntimeError(f"Error in communication with regmsgd: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error sending message: {str(e)}")

    def __enter__(self):
        """Enable usage as context manager."""
        self.connect()
        return self

    def __exit__(
        self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any | None
    ) -> None:
        """Ensure connection is closed when exiting context manager."""
        self.disconnect()


# Compatibility functions to maintain original interface
# Global context and socket (optional; could also be kept inside a class)
_context: zmq.Context[Any] | None = None
_socket: zmq.Socket[Any] | None = None


def regmsg_connect(
    address: str = "ipc:///var/run/regmsgd.sock", timeout: int = 5000
) -> RegMsgClient:
    """
    Compatibility function to connect to regmsgd.

    Args:
        address: IPC socket address for regmsgd
        timeout: Timeout in milliseconds for operations

    Returns:
        RegMsgClient instance ready for use
    """
    global _context, _socket
    client = RegMsgClient(address, timeout)
    client.connect()

    # Store references to maintain compatibility with old interface
    _context = client.context
    _socket = client.socket

    return client


def regmsg_send_message(message: str, timeout: int = 5000) -> str:
    """
    Compatibility function to send message to regmsgd.

    Args:
        message: Message to be sent
        timeout: Timeout in milliseconds for operations (optional)

    Returns:
        Response from regmsgd service
    """
    global _socket, _context

    # If already connected globally, use existing socket
    if _socket is not None and _context is not None:
        try:
            _socket.setsockopt(zmq.RCVTIMEO, timeout)
            _socket.setsockopt(zmq.SNDTIMEO, timeout)
            _socket.send_string(message)
            reply = _socket.recv_string()
            return reply
        except zmq.Again:
            raise RuntimeError(f"Timeout in communication with regmsgd (>{timeout}ms)")
        except zmq.error.ZMQError as e:
            raise RuntimeError(f"Error in communication with regmsgd: {str(e)}")
        except AttributeError:
            # Handle the case where socket methods are not available (is None)
            raise RuntimeError("Socket is None, cannot send/receive message")
        except Exception as e:
            raise RuntimeError(f"Unexpected error sending message: {str(e)}")
    else:
        # If no global connection exists, create temporarily
        with RegMsgClient(timeout=timeout) as client:
            return client.send_message(message)


def regmsg_disconnect() -> None:
    """Compatibility function to disconnect from regmsgd."""
    global _socket, _context

    if _socket is not None:
        try:
            _socket.close()
        except zmq.error.Again:
            pass
        except AttributeError:
            # Handle case where socket is None during close attempt
            pass
        _socket = None

    if _context is not None:
        try:
            _context.term()
        except zmq.error.Again:
            pass
        except AttributeError:
            # Handle case where context is None during term attempt
            pass
        _context = None


@contextlib.contextmanager
def regmsg_client(address: str = "ipc:///var/run/regmsgd.sock", timeout: int = 5000):
    """
    Context manager for safe usage of regmsg client.

    Args:
        address: IPC socket address for regmsgd
        timeout: Timeout in milliseconds for operations
    """
    client = RegMsgClient(address, timeout)
    try:
        client.connect()
        yield client
    finally:
        client.disconnect()
