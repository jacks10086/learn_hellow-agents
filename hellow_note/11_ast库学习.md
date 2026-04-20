# Python ast 库学习笔记

> ast（Abstract Syntax Tree）抽象语法树，用于解析 Python 代码，进行分析、修改、安全执行。

---

## 一、核心概念

### 1.1 什么是 AST？

```
源代码字符串 → ast.parse() → 语法树(AST) → 分析/修改/执行
```

**AST 是代码的结构化表示**，每个节点代表代码中的一个元素（函数、变量、操作符等）。

### 1.2 为什么需要 AST？

| 场景 | 传统方式 | AST 方式 |
|------|---------|---------|
| 执行表达式 | `eval()` 危险！ | 白名单控制，安全 |
| 分析代码结构 | 正则匹配，不可靠 | 解析语法树，精确 |
| 生成文档 | 手写 | 自动提取函数签名 |
| 代码检查 | 运行时发现 | 静态分析，提前发现 |

---

## 二、基础用法

### 2.1 解析代码

```python
import ast

# 解析代码字符串
code = '''
x = 1 + 2
print(x)
'''

tree = ast.parse(code)
print(ast.dump(tree, indent=2))
```

**输出结构**：

```
Module(
  body=[
    Assign(
      targets=[Name(id='x', ctx=Store())],
      value=BinOp(
        left=Constant(value=1),
        op=Add(),
        right=Constant(value=2))),
    Expr(
      value=Call(
        func=Name(id='print', ctx=Load()),
        args=[Name(id='x', ctx=Load())]))])
```

### 2.2 常见 AST 节点类型

| 节点类型 | 含义 | 示例 |
|---------|------|------|
| `Module` | 模块（根节点） | 整个文件 |
| `FunctionDef` | 函数定义 | `def foo(): ...` |
| `ClassDef` | 类定义 | `class Foo: ...` |
| `Assign` | 赋值语句 | `x = 1` |
| `BinOp` | 二元操作 | `1 + 2` |
| `Call` | 函数调用 | `print(x)` |
| `Constant` | 常量 | `1`, `"hello"`, `True` |
| `Name` | 变量名 | `x`, `foo` |
| `Return` | 返回语句 | `return x` |

---

## 三、实战场景

### 3.1 安全执行数学表达式（LLM 工具常用）

**问题**：LLM 生成的代码不能直接 `eval()`，太危险。

```python
# ❌ 危险！可以执行任意代码
eval("__import__('os').system('rm -rf /')")

# ✅ 安全！只允许数学运算
safe_eval("1 + 2 * 3")  # 7
```

**实现**：

```python
import ast
import operator

# 白名单：允许的操作符
ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

ALLOWED_UNARY_OPS = {
    ast.USub: operator.neg,  # 负号
}

ALLOWED_FUNCS = {
    'abs': abs,
    'round': round,
    'min': min,
    'max': max,
}

def safe_eval(expr: str):
    '''安全计算数学表达式'''
    tree = ast.parse(expr, mode='eval')

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            op = ALLOWED_OPS.get(type(node.op))
            if not op:
                raise ValueError(f'禁止: {type(node.op).__name__}')
            return op(_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op = ALLOWED_UNARY_OPS.get(type(node.op))
            if not op:
                raise ValueError(f'禁止: {type(node.op).__name__}')
            return op(_eval(node.operand))
        elif isinstance(node, ast.Call):
            name = node.func.id
            if name not in ALLOWED_FUNCS:
                raise ValueError(f'禁止函数: {name}')
            args = [_eval(a) for a in node.args]
            return ALLOWED_FUNCS[name](*args)
        else:
            raise ValueError(f'禁止: {type(node).__name__}')

    return _eval(tree.body)

# 使用
print(safe_eval("1 + 2 * 3"))      # 7
print(safe_eval("abs(-5)"))         # 5
print(safe_eval("max(1, 5, 3)"))    # 5

# 危险操作被拒绝
safe_eval("__import__('os').system('ls')")  # ValueError!
```

### 3.2 提取函数签名（自动生成工具描述）

```python
import ast

def get_function_info(code: str):
    '''从代码中提取函数信息'''
    tree = ast.parse(code)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            name = node.name

            # 提取参数
            args = []
            for arg in node.args.args:
                arg_name = arg.arg
                arg_type = ast.unparse(arg.annotation) if arg.annotation else 'Any'
                args.append(f'{arg_name}: {arg_type}')

            # 提取返回类型
            returns = ast.unparse(node.returns) if node.returns else 'Any'

            # 提取文档字符串
            docstring = ast.get_docstring(node) or ''

            functions.append({
                'name': name,
                'args': args,
                'returns': returns,
                'docstring': docstring,
            })

    return functions

# 测试
code = '''
def calculate_price(price: float, tax_rate: float = 0.1) -> float:
    """计算含税价格"""
    return price * (1 + tax_rate)
'''

funcs = get_function_info(code)
for f in funcs:
    print(f"函数: {f['name']}({', '.join(f['args'])}) -> {f['returns']}")
    print(f"文档: {f['docstring']}")
```

### 3.3 自动生成 OpenAI 工具描述

