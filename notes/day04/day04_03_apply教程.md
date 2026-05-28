# Day04 · 第三节：apply 与向量化函数

> 课程视频 12-14。深度对标 [[day04_01_表合并教程]] 和 [[day04_02_缺失值处理教程]]。**这一节代码量极小，但藏着 Pandas 最关键的性能观念**——10 万行数据，apply 写法慢 100 倍是常态。

---

## 你已经摸过的部分

泰坦尼克号项目里你写过这种东西：

```python
df['age_double'] = df['age'] * 2          # 向量化
df['age_group'] = df['age'].fillna(0)     # 内置方法
```

这些都是 **向量化操作**——一行代码，Pandas 内部跑 C 代码，秒级。

**但有些逻辑没办法用 `*`、`+`、`>` 这种算子写**，比如：

> "如果 age 是 NaN 返回 '未知'；小于 18 返回 '少年'；大于 60 返回 '老年'；其余返回 '成人'。"

这种 **"需要自己写 if/else"** 的逻辑，向量化算子搞不定。这时候才轮到 `apply` 出场。

---

## 一句话定位 apply

```
apply = "把一个自定义函数，套到 Series 的每个元素 / DataFrame 的每一行（或每一列）"
```

它是 Pandas **给"复杂自定义逻辑"留的后门**——灵活，但慢。

---

## 三种 apply 形态（先记住有几种，再分别学）

```
①  Series.apply(func)            ── func 接收"一个元素"
②  DataFrame.apply(func, axis=0) ── func 接收"一整列 Series"（默认）
③  DataFrame.apply(func, axis=1) ── func 接收"一整行 Series"
```

> 🔥 **第一卡点**：很多人记不住"Series.apply 接元素"和"DataFrame.apply 接 Series"的区别。**这是 apply 最容易绕晕的点**，下面会反复对比。

---

## ① Series.apply —— 对每个元素跑一遍函数

### 1.1 最简形态

```python
import pandas as pd

s = pd.Series([10, 20, 30])

def double(x):           # x 是 Series 里"一个元素"（标量）
    return x * 2

s.apply(double)
# 0    20
# 1    40
# 2    60
```

**关键认知**：`func` 被调用了 **3 次**——分别传入 10、20、30。每次传的是 **一个标量**，不是整个 Series。

### 1.2 配合 lambda

```python
s.apply(lambda x: x * 2)   # 一次性，懒得起名字时用
```

效果一样，**90% 实战都写 lambda**——简洁。

### 1.3 写复杂的 if/else（这是 apply 最大的用途）

```python
def grade(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 60:
        return 'C'
    else:
        return 'D'

scores = pd.Series([95, 82, 67, 45])
scores.apply(grade)
# 0    A
# 1    B
# 2    C
# 3    D
```

**这就是 apply 该出现的地方**——多条分支、向量化算子写不出来。

### 1.4 给 func 多传一个参数（视频里讲的）

```python
def times(x, p):
    return x * p

s.apply(times, p=3)        # ← 关键字参数传 p
# 0    30
# 1    60
# 2    90
```

**注意**：`apply` 把多余的关键字参数原样转发给 `func`。位置参数也支持：

```python
s.apply(times, args=(3,))   # 用 args= 传位置参数
```

实战中 99% 都用关键字参数（清晰）。

---

## ② DataFrame.apply（axis=0）—— 对每一列跑函数

### 2.1 最容易困惑的点

```python
df = pd.DataFrame({"a": [10, 20, 30], "b": [40, 50, 60]})

def func(col):           # ← col 是什么？
    return col.sum()

df.apply(func, axis=0)
# a     60
# b    150
```

**关键认知**：

| 比较项 | Series.apply | DataFrame.apply(axis=0) |
|---|---|---|
| `func` 接收什么 | 一个**元素** (标量) | 一**整列 Series** |
| `func` 被调用几次 | n 个元素就调 n 次 | 有几列就调几次 |
| 例子 | `func(10), func(20), ...` | `func(df['a']), func(df['b'])` |

**思维模型**：`DataFrame.apply(axis=0)` = "把 DataFrame 按列拆，每列拆出来的 Series 喂给 func。"

### 2.2 axis=0 的记忆口诀

```
axis=0  → 沿"行"方向滑动 → 一列一列处理 → 每次传一整列
axis=1  → 沿"列"方向滑动 → 一行一行处理 → 每次传一整行
```

如果你忘了——回到 [[numpy轴的理解]]。**axis 是"消失的那个轴"**：

