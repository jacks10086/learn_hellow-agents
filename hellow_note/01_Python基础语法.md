# Python 基础语法笔记

## 一、注释

### 单行注释
```python
# 这是单行注释
x = 10  # 行尾注释
```

### 多行注释
```python
"""
这是多行注释
用三引号包裹
"""

'''
单引号也可以
效果一样
'''
```

### C++ 对照
| Python | C++ |
|--------|-----|
| `# 注释` | `// 注释` |
| `"""多行"""` | `/* 多行 */` |

---

## 二、函数定义

### 基本语法
```python
def 函数名(参数) -> 返回类型:
    函数体
    return 返回值
```

### 类型注解是可选的
```python
# 无类型注解
def add(a, b):
    return a + b

# 完整类型注解
def add(a: int, b: int) -> int:
    return a + b
```

### C++ 对照
```cpp
// C++
int add(int a, int b) {
    return a + b;
}
```

```python
# Python
def add(a: int, b: int) -> int:
    return a + b
```

---

## 三、缩进规则

### Python 用缩进代替大括号
```python
if x > 0:
    print("正数")      # 必须缩进 4 空格
    if x > 10:
        print("大于10") # 再缩进 4 空格
```

### 为什么不用 Tab？
- Tab 在不同编辑器显示宽度不同
- Python 不允许 Tab 和空格混用
- 统一用 4 空格，跨编辑器一致

---

## 四、f-string 格式化

### 基本用法
```python
name = "张三"
age = 25

# f 开头，{} 里放变量
info = f"我叫{name}，今年{age}岁"
# 结果: "我叫张三，今年25岁"

# {} 里可以写表达式
info = f"明年{age + 1}岁"
# 结果: "明年26岁"
```

### 不加 f 的区别
```python
city = "北京"

# 不加 f - 原样输出
url = "https://wttr.in/{city}"
# 结果: "https://wttr.in/{city}"

# 加 f - 变量替换
url = f"https://wttr.in/{city}"
# 结果: "https://wttr.in/北京"
```

---

## 五、字典和列表

### 列表
```python
# 创建列表
fruits = ["苹果", "香蕉", "橙子"]

# 访问
fruits[0]  # "苹果"

# 添加
fruits.append("葡萄")
```

### 字典
```python
# 创建字典
person = {"name": "张三", "age": 25}

# 访问
person["name"]  # "张三"

# 添加
person["city"] = "北京"
```

### 列表 + 字典（常用结构）
```python
messages = [
    {"role": "system", "content": "你是助手"},
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！"}
]

# 访问
messages[0]["role"]      # "system"
messages[1]["content"]   # "你好"
```

### C++ 对照
| Python | C++ |
|--------|-----|
| `list` | `std::vector` |
| `dict` | `std::map` |
| `[1, 2, 3]` | `std::vector<int>{1, 2, 3}` |
| `{"a": 1}` | `std::map<string, int>{{"a", 1}}` |

---

## 六、print 函数

### 默认换行
```python
print("Hello")    # 输出后换行
print("World")
# 输出:
# Hello
# World
```

### 不换行
```python
print("Hello", end=" ")
print("World")
# 输出: Hello World
```

---

## 七、转义字符

| 转义字符 | 含义 |
|---------|------|
| `\n` | 换行 |
| `\t` | 制表符（Tab） |
| `\\` | 反斜杠 |
| `\"` | 双引号 |
| `\'` | 单引号 |

### 示例
```python
print("第一行\n第二行")
# 输出:
# 第一行
# 第二行

print("列1\t列2")
# 输出: 列1    列2
```

---

## 八、join 方法

### 语法
```python
分隔符.join(列表)
```

### 示例
```python
words = ["Python", "是", "最好的", "语言"]

" ".join(words)   # "Python 是 最好的 语言"
"-".join(words)   # "Python-是-最好的-语言"
"\n".join(words)  # 用换行连接
```

---

## 九、字典的 items() 方法

