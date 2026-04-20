# Python 进阶语法笔记

> 本章记录 Python 进阶语法，围绕 hello-agents 项目学习

---

## 一、类型注解进阶

### 1.1 TypedDict - 结构化字典

给字典的键指定类型，类似 C++ 的 struct：

```python
from typing import TypedDict

class SearchState(TypedDict):
    messages: list           # 对话历史
    user_query: str          # 用户查询
    final_answer: str        # 最终答案
```

**本质**：运行时仍是普通 dict，只是给 IDE 和类型检查器看的"说明书"。

### 1.2 Annotated - 类型元数据

给类型附加额外信息，供框架读取：

```python
from typing import Annotated

# 基本语法
Age = Annotated[int, "必须 >= 0 且 <= 150"]

# LangGraph 中的用法
class State(TypedDict):
    messages: Annotated[list, add_messages]  # add_messages 是 reducer 函数
```

**核心用途**：框架读取元数据做特殊处理（如 LangGraph 用 `add_messages` 合并消息列表）。

### 1.3 Literal - 字面量类型

限制变量只能是特定的几个值：

```python
from typing import Literal

Provider = Literal['openai', 'deepseek', 'modelscope']

def set_provider(p: Provider):
    print(p)

set_provider('deepseek')  # ✅
set_provider('unknown')   # ⚠️ 类型检查警告
```

**类比 C++**：类似枚举 `enum`，但值直接是字符串/数字。

---

## 二、函数参数进阶

### 2.1 *args 和 **kwargs

```python
def func(*args, **kwargs):
    print(f"args: {args}")      # 元组
    print(f"kwargs: {kwargs}")  # 字典

func(1, 2, 3, name="张三", age=25)
# args: (1, 2, 3)
# kwargs: {'name': '张三', 'age': 25}
```

### 2.2 混合写法（最佳实践）

```python
class MyLLM(HelloAgentsLLM):
    def __init__(
        self,
        model: Optional[str] = None,    # 显式定义常用参数
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs                         # 其他参数透传给父类
    ):
        super().__init__(**kwargs)
```

**好处**：
- 显式参数 → IDE 代码提示友好
- **kwargs → 灵活透传，父类改参数子类不用改

### 2.3 怎么知道 **kwargs 里面有什么？

**问题**：使用 **kwargs 时，怎么知道传了哪些参数？

**方法1：调试时直接打印**

```python
def my_func(**kwargs):
    print(f'kwargs 类型: {type(kwargs)}')  # <class 'dict'>
    print(f'kwargs 内容: {kwargs}')        # {'name': '张三', 'age': 25}
    print(f'所有键: {kwargs.keys()}')      # dict_keys(['name', 'age'])
```

**方法2：看源码追踪**

```python
# hello-agents 项目中的追踪链
SimpleAgent.stream_run(**kwargs)
    ↓
HelloAgentsLLM.stream_invoke(messages, **kwargs)
    ↓
OpenAI client.chat.completions.create(
    temperature=kwargs.get('temperature'),  # 从 kwargs 取值
    max_tokens=kwargs.get('max_tokens'),
    **kwargs  # 其他参数透传
)
```

**方法3：用 .get() 取已知参数**

```python
def invoke(self, messages, **kwargs):
    # 从 kwargs 中取已知参数，没有就用默认值
    temperature = kwargs.get('temperature', 0.7)
    max_tokens = kwargs.get('max_tokens', 4096)

    # 其他参数透传
    other_params = {k: v for k, v in kwargs.items()
                    if k not in ['temperature', 'max_tokens']}
```

**方法4：文档注释说明**

```python
def stream_run(self, input_text: str, **kwargs):
    '''
    流式运行 Agent

    Args:
        input_text: 用户输入
        **kwargs: 透传给 LLM 的参数
            - temperature: 温度参数 (0-2)
            - max_tokens: 最大输出 token 数
            - top_p: 核采样参数
    '''
    pass
```

### 2.4 kwargs 的三种处理方式

| 方式 | 代码 | 说明 |
|------|------|------|
| 取值 | `kwargs.get('key', default)` | 安全取值，可设默认值 |
| 解包 | `func(**kwargs)` | 整体传给另一个函数 |
| 过滤 | `{k:v for k,v in kwargs.items() if ...}` | 筛选后使用 |

**最佳实践**：常用参数显式定义 + kwargs 透传其他

```python
def invoke(
    self,
    messages: list,
    temperature: float = 0.7,      # 显式定义，IDE 有提示
    max_tokens: int = 4096,
    **kwargs                        # 其他参数透传
):
    # 已知参数直接用
    print(f'temperature: {temperature}')
    # 其他参数透传
    other = kwargs  # {'top_p': 0.9, ...}
```