- `axis=0` 消失行轴 → 每列被压成 1 个值（每列调一次 func）
- `axis=1` 消失列轴 → 每行被压成 1 个值（每行调一次 func）

---

## ③ DataFrame.apply（axis=1）—— 对每一行跑函数

### 3.1 最常用的场景

```python
df = pd.DataFrame({"a": [10, 20, 30], "b": [40, 50, 60]})

def divide(row):           # row 是一整行 Series
    return row['a'] / row['b']

df.apply(divide, axis=1)
# 0    0.25
# 1    0.40
# 2    0.50
```

**关键认知**：`func` 收到的 `row` 是个 Series，**index 是列名** (`'a'`, `'b'`)。所以 `row['a']` 取这一行 a 列的值。

### 3.2 实战例子：泰坦尼克号"造一个新列"

> 想给每行加一列 `family_size = sibsp + parch + 1`（兄弟姐妹 + 父母子女 + 自己）：

```python
# 写法 A：apply
df['family_size'] = df.apply(lambda row: row['sibsp'] + row['parch'] + 1, axis=1)

# 写法 B：向量化（推荐！）
df['family_size'] = df['sibsp'] + df['parch'] + 1
```

**两种写法结果一样**。但 B 比 A 快 50-100 倍。下面会展开说。

### 3.3 axis=1 真正必须用 apply 的场景

什么时候 `apply(axis=1)` 不可替代？**当一行内多列的逻辑需要 if/else**：

```python
def classify(row):
    if row['age'] < 18:
        return f"少年-{row['sex']}"
    elif row['fare'] > 100:
        return f"富人-{row['sex']}"
    else:
        return f"普通-{row['sex']}"

df['label'] = df.apply(classify, axis=1)
```

这种 **多列联动 + 字符串拼接 + 分支** 的逻辑，没办法纯向量化。**apply(axis=1) 才是它的舞台**。

---

## ④ 向量化函数 —— apply 的"加速版"

### 4.1 为什么 apply 慢

apply 慢的本质：**它要进 Python 解释器循环 N 次**。

```
df['age'].apply(func)
↓ 内部其实是：
for x in df['age']:
    result.append(func(x))     # ← N 次 Python 函数调用
```

每次调用 Python 函数都有开销（栈帧、类型检查、对象引用计数……）。10 万行 = 10 万次开销。

而向量化操作 `df['age'] * 2`：

```
直接调 NumPy 的 C 实现，一次性把 10 万个数组元素 × 2，零 Python 开销
```

**典型差距**：10 万行 `apply(lambda x: x*2)` 大约 50 ms，向量化 `df['age']*2` 大约 0.5 ms。**100 倍**。

### 4.2 视频 14：`@np.vectorize` 装饰器

视频里给的例子：

```python
import numpy as np

@np.vectorize        # ← 把普通函数"包装"成向量化版本
def f(x, y):
    if y == 0:
        return np.nan
    return x / y

df = pd.DataFrame({"a": [10, 20, 30], "b": [40, 0, 60]})

f(df["a"], df["b"])
# array([0.25, nan, 0.5])
```

**注意看用法**：

```python
f(df['a'], df['b'])         # ← 直接传两列进去！不需要 apply
```

`@np.vectorize` 让你写 **接收标量的 Python 函数**，但能像 NumPy 算子一样 **直接传 Series/数组**。

### 4.3 关键误区：`@np.vectorize` 并不是真正的"向量化"

**坑预警**——这是个新手非常容易误会的点：

> `np.vectorize` 只是 **语法糖**——内部仍然是一个 Python 循环，**性能跟 apply 差不多**，并不会加速。

NumPy 官方文档原文写了："The vectorize function is provided primarily for convenience, not for performance. The implementation is essentially a for loop."

**那它的真正用途是什么？** —— **让代码长得像向量化操作**：

```python
# 不用 @np.vectorize：必须手写 apply
df['ratio'] = df.apply(lambda row: f(row['a'], row['b']), axis=1)

# 用了 @np.vectorize：写起来更优雅
f = np.vectorize(f)
df['ratio'] = f(df['a'], df['b'])
```

**结论**：`@np.vectorize` 主要是 **语法清爽**，不是 **加速工具**。真要快，必须用 NumPy 原生算子。

### 4.4 真正的向量化怎么写

把刚才那个除法 + 处理 0 的逻辑用真正向量化重写：

```python
# 真·向量化（用 np.where 替代 if/else）
df['ratio'] = np.where(df['b'] == 0, np.nan, df['a'] / df['b'])
```