### 遍历键值对
```python
person = {"name": "张三", "age": 25}

for key, value in person.items():
    print(f"{key}: {value}")
# 输出:
# name: 张三
# age: 25
```

### 列表推导中使用
```python
tools = {"Search": {"description": "搜索"}, "Calc": {"description": "计算"}}

result = "\n".join([
    f"- {name}: {info['description']}"
    for name, info in tools.items()
])
# 结果:
# - Search: 搜索
# - Calc: 计算
```

---

## 十、字典的 get 方法

### 基本用法
```python
person = {"name": "张三"}

# 键存在
person.get("name")        # "张三"

# 键不存在，返回 None
person.get("age")         # None

# 键不存在，返回默认值
person.get("age", 0)      # 0
```

### 链式调用
```python
tools = {"Search": {"description": "搜索", "func": search_func}}

# 安全获取嵌套值
tools.get("Search", {}).get("func")
# 如果 "Search" 不存在，返回 {}，再 get("func") 返回 None
# 避免了 KeyError
```

---

## 十一、raise 抛出异常

### 基本语法
```python
raise 异常类型("错误信息")
```

### 示例
```python
def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

# 使用
try:
    divide(10, 0)
except ValueError as e:
    print(e)  # "除数不能为零"
```

### C++ 对照
```cpp
// C++
throw std::invalid_argument("除数不能为零");
```

```python
# Python
raise ValueError("除数不能为零")
```

---

## 十二、all() 函数

### 检查所有元素是否为 True
```python
all([True, True, True])   # True
all([True, False, True])  # False
all([])                   # True（空列表默认 True）
```

### 常用场景：检查参数
```python
if not all([model, api_key, base_url]):
    raise ValueError("参数不完整")
```

---

## 十三、callable 可调用对象

### 内置函数 callable()
```python
def my_func():
    pass

callable(my_func)   # True（函数可调用）
callable(123)       # False（数字不可调用）
callable(MyClass)   # True（类可调用）
```

### 类型注解 Callable
```python
from typing import Callable

def register_tool(func: Callable) -> None:
    # func 是可调用对象（函数、方法等）
    func()
```

### 什么对象是 callable？
| 对象 | callable? |
|------|-----------|
| 函数 | ✅ |
| 方法 | ✅ |
| 类 | ✅ |
| lambda | ✅ |
| 带 `__call__` 的对象 | ✅ |
| 数字、字符串 | ❌ |

---

## 十四、魔术方法 `__xxx__`

### 什么是魔术方法？

双下划线包围的方法，Python 解释器会在特定场景**自动调用**。

```python
class MyClass:
    def __init__(self):      # 构造函数，创建对象时自动调用
        pass

    def __str__(self):       # print() 时自动调用
        return "字符串表示"

    def __len__(self):       # len() 时自动调用
        return 10

obj = MyClass()      # 自动调用 __init__
print(obj)           # 自动调用 __str__，输出：字符串表示
print(len(obj))      # 自动调用 __len__，输出：10
```

### 为什么叫"魔术"？

不需要显式调用，Python 自动触发：

```python
# 不需要这样写
obj.__str__()
obj.__len__()

# 直接这样，Python 自动找对应的魔术方法
print(obj)   # Python 自动调用 obj.__str__()
len(obj)     # Python 自动调用 obj.__len__()
```

---

### 常见魔术方法分类

#### 1. 对象生命周期

```python
class Person:
    def __init__(self, name):
        # 构造函数：创建对象时调用
        self.name = name

    def __del__(self):
        # 析构函数：对象销毁时调用
        print(f"{self.name} 被销毁")

p = Person("张三")  # 调用 __init__
del p              # 调用 __del__
```

#### 2. 字符串表示

```python
class Person:
    def __str__(self):
        return "用户友好显示"

    def __repr__(self):
        return "开发者调试显示"

p = Person()
print(p)   # 用户友好显示（调用 __str__）
p          # 开发者调试显示（调用 __repr__）
```

