import socket
import multiprocessing
import threading
from threading import Thread


def process_conn(cnn: socket.socket, add):
    # 这个连接是从哪里来的
    print('connect from {}'.format(add))
    while True:
        try:
            # 从目标连接接收消息
            data = cnn.recv(1024).decode()
            # 打印消息
            print('{} say {}'.format(add, data))
            # 反馈,已经收到消息
            cnn.send(b'OK')
        except ConnectionAbortedError:
            print(f"连接关闭{add}")
            return


if __name__ == '__main__':
    s = socket.socket()
    s.bind(('127.0.0.1', 9090))
    s.listen(5)
    thread_list = []
    while True:
        # 阻塞 等待一个TCP连接
        con, add = s.accept()
        # 开启一个新进程 处理 TCP连接
        thread = Thread(target=process_conn, args=(con, add))
        thread.start()
        #
        thread_list.append(thread)
