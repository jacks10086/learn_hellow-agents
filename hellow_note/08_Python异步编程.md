# Python 异步编程笔记

> 基于 C++/Qt 背景理解 Python 异步编程

---

## 一、核心概念对比

| Python | C++/Qt 类比 | 说明 |
|--------|------------|------|
| `async def` | 返回 `QFuture` 的函数 | 定义异步函数 |
| `await` | 等待 `QFuture` 结果 | 非阻塞等待 |
| `asyncio.run()` | 启动 `QEventLoop` | 启动事件循环 |
| `asyncio.gather()` | 多个 `QFuture` 并发 | 并发执行多个任务 |
| `asyncio.Lock` | `std::mutex` / `QMutex` | 协程锁 |

---

## 二、同步 vs 异步

### 2.1 执行方式对比

```python
# 同步：逐个执行，阻塞等待
def sync_task():
    time.sleep(1)  # 整个线程卡住
    return "结果"

# 异步：并发执行，等待时可切换
async def async_task():
    await asyncio.sleep(1)  # 让出控制权，可执行其他协程
    return "结果"
```

### 2.2 性能对比

| 场景 | 同步耗时 | 异步耗时 |
|------|---------|---------|
| 10 个 API 请求（各 1 秒） | 10 秒 | ~1 秒 |
| 100 个 API 请求（各 1 秒） | 100 秒 | ~1-2 秒 |

**适用场景**：
- ✅ I/O 密集型：网络请求、文件读写、数据库查询
- ❌ CPU 密集型：大量计算（用多进程）

---

## 三、协程基础

### 3.1 async/await 语法

```python
import asyncio

# 定义协程函数
async def my_coroutine():
    await asyncio.sleep(1)
    return "结果"

# 调用协程函数 → 返回协程对象（不会执行！）
coro = my_coroutine()  # 得到 coroutine 对象

# 必须用 await 或 asyncio.run 来执行
result = await my_coroutine()  # 在 async 函数内
asyncio.run(my_coroutine())    # 程序入口
```

### 3.2 常见陷阱

```python
async def func():
    return "结果"

# ❌ 错误：直接调用不会执行
result = func()  # 得到 coroutine 对象，没有执行！

# ✅ 正确：await 执行
result = await func()
```

---

## 四、核心 API

### 4.1 asyncio.gather() - 并发执行

```python
async def main():
    # 并发执行多个任务
    results = await asyncio.gather(
        task1(),
        task2(),
        task3(),
    )
    # results = [结果1, 结果2, 结果3]
```

### 4.2 asyncio.create_task() - 后台任务

```python
async def main():
    # 创建后台任务，立即返回
    task = asyncio.create_task(background_work())

    # 做其他事情
    await do_something_else()

    # 需要时等待结果
    result = await task
```

### 4.3 asyncio.wait_for() - 超时控制

```python
try:
    result = await asyncio.wait_for(
        fetch_data(),
        timeout=5.0
    )
except asyncio.TimeoutError:
    print("请求超时")
```

### 4.4 asyncio.Semaphore - 并发限制

```python
async def fetch_with_limit(urls, max_concurrent=5):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_one(url):
        async with semaphore:  # 获取许可
            return await fetch(url)

    tasks = [fetch_one(url) for url in urls]
    return await asyncio.gather(*tasks)
```

---

## 五、异步 IO 操作

### 5.1 aiohttp - 异步 HTTP 客户端

```python
import aiohttp

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def fetch_multiple(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.get(url) for url in urls
        ]
        responses = await asyncio.gather(*tasks)
        return [await r.text() for r in responses]
```

### 5.2 aiofiles - 异步文件操作

```python
import aiofiles

async def read_file(path):
    async with aiofiles.open(path, 'r') as f:
        return await f.read()

async def write_file(path, content):
    async with aiofiles.open(path, 'w') as f:
        await f.write(content)
```

---

## 六、竞态条件与锁

### 6.1 问题：跨 await 读写共享变量

```python
cnt = 0

async def bad_func():
    global cnt
    temp = cnt
    await asyncio.sleep(0)  # ← 切换点！其他协程可能修改 cnt
    cnt = temp + 1          # ← 用旧值覆盖，数据丢失！
```

**执行结果**：100 次调用，cnt 可能只有 1！

### 6.2 解决方案

#### 方案 1：单行原子操作（推荐）

