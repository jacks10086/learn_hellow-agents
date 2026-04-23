# Agent 框架设计方法笔记

> 基于 Chapter 7 文档，梳理 Agent 框架设计方法论

---

## 一、为什么自己造轮子？

### 1.1 现有框架痛点

| 痛点 | 现有框架问题 | 自建框架优势 |
|------|-------------|-------------|
| **过度抽象** | LangChain 学习十几个概念才能完成简单任务 | 只学核心概念，渐进式扩展 |
| **快速迭代导致不稳定** | API 频繁变化，升级后代码跑不通 | 完全掌控，稳定可控 |
| **黑盒实现** | 封装太紧，出问题只能等社区 | 每行代码都自己写，完全透明 |
| **依赖复杂** | 大量依赖包，安装冲突 | 只依赖 OpenAI SDK，轻量 |

### 1.2 核心价值

从"用户"变成"构建者"，真正理解 Agent 工作原理。

---

## 二、设计哲学：四个核心原则

```
┌─────────────────────────────────────────────────────────┐
│              HelloAgents 设计哲学                        │
├─────────────────────────────────────────────────────────┤
│  (1) 轻量 + 教学友好：只依赖 OpenAI SDK，无重依赖        │
│  (2) 基于标准 API：兼容 OpenAI 接口，易于迁移            │
│  (3) 渐进式学习路径：每章一个版本，可回溯                │
│  (4) 统一工具抽象：除 Agent 外，一切都是 Tool            │
└─────────────────────────────────────────────────────────┘
```

### 2.1 统一工具抽象

**关键洞察**：Memory、RAG、MCP 等模块，在其他框架是独立概念，在 HelloAgents 统一抽象为 Tool。

```python
# 其他框架：多个抽象层
Memory → Retriever → VectorStore → Embeddings ...

# HelloAgents：一切皆 Tool
Memory(Tool) → tool.run("recall=user_info")
RAG(Tool)    → tool.run("query=Python教程")
```

**好处**：消除不必要的抽象层，回归最直观的"Agent 调用工具"核心逻辑。

---

## 三、框架架构：三层结构

```
┌─────────────────────────────────────────────────────────┐
│                    应用层 agents/                        │
│  SimpleAgent | ReActAgent | ReflectionAgent | PlanAgent │
│  ← 继承 Agent 基类，实现不同策略                         │
├─────────────────────────────────────────────────────────┤
│                    核心层 core/                          │
│  Agent(ABC) | HelloAgentsLLM | Message | Config         │
│  ← 定义抽象接口、底层能力                                │
├─────────────────────────────────────────────────────────┤
│                    工具层 tools/                         │
│  Tool(ABC) | ToolRegistry | ToolChain | AsyncExecutor   │
│  ← 扩展能力、统一管理                                    │
└─────────────────────────────────────────────────────────┘
```

### 3.1 层级职责

| 层级 | 模块 | 职责 |
|------|------|------|
| 应用层 | agents/ | 业务逻辑，不同 Agent 策略实现 |
| 核心层 | core/ | 抽象接口、底层能力封装 |
| 工具层 | tools/ | 能力扩展、工具管理 |

### 3.2 依赖方向

```
应用层 → 核心层 → 工具层
    │         │
    └─────────┴───→ 上层依赖下层，下层不知道上层存在
```

---

## 四、设计切入点：迭代式方法

### 4.1 设计顺序

```
第1步：HelloAgentsLLM（LLM 客户端）
    ↓ 最底层能力，没有它 Agent 无法思考
第2步：多 Provider 支持 + 自动检测
    ↓ 兼容多厂商，零配置切换
第3步：核心接口（Message、Config、Agent基类）
    ↓ 数据结构 + 抽象接口
第4步：具体 Agent 实现（Simple → ReAct → Reflection → Plan）
    ↓ 不同策略实现
第5步：工具系统（Tool、Registry、Chain）
    ↓ 扩展 Agent 能力边界
```

### 4.2 顺序逻辑

| 顺序 | 模块 | 理由 |
|------|------|------|
| 1 | LLM 客户端 | 最底层能力，没有它 Agent 无法思考 |
| 2 | 消息/配置 | 数据结构，支撑上层逻辑 |
| 3 | Agent 基类 | 定义"什么是 Agent" |
| 4 | 具体 Agent | 实现"Agent 怎么工作" |
| 5 | 工具系统 | 扩展 Agent 能力边界 |