---

## 三、数据结构

### 3.1 四大结构对比

| 类型 | 符号 | 特点 | C++ 类比 |
|------|------|------|---------|
| `list` | `[]` | 可变、有序 | `std::vector` |
| `tuple` | `()` | 不可变、有序 | `std::array` |
| `dict` | `{}` | 键值对 | `std::map` |
| `set` | `{}` | 无序、唯一 | `std::set` |

### 3.2 实战用法

```python
# List：动态数据收集
messages = []
messages.append({"role": "user", "content": "你好"})

# Tuple：固定结构返回值
def get_credentials():
    return "api_key", "https://api.example.com"

api_key, base_url = get_credentials()  # 解包

# Dict：配置和消息
config = {"model": "gpt-4", "temperature": 0.7}

# Set：去重
ids = [1, 2, 2, 3, 3, 4]
unique = list(set(ids))  # [1, 2, 3, 4]
```

### 3.3 返回类型注解

```python
def _resolve_credentials(...) -> tuple[str, str]:
    return api_key, base_url
```

---

## 四、内置函数

### 4.1 all() 和 any()

```python
# all()：全部为真才返回 True
all([True, True, True])   # True
all([True, False, True])  # False

# any()：任一为真就返回 True
any([False, False, True])  # True
any([False, False, False]) # False

# 实战：检查多个配置是否存在
if not all([self.api_key, self.base_url]):
    raise ValueError("缺少配置")

# 实战：检查是否包含特定端口
if any(port in url for port in [":8080", ":7860", ":5000"]):
    print("本地服务")
```

### 4.2 生成器表达式

```python
# 用 () 是生成器（惰性求值，高效）
any(x in text for x in [a, b, c])

# 用 [] 是列表推导式（全部计算，效率低）
any([x in text for x in [a, b, c]])
```

---

## 五、空值判断

### 5.1 Python 中的"空"

| 值 | 类型 | 布尔值 |
|---|------|--------|
| `None` | NoneType | False |
| `""` | str | False |
| `[]` | list | False |
| `{}` | dict | False |
| `0` | int | False |
| `False` | bool | False |

### 5.2 判断方式

```python
# 判断是否为 None（精确）
if x is None:

# 判断是否为空（通用）
if not x:

# 判断是否非空
if x:
```

### 5.3 None vs 空容器

```python
result = None      # 还没有结果
result = []        # 查到了，但没有数据

# 区分场景
if result is None:
    print("查询失败")
elif not result:
    print("没有数据")
else:
    print(f"找到 {len(result)} 条")
```

---

## 六、环境变量与 dotenv

### 6.1 系统环境变量 vs .env 文件

```python
import os
from dotenv import load_dotenv

# 系统环境变量：直接读取
path = os.getenv("PATH")

# .env 文件：需要先加载
load_dotenv()  # 加载到内存
api_key = os.getenv("LLM_API_KEY")  # 现在可以读到了
```

### 6.2 优先级

1. 直接传入的参数
2. 系统环境变量
3. .env 文件中的值

---

## 七、第七章项目结构

```
code/chapter7/
│
├── .env                    # 环境变量配置
├── my_llm.py               # 自定义 LLM 客户端
├── my_simple_agent.py      # 自定义简单 Agent
├── my_react_agent.py       # 自定义 ReAct Agent
├── my_calculator_tool.py   # 自定义工具
├── test_xxx.py             # 测试文件
```

### 7.1 HelloAgentsLLM 的意义

```
OpenAI SDK（底层）        →  需要手动配置所有参数
    ↓
HelloAgentsLLM（封装层）  →  自动配置 + 简化接口
    ↓
MyLLM（自定义层）         →  可进一步扩展
```

### 7.2 provider 的定位

| 角色 | 价值 |
|------|------|
| 预设模板 | ✅ 自动填充 base_url 和默认模型 |
| 必须依赖 | ❌ 限制了灵活性 |

**正确理解**：provider 是便利层，真正重要的是 `api_key` + `base_url` + `model`。

---

## 八、ABC 模块（抽象基类）

### 8.1 核心概念

`ABC` = Abstract Base Class（抽象基类），用于定义**不能直接实例化的类**，强制子类实现特定方法。

**类比 C++ 纯虚函数**：

```cpp
// C++
class Animal {
public:
    virtual void speak() = 0;  // 纯虚函数
};

Animal a;  // ❌ 编译错误！
```

```python
# Python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

a = Animal()  # ❌ TypeError!
```

### 8.2 实际应用（hello_agents）