`np.where(条件, A, B)` = "条件成立返回 A，不成立返回 B"。**全程零 Python 循环**，10 万行 < 1ms。

记住这个套路——它是 **大数据场景里替代 apply 的标准答案**。

---

## 三种 apply 的速度对比（实测概念）

```python
import pandas as pd, numpy as np, time

df = pd.DataFrame({'a': np.random.rand(100000), 'b': np.random.rand(100000)})

# 方案 1：apply  ── 慢
t1 = time.time()
df.apply(lambda row: row['a'] + row['b'], axis=1)
print('apply:    ', time.time() - t1, 's')   # ≈ 1.2s

# 方案 2：np.vectorize  ── 几乎和 apply 一样慢
@np.vectorize
def add(a, b):
    return a + b
t2 = time.time()
add(df['a'], df['b'])
print('vectorize:', time.time() - t2, 's')   # ≈ 0.8s

# 方案 3：真向量化  ── 快 1000 倍
t3 = time.time()
df['a'] + df['b']
print('真向量化: ', time.time() - t3, 's')   # ≈ 0.001s
```

**记死这张表**：

| 写法 | 10 万行耗时 | 适用场景 |
|---|---|---|
| `df.apply(func, axis=1)` | 1 s 左右 | 复杂行内多列逻辑 + 不在意速度 |
| `@np.vectorize` | 0.8 s 左右 | 想让代码看起来清爽 |
| `df['a'] + df['b']` / `np.where` | 1 ms 左右 | **能用就一定用这个** |

---

## 三兄弟辨析：`apply` / `map` / `applymap`

很多教程会混着讲，先一图理清：

| API | 对象 | 接收什么 | 一句话 |
|---|---|---|---|
| `s.apply(f)` | Series | 元素 | 对 Series 每个元素跑 f |
| `s.map(f)` | Series | 元素 **或字典** | 类似 apply，但能传 dict 做映射 |
| `df.apply(f, axis=)` | DataFrame | 一整行/列 Series | 按行或列跑 f |
| `df.applymap(f)` | DataFrame | 元素 | 对每个 cell 跑 f（**已弃用，改用 `df.map`**）|

**Series.map 的独门绝活**——传字典直接做映射：

```python
s = pd.Series(['M', 'F', 'M', 'F'])
s.map({'M': '男', 'F': '女'})
# 0    男
# 1    女
# 2    男
# 3    女
```

这个用法 **泰坦尼克号洗 sex 字段时极常用**。`apply` 也能做但要 `apply(lambda x: {'M':'男','F':'女'}[x])`，繁琐。

**记忆口诀**：

- 想对 Series 每个元素做事 → **apply**（函数复杂时）或 **map**（字典映射时）
- 想对 DataFrame 每行/列做事 → **apply + axis**
- 想对 DataFrame 每个 cell 做事 → **`df.map(f)`**（新 Pandas）

---

## iOS 类比

```swift
// Series.apply 相当于 Swift 的 map
let scores = [95, 82, 67, 45]
let grades = scores.map { score -> String in
    if score >= 90 { return "A" }
    else if score >= 80 { return "B" }
    else if score >= 60 { return "C" }
    else { return "D" }
}

// DataFrame.apply(axis=1) 相当于 Swift 数组 of dict 的 map
let people = [["age": 25, "fare": 100], ["age": 17, "fare": 50]]
let labels = people.map { row in
    return row["age"]! < 18 ? "少年" : "成人"
}

// 关键差别：Swift 的 map 永远是 Python 循环级别的速度，
// 没有 NumPy 那种"底层 C 批量算"的概念。这也是为什么搞数据分析
// 必须改用 NumPy/Pandas——单纯 Swift Array 处理 10 万行慢得无法忍受。
```

> 这里有个 **认知升级点**：iOS 开发不太在意 `Array.map` 的性能（数据量小、UI 主导），但**数据分析里，能不能用向量化决定了你的程序能不能跑**。10 万行数据用 apply 跑半分钟 vs 向量化 0.1 秒——这就是为什么大家天天念叨"向量化"。

---

## 速查 API 表