---

## 五、核心接口设计

### 5.1 HelloAgentsLLM：统一 LLM 接口

```python
class HelloAgentsLLM:
    # 设计决策：用 OpenAI SDK 作为底层
    # 理由：行业标准，所有厂商都兼容

    def __init__(self, provider="auto", ...):
        # 自动检测逻辑：环境变量 → base_url → api_key格式
        self.provider = self._auto_detect_provider()
        self.api_key, self.base_url = self._resolve_credentials()
        self._client = OpenAI(api_key, base_url)  # 核心就这一句

    def invoke(self, messages) -> str: ...       # 非流式
    def stream_invoke(self, messages) -> str: ... # 流式
```

**设计亮点**：
- `_auto_detect_provider()`：自动检测 Provider（环境变量 → URL → Key格式）
- `_resolve_credentials()`：根据 Provider 填充默认配置
- 用户只需 `HelloAgentsLLM()` 即可，零配置

### 5.2 Agent 基类：抽象接口

```python
class Agent(ABC):
    # 设计决策：用 ABC 强制子类实现 run()
    # 理由：保证所有 Agent 有统一入口

    def __init__(self, name, llm, system_prompt, config):
        self._history: list[Message] = []  # 内部状态

    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        pass  # 子类必须实现

    # 公共方法：历史管理
    def add_message(self, msg): ...
    def clear_history(self): ...
    def get_history(self): ...
```

**设计原则**：
- 抽象方法定义"必须做什么"
- 公共方法定义"可以做什么"
- C++ 类比：纯虚函数 + 普通成员函数

### 5.3 Message：标准化数据结构

```python
class Message(BaseModel):
    # 设计决策：用 Pydantic + Literal
    # 理由：类型安全 + 自动验证

    content: str
    role: Literal["user", "assistant", "system", "tool"]  # 限制四种角色
    timestamp: datetime = None      # 扩展字段
    metadata: Optional[Dict] = None # 预留扩展

    def to_dict(self) -> Dict:
        return {"role": self.role, "content": self.content}  # OpenAI 格式
```

**设计要点**：
- `Literal` 限制角色类型，防止拼写错误
- `to_dict()` 输出 OpenAI 兼容格式
- 额外字段（timestamp、metadata）为未来扩展预留

### 5.4 Config：配置管理

```python
class Config(BaseModel):
    default_model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    debug: bool = False
    max_history_length: int = 100

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量创建配置"""
        return cls(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            ...
        )
```

**设计要点**：
- 每个配置项有默认值，零配置可用
- `from_env()` 支持环境变量覆盖

---

## 六、Agent 策略实现模式

### 6.1 继承 + 重写 = 不同策略

```python
# SimpleAgent：最简单实现
class SimpleAgent(Agent):
    def run(self, input_text, **kwargs) -> str:
        messages = [{"role": "user", "content": input_text}]
        return self.llm.invoke(messages)

# ReActAgent：带工具调用
class ReActAgent(Agent):
    def __init__(self, name, llm, tool_registry, ...):
        self.tool_registry = tool_registry  # 额外依赖

    def run(self, input_text, **kwargs) -> str:
        while step < max_steps:
            response = self.llm.invoke(prompt)
            action = self._parse_action(response)
            if action == "Finish": return result
            observation = self.tool_registry.execute_tool(...)
            # 继续循环...
```

### 6.2 四种 Agent 策略

| Agent 类型 | 核心逻辑 | 适用场景 |
|-----------|---------|---------|
| SimpleAgent | 直接调用 LLM | 简单对话 |
| ReActAgent | 思考 → 行动 → 观察 → 循环 | 需要工具调用 |
| ReflectionAgent | 初答 → 反思 → 改进 | 需要自我优化 |
| PlanAndSolveAgent | 规划 → 逐步执行 | 复杂多步骤任务 |

### 6.3 设计模式：模板方法

```python
# 基类定义骨架
class Agent(ABC):
    def run(self, input_text, **kwargs) -> str:
        self._prepare()           # 准备阶段
        result = self._execute()  # 执行阶段（抽象）
        self._cleanup()           # 清理阶段
        return result

    @abstractmethod
    def _execute(self): ...

# 子类填充细节
class ReActAgent(Agent):
    def _execute(self):
        # ReAct 特定逻辑
        pass
```