```python
# core/agent.py
class Agent(ABC):
    """Agent基类，所有 Agent 必须实现 run 方法"""

    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        """运行Agent"""
        pass

# 子类必须实现 run()
class SimpleAgent(Agent):
    def run(self, input_text: str, **kwargs) -> str:
        return self.llm.invoke(input_text)

# 不实现会报错
class BadAgent(Agent):
    pass

BadAgent()  # ❌ TypeError: 必须实现 run()
```

### 8.3 ABC 的价值

| 价值 | 说明 |
|------|------|
| 强制规范 | 子类必须实现特定方法 |
| 接口定义 | 定义"有什么方法"，不关心"怎么实现" |
| 提前发现错误 | 实例化时检查，而非运行时 |

**对比**：

```
不用 ABC：运行时才发现缺少方法
用 ABC：创建实例时就报错
```

### 8.4 抽象方法 vs 普通方法

```python
from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def run(self, input_text: str) -> str:
        '''抽象方法：子类必须实现'''
        pass

    @abstractmethod
    def validate(self, input_text: str) -> bool:
        '''抽象方法：子类必须实现'''
        pass

    # 普通方法：子类可以直接用，也可以覆盖
    def add_message(self, message):
        '''普通方法：提供默认实现'''
        print(f'添加消息: {message}')

    # 钩子方法：子类可以覆盖，也可以不覆盖
    def before_run(self):
        '''钩子方法：可选实现'''
        pass

# 子类只需实现抽象方法
class SimpleAgent(Agent):
    def run(self, input_text: str) -> str:
        self.before_run()  # 可选调用钩子
        return f'回答: {input_text}'

    def validate(self, input_text: str) -> bool:
        return len(input_text) > 0
```

### 8.5 实战场景

**场景1：插件系统**

```python
from abc import ABC, abstractmethod

class Plugin(ABC):
    name: str

    @abstractmethod
    def execute(self, data: dict) -> dict:
        '''执行插件'''
        pass

    @abstractmethod
    def validate(self, data: dict) -> bool:
        '''验证输入'''
        pass

    def log(self, msg: str):
        '''公共方法'''
        print(f'[{self.name}] {msg}')

class DataCleaner(Plugin):
    name = 'DataCleaner'

    def validate(self, data: dict) -> bool:
        return 'text' in data

    def execute(self, data: dict) -> dict:
        self.log('清理数据')
        return {'text': data['text'].strip()}

# 使用
plugins = [DataCleaner()]
for p in plugins:
    if p.validate(data):
        data = p.execute(data)
```

**场景2：工具基类（hello_agents tools）**

```python
class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        '''工具名称'''
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        '''工具描述'''
        pass

    @abstractmethod
    def run(self, *args, **kwargs) -> str:
        '''执行工具'''
        pass

    def to_openai_schema(self) -> dict:
        '''公共方法：生成 OpenAI 工具定义'''
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
            }
        }

class Calculator(Tool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "执行数学计算"

    def run(self, expression: str) -> str:
        return str(eval(expression))
```

### 8.6 什么时候用 ABC？

| 场景 | 用 ABC | 不用 ABC |
|------|--------|---------|
| 框架基类 | ✅ 强制子类实现关键方法 | - |
| 插件系统 | ✅ 定义插件接口 | - |
| 简单继承 | - | ✅ 只是共享代码 |
| Mixin 类 | - | ✅ 只添加功能 |

### 8.7 ABC 速查表

```python
from abc import ABC, abstractmethod

# 1. 继承 ABC
class MyAbstractClass(ABC):

    # 2. 用 @abstractmethod 标记必须实现的方法
    @abstractmethod
    def must_implement(self):
        pass

    # 3. 普通方法子类可以直接用
    def common_method(self):
        print('公共实现')

    # 4. @property + @abstractmethod = 抽象属性
    @property
    @abstractmethod
    def name(self) -> str:
        pass

# 5. 子类必须实现所有抽象方法才能实例化
class Concrete(MyAbstractClass):
    @property
    def name(self) -> str:
        return "concrete"

    def must_implement(self):
        return "实现"
```

---

## 九、项目模块划分设计

### 9.1 hello_agents 项目架构

```
hello_agents/
│
├─ core/                   # 核心层（底层能力）
│   ├─ llm.py             # LLM 客户端
│   ├─ agent.py           # Agent 基类
│   ├─ message.py         # 消息类
│   └─ config.py          # 配置类
│
├─ agents/                 # 智能体层（业务逻辑）
│   ├─ simple_agent.py
│   ├─ react_agent.py
│   └─ reflection_agent.py
│
├─ tools/                  # 工具层（基础设施）
│   ├─ base.py            # 工具基类
│   ├─ registry.py        # 工具注册表
│   └─ builtin/           # 内置工具
│
└─ utils/                  # 工具函数层
    ├─ logging.py
    └─ helpers.py
```