#### 3. 比较运算

```python
class Person:
    def __init__(self, age):
        self.age = age

    def __eq__(self, other):
        return self.age == other.age  # p1 == p2

    def __lt__(self, other):
        return self.age < other.age   # p1 < p2

p1, p2 = Person(20), Person(25)
print(p1 == p2)  # False，调用 __eq__
print(p1 < p2)   # True，调用 __lt__
```

#### 4. 算术运算

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

v1 = Vector(1, 2)
v2 = Vector(3, 4)
v3 = v1 + v2   # 调用 __add__
v4 = v1 * 2    # 调用 __mul__
```

#### 5. 容器操作

```python
class MyList:
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)       # len(obj)

    def __getitem__(self, index):
        return self.data[index]     # obj[index]

    def __contains__(self, item):
        return item in self.data    # item in obj

lst = MyList([1, 2, 3])
print(len(lst))    # 3
print(lst[0])      # 1
print(2 in lst)    # True
```

#### 6. 可调用对象

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, x):
        return x * self.factor

double = Multiplier(2)
print(double(5))   # 10，像函数一样调用
```

#### 7. 上下文管理器

```python
class FileManager:
    def __enter__(self):
        # with 语句开始时调用
        self.file = open("test.txt", 'r')
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        # with 语句结束时调用
        self.file.close()

with FileManager() as f:
    content = f.read()
# 自动调用 __exit__，文件被关闭
```

---

### 魔术方法速查表

| 类别 | 方法 | 触发场景 |
|------|------|---------|
| **生命周期** | `__init__`, `__del__` | 创建/销毁对象 |
| **字符串** | `__str__`, `__repr__` | `print()`, 调试 |
| **比较** | `__eq__`, `__lt__`, `__gt__` | `==`, `<`, `>` |
| **算术** | `__add__`, `__sub__`, `__mul__` | `+`, `-`, `*` |
| **容器** | `__len__`, `__getitem__`, `__setitem__` | `len()`, `[]` |
| **可调用** | `__call__` | `obj()` |
| **上下文** | `__enter__`, `__exit__` | `with obj:` |
| **迭代** | `__iter__`, `__next__` | `for x in obj` |
| **属性** | `__getattr__`, `__setattr__` | 访问属性 |

---

### 可以自己定义魔术方法吗？

**可以！** 只要遵循 `__xxx__` 格式，Python 会自动识别。

```python
class MyNumber:
    def __init__(self, value):
        self.value = value

    # 自己定义加法
    def __add__(self, other):
        return MyNumber(self.value + other.value)

    # 自己定义字符串表示
    def __str__(self):
        return str(self.value)

a = MyNumber(10)
b = MyNumber(20)

print(a + b)   # 30，调用 __add__
print(a)       # 10，调用 __str__
```

**注意**：只有 Python 预定义的魔术方法名才会被自动触发。

---

### C++ 对比

```cpp
// C++ 运算符重载
class Vector {
public:
    int x, y;

    // __add__ ≈ operator+
    Vector operator+(const Vector& other) {
        return Vector(x + other.x, y + other.y);
    }

    // __call__ ≈ operator()
    int operator()(int n) {
        return x + n;
    }
};
```

| Python | C++ |
|--------|-----|
| `__add__` | `operator+` |
| `__sub__` | `operator-` |
| `__call__` | `operator()` |
| `__getitem__` | `operator[]` |
| `__str__` | `operator<<` 重载 |

---

### 完整示例：自定义向量类

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __len__(self):
        return 2

    def __getitem__(self, index):
        return [self.x, self.y][index]

    def __call__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5  # 向量长度

v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(v1)           # Vector(3, 4)
print(v1 + v2)      # Vector(4, 6)
print(v1 * 2)       # Vector(6, 8)
print(v1 == v2)     # False
print(len(v1))      # 2
print(v1[0], v1[1]) # 3 4
print(v1())         # 5.0
```

---

### 项目中的应用

```python
# agent.py
class Agent(ABC):
    def __str__(self):
        return f"Agent(name={self.name})"

    def __repr__(self):
        return self.__str__()