```python
cnt = 0

async def good_func():
    global cnt
    cnt = cnt + 1  # Python 单行赋值是原子的，不需要锁
```

**原理**：Python 有 GIL，单行赋值不会被中断。

#### 方案 2：asyncio.Lock（必要时）

```python
cnt = 0
lock = asyncio.Lock()

async def safe_func():
    global cnt
    # 先做耗时操作（锁外）
    await do_async_work()

    # 只在操作共享状态时加锁
    async with lock:
        cnt = cnt + 1
```

### 6.3 锁粒度原则

```python
# ❌ 锁范围太大 → 变成串行
async with lock:
    await fetch_data()   # 耗时操作在锁内
    cnt += 1

# ✅ 只锁关键部分 → 保持并发
await fetch_data()       # 耗时操作在锁外
async with lock:
    cnt += 1             # 只锁共享状态访问
```

**原则**：
- 锁 = 交通信号灯
- ❌ 锁整个函数 = 整条路封死
- ✅ 只锁关键部分 = 只在路口设红绿灯

---

## 七、企业级用法

### 7.1 连接池管理

```python
import aiohttp

class HttpClient:
    """单例 HTTP 客户端，带连接池"""

    _instance = None
    _session: aiohttp.ClientSession = None

    async def get_session(self):
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,           # 总连接数上限
                limit_per_host=10,   # 每 host 连接数上限
            )
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
            )
        return self._session

    async def get(self, url):
        session = await self.get_session()
        async with session.get(url) as resp:
            return await resp.json()

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
```

### 7.2 重试机制

```python
async def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await fetch(url)
        except Exception as e:
            if attempt < max_retries - 1:
                # 指数退避
                wait = 1 * (2 ** attempt)
                await asyncio.sleep(wait)
            else:
                raise
```

### 7.3 优雅关闭

```python
import signal

class Application:
    def __init__(self):
        self.running = True

    def shutdown(self):
        self.running = False

    async def run(self):
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.shutdown)

        while self.running:
            await do_work()
```

---

## 八、速查表

```python
import asyncio

# 1. 定义协程
async def func():
    await asyncio.sleep(1)
    return "结果"

# 2. 并发执行
results = await asyncio.gather(func(), func(), func())

# 3. 限流
semaphore = asyncio.Semaphore(5)
async with semaphore:
    await do_work()

# 4. 超时
result = await asyncio.wait_for(func(), timeout=5)

# 5. 后台任务
task = asyncio.create_task(func())
result = await task

# 6. 启动
asyncio.run(main())
```

---

## 九、常见问题

### Q1: 什么时候用异步？

| 场景 | 用异步 | 用多线程/多进程 |
|------|--------|----------------|
| 网络请求 | ✅ | ❌ |
| 文件 IO | ✅ | ❌ |
| 数据库查询 | ✅ | ❌ |
| CPU 密集计算 | ❌ | ✅ 多进程 |

### Q2: 单线程也有竞态条件？

**是的！** 虽然异步是单线程，但 `await` 点会切换协程：

```python
temp = cnt
await something()  # ← 切换点
cnt = temp + 1     # ← 可能被其他协程的更新覆盖
```

### Q3: 什么时候需要锁？

```python
# 不需要锁
cnt = cnt + 1  # 单行赋值，原子操作

# 需要锁
temp = cnt
await something()  # 跨 await 读写
cnt = temp + 1
```

---

## 十、与 C++/Qt 的思维映射

| Qt | Python asyncio |
|----|----------------|
| `QEventLoop` | `asyncio.run()` |
| `QFuture<T>` | `coroutine` 对象 |
| `future.result()` | `await coroutine` |
| `QtConcurrent::run()` | `asyncio.create_task()` |
| `QMutex` | `asyncio.Lock` |
| `QSemaphore` | `asyncio.Semaphore` |

**核心区别**：
- Qt 多线程：任务可能在不同线程执行
- Python 异步：单线程内切换，更轻量

---

## 十一、常见疑问解答

### Q1: 每次 asyncio.run() 是同一个协程吗？

**不是！** 每次调用 `asyncio.run()` 都是全新、独立、隔离的：

- 全新的事件循环
- 全新的协程对象
- 数据、状态、内存完全不共享

```python
import asyncio

count = 0

async def add():
    global count
    count += 1
    print(count)

asyncio.run(add())  # 输出 1
asyncio.run(add())  # 输出 1（不是 2！）
```

**类比**：像打开两次 cmd 运行程序，完全独立。

