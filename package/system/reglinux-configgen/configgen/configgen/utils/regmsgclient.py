import zmq

# Global context and socket (optional; could also be kept inside a class)
context = None
socket = None

def regmsg_connect(address="ipc:///var/run/regmsgd.sock"):
    global context, socket
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(address)

def regmsg_send_message(message: str) -> str:
    if socket is None:
        raise RuntimeError("Socket not connected. Call connect() first.")
    socket.send_string(message)
    reply = socket.recv_string()
    return reply

def regmsg_disconnect():
    global socket, context
    if socket:
        socket.close()
        socket = None
    if context:
        context.term()
        context = None