### 9.2 模块划分原则

| 原则 | 说明 | 实践 |
|------|------|------|
| 单一职责 | 每个模块只做一件事 | `llm.py` 只管 LLM 调用 |
| 分层架构 | 上层依赖下层 | `agents` → `core` → `utils` |
| 开闭原则 | 扩展开放，修改关闭 | 继承基类添加新 Agent |
| 依赖倒置 | 依赖抽象而非具体 | Agent 依赖 LLM 接口 |

### 9.3 分层依赖关系

```
agents/     ← 上层：业务逻辑
    ↓ 依赖
core/       ← 中层：核心能力
    ↓ 依赖
tools/      ← 下层：基础设施
utils/      ← 底层：通用工具
```

**原则**：上层依赖下层，下层不知道上层存在。

### 9.4 设计示例：智能客服系统

```
smart_customer_service/
│
├─ core/                   # 核心层
│   ├─ llm.py             # LLM 客户端
│   └─ config.py          # 配置
│
├─ agents/                 # 智能体层
│   ├─ chat_agent.py      # 对话 Agent
│   └─ router_agent.py    # 路由 Agent
│
├─ knowledge/              # 知识库模块
│   ├─ retriever.py       # 检索器
│   └─ vector_store.py    # 向量存储
│
├─ tools/                  # 工具层
│   ├─ order_query.py     # 查订单
│   └─ logistics.py       # 查物流
│
└─ api/                    # API 层
    └─ routes.py          # FastAPI 路由
```

### 9.5 常见模块划分模式

**模式一：按技术分层**
```
project/
├─ api/          # 接口层
├─ service/      # 业务逻辑层
├─ repository/   # 数据访问层
└─ model/        # 数据模型
```

**模式二：按业务领域**
```
project/
├─ user/         # 用户模块
├─ order/        # 订单模块
├─ product/      # 商品模块
└─ payment/      # 支付模块
```

**模式三：按功能职责（hello_agents 采用）**
```
project/
├─ core/         # 核心能力
├─ agents/       # 业务实体
├─ tools/        # 工具组件
└─ utils/        # 辅助功能
```

---

## 十、C++/Qt 对比速查

| Python | C++ | Qt |
|--------|-----|-----|
| `None` | `nullptr` | `nullptr` |
| `list` | `std::vector` | `QList` |
| `dict` | `std::map` | `QMap` |
| `tuple` | `std::array` | - |
| `set` | `std::set` | `QSet` |
| `Literal` | `enum` | - |
| `TypedDict` | `struct` | - |
| `ABC` + `@abstractmethod` | 纯虚函数 `= 0` | `QAbstractXxx` |
| `async/await` | `QFuture` | `QEventLoop` |
| `yield` | 协程/迭代器 | - |
| `@classmethod` | 静态方法 | - |
| `@staticmethod` | 静态方法 | - |

---

## 十一、VSCode 常用快捷键

| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 快速打开文件 | `Ctrl + P` | 输入文件名搜索 |
| 全局搜索 | `Ctrl + Shift + F` | 在所有文件中搜索 |
| 转到定义 | `F12` | 跳转到定义处 |
| 命令面板 | `Ctrl + Shift + P` | 执行各种命令 |
| 打开文件夹 | `Ctrl + K, Ctrl + O` | 打开新目录 |
| 切换侧边栏 | `Ctrl + B` | 显示/隐藏资源管理器 |

---

## 十二、yield 生成器

### 12.1 yield vs return

| | return | yield |
|--|--------|-------|
| 执行 | 函数结束 | 函数暂停 |
| 返回 | 一次性返回所有 | 逐个返回 |
| 内存 | 占用大 | 省内存 |

```python
# return：一次返回
def get_list():
    return [1, 2, 3]

# yield：逐个返回
def get_generator():
    yield 1
    yield 2
    yield 3

# 使用
for num in get_generator():
    print(num)
```

### 12.2 yield from 透传

```python
def outer():
    yield 'start'
    yield from inner()  # 透传 inner 的所有 yield
    yield 'end'

def inner():
    yield 'a'
    yield 'b'

list(outer())  # ['start', 'a', 'b', 'end']
```

### 12.3 LLM 流式输出应用

```python
def stream_invoke(self, messages, **kwargs):
    '''流式调用 LLM'''
    for chunk in self.llm.stream(messages):
        yield chunk  # 逐块返回

# 使用
for chunk in agent.stream_run("你好"):
    print(chunk, end='')  # 实时显示
```

**好处**：
- 用户实时看到内容
- 省内存
- 可随时中断

---

## 十三、invoke 和 stream_invoke 设计