# 使用
agent = SimpleAgent("助手", llm)
print(agent)  # Agent(name=助手, provider=deepseek)
```

---

## 十五、return 返回引用与副本

### Python return 返回的是引用

**Python 中 return 返回的是对象的引用，不是副本！**

```python
class MyClass:
    def __init__(self):
        self.data = [1, 2, 3]

    def get_data(self):
        return self.data  # 返回引用，不是副本！

obj = MyClass()
d = obj.get_data()
d.append(4)
print(obj.data)  # [1, 2, 3, 4] ← 内部数据被修改了！
```

---

### 为什么项目用 `.copy()`？

```python
def get_history(self) -> list[Message]:
    return self._history.copy()  # 返回副本，保护内部数据
```

**对比**：

```python
# 不用 copy()：返回引用
def get_history(self):
    return self._history

history = agent.get_history()
history.append(...)  # 直接修改了 agent._history！

# 用 copy()：返回副本
def get_history(self):
    return self._history.copy()

history = agent.get_history()
history.append(...)  # 只修改副本，agent._history 不受影响
```

---

### Python 引用机制

```python
# 赋值是传递引用
a = [1, 2, 3]
b = a           # b 和 a 指向同一个列表
b.append(4)
print(a)        # [1, 2, 3, 4] ← a 也变了！

# copy() 创建新对象
a = [1, 2, 3]
b = a.copy()    # b 是 a 的副本
b.append(4)
print(a)        # [1, 2, 3] ← a 不变
print(b)        # [1, 2, 3, 4]
```

---

### 图解

```
不用 copy()：
a ──► 列表对象 [1, 2, 3] ◄── b
       （a 和 b 指向同一个对象）

用 copy()：
a ──► 列表对象 A [1, 2, 3]
b ──► 列表对象 B [1, 2, 3]
       （各自独立）
```

---

### 哪些类型需要 copy？

| 类型 | 可变？ | return 时需要 copy？ |
|------|--------|---------------------|
| `int`, `float`, `str`, `tuple` | 不可变 | ❌ 不需要 |
| `list`, `dict`, `set` | 可变 | ✅ 需要保护时用 |
| 自定义对象 | 可变 | ✅ 视情况 |

---

### C++ 对比

```cpp
// C++ 返回引用
class MyClass {
    vector<int> data = {1, 2, 3};
public:
    vector<int>& get_data() {  // 返回引用
        return data;
    }
};
// 外部可以修改 data

// C++ 返回值（自动复制）
class MyClass {
    vector<int> data = {1, 2, 3};
public:
    vector<int> get_data() {  // 返回值，自动复制
        return data;
    }
};
// 外部拿到副本，不影响 data
```

**关键区别**：
- C++：返回值类型决定是否复制
- Python：总是返回引用，需要显式 `.copy()`

---

## 十六、可变与不可变对象

### 什么是不可变？

**不可变 = 创建后不能修改其内容**

```python
# 可变对象：可以修改内容
lst = [1, 2, 3]
lst.append(4)   # ✅ 修改了原对象
print(lst)      # [1, 2, 3, 4]

# 不可变对象：不能修改内容
s = "hello"
s[0] = "H"      # ❌ TypeError: 'str' object does not support item assignment
```

---

### "赋值改变" 的真相

```python
x = 10
x = 20   # 看起来改变了？

s = "hello"
s = "world"  # 看起来改变了？
```

**真相**：不是修改原对象，而是**创建新对象，变量指向新对象**！

```python
x = 10          # x ──► 整数对象 10
x = 20          # x ──► 整数对象 20（新对象，不是把 10 改成 20）

s = "hello"     # s ──► 字符串对象 "hello"
s = "world"     # s ──► 字符串对象 "world"（新对象）

