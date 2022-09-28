"""
测试多线程并行的demo py文件
"""
import logging
import threading
import time
import random
from queue import Queue

logging.basicConfig(level=logging.INFO)


def test_semaphore():
    """
    使用信号量 进行线程同步
    :return:
    """
    semaphore = threading.Semaphore(0)
    item = 0

    def consumer():
        logging.info('consumer:{} is waiting'.format(threading.currentThread()))
        semaphore.acquire()
        logging.info('Consumer notify:item number{}'.format(item))

    def producer():
        time.sleep(3)
        item = random.randint(0, 1000)
        logging.info('Producer:{} notify: item number{}'.format(threading.currentThread(), item))
        semaphore.release()

    for i in range(0, 10):
        t1 = threading.Thread(target=consumer)
        t2 = threading.Thread(target=producer)

        t1.start()
        t2.start()

        t1.join()
        t2.join()


def test_condition():
    """
    使用条件进行线程同步
    :return:
    """
    items = []
    condition = threading.Condition()

    class Consumer(threading.Thread):
        def __init__(self, *args, **kwargs):
            super(Consumer, self).__init__(*args, **kwargs)

        def consume(self):
            with condition:
                if len(items) == 0:
                    logging.info('no items to consume')
                    condition.wait()

                items.pop()
                logging.info('consumed one item')
                condition.notify()

        def run(self) -> None:
            for i in range(20):
                time.sleep(2)
                self.consume()

    class Producer(threading.Thread):
        def __init__(self, *args, **kwargs):
            super(Producer, self).__init__(*args, **kwargs)

        def produce(self):
            with condition:
                if len(items) == 10:  # 若 列表满了 则等待 通知
                    logging.info('items produced {} Stopped'.format(items))
                    condition.wait()
                # 通知到达 / 没满 则生成一个
                items.append(1)
                logging.info('total items {}'.format(len(items)))
                condition.notify()

        def run(self) -> None:
            for i in range(20):
                time.sleep(0.5)
                self.produce()

    consumer = Consumer()
    producer = Producer()
    consumer.start()
    producer.start()

    consumer.join()
    producer.join()


def test_event():
    """
    使用事件进行线程同步
    :return:
    """
    items = []
    event = threading.Event()

    class Consumer(threading.Thread):
        def __init__(self, *args, **kwargs):
            super(Consumer, self).__init__(*args, **kwargs)

        def run(self) -> None:
            while True:
                time.sleep(2)
                event.wait()  # 等待事件
                item = items.pop()
                logging.info('Consumer notify:{} popped by:{}'.format(item, self.name))

    class Producer(threading.Thread):
        def __init__(self, *args, **kwargs):
            super(Producer, self).__init__(*args, **kwargs)

        def run(self) -> None:
            for i in range(20):
                time.sleep(2)
                item = random.randint(0, 1000)
                items.append(item)
                logging.info('Producer notify: item {} appended by {}'.format(item, self.name))

                event.set()  # 设置事件

                event.clear()  # 清除事件

    producer = Producer()
    consumer = Consumer()

    producer.start()
    consumer.start()

    producer.join()
    consumer.join()


def test_barrier():
    """
    使用屏障进行事件同步
    :return:
    """
    num_runner = 3
    finish_line = threading.Barrier(num_runner)
    runners = ['A', 'B', 'C']

    def runner():
        name = runners.pop()
        time.sleep(random.randrange(2, 5))
        print('%s reached the barrier at: %s \n' % (name, time.ctime()))
        finish_line.wait()  # 当前线程到达 终点 阻塞 等待 所有线程 都到达终点 才会停止阻塞

    threads = []
    print('start race!!')
    for i in range(num_runner):
        threads.append(threading.Thread(target=runner))
        threads[-1].start()
    for thread in threads:
        thread.join()  # 登台线程 执行结束
    print('race over')


def test_queue():
    """
    使用队列的线程同步
    :return:
    """

    class Producer(threading.Thread):
        def __init__(self, queue):
            super(Producer, self).__init__()
            self.queue: Queue = queue

        def run(self) -> None:
            for i in range(5):
                time.sleep(2)
                item = random.randint(0, 256)
                self.queue.put(item)# 会在内部wait
                print(f'Producer notify: item:{item} put to queue by {self.name}')

    class Consumer(threading.Thread):
        def __init__(self, queue):
            super(Consumer, self).__init__()

            self.queue: Queue = queue

        def run(self) -> None:
            while True:
                time.sleep(2)
                item = self.queue.get()#会在内部wait
                print(f'Consumer notify: {item} popped from queue by {self.name}')
                self.queue.task_done()#

    queue = Queue()
    t1 = Producer(queue)
    t2 = Producer(queue)
    t3 = Consumer(queue)
    t4 = Consumer(queue)

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()


if __name__ == '__main__':
    # test_condition()
    # test_semaphore()
    # test_event()
    # test_barrier()
    test_queue()
