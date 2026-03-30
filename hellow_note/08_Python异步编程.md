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

*整理自 LangGraph 学习过程中的异步编程讨论*