# 旧对象 10 和 "hello" 还在内存中，只是变量不再指向它们
```

---

### 用 id() 验证

```python
x = 10
print(id(x))   # 140123456789  ← 内存地址

x = 20
print(id(x))   # 140123456999  ← 地址变了！说明是新对象

# 对比可变对象
lst = [1, 2, 3]
print(id(lst))  # 140123456789

lst.append(4)
print(id(lst))  # 140123456789  ← 地址不变！说明是修改原对象
```

---

### 为什么不可变对象不需要 copy？

```python
class Agent:
    def __init__(self):
        self._history = []    # 可变
        self.name = "助手"     # 不可变

    # 不需要 copy：str 不可变
    def get_name(self):
        return self.name  # 外部拿到引用也无所谓

    # 需要 copy：list 可变
    def get_history(self):
        return self._history.copy()  # 外部可能修改
```

**原因**：
- `str` 不可变：外部拿到引用后，无法修改内容
- `list` 可变：外部拿到引用后，可以 append、remove 等

```python
agent = Agent()

# 不可变对象：即使拿到引用也无法修改
name = agent.get_name()
name = "新名字"   # 只是让 name 指向新字符串
                  # agent.name 还是 "助手"

# 可变对象：拿到引用可以修改
history = agent.get_history()
history.append(...)  # 如果没有 copy，agent._history 就被修改了
```

---

### 不可变对象的"修改"操作

```python
# 字符串
s = "hello"
s = s.upper()   # 看起来修改，实际创建新对象
print(s)        # "HELLO"

# 原过程：
# s ──► "hello"
# s.upper() 创建 "HELLO"
# s ──► "HELLO"（新对象）

# 元组
t = (1, 2, 3)
t = t + (4,)    # 创建新元组
print(t)        # (1, 2, 3, 4)
```

---

### 可变 vs 不可变对比

```python
# 可变：原地修改
lst = [1, 2, 3]
lst.append(4)   # 原地修改，id 不变
lst[0] = 10     # 原地修改，id 不变

# 不可变：创建新对象
s = "hello"
s = s + " world"  # 创建新对象，id 变了
s[0] = "H"        # ❌ 报错，不能修改
```

---

### 为什么这样设计？

| 设计选择 | 好处 |
|---------|------|
| `int`, `str` 不可变 | 可以安全共享、作为字典键、线程安全 |
| `list`, `dict` 可变 | 高效修改、不需要频繁创建新对象 |

```python
# 不可变对象可以作为字典键
d = {"name": "张三"}  # str 作为键 ✅
d = {[1, 2]: "xxx"}   # list 作为键 ❌ TypeError

# 不可变对象可以安全共享
a = 100
b = 100
print(a is b)  # True，同一个对象（小整数缓存）

s1 = "hello"
s2 = "hello"
print(s1 is s2)  # True，字符串驻留
```

---

### C++ 类比

```cpp
// C++ 的 const 类似"不可变"
const int x = 10;
x = 20;  // ❌ 编译错误

// C++ 指针/引用可以修改指向
int a = 10;
int* p = &a;
int b = 20;
p = &b;  // p 指向 b

// Python 变量更像 C++ 的指针
// x = 10 → x 指向整数对象 10
// x = 20 → x 指向整数对象 20（新对象）
```

---

### 完整示例

```python
class Agent:
    def __init__(self):
        self._history = []      # 可变
        self._config = {"model": "gpt-4"}  # 可变
        self.name = "助手"       # 不可变
        self.version = 1        # 不可变

    # 不可变：不需要 copy
    def get_name(self):
        return self.name

    def get_version(self):
        return self.version

    # 可变：需要 copy 保护
    def get_history(self):
        return self._history.copy()

    def get_config(self):
        return self._config.copy()  # dict 也需要 copy