### 13.1 对比

| 方法 | 返回 | 适用场景 |
|------|------|---------|
| `invoke` | 完整响应 | 后台任务、API 服务 |
| `stream_invoke` | 逐块响应 | 用户对话、实时体验 |

### 13.2 代码解析

```python
# invoke：非流式，一次返回
def invoke(self, messages, **kwargs):
    response = self._client.chat.completions.create(
        model=self.model,
        messages=messages,
        temperature=kwargs.get('temperature', self.temperature),
        max_tokens=kwargs.get('max_tokens', self.max_tokens),
        **{k: v for k, v in kwargs.items()
           if k not in ['temperature', 'max_tokens']}
    )
    return response.choices[0].message.content

# stream_invoke：流式，逐块返回
def stream_invoke(self, messages, **kwargs):
    temperature = kwargs.get('temperature')
    yield from self.think(messages, temperature)
```

### 13.3 kwargs 处理模式

```python
# 优先级：用户传入 > 实例默认值
temperature=kwargs.get('temperature', self.temperature)

# 过滤已处理参数，透传其他
**{k: v for k, v in kwargs.items()
   if k not in ['temperature', 'max_tokens']}
```

---

## 十四、方法重写添加参数

### 14.1 参数提升模式

```python
# 基类：**kwargs 兜底
class Agent(ABC):
    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        pass

# 子类：提升参数为显式定义
class MyAgent(Agent):
    def run(self, input_text: str, max_iterations: int = 3, **kwargs):
        # 可以直接用 max_iterations
        pass
```

### 14.2 为什么可以这样？

基类 `**kwargs` 接收任意参数，子类可以把常用参数"提升"为显式参数。

**调用方式都兼容**：

```python
agent.run("hello")                      # 用默认值
agent.run("hello", max_iterations=5)    # 显式传值
agent.run("hello", temperature=0.7)     # 透传其他参数
```

### 14.3 设计意义

不同子类需要不同参数，基类不需要预知所有参数：

```python
SimpleAgent.run(input_text, **kwargs)
ReActAgent.run(input_text, max_iterations=3, **kwargs)
PlanAgent.run(input_text, max_steps=5, **kwargs)
```

---

## 十五、LLM 消息四种角色

### 15.1 角色定义

| 角色 | 谁发的 | 作用 |
|------|--------|------|
| `system` | 开发者 | 设定 AI 行为规则 |
| `user` | 用户 | 用户输入 |
| `assistant` | AI | AI 回复 |
| `tool` | 工具 | 工具执行结果 |

### 15.2 消息流程

```
1. system: "你是一个助手"
2. user: "北京天气"
3. assistant: [决定调用工具] + tool_calls
4. tool: "北京 25°C，晴"
5. assistant: "北京今天天气晴朗"
```

### 15.3 tool 角色的意义

**为什么需要 tool 角色？**

AI 需要区分"我说的"和"工具返回的数据"：

```
assistant: "我需要查天气"    ← AI 思考
tool: "北京 25°C"           ← 工具数据（可信）
assistant: "北京今天 25°C"  ← AI 基于数据回答
```

**ReAct Agent 的核心**：

```
思考 → 行动(tool_calls) → 观察(tool角色返回) → 继续思考
```

---

## 十六、今日学习总结

### 16.1 Python 语法

| 主题 | 核心理解 |
|------|---------|
| `**kwargs` | 字典打包，`.get()` 取值，透传用 `**kwargs` |
| `@classmethod` | 工厂方法，`cls` 指向类 |
| `ABC` | 抽象基类，强制子类实现方法 |
| `yield` | 生成器，暂停执行，逐个返回 |
| 参数提升 | 子类可以把 kwargs 参数提升为显式参数 |

### 16.2 Pydantic BaseModel

| 主题 | 核心理解 |
|------|---------|
| `BaseModel` | 数据验证 + 序列化 |
| `@field_validator` | 单字段验证，用 `cls` |
| `@model_validator` | 多字段联合验证 |
| 工厂方法 | `@classmethod` 定义 `from_env()` 等 |

### 16.3 项目设计

| 主题 | 核心理解 |
|------|---------|
| 模块划分 | 单一职责、分层架构、依赖倒置 |
| invoke/stream_invoke | 非流式/流式两种调用方式 |
| LLM 消息角色 | system/user/assistant/tool 四种角色 |

---

## 十七、ABC vs BaseModel 使用场景对比

### 17.1 核心区别

| 工具 | 关注点 | 核心能力 |
|------|--------|---------|
| `ABC` | **行为**（方法） | 强制子类实现方法 |
| `BaseModel` | **数据**（字段） | 验证、序列化 |

### 17.2 使用场景选择