---

## 七、工具系统设计

### 7.1 Tool 基类

```python
class Tool(ABC):
    @abstractmethod
    def run(self, params: Dict) -> str: ...

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]: ...

    def validate_parameters(self, params): ...  # 公共验证逻辑
```

### 7.2 ToolRegistry：两种注册方式

```python
class ToolRegistry:
    def register_tool(self, tool: Tool): ...           # 方式1：Tool对象
    def register_function(self, name, desc, func): ... # 方式2：函数
    def execute_tool(self, name, input_text): ...      # 统一执行入口

# 全局单例
global_registry = ToolRegistry()
```

### 7.3 设计意图

| 注册方式 | 适用场景 | 特点 |
|---------|---------|------|
| Tool 对象 | 复杂工具、多参数、需验证 | 结构化、可扩展 |
| 函数直接注册 | 简单工具、快速原型 | 轻量、便捷 |

---

## 八、设计决策总结

| 决策点 | 选择 | 理由 |
|--------|------|------|
| LLM 底层 | OpenAI SDK | 行业标准，兼容性最好 |
| Agent 接口 | ABC 抽象类 | 强制统一接口，便于扩展 |
| 消息格式 | Pydantic + Literal | 类型安全，自动验证 |
| 工具抽象 | Tool(ABC) + 函数两种方式 | 兼顾复杂与简单场景 |
| 工具管理 | 全局注册表 | 跨模块共享，无需传递 |
| Provider 切换 | 自动检测 + 手动指定 | 零配置 + 灵活控制 |
| 配置管理 | 环境变量 + 参数 | 部署友好 + 代码可控 |

---

## 九、从零设计 Agent 框架路径

```
┌─────────────────────────────────────────────────────────┐
│                  设计路径速查                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  第1步：定义核心概念                                     │
│  ├─ Agent 是什么？→ ABC 抽象基类                        │
│  ├─ LLM 怎么调？→ HelloAgentsLLM 统一接口               │
│  ├─ 消息怎么表示？→ Message + Pydantic                  │
│  └─ 配置从哪来？→ Config + 环境变量                     │
│                                                         │
│  第2步：实现底层能力                                     │
│  ├─ HelloAgentsLLM：多 Provider + 自动检测              │
│  └─ 异常处理：HelloAgentsException                      │
│                                                         │
│  第3步：定义扩展接口                                     │
│  ├─ Tool(ABC)：工具基类                                 │
│  └─ ToolRegistry：工具注册表                            │
│                                                         │
│  第4步：实现具体 Agent                                   │
│  ├─ SimpleAgent：最简单对话                              │
│  ├─ ReActAgent：思考 + 行动                             │
│  ├─ ReflectionAgent：自我反思                           │
│  └─ PlanAndSolveAgent：规划 + 执行                      │
│                                                         │
│  第5步：扩展能力                                         │
│  ├─ ToolChain：工具链                                   │
│  ├─ AsyncExecutor：异步执行                             │
│  └─ 内置工具：Calculator、Search...                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 十、C++/Qt 类比

| Python 框架 | Qt 框架 | 设计思路 |
|-------------|---------|----------|
| `Agent(ABC)` | `QAbstractItemModel` | 抽象基类定义接口 |
| `HelloAgentsLLM` | `QNetworkAccessManager` | 封装底层调用 |
| `ToolRegistry` | `QPluginLoader` | 管理扩展组件 |
| `Message` | `QVariant` | 数据载体 |
| `global_registry` | `QCoreApplication::instance()` | 全局单例 |

**共同点**：
- 抽象基类定义"是什么"
- 具体子类定义"怎么做"
- 管理器类负责"协调"

---

## 十一、关键洞察

### 11.1 框架设计本质

先定义概念（ABC），再实现能力（LLM/Tool），最后组合策略（Agent）。

### 11.2 HelloAgents 的独特价值

一切皆 Tool，消除了 Memory、RAG 等独立抽象层。

### 11.3 迭代式设计

不要一开始就追求完美，先实现 SimpleAgent 能跑起来，再逐步增强。

---

*整理自 Chapter 7 文档*
