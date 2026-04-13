# Pydantic BaseModel 学习笔记

> Pydantic 是 Python 数据验证库，使用类型提示定义数据模式，提供快速可扩展的验证。
>
> 新版的python 越来越接近静态编译语言，或者说往这方面走

---

## 一、核心概念

### 1.1 BaseModel 是什么？

`BaseModel` 是 Pydantic 的核心类，用于：
- **数据验证**：自动检查字段类型（int/str/list 等严格检查）
- **类型转换**：能转换的自动转换（`"25"` → `25`、`"true"` → `True`）
- **序列化**：==与 JSON/dict 互转==
- 字段约束（长度、范围、正则、邮箱、URL 等）
- 嵌套模型、枚举、Optional、默认值
- 配置管理（BaseSettings）
- 自动生成 OpenAPI / JSON Schema（FastAPI 内置）

### 1.2 与普通类对比

```python
# 普通 Python 类 - 无验证
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

user = User(name=123, age="abc")  # ✅ 不报错

# Pydantic BaseModel - 有验证
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

user = User(name=123, age="abc")  # ❌ ValidationError!
```

---

## 二、字段定义

### 2.1 基础字段

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int                      # 必填
    name: str = "匿名"           # 有默认值，非必填
    email: Optional[str] = None  # 可选字段
    created_at: datetime | None = None  # Python 3.10+ 语法
```

### 2.2 Field() - 字段约束

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0, description="价格，非负数")
    quantity: int = Field(gt=0, le=1000, default=1)
    tags: list[str] = Field(default_factory=list)  # 可变默认值用 default_factory

# 常用约束
# 字符串: min_length, max_length, pattern (正则)
# 数值: ge (>=), gt (>), le (<=), lt (<), multiple_of
# 列表: min_length, max_length
```

### 2.3 特殊类型

```python
from pydantic import BaseModel, EmailStr, HttpUrl, PostgresDsn
from uuid import UUID

class Config(BaseModel):
    email: EmailStr        # 自动验证邮箱格式
    website: HttpUrl       # 自动验证 URL 格式
    db_url: PostgresDsn    # PostgreSQL 连接字符串
    user_id: UUID          # UUID 格式
```

---

## 三、验证方法

### 3.1 创建实例的方式

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

# 方式1：关键字参数
user1 = User(id=1, name="张三")

# 方式2：字典解包
data = {"id": 2, "name": "李四"}
user2 = User(**data)

# 方式3：model_validate（Python 对象）
user3 = User.model_validate(data)

# 方式4：model_validate_json（JSON 字符串）
json_str = '{"id": 3, "name": "王五"}'
user4 = User.model_validate_json(json_str)

# 方式5：model_validate_strings（字符串字典）
str_data = {"id": "4", "name": "赵六"}  # 字符串值
user5 = User.model_validate_strings(str_data)  # 自动转换
```

### 3.2 验证错误处理

```python
from pydantic import ValidationError

try:
    user = User(id="abc", name=123)
except ValidationError as e:
    print(e.error_count())      # 错误数量
    print(e.errors())           # 错误列表
    for error in e.errors():
        print(f"字段: {error['loc'][0]}")
        print(f"错误: {error['msg']}")
        print(f"输入: {error['input']}")
```

---

## 四、自定义验证器

### 4.1 @field_validator - 单字段验证器

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    age: int

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('姓名不能为空')
        return v.strip()

    @field_validator('age')
    @classmethod
    def age_must_be_reasonable(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError('年龄必须在 0-150 之间')
        return v
```

### 4.1.1 疑问：为什么到处看到 cls 和 @classmethod？

**核心理解**：

```python
# cls 就是当前类
# 凡是 @classmethod / @model_validator / @field_validator
# 第一个参数必须写 cls
```

**self vs cls 对比**：

| 名称 | 用在 | 指向 | C++ 类比 |
|------|------|------|---------|
| `self` | 实例方法 | 实例对象 | `this` 指针 |
| `cls` | 类方法 | 类本身 | 静态成员函数 |

```python
class Demo:
    class_var = '类属性'

    # 实例方法 - 用 self
    def instance_method(self):
        print(self.name)        # 访问实例属性
        print(self.class_var)   # 也可以访问类属性

    # 类方法 - 用 cls
    @classmethod
    def class_method(cls):
        print(cls.class_var)    # 只能访问类属性
        # print(cls.name)       # ❌ 不能访问实例属性
```

**为什么验证器用 cls 而不是 self？**

1. 验证发生在**创建实例之前**，还没有 `self`
2. 验证器可能需要访问**类级别的配置**（如 `cls.ALLOWED_ROLES`）
3. 这是**工厂模式**的一种体现

**@classmethod 必须写吗？**

```python
# 写法1：显式写（推荐，意图清晰）
@field_validator('name')
@classmethod
def validate_name(cls, v: str) -> str:
    return v

# 写法2：省略（也可以，Pydantic V2 自动处理）
@field_validator('name')
def validate_name(cls, v: str) -> str:
    return v
```

