"""
Python异步编程 测试
"""
import concurrent.futures
import random
import time
import asyncio
import types


def test_pool():
    number_list = list(range(1, 11))

    def count(number: int):
        i = 0
        for i in range(0, 10000000):
            i += 1
        return i * number

    def evaluate(item):
        result_item = count(item)
        print('item:{} result:{}'.format(item, result_item))

    start_time = time.perf_counter()
    for item in number_list:
        evaluate(item)
    print('顺序执行耗时:{}'.format(time.perf_counter() - start_time))

    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for item in number_list:
            executor.submit(evaluate, item)
    print('线程池执行耗时:{}'.format(time.perf_counter() - start_time))

    start_time = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        for item in number_list:
            executor.submit(evaluate, item)
    print('进程池执行耗时:{}'.format(time.perf_counter() - start_time))
    time.sleep(20)


def test_asyncio_event_loop():
    def task_a(end_time, loop):
        print('task a called')
        time.sleep(random.randint(0, 5))
        if (loop.time() + 1) < end_time:
            loop.call_later(1, task_b, end_time, loop)
        else:
            loop.stop()

    def task_b(end_time, loop):
        print('task b called')
        time.sleep(random.randint(3, 7))
        if (loop.time() + 1) < end_time:
            loop.call_later(1, task_c, end_time, loop)
        else:
            loop.stop()

    def task_c(end_time, loop):
        print('task c called')
        time.sleep(random.randint(5, 10))
        if (loop.time() + 1) < end_time:
            loop.call_later(1, task_a, end_time, loop)
        else:
            loop.stop()

    # 获取一个当前事件循环
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    # 定义事件循环的结束时间
    end_loop = loop.time() + 60
    # 立刻开始调用 task_a 进
    loop.call_soon(task_a, end_loop, loop)
    # 一直run 知道 loop.stop()被调用
    loop.run_forever()
    # 关闭事件循环
    loop.close()


def test_asyncio_coroutine():
    @asyncio.coroutine
    def start_state():
        print('start state called')
        input_value = random.randint(0, 1)
        time.sleep(1)
        if input_value == 0:
            result = yield from state2(input_value)  # 等待协程state2 完成任务
        else:
            result = yield from state1(input_value)  # 等待协程state3完成任务
        print('resume of transition:\nstart state calling {}\n'.format(result))

    @asyncio.coroutine
    def state1(transition_value: int) -> str:
        output_value = 'state1 with transition_value:{}'.format(transition_value)
        input_value = random.randint(0, 1)
        print('evaluating.......')
        if input_value == 0:
            result = yield from state3(input_value)
        else:
            result = yield from state2(input_value)
        return output_value + 'state1 calling {}'.format(result)

    @asyncio.coroutine
    def state2(transition_value: int) -> str:
        output_value = 'state2 with transition_value:{}'.format(transition_value)
        input_value = random.randint(0, 1)
        print('evaluating.......')
        if input_value == 0:
            result = yield from state1(input_value)
        else:
            result = yield from state3(input_value)
        return output_value + 'state2 calling {}\n'.format(result)

    @asyncio.coroutine
    def state3(transition_value: int) -> str:
        output_value = 'state2 with transition_value:{}'.format(transition_value)
        input_value = random.randint(0, 1)
        print('evaluating.......')
        if input_value == 0:
            result = yield from state1(input_value)
        else:
            result = yield from end_state(input_value)
        return output_value + 'state2 calling {}\n'.format(result)

    @asyncio.coroutine
    def end_state(transition_value: int) -> str:
        output_value = 'end state with transition:{}'.format(transition_value)
        print('stop computation....')
        return output_value

    print('finite state machine simulation with asyncio coroutine')
    loop = asyncio.get_event_loop()
    # 等待协程return
    loop.run_until_complete(start_state())


def test_asyncio_coroutine_py38():
    async def s1():
        # 等待协程完成任务 此时s1不会阻塞.. 会一边凉快去
        print(await s2())

    async def s2():
        return "dad"

    loop = asyncio.get_event_loop()
    loop.run_until_complete(s1())


def test_asyncio_task_coroutine():
    async def factorial(number: int):
        f, i = 1, 0
        for i in range(2, number + 1):
            print('Asyncio Task: Compute factorial({})'.format(i))
            await asyncio.sleep(1)
            f *= 1
        print('Asyncio Task - factorial({})'.format(i))

    async def fibonacci(number: int):
        a, b = 0, 1
        for i in range(number):
            print('Asyncio Task: Compute fibonacci({})'.format(i))
            await asyncio.sleep(1)
            a, b = b, a + b
        print('Asyncio Task: Compute fibonacci({}) = {}'.format(number, a))

    async def binomial_coefficient(n, k):
        result = 1
        for i in range(1, k + 1):
            result = result * (n - i + 1) / i
            print('Asyncio Task: Compute binomial_coefficient({})'.format(i))
            await asyncio.sleep(1)
        print('Asyncio Task: Compute binomial_coefficient({},{}) = {}'.format(n, k, result))

    # 需要并行计算的函数
    task_list = [
        asyncio.Task(factorial(10)),
        asyncio.Task(fibonacci(10)),
        asyncio.Task(binomial_coefficient(20, 10)),
    ]
    loop = asyncio.get_event_loop()
    # 直到任务都完成
    loop.run_until_complete(asyncio.wait(task_list))
    loop.close()


def test_asyncio_future(num1, num2):
    async def first_coroutine(future: asyncio.Future, num):
        count = 0
        for i in range(1, num + 1):
            count += 1
        await asyncio.sleep(1)
        future.set_result('First coroutine (sum of N integers) result = {}'.format(count))

    async def second_coroutine(future, num):
        count = 1
        for i in range(1, num + 1):
            count *= 1
        await asyncio.sleep(2)
        future.set_result('Second coroutine (factorial) result = {}'.format(count))

    def get_result(future):
        print(future.result())

    loop = asyncio.get_event_loop()
    # 定义两个future
    future1 = asyncio.Future()
    future2 = asyncio.Future()

    tasks = [
        first_coroutine(future1, num1),
        second_coroutine(future2, num2)
    ]
    # 为future增加回调函数
    future1.add_done_callback(get_result)
    future2.add_done_callback(get_result)

    # 执行任务
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == '__main__':
    # test_pool()
    # test_asyncio_event_loop()
    # test_asyncio_coroutine()
    # test_asyncio_coroutine_py38()
    # test_asyncio_task_coroutine()
    test_asyncio_future(3, 3)
