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