---

### Q2: 单线程和多线程如何区分？

| | 单线程 | 多线程 |
|--|--------|--------|
| 执行方式 | 一条流水线排队执行 | 多条流水线同时执行 |
| 同一时间 | 只能做一件事 | 能做多件事 |
| 变量冲突 | 不会有 | 需要加锁 |

**JavaScript 的特殊情况**：
- JS 引擎本身是单线程的
- 但浏览器/Node 底层是 C++ 写的多线程程序
- JS 可以"委托"后台线程处理网络请求、定时器等

**类比**：你（JS主线程）在前台接单，后厨（浏览器后台线程）做菜，做完通知你。

---

### Q3: Python 也是单线程语言吗？

**不是！** Python 天生支持多线程，但有 GIL 限制。

| | JavaScript | Python |
|--|------------|--------|
| 语言设计 | 单线程 | 多线程 |
| 能否创建线程 | 不能（只能浏览器开） | 能 |
| GIL 锁 | 无 | 有 |

**GIL（全局解释器锁）**：同一时刻只允许一个线程执行 Python 字节码。

**影响**：
- IO 密集型：多线程有用（等待时 GIL 会释放）
- CPU 密集型：多线程没用（无法多核并行），要用多进程

---

### Q4: IO 密集型用协程就够了，多线程还有什么用？

**答：很多库不支持 async！**

```python
# 同步阻塞函数，asyncio 拿它没办法
def sync_get_data():
    requests.get("https://baidu.com")  # 会阻塞整个事件循环！
```

**解决方案**：用线程跑同步代码

```python
async def test():
    # 同步函数丢到线程里跑，不阻塞事件循环
    await asyncio.to_thread(requests.get, "https://baidu.com")
```

---

### Q5: 多线程和多进程怎么选？

| 场景 | 方案 |
|------|------|
| CPU 密集型（大量计算） | 多进程（绕过 GIL，利用多核） |
| IO 密集型 + 同步老代码 | 多线程（兼容老库） |
| IO 密集型 + 异步 async | 协程（最佳） |

**口诀**：计算多 → 多进程，等待多 → 多线程/协程

---

### Q6: asyncio 事件循环和 Qt 主循环一样吗？

**几乎一模一样！**

| Qt 主循环 | asyncio 事件循环 |
|-----------|-----------------|
| 检查鼠标、键盘、网络事件 | 检查 IO 完成、定时器、协程就绪 |
| 有事件就处理 | 有事件就处理 |
| 处理时不能阻塞 | 处理时不能阻塞 |

**共同点**：单线程、无限循环、事件驱动、不能跑阻塞代码。

**唯一区别**：Qt 处理 GUI 事件，asyncio 处理 IO/协程事件。

---

### Q7: 如何判断 IO 操作是同步还是异步？

**一眼判断规则**：

| 特征 | 异步（不阻塞） | 同步（阻塞） |
|------|---------------|-------------|
| 函数定义 | `async def` | `def` |
| 调用方式 | `await func()` | `func()` |
| 库名 | aiohttp, asyncpg | requests, pymysql |

**常见库对比**：

| 同步阻塞 | 异步非阻塞 |
|---------|-----------|
| requests | aiohttp |
| pymysql | asyncpg |
| redis-py | redis-py async |
| openai（同步） | openai（async） |

**判断口诀**：
```
async + await = 异步不阻塞
普通 def 无 await = 同步必阻塞
```

---

### Q8: 库不支持 async 是指没有实现资源锁吗？

**不是！和锁无关！**

"不支持 async" = 函数是阻塞式 IO，调用时死等，不交出控制权。

**类比**：
- 异步函数：像会举手的学生，"老师我先等资料，你叫别人" → 不耽误课堂
- 同步函数：像霸占黑板的学生，"我没写完谁都别上来" → 全班卡死

---

### Q9: requests.get() 不能加 await 吗？

**不能！加了直接报错！**

```python
import requests

async def test():
    await requests.get("https://www.baidu.com")  # TypeError!
```

**原因**：`requests.get()` 返回 `Response` 对象，不是协程对象，不能 `await`。

**正确做法**：丢到线程里跑

```python
async def test():
    result = await asyncio.to_thread(requests.get, "https://www.baidu.com")
```

**口诀**：异步函数才能 await，同步函数不能加，加了直接报语法错。

---

*整理自 LangGraph 学习过程中的异步编程讨论*
