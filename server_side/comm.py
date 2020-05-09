from time import sleep
HEADER = 64
FORMAT = 'utf-8'
MAX = 150

# without header
def receive_msg(conn):
    try:
        msg = conn.recv(MAX).decode(FORMAT).strip()
        if msg:
            return msg
    except:
        print("[ERROR] Can't receive msg")
    return False
    
def send(conn, msg):
    message = msg.encode(FORMAT)
    message += b' ' * (MAX - len(message))
    try:
        conn.send(message)
    except:
        print('[ERROR] failure to send message:'+msg)

# wiht header
def receive_msg1(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        try:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            return msg
        except:
            sleep(0.01)
            print("[ERROR] Can't receive msg")
    return False

def send1(conn, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    try:
        conn.send(send_length)
        conn.send(message)
    except:
        print('[ERROR] failure to send message:'+msg)