```python
# Series 上的 apply
s.apply(func)                         # 对每个元素跑 func
s.apply(func, p=2)                    # 给 func 传关键字参数
s.apply(lambda x: x * 2)              # lambda 形式

# Series 上的 map（独门：传字典）
s.map({'M': '男', 'F': '女'})         # 字典映射
s.map(func)                           # 类似 apply

# DataFrame 上的 apply
df.apply(func, axis=0)                # 每列一个 Series 喂给 func（默认）
df.apply(func, axis=1)                # 每行一个 Series 喂给 func
df.apply(lambda col: col.max(), axis=0)
df.apply(lambda row: row['a']+row['b'], axis=1)

# DataFrame 上的 map（新版 pandas，旧版叫 applymap）
df.map(func)                          # 每个 cell 跑 func

# 向量化"语法糖"（不真正加速）
@np.vectorize
def f(x, y): ...
f(df['a'], df['b'])

# 真正的向量化（首选！）
df['a'] + df['b']
df['a'] * 2
np.where(df['b'] == 0, np.nan, df['a'] / df['b'])
df['age'].clip(0, 100)
```

---

## 工作流：什么时候用哪种？

```
要写一段数据处理逻辑
       ↓
能用 +, *, >, &, |, np.where 等向量化算子写吗？
   ├─ 能 → 直接写算子表达式 ✅（最快、最优雅）
   └─ 不能（必须 if/else 分支）
              ↓
        是单列变换吗？
           ├─ 是 → Series.apply(func)
           └─ 否（多列联动）
                   ↓
                 DataFrame.apply(func, axis=1)
                       │
                       └─ 如果数据量大（>10 万行），
                          考虑改写为多个 np.where 嵌套
```

**面试 / 项目里的常见做法**：

```python
# 不优雅但勉强能用
df['label'] = df.apply(lambda r: '富人' if r['fare']>100 else '穷人', axis=1)

# 等价但快 100 倍
df['label'] = np.where(df['fare'] > 100, '富人', '穷人')
```

养成 **"先试向量化，搞不定再 apply"** 的思维习惯。

---

## 你会撞到的卡点预测

基于前两节的经验，预判这几个会让你停下来：

1. **`Series.apply` 接元素 vs `DataFrame.apply` 接 Series 的区别** —— 写错过一次就死记了，看一次记不住
2. **`axis=0/1` 到底哪个是行哪个是列** —— 回到 [[numpy轴的理解]] 的"消失的轴"心法即可
3. **`@np.vectorize` 看起来像加速，实际不加速** —— 90% 的中文教程都没讲清这点
4. **`apply` 和 `map` 什么区别** —— 简单说：单元素逻辑两个都行，map 多了"传字典"这个用法
5. **什么时候该坚持向量化？** —— 几乎永远。数据量上千就值得想一下

撞到任何一个**直接告诉我**，按 P05_Weather 的标准（4-5 个 Claude 讲解 cell）来拆。

---

## 一道自测题（请复述）

不要看下面的答案，**先合上笔记自己说**：

> 我有一个 DataFrame 有 `age`, `sex`, `fare` 三列。我想生成一个新列 `label`：
> - 如果 `age < 18` 标 "少年"
> - 如果 `fare > 100` 标 "富人"
> - 其他标 "普通"
>
> 写两种实现：(A) `apply` 写法 (B) 向量化写法。它们的性能差异大致是多少？

<details>
<summary>👇 答案展开</summary>

```python
# (A) apply 写法
def classify(row):
    if row['age'] < 18:
        return '少年'
    elif row['fare'] > 100:
        return '富人'
    else:
        return '普通'
df['label'] = df.apply(classify, axis=1)

# (B) 向量化写法（np.where 嵌套）
df['label'] = np.where(df['age'] < 18, '少年',
              np.where(df['fare'] > 100, '富人', '普通'))

# 10 万行性能：A ≈ 1s，B ≈ 1ms，差距约 1000 倍
```
</details>

---

## 配套笔记

- [[pandas理解]] —— Series/DataFrame 全局
- [[numpy轴的理解]] —— axis=0/1 心法（apply 必备）
- [[groupby系统理解]] —— groupby + apply 的组合在第四节会讲
- [[day04_00_概念地图]] —— Day04 主题地图

---

**学完这节你应该能做到**：

- ✅ 看到一段 `df.apply(...)` 代码，第一眼能说出 "这是按行还是按列、func 收到的是什么"
- ✅ 写自定义"分箱/标签"逻辑时，先想 `np.where`，搞不定再 `apply`
- ✅ 知道 `@np.vectorize` 是语法糖不是加速
- ✅ 不在 10 万行数据上写 `df.apply(..., axis=1)` 而不眨眼

**下一节预告**：第四节 `groupby` 进阶（`agg` / `transform` / `filter` + `cut`）——这是 Day04 的最后一块拼图，也是你已经在 P05_Weather 打下扎实基础的部分。