**结论**：Pydantic V2 会自动把 `@field_validator` 装饰的函数变成类方法，所以 `@classmethod` 可以省略，但写上更清晰。

### 4.1.2 疑问：from_env 用 @classmethod，to_dict 却不用？

**核心区别**：创建实例 vs 操作实例

```python
class Config(BaseModel):
    debug: bool = False

    # 工厂方法 - 创建实例（还没有实例）
    @classmethod
    def from_env(cls):
        return cls(debug=os.getenv('DEBUG') == 'true')

    # 实例方法 - 操作实例（已经有实例了）
    def to_dict(self):
        return self.model_dump()
```

**时间线理解**：

```
1. 类存在（还没有实例）
   │
   │  Config.from_env()  ← @classmethod，创建实例
   ↓
2. 实例被创建
   │
   │  config = Config.from_env()
   ↓
3. 实例存在（可以操作实例）
   │
   │  config.to_dict()  ← 实例方法，访问 self.debug
   ↓
4. 返回结果
```

**记忆口诀**：

```
创建实例 → 没有 self → 用 cls（类方法）
使用实例 → 有 self → 用 self（实例方法）
```

**类比**：
- `from_env` = 工厂的**生产线**（生产产品）
- `to_dict` = 产品的**功能**（产品能做什么）

### 4.1.3 工厂方法模式

**什么是工厂方法？**

当有多种方式创建实例时，用 `@classmethod` 定义工厂方法：

```python
class Config(BaseModel):
    debug: bool = False
    log_level: str = 'INFO'

    # 工厂方法1：从环境变量创建
    @classmethod
    def from_env(cls):
        return cls(
            debug=os.getenv('DEBUG') == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
        )

    # 工厂方法2：从文件创建
    @classmethod
    def from_file(cls, path: str):
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

    # 工厂方法3：从字典创建
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

# 使用 - 语义清晰
config1 = Config.from_env()
config2 = Config.from_file('config.json')
config3 = Config.from_dict({'debug': True})
```

**为什么用 @classmethod 而不是 @staticmethod？**

```python
# @classmethod - 子类调用返回子类实例 ✅
class DevConfig(Config):
    pass

DevConfig.from_env()  # 返回 DevConfig 实例

# @staticmethod - 写死了，永远返回 Config ❌
@staticmethod
def from_env():
    return Config(...)  # 子类调用还是返回 Config
```

**好处**：
- 统一入口：多种创建方式，命名清晰
- 支持继承：子类调用返回子类实例
- 语义明确：`Config.from_env()` 比 `Config(os.getenv...)` 更直观

### 4.2 @model_validator - 模型验证器

- mode = 'before'
- mode = 'after'



| 模式       | 执行时机   | 能拿到什么 | 用途               |
| ---------- | ---------- | ---------- | ------------------ |
| **before** | 字段校验前 | 原始 dict  | 清洗、改名、补字段 |
| **after**  | 字段校验后 | 完整 self  | 多字段联合校验     |

after已经创建类对象，可用self访问属性; before模式下，只能访问原始dict，用cls访问类属性
```python
from pydantic import BaseModel, model_validator

class PasswordChange(BaseModel):
    password: str
    confirm_password: str

    //字段初始化后执行函数
    @model_validator(mode='after')
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('两次密码不一致')
        return self
```

### 4.3 验证器模式

| mode | 说明 | 执行时机 |
|------|------|---------|
| `before` | 类型转换前 | 原始数据 |
| `after` | 类型转换后 | 已转换数据 |
| `wrap` | 包装验证 | 可控制验证流程 |

---

## 五、序列化方法

### 5.1 输出方法

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str | None = None

user = User(id=1, name="张三", email=None)

# 转 dict
user.model_dump()
# {'id': 1, 'name': '张三', 'email': None}

# 转 dict（排除 None）
user.model_dump(exclude_none=True)
# {'id': 1, 'name': '张三'}

# 转 JSON 字符串
user.model_dump_json()
# '{"id":1,"name":"张三","email":null}'

# 转 JSON（格式化）
user.model_dump_json(indent=2)
# {
#   "id": 1,
#   "name": "张三",
#   "email": null
# }
```

### 5.2 序列化选项

```python
# 排除特定字段
user.model_dump(exclude={'email'})

# 只包含特定字段
user.model_dump(include={'id', 'name'})

# 排除未设置的字段
user.model_dump(exclude_unset=True)

# 排除默认值
user.model_dump(exclude_defaults=True)
```

---

## 六、嵌套模型

### 6.1 模型嵌套

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    city: str
    street: str

class User(BaseModel):
    name: str
    addresses: List[Address]

# 使用
user = User(
    name="张三",
    addresses=[
        {"city": "北京", "street": "长安街"},
        {"city": "上海", "street": "南京路"},
    ]
)

print(user.addresses[0].city)  # 北京
```

