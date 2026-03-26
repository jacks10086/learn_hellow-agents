# OpenAI 库学习笔记

## 一、基本调用

```python
from openai import OpenAI

client = OpenAI(
    api_key="xxx",
    base_url="xxx"  # 兼容 OpenAI 接口的服务地址
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "你好"}
    ]
)

print(response.choices[0].message.content)
```

---

## 二、调用链解析

```python
response = client.chat.completions.create(...)
#              │      │          │      │
#              │      │          │      └── 方法：创建聊天完成
#              │      │          └── 对象：完成结果
#              │      └── 对象：聊天
#              └── 客户端实例
```

---

## 三、messages 结构

### 三种角色

| role | 角色 | 作用 |
|------|------|------|
| `"system"` | 系统指令 | 设定 AI 的行为、性格 |
| `"user"` | 用户 | 你问的问题 |
| `"assistant"` | 助手 | AI 的回复 |

### 示例
```python
messages = [
    {"role": "system", "content": "你是一个Python导师"},
    {"role": "user", "content": "什么是装饰器？"},
    {"role": "assistant", "content": "装饰器是..."},
    {"role": "user", "content": "能举个例子吗？"},
]
```

### 为什么需要历史？
- AI 需要上下文理解你的问题
- 多轮对话必须带上完整历史

---

## 四、choices 结构

**choices 是回复列表，每个元素是一个可能的答案。**

```python
# 默认 n=1，只有一个选择
response.choices[0].message.content  # 获取回复

# 设置 n=3，生成 3 个不同答案
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    n=3
)

for choice in response.choices:
    print(choice.message.content)
```

### finish_reason
| 值 | 含义 |
|----|------|
| `"stop"` | 自然结束 |
| `"length"` | 达到 max_tokens |
| `"tool_calls"` | 工具调用 |

---

## 五、流式响应

### 非流式
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    stream=False
)
print(response.choices[0].message.content)  # 一次性输出
```

### 流式
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    stream=True
)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 区别
| 模式 | 访问方式 |
|------|----------|
| 非流式 | `.choices[0].message.content` |
| 流式 | `.choices[0].delta.content` |

---

## 六、工具调用（tool_calls）

**这是 Agent 的核心功能！**

### 定义工具
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取城市天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"]
            }
        }
    }
]
```

### 调用
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "北京天气？"}],
    tools=tools
)

if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    print(tool_call.function.name)       # "get_weather"
    print(tool_call.function.arguments)  # '{"city": "北京"}'
```

---

## 七、常用参数

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],

    temperature=0.7,      # 随机性 (0-2)
    max_tokens=1000,      # 最大生成长度
    top_p=0.9,            # 核采样
    n=1,                  # 生成几个回复
    stop=["结束"],        # 停止词
    stream=False,         # 是否流式
    tools=[...],          # 工具定义
)
```

### temperature
| 值 | 效果 | 适用场景 |
|----|------|----------|
| 0 - 0.3 | 确定性高 | 代码、数学 |
| 0.3 - 0.7 | 平衡 | 日常对话 |
| 0.7 - 2.0 | 创意性高 | 诗歌、创意 |

---

## 八、错误处理

```python
from openai import APIError, RateLimitError, APIConnectionError

try:
    response = client.chat.completions.create(...)
except RateLimitError:
    print("请求太频繁")
except APIConnectionError:
    print("网络连接失败")
except APIError as e:
    print(f"API 错误: {e}")
```
