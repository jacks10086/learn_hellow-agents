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