**只用 ABC**：
```python
# 关注"能做什么"（行为）
class Tool(ABC):
    @abstractmethod
    def run(self, *args, **kwargs) -> str:
        pass

class Calculator(Tool):
    def run(self, expression: str) -> str:
        return str(eval(expression))
```

**只用 BaseModel**：
```python
# 关注"数据是什么"（字段）
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

msg = Message(role="user", content="你好")  # 验证通过
```

**ABC + BaseModel 组合**：
```python
# 既要数据验证，又要强制行为
class MessageBase(BaseModel, ABC):
    role: Literal["user", "assistant"]
    content: str

    @abstractmethod
    def format(self) -> str:
        pass

class UserMessage(MessageBase):
    def format(self) -> str:
        return f"[用户] {self.content}"
```

### 17.3 选择指南

| 需求 | 选择 |
|------|------|
| 只关心"能做什么" | ABC |
| 只关心"数据是什么" | BaseModel |
| 两者都要 | BaseModel + ABC 多继承 |

### 17.4 hello_agents 项目的设计选择

```python
# ✅ 工具基类：只用 ABC（关注行为）
class Tool(ABC):
    @abstractmethod
    def run(self, *args, **kwargs) -> str:
        pass

# ✅ 消息类：只用 BaseModel（关注数据）
class Message(BaseModel):
    role: str
    content: str

# ✅ Agent 基类：只用 ABC（关注行为）
class Agent(ABC):
    @abstractmethod
    def run(self, input_text: str) -> str:
        pass

# ✅ 配置类：只用 BaseModel（关注数据验证）
class Config(BaseModel):
    debug: bool = False
    temperature: float = Field(ge=0, le=2)
```

**设计原则**：不强制统一，根据职责选择合适的工具。

### 17.5 速查表

```
┌───────────────────────────────────────────────────────────────────────┐
│                    ABC vs BaseModel 选择速查                           │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  【只用 ABC】                                                          │
│  ├─ 纯行为接口（不需要数据验证）                                        │
│  ├─ 工具基类、插件系统、Agent 基类                                      │
│  └─ 例：Tool、Agent、Plugin                                           │
│                                                                       │
│  【只用 BaseModel】                                                    │
│  ├─ 纯数据模型（不需要强制方法）                                        │
│  ├─ API 请求/响应、配置类、消息类                                       │
│  └─ 例：Message、Config、User                                         │
│                                                                       │
│  【ABC + BaseModel 组合】                                              │
│  ├─ 既要数据验证，又要强制行为                                          │
│  ├─ 领域模型、复杂业务对象                                              │
│  └─ 例：Document（需要验证字段 + 必须实现 render 方法）                  │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 十八、生成器表达式 + all() 函数

### 18.1 语法解析

```python
all(param in parameters for param in required_params)
```

**分步理解**：

1. `for param in required_params` → 遍历每个参数名
2. `param in parameters` → 检查是否在参数字典中，返回 True/False
3. `all(...)` → 所有结果都为 True 才返回 True

### 18.2 等价写法

```python
# 生成器表达式（推荐，省内存）
all(param in parameters for param in required_params)

# 列表推导式（创建中间列表）
all([param in parameters for param in required_params])

# 传统写法
def check_all():
    for param in required_params:
        if param not in parameters:
            return False
    return True
```

### 18.3 `in` 的两种含义

```python
all(param in parameters for param in required_params)
#        ↑ 第一个 in：成员检查（返回 True/False）
#                              ↑ 第二个 in：循环遍历
```

---

## 十九、类属性 vs 实例属性

### 19.1 核心区别

| | 类属性 | 实例属性 |
|--|--------|---------|
| 定义位置 | 类名下 | `__init__` 里用 `self.xxx` |
| 访问方式 | `Class.attr` 或 `self.attr` | `self.attr` |
| 内存 | 所有实例**共享**一份 | 每个实例**各自**一份 |
| C++ 类比 | `static` 静态成员 | 普通成员变量 |

### 19.2 代码对比

```python
class Dog:
    species = "犬科"  # 类属性（共享）

    def __init__(self, name):
        self.name = name  # 实例属性（独立）

dog1 = Dog("旺财")
dog2 = Dog("大黄")

Dog.species = "哺乳动物"  # 修改类属性，所有实例都变
print(dog1.species)  # 哺乳动物
print(dog2.species)  # 哺乳动物

dog1.name = "小黑"  # 修改实例属性，只影响自己
print(dog1.name)    # 小黑
print(dog2.name)    # 大黄（不变）
```

### 19.3 Pydantic 特例

Pydantic 用类属性语法定义字段，但自动转换为实例属性：

```python
class User(BaseModel):
    name: str  # 看起来是类属性，实际变成实例属性

