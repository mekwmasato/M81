import socket
import threading

IPADDR = "127.0.0.1"
PORT = 49152

sock_sv = socket.socket(socket.AF_INET)
sock_sv.bind((IPADDR, PORT))
sock_sv.listen()

# クライアントのリスト
client_list = []

def recv_client(sock, addr):
    while True:
        try:
            data = sock.recv(1024)
            if data == b"":
                break

            print("$ say client:{}".format(addr))

            # 受信データを全クライアントに送信
            for client in client_list:
                client[0].send(data)

        except ConnectionResetError:
            break

    # クライアントリストから削除
    client_list.remove((sock, addr))
    print("- close client:{}".format(addr))

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

# クライアント接続待ちループ
while True:
    sock_cl, addr = sock_sv.accept()
    # クライアントをリストに追加
    client_list.append((sock_cl, addr))
    print("+ join client:{}".format(addr))

    thread = threading.Thread(target=recv_client, args=(sock_cl, addr))
    thread.start()