```

---

### 速查表

| 类型 | 可变？ | 操作示例 | 能否作为字典键 |
|------|--------|---------|---------------|
| `int` | ❌ 不可变 | `x = 10` | ✅ |
| `float` | ❌ 不可变 | `x = 3.14` | ✅ |
| `str` | ❌ 不可变 | `s = "hello"` | ✅ |
| `tuple` | ❌ 不可变 | `t = (1, 2)` | ✅ |
| `list` | ✅ 可变 | `lst.append(1)` | ❌ |
| `dict` | ✅ 可变 | `d["key"] = val` | ❌ |
| `set` | ✅ 可变 | `s.add(1)` | ❌ |

---

## 十七、Python 变量的本质：标签 vs 盒子

### C++ vs Python 的本质区别

```cpp
// C++ 思维：变量是盒子
int x = 10;   // 给 x 分配内存，存入 10
x = 20;       // 把 x 内存里的值改成 20
```

```python
# Python 思维：变量是标签
x = 10   # 先创建对象 10，然后把标签 x 贴上去
x = 20   # 先创建对象 20，然后把标签 x 移过去
```

---

### 图解对比

#### C++：变量 = 盒子

```
int x = 10;

┌───────┐
│   x   │  ← 变量是盒子，有固定内存地址
├───────┤
│  10   │  ← 盒子里装着值
└───────┘

x = 20;

┌───────┐
│   x   │  ← 同一个盒子
├───────┤
│  20   │  ← 盒子里的值变了
└───────┘
```

#### Python：变量 = 标签

```
x = 10;

    对象 10  ← 先创建对象（在右侧）
        ↑
        │
        x  ← 标签 x 贴到对象上

x = 20;

    对象 10  ← 还在内存里（可能被回收）

    对象 20  ← 创建新对象（在右侧）
        ↑
        │
        x  ← 标签 x 移到新对象上
```

---

### 验证：右侧先创建对象

```python
# 用 id() 证明
print(id(10))    # 先有对象 10
x = 10           # 再把 x 贴上去
print(id(x))     # 地址相同！

# 等价于
# 1. 创建对象 10（右侧）
# 2. 让 x 指向它（左侧）
```

---

### 多条标签指向同一对象

```python
a = [1, 2, 3]   # 创建列表对象，a 贴上去
b = a           # b 也贴到同一个对象

print(a is b)   # True，同一个对象

# 图示：
# [1, 2, 3] ← 对象
#    ↑  ↑
#    a  b   ← 两个标签
```

---

### 函数参数也是贴标签

```python
def modify(lst):
    lst.append(4)  # 修改 lst 指向的对象

data = [1, 2, 3]
modify(data)
print(data)  # [1, 2, 3, 4] ← 原对象被修改了！

# 图示：
# [1, 2, 3] ←─── data（外部标签）
#     ↑
#    lst（函数内标签，指向同一对象）
#
# lst.append(4) 修改了对象
# data 还是指向这个对象，所以看到变化
```

---

### 重新赋值 = 换标签

```python
a = [1, 2, 3]
b = a           # a, b 指向同一对象

b = [4, 5, 6]   # b 换了标签，指向新对象

print(a)  # [1, 2, 3]  ← a 还是指向原对象
print(b)  # [4, 5, 6]  ← b 指向新对象

# 图示：
# [1, 2, 3] ← a
#
# [4, 5, 6] ← b（新对象）
```

---

### C++ 指针类比

```cpp
// C++ 指针类比
int* x = new int(10);  // 创建对象，x 指向它
x = new int(20);       // x 指向新对象，旧对象泄漏

