import socket


def main():
    s = socket.socket()
    try:
        s.connect(('127.0.0.1', 9090))
    except ConnectionRefusedError:
        print('Server 未接受连接请求')
        return
    while True:
        data = input('请输入:')
        try:
            s.send(data.encode('utf-8'))
            print(s.recv(1024).decode())
        except ConnectionResetError:
            print('连接已关闭')
            return


if __name__ == '__main__':
    main()