u1 = User(name="张三")
u2 = User(name="李四")
# u1.name 和 u2.name 互不影响
```

### 19.4 选择指南

| 场景 | 用类属性 | 用实例属性 |
|------|---------|-----------|
| 常量/配置 | ✅ `PI = 3.14` | ❌ |
| 计数器 | ✅ `count = 0` | ❌ |
| Pydantic 模型 | ✅ 特殊处理 | ❌ |
| 每个实例独立的值 | ❌ | ✅ `self.name` |
| 运行时创建的数据 | ❌ | ✅ `self._tools = {}` |

---

## 二十、tools 模块设计

### 20.1 模块职责

| 文件 | 职责 | 类比 |
|------|------|------|
| `base.py` | 定义"工具是什么" | 接口定义 |
| `registry.py` | 管理"有哪些工具" | 容器/管理器 |

### 20.2 架构图

```
base.py                          registry.py
┌─────────────────────┐          ┌─────────────────────┐
│ ToolParameter       │          │ ToolRegistry        │
│ (BaseModel)         │          │                     │
│ - name, type, desc  │          │ - _tools: dict      │
│                     │          │ - _functions: dict  │
│ Tool (ABC)          │          │                     │
│ - name, description │◄─────────│ register_tool()     │
│ - run() [抽象]      │   注册   │ execute_tool()      │
│ - get_parameters()  │          │ get_tools_desc()    │
│ - validate_params() │          └─────────────────────┘
│ - to_dict()         │
└─────────────────────┘
```

### 20.3 两种注册方式

| 方式 | 方法 | 适用场景 |
|------|------|---------|
| Tool 对象 | `register_tool(Tool实例)` | 复杂工具、参数验证、多参数 |
| 函数直接 | `register_function(name, desc, func)` | 简单工具、快速原型 |

### 20.4 全局注册表

```python
# registry.py 末尾
global_registry = ToolRegistry()
```

**作用**：模块级单例，整个项目共享同一个注册表。

```python
# 文件 A
from hello_agents.tools import global_registry
global_registry.register_tool(tool)

# 文件 B（同一个注册表）
from hello_agents.tools import global_registry
global_registry.execute_tool('tool_name')  # ✅ 能找到
```

**原理**：Python 模块只加载一次，模块级变量天然是单例。

---

## 二十一、今日学习总结

### 21.1 Python 语法进阶

| 主题 | 核心理解 |
|------|---------|
| 生成器表达式 | `(x for x in iter)` 省内存，配合 `all()`/`any()` |
| 类属性 vs 实例属性 | 类名下 vs `self.xxx`；共享 vs 独立 |
| `in` 两种用法 | 成员检查 vs 循环遍历 |

### 21.2 项目设计

| 主题 | 核心理解 |
|------|---------|
| ABC vs BaseModel | 行为接口 vs 数据验证，按需选择 |
| tools 模块 | base.py 定义接口，registry.py 管理实例 |
| 注册表模式 | 统一管理工具，动态注册/执行 |
| 全局注册表 | 模块级单例，跨文件共享 |

---

## 二十二、Callable 类型注解

### 22.1 基本语法

```python
from typing import Callable

Callable[[参数类型...], 返回类型]
```

**含义**：描述一个**可调用对象**（函数、lambda、带 `__call__` 的类）的类型。

### 22.2 常见形式

| 类型 | 含义 | 示例 |
|------|------|------|
| `Callable[[str], str]` | 接收 str，返回 str | `lambda s: s.upper()` |
| `Callable[[int, int], int]` | 接收两个 int，返回 int | `lambda a, b: a + b` |
| `Callable[[], str]` | 无参数，返回 str | `lambda: "hello"` |
| `Callable[..., Any]` | 任意参数，任意返回 | 通用函数 |
| `Callable` | 任意可调用对象 | 不限定签名 |

### 22.3 实际应用

**作为参数类型**：

```python
from typing import Callable

def apply_func(func: Callable[[str], str], value: str) -> str:
    '''func 必须是：接收 str，返回 str'''
    return func(value)

# 使用
result = apply_func(lambda s: s.upper(), "hello")
print(result)  # HELLO
```

**在注册表中**：

```python
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable[[str], str]] = {}

    def register(self, name: str, func: Callable[[str], str]):
        self._tools[name] = func

    def execute(self, name: str, arg: str) -> str:
        return self._tools[name](arg)
```

### 22.4 C++ 类比

```cpp
// C++ std::function
std::function<std::string(std::string)> func;