### 6.2 递归模型

```python
from pydantic import BaseModel
from typing import List, Optional

class Category(BaseModel):
    name: str
    subcategories: List["Category"] = []  # 引用自身

# 使用
cat = Category(
    name="电子产品",
    subcategories=[
        Category(name="手机"),
        Category(name="电脑"),
    ]
)
```

---

## 七、LLM 项目实战应用

### 7.1 消息格式定义

```python
from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
    timestamp: datetime = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = datetime.now()

# 使用
messages = [
    Message(role="system", content="你是一个助手"),
    Message(role="user", content="你好"),
]

# 转成 API 调用格式
api_messages = [m.model_dump(exclude={'timestamp'}) for m in messages]
```

### 7.2 结构化输出（Structured Output）

```python
from pydantic import BaseModel, Field
from typing import List

class ReasoningStep(BaseModel):
    thought: str = Field(description="推理过程")
    action: str | None = Field(description="要执行的动作")

class Answer(BaseModel):
    reasoning: List[ReasoningStep]
    final_answer: str
    confidence: float = Field(ge=0, le=1)

# 让 LLM 返回结构化数据
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "..."}],
    response_format=Answer  # 强制返回符合 schema 的 JSON
)

# 解析
answer = Answer.model_validate_json(response.content)
print(answer.final_answer)
```

### 7.3 配置管理

```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class LLMConfig(BaseModel):
    model: str = "gpt-4"
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(4096, ge=1)

class AppConfig(BaseSettings):
    llm: LLMConfig
    api_key: str
    base_url: str = "https://api.openai.com/v1"

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"  # 环境变量: LLM__MODEL=gpt-4
```

---

## 八、高级功能

### 8.1 计算字段

```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

rect = Rectangle(width=3, height=4)
print(rect.area)  # 12.0
print(rect.model_dump())  # {'width': 3.0, 'height': 4.0, 'area': 12.0}
```

### 8.2 别名

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(alias="userName")
    age: int = Field(alias="userAge")

# 使用别名创建
user = User(userName="张三", userAge=25)

# 序列化时使用别名
user.model_dump(by_alias=True)  # {'userName': '张三', 'userAge': 25}
```

### 8.3 不可变模型

```python
from pydantic import BaseModel

class Config(BaseModel, frozen=True):
    api_key: str
    base_url: str

config = Config(api_key="xxx", base_url="xxx")
config.api_key = "yyy"  # ❌ FrozenInstanceError!
```

---

## 九、性能优化

### 9.1 模式配置

```python
from pydantic import BaseModel, ConfigDict

class FastModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=False,  # 赋值时不验证
        use_enum_values=True,       # 枚举使用值
        extra="ignore",             # 忽略额外字段
    )

    name: str
```

### 9.2 验证模式

```python
# 宽松模式（默认）：自动类型转换
class LaxModel(BaseModel, extra="ignore"):
    model_config = ConfigDict(strict=False)

# 严格模式：必须精确匹配类型
class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)

    age: int

StrictModel(age=25)      # ✅
StrictModel(age="25")    # ❌ 严格模式下不转换
```

---

## 十、常见问题

### 10.1 可变默认值

```python
# ❌ 错误：所有实例共享同一个列表
class Bad(BaseModel):
    tags: list = []

# ✅ 正确：使用 default_factory
class Good(BaseModel):
    tags: list = Field(default_factory=list)
```

### 10.2 继承

```python
class BaseUser(BaseModel):
    name: str

class User(BaseUser):
    email: str

# 字段会合并
user = User(name="张三", email="xxx@example.com")
```

### 10.3 动态模型

```python
from pydantic import create_model

DynamicModel = create_model(
    'DynamicModel',
    name=(str, ...),
    age=(int, 18),
)

user = DynamicModel(name="张三")
```

---

## 十一、速查表

| 操作 | 代码 |
|------|------|
| 定义模型 | `class M(BaseModel): ...` |
| 必填字段 | `name: str` |
| 可选字段 | `name: str \| None = None` |
| 默认值 | `name: str = "默认"` |
| 字段约束 | `Field(ge=0, le=100)` |
| 自定义验证 | `@field_validator('field')` |
| 转 dict | `model.model_dump()` |
| 转 JSON | `model.model_dump_json()` |
| 从 dict | `Model(**data)` |
| 从 JSON | `Model.model_validate_json(json)` |
| 排除 None | `model.model_dump(exclude_none=True)` |

---

## 十二、C++/Qt 类比

| Pydantic | C++ | Qt |
|----------|-----|-----|
| `BaseModel` | `struct` + 验证函数 | `QObject` + 属性 |
| `Field(ge=0)` | `assert(value >= 0)` | `QIntValidator` |
| `ValidationError` | 异常 | `QValidator::Invalid` |
| `model_dump()` | 序列化函数 | `QJsonObject` |
| `@field_validator` | 构造函数检查 | `Q_PROPERTY` setter |