// Python 的变量就像 C++ 的指针
// 但 Python 有垃圾回收，不会泄漏
```

| C++ | Python |
|-----|--------|
| 变量是盒子，存储值 | 变量是标签，指向对象 |
| `int x = 10` 给 x 分配内存 | `x = 10` 创建对象 10，x 指向它 |
| `x = 20` 修改 x 内存 | `x = 20` x 指向新对象 |
| 指针 `int* p = &a` | 所有变量都是"指针"概念 |
| `const` 不可修改 | 不可变对象 |

---

## 十八、Python 内存优化机制

### 问题：不断赋值不会内存爆炸吗？

```python
x = 10
x = 20
x = 30
# 不断创建新对象，内存不会爆？
```

**答案：Python 有多种优化机制！**

---

### 1. 小整数缓存

Python 预先创建 -5 到 256 的整数对象，所有这个范围的整数都复用：

```python
a = 100
b = 100
print(a is b)  # True，同一个对象！

c = 1000
d = 1000
print(c is d)  # False，大整数不缓存
```

```python
# 验证缓存范围
x = 256
y = 256
print(x is y)  # True

x = 257
y = 257
print(x is y)  # False（超出缓存范围）
```

---

### 2. 字符串驻留（Interning）

相同内容的字符串只存储一份：

```python
a = "hello"
b = "hello"
print(a is b)  # True，同一个对象！

# 但动态创建的字符串不一定驻留
a = "hello"
b = "hel" + "lo"
print(a is b)  # True（编译时优化）

c = "".join(["hel", "lo"])
print(a is c)  # False（运行时创建）
```

---

### 3. 垃圾回收

不再被引用的对象会被自动回收：

```python
x = 10       # 创建对象 10，x 引用它
x = 20       # 创建对象 20，x 改为引用它
             # 对象 10 没有引用了，等待垃圾回收
```

```python
# 循环创建，内存不会爆炸
for i in range(1000000):
    x = i    # 每次创建新对象，旧对象被回收
```

---

### 内存复用示意图

```
小整数缓存：
┌─────────────────────────────────────┐
│ 预创建对象：-5, -4, ..., 255, 256   │
├─────────────────────────────────────┤
│ a = 100  ──► 引用缓存中的 100       │
│ b = 100  ──► 引用同一个 100         │
│ a = 200  ──► 引用缓存中的 200       │
│          └─► 100 没有被抛弃         │
└─────────────────────────────────────┘

大整数：
┌─────────────────────────────────────┐
│ a = 1000  ──► 新对象 1000           │
│ a = 2000  ──► 新对象 2000           │
│            └─► 对象 1000 无引用，    │
│               等待垃圾回收          │
└─────────────────────────────────────┘
```

---

### C++ 对比

```cpp
// C++ 手动管理
int* p = new int(10);
delete p;  // 手动释放

// C++ 栈上分配，自动释放
int x = 10;
x = 20;  // 栈变量，自动管理
```

```python
# Python 自动垃圾回收
x = 10
x = 20  # 对象 10 自动回收
```

---

### 验证垃圾回收

```python
import sys

# 查看引用计数
x = 10
print(sys.getrefcount(x))  # 很多引用（缓存被共享）

y = 10000
print(sys.getrefcount(y))  # 较少引用（新对象）

# 手动触发垃圾回收
import gc
gc.collect()
```

---

### 为什么这样设计？

| 机制 | 好处 |
|------|------|
| 小整数缓存 | 常用数字不重复创建 |
| 字符串驻留 | 相同字符串只存一份 |
| 垃圾回收 | 无引用对象自动释放 |
| 引用计数 | 实时追踪对象使用 |

---

### 核心总结

| 概念 | 说明 |
|------|------|
| **变量是标签** | `=` 右侧创建对象，左侧贴标签 |
| **小整数缓存** | -5 到 256 永远复用 |
| **字符串驻留** | 相同字符串共享内存 |
| **垃圾回收** | 无引用对象自动释放 |

---

### C++ 程序员的关键认知转变

```
C++ 思维：
  int x = 10;    // x 是盒子，装着 10
  x = 20;        // 盒子里换成 20

Python 思维：
  x = 10;    # 对象 10 存在，x 是它的标签
  x = 20;    # 对象 20 存在，x 移到新标签

理解这个区别，就理解了 Python 的引用机制！
```