// Python Callable
Callable[[str], str]
```

### 22.5 核心价值

| 价值 | 说明 |
|------|------|
| 类型安全 | IDE 检查传入的函数是否符合预期 |
| 代码提示 | IDE 知道这个参数是一个函数 |
| 文档化 | 一眼看出函数接收什么、返回什么 |

---

## 二十三、enumerate 内置函数

### 23.1 核心作用

在遍历时**同时获取索引和值**。

```python
# 基本用法
fruits = ['apple', 'banana', 'cherry']
for i, fruit in enumerate(fruits):
    print(i, fruit)
# 0 apple
# 1 banana
# 2 cherry

# 指定起始索引
for i, fruit in enumerate(fruits, start=1):
    print(i, fruit)
# 1 apple
# 2 banana
# 3 cherry
```

### 23.2 C++ 对比

```cpp
// C++ 传统写法
for (int i = 0; i < steps.size(); i++) {
    auto& step = steps[i];
    std::cout << i << ": " << step << std::endl;
}

# Python 写法（等价但更简洁）
for i, step in enumerate(steps):
    print(f"{i}: {step}")
```

### 23.3 返回值

```python
e = enumerate(['a', 'b', 'c'])
print(list(e))
# [(0, 'a'), (1, 'b'), (2, 'c')]  # 返回 (索引, 值) 元组
```

### 23.4 常用场景

| 场景 | 写法 |
|------|------|
| 遍历列表带索引 | `for i, item in enumerate(lst)` |
| 显示步骤进度 | `f"步骤 {i+1}/{len(lst)}"` |
| 修改列表元素 | `for i, val in enumerate(lst): lst[i] = val * 2` |

---

## 二十四、字符串 format 方法

### 24.1 基本语法

```python
# 位置占位符
template = "你好，{}，欢迎来到{}"
result = template.format("张三", "北京")
# "你好，张三，欢迎来到北京"

# 命名占位符（项目中使用）
template = "搜索关键词：{keyword}，数量：{count}"
result = template.format(keyword="天气", count=5)
# "搜索关键词：天气，数量：5"
```

### 24.2 **kwargs 解包

```python
context = {"keyword": "天气", "count": 5}

# 不用解包（繁琐）
"{keyword} - {count}".format(keyword=context["keyword"], count=context["count"])

# 用 ** 解包（简洁）
"{keyword} - {count}".format(**context)
# 自动把字典键值展开成关键字参数
```

### 24.3 三种格式化方式对比

```python
name, age = "张三", 25

# 1. % 格式化（老式）
"姓名：%s，年龄：%d" % (name, age)

# 2. format 方法（Python 2.6+）
"姓名：{}，年龄：{}".format(name, age)
"姓名：{n}，年龄：{a}".format(n=name, a=age)

# 3. f-string（Python 3.6+，最推荐）
f"姓名：{name}，年龄：{age}"
```

**选择指南**：

| 场景 | 推荐 |
|------|------|
| 模板内容硬编码 | f-string（最简洁） |
| 模板来自配置/用户输入 | `format(**dict)` |
| 兼容旧版本 | `%` 格式化 |

---

## 二十五、Optional 类型注解

### 25.1 核心作用

表示返回值**可能为 None**。

```python
from typing import Optional

def get_chain_info(self, name: str) -> Optional[Dict[str, Any]]:
    # 返回值可能是：Dict 或 None
```

### 25.2 为什么用 Optional？

```python
# 不用 Optional（返回 Dict）
def get_chain_info(self, name: str) -> Dict[str, Any]:
    # 如果链不存在，必须返回空字典 {} 或抛异常
    # 无法区分"没找到"和"找到空结果"

# 用 Optional
def get_chain_info(self, name: str) -> Optional[Dict[str, Any]]:
    if name not in self.chains:
        return None  # 明确表达"没找到"
    return {...}     # 找到了，返回字典
```

### 25.3 三种处理"没找到"的方式

| 方式 | Python 示例 | 适用场景 |
|------|-------------|----------|
| 返回 `None` | `Optional[Dict]` | 需要区分"没找到"和"找到空结果" |
| 返回空容器 | `return {}` | 调用者只需迭代，不关心是否有数据 |
| 抛异常 | `raise KeyError()` | "没找到"是异常情况 |

### 25.4 C++ 类比

```cpp
// C++17 std::optional
std::optional<QVariantMap> getChainInfo(const QString& name) {
    if (!chains.contains(name)) {
        return std::nullopt;  // 对应 Python 的 None
    }
    return chainToMap(chains[name]);  // 对应 Python 的 Dict
}
```

### 25.5 Python 3.10+ 新写法

```python
# 旧写法
from typing import Optional
def func() -> Optional[Dict[str, Any]]: ...

# 新写法（Python 3.10+）
def func() -> Dict[str, Any] | None: ...