```python
import ast
import json

def tool_from_function(func_code: str):
    '''从函数代码自动生成 OpenAI 工具描述'''
    tree = ast.parse(func_code)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            name = node.name
            docstring = ast.get_docstring(node) or '无描述'

            # 提取参数
            params = []
            for arg in node.args.args:
                param_name = arg.arg
                param_type = ast.unparse(arg.annotation) if arg.annotation else 'str'
                params.append({'name': param_name, 'type': param_type})

            # 生成 OpenAI 工具格式
            return {
                'type': 'function',
                'function': {
                    'name': name,
                    'description': docstring,
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            p['name']: {'type': p['type']}
                            for p in params
                        },
                        'required': [p['name'] for p in params]
                    }
                }
            }
    return None

# 测试
code = '''
def get_weather(city: str, unit: str = 'celsius') -> str:
    """获取指定城市的天气信息"""
    return f"{city} 的天气: 晴"
'''

schema = tool_from_function(code)
print(json.dumps(schema, indent=2, ensure_ascii=False))
```

---

## 四、AST 遍历方式

### 4.1 ast.walk() - 简单遍历

```python
import ast

code = "x = 1 + 2"
tree = ast.parse(code)

for node in ast.walk(tree):
    print(type(node).__name__)
```

### 4.2 ast.NodeVisitor - 访问者模式

```python
import ast

class FunctionVisitor(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        print(f"发现函数: {node.name}")
        self.generic_visit(node)  # 继续遍历子节点

code = '''
def foo(): pass
def bar(): pass
'''

tree = ast.parse(code)
visitor = FunctionVisitor()
visitor.visit(tree)
```

### 4.3 ast.NodeTransformer - 修改语法树

```python
import ast

class VariableRenamer(ast.NodeTransformer):
    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name

    def visit_Name(self, node):
        if node.id == self.old_name:
            node.id = self.new_name
        return node

code = "x = x + 1"
tree = ast.parse(code)

renamer = VariableRenamer('x', 'count')
new_tree = renamer.visit(tree)

print(ast.unparse(new_tree))  # count = count + 1
```

---

## 五、解析模式

| 模式 | 用途 | 示例 |
|------|------|------|
| `mode='exec'` | 解析模块/多条语句 | 函数定义、类定义 |
| `mode='eval'` | 解析单个表达式 | `1 + 2` |
| `mode='single'` | 解析单条语句 | `x = 1` |

```python
# exec 模式：多条语句
tree = ast.parse("x = 1\ny = 2", mode='exec')

# eval 模式：单个表达式
tree = ast.parse("1 + 2", mode='eval')

# single 模式：单条语句
tree = ast.parse("x = 1", mode='single')
```

---

## 六、常用 API

| API | 说明 |
|-----|------|
| `ast.parse(code)` | 解析代码字符串 |
| `ast.dump(tree)` | 打印 AST 结构 |
| `ast.unparse(node)` | AST 转回代码字符串 |
| `ast.walk(tree)` | 遍历所有节点 |
| `ast.get_docstring(node)` | 获取文档字符串 |
| `ast.NodeVisitor` | 访问者模式基类 |
| `ast.NodeTransformer` | 转换器基类 |
| `ast.literal_eval(node)` | 安全计算字面量 |

---

## 七、在 LLM/Agent 项目中的应用

### 7.1 计算器工具

```python
# LLM 生成的数学表达式，安全执行
result = safe_eval("(100 + 50) * 0.8 - 10")
```

### 7.2 自动生成工具 Schema

```python
# 从 Python 函数自动生成 OpenAI 工具描述
@tool
def calculate(expression: str) -> float:
    """计算数学表达式"""
    return safe_eval(expression)

# 自动生成 schema 给 LLM
schema = tool_from_function(calculate.__source__)
```

### 7.3 代码解释器

```python
# 安全执行用户代码片段
def run_user_code(code: str, allowed_builtins: dict):
    tree = ast.parse(code, mode='exec')
    # 检查是否只用了允许的函数
    # 编译并执行
    compiled = compile(tree, '<string>', 'exec')
    exec(compiled, {'__builtins__': allowed_builtins})
```

---

## 八、eval vs exec vs ast

| 方式 | 安全性 | 灵活性 | 用途 |
|------|--------|--------|------|
| `eval()` | ❌ 危险 | 高 | 执行表达式 |
| `exec()` | ❌ 危险 | 高 | 执行代码块 |
| `ast.literal_eval()` | ✅ 安全 | 低 | 只能计算字面量 |
| `ast.parse()` + 白名单 | ✅ 安全 | 中 | 自定义控制 |

**最佳实践**：

```python
# 简单字面量 → ast.literal_eval
result = ast.literal_eval('{"name": "张三", "age": 25}')

# 复杂表达式 → ast.parse + 白名单
result = safe_eval("abs(-10) + max(1, 2, 3)")

# 永远不要直接 eval/exec 用户/LLM 的代码！
```

---

## 九、C++ 类比

| Python ast | C++ 编译器前端 |
|------------|---------------|
| `ast.parse()` | 词法分析 + 语法分析 |
| AST 节点 | 抽象语法树 |
| `ast.walk()` | 遍历 AST |
| `ast.NodeVisitor` | 访问者模式 |
| `ast.NodeTransformer` | AST 重写 |
| `compile()` | 生成字节码 |

---

## 十、速查表

```python
import ast

# 1. 解析代码
tree = ast.parse(code)

# 2. 查看结构
ast.dump(tree, indent=2)

# 3. 遍历节点
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(node.name)

# 4. 安全计算字面量
ast.literal_eval('{"key": "value"}')

# 5. AST 转回代码
ast.unparse(tree)

# 6. 编译执行
compiled = compile(tree, '<string>', 'exec')
exec(compiled, namespace)
```

---

## 十一、注意事项

1. **永远不要直接 eval/exec 用户/LLM 代码**
2. **使用白名单机制控制允许的操作**
3. **ast.literal_eval 只支持字面量，不支持变量和函数调用**
4. **复杂表达式需要自己实现遍历逻辑**
5. **Python 版本不同，AST 结构可能有差异**
