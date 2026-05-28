# Day03 · 第一节：DataFrame 全套（P01 + P02）

> 这是 Day03 的**重头戏**——Pandas 真正的"主对象"DataFrame 从无到有讲一遍。**学完这一节才算正式入门 Pandas**。

---

## 你已经摸过的部分

P05_Weather / 泰坦尼克号项目里你已经用过：

```python
df.head()
df["age"]
df[df["age"] > 25]
df.groupby("month")[["temp_max"]].mean()
```

这些都是 DataFrame 的 **零散动作**。这一节把它**系统化**——讲清"DataFrame 是什么、怎么造、有哪些属性、怎么改"。

---

## 一句话定位 DataFrame

> **DataFrame = 一张带标签的二维表**——可以看作"Excel 表 + 行索引 + 列名"，也可以看作"多列 Series 拼起来"。

```
        ─── columns（列名）───→
        ┌───┬─────┬─────┐
   ↑    │ id│name │ age │   ← 列名作为列标签
   │    ├───┼─────┼─────┤
 index  │101│张三 │ 20  │
        │102│李四 │ 30  │
   │    │103│王五 │ 40  │
   ↓    └───┴─────┴─────┘
   ↑
 （行索引）
```

**关键认知**：DataFrame 既不是 dict（key→value 一对一），也不是 list of list（无标签），**是 dict of Series**——每一列是一个 Series，列名是 key，所有 Series 共享同一个 index。

---

## 第一部分：P01 — Series 索引速复习

> Day02 已经学透，**这一节就是热身**。会的可以跳过，记不清的 5 分钟扫一下。

### 1.1 三种取值器

```python
import pandas as pd
s = pd.Series([10,20,30,40,50], index=['a','b','c','d','e'])

s.loc["a":"c"]    # 标签切片，闭区间 → 10, 20, 30
s.iloc[1:4]       # 位置切片，左闭右开 → 20, 30, 40
s[1:4]            # 默认 = iloc 的行为
```

🔥 **第一卡点**：`loc` 是 **闭区间**（包含末尾），`iloc` 是 **左闭右开**（不含末尾）。

```python
s.loc["a":"c"]    # 包含 c
s.iloc[0:3]       # 不包含 3
```

**记忆口诀**：

- `loc` = label = 标签 = SQL 风格 = "from a to c"，c 也要 → 闭区间
- `iloc` = index = 位置 = Python list 风格 = 左闭右开

### 1.2 布尔过滤（**重点**）

```python
s = pd.Series({"a": -1.2, "b": 3.5, "c": 6.8, "d": 2.9})

bools = s > s.mean()   # 生成等长 bool Series
# a    False
# b     True
# c     True
# d    False

s[bools]               # 用 bool Series 过滤 → 只保留 True 的
# b    3.5
# c    6.8
```

**两步动作分开写更清晰**：

```python
# 一行写法（实战常用）
s[s > s.mean()]

# 两步写法（理解原理时用）
bools = s > s.mean()
s[bools]
```

🔥 **这是 Pandas 数据筛选的标准动作**——后面 DataFrame 的 `df[df["age"]>25]` 完全一致。

---

## 第二部分：P02 — DataFrame 创建

### 2.1 三种创建方式

#### 法 A：传 dict，key 当列名

```python
import pandas as pd
df = pd.DataFrame({
    "id":   [100, 200, 300],
    "name": ["张三", "李四", "王五"],
    "age":  [10, 20, 30]
})
```

**最常用**——99% 实战手写表都用这种。

#### 法 B：dict of Series

```python
mango  = pd.Series([4,5,6,3,1], name='Mango')
apple  = pd.Series([5,4,3,0,2], name='Apple')
banana = pd.Series([2,3,5,2,7], name='Banana')

df = pd.DataFrame({"Mango": mango, "Apple": apple, "Banana": banana})
```

**适合**已经有零散 Series 要拼成表的场景。

#### 法 C：指定 `columns` 和 `index`（控制顺序）

```python
df = pd.DataFrame(
    {"name": ["张三","李四","王五"], "age": [10,20,30]},
    columns=["age","name"],          # ← 指定列的顺序（age 在前）
    index=[100, 200, 300]            # ← 指定行标签
)
```

输出：

```
     age  name
100   10   张三
200   20   李四
300   30   王五
```

**关键**：

- `columns=[...]` 指定列名 **和顺序**
- `index=[...]` 给行起标签（默认是 `0, 1, 2, ...`）

---

## 第三部分：DataFrame 的 **核心属性**

```python
df = pd.DataFrame(
    {"id":[101,102,103], "name":["张三","李四","王五"], "age":[20,30,40]},
    index=["aa","bb","cc"]
)
```

### 3.1 12 个常用属性

| 属性 | 含义 | 例子返回 |
|---|---|---|
| `df.index` | 行索引 | `Index(['aa','bb','cc'], dtype='object')` |
| `df.columns` | 列名 | `Index(['id','name','age'], dtype='object')` |
| `df.values` | 数据值（**ndarray**）| `array([[101,'张三',20],...])` |
| `df.dtypes` | 各列类型 | `id int64 / name object / age int64` |
| `df.ndim` | 维度 | `2` |
| `df.shape` | 形状元组 | `(3, 3)` |
| `df.size` | 元素总数 | `9`（= 3×3）|
| `df.T` | 行列转置 | 列变行、行变列 |

🔥 **关键认知**：`df.values` 把整张表退化成 NumPy ndarray——**列名和 index 都丢失**。所以 99% 实战都用 `df`，只在真要做 NumPy 运算时才用 `.values`。

### 3.2 4 种取值器

这是 DataFrame 最容易混的点。**先看一张对照表**：

| 取值器 | 索引方式 | 区间 | 用途 |
|---|---|---|---|
| `df.loc[行标签, 列标签]` | **标签** | 闭区间 | 按行/列名取 |
| `df.iloc[行位置, 列位置]` | **位置** | 左闭右开 | 按整数位置取 |
| `df.at[行标签, 列标签]` | 标签 | 单元素 | **取单个值最快** |
| `df.iat[行位置, 列位置]` | 位置 | 单元素 | **取单个值最快** |

#### 例子（接 3.1 那个 df）

```python
# loc —— 标签
df.loc["aa", "id":"age"]       # 'aa' 行的 id 到 age 列（闭区间）
df.loc["bb"]                   # 整行
df.loc[:, "name"]              # 所有行的 name 列

# iloc —— 位置
df.iloc[1:, :]                 # 第 1 行到最后，所有列
df.iloc[0]                     # 第 0 行
df.iloc[-1]                    # 最后一行（负索引能用）

# at / iat —— 单值
df.at["bb", "name"]            # → '李四'
df.iat[1, 1]                   # → '李四'
```

**何时用 `at` / `iat`**：在循环里逐个取值时，`at` 比 `loc` 快好几倍。**90% 场景用 `loc/iloc` 就够了**。

🔥 **第二卡点**：`df["age"]` 和 `df.loc[:, "age"]` 完全等价——**列名直接当 key 取**是 Pandas 的语法糖。但行标签不能这样：`df["aa"]` ❌（会被当成"找叫 aa 的列"）。

```python
df["age"]            # ✅ 取 age 列
df.loc[:, "age"]     # ✅ 一样
df["aa"]             # ❌ 报错（没有叫 aa 的列）
df.loc["aa"]         # ✅ 取 aa 行
```

---

## 第四部分：DataFrame 的 **常用方法**（一大坨，分类记）

视频里把 30 多个方法一口气过——别被吓到，**按用途分 9 类记**：

### 4.1 预览类（看局部）

```python
df.head()           # 前 5 行
df.head(10)         # 前 10 行
df.tail()           # 后 5 行
df.sample()         # 随机抽 1 行（默认）
df.sample(5)        # 随机抽 5 行
```

### 4.2 总览类（一键概览）

```python
df.describe()       # 数值列的 8 大统计：count/mean/std/min/25%/50%/75%/max
df.describe(include=[np.float64])  # 只对 float 列做统计
df.info()           # 各列 dtype + 非空数 + 内存占用
```

**实战中拿到新数据集，第一步就是这两个**——`df.head()` 看长什么样，`df.info()` 看 dtype 和 NaN。

### 4.3 统计九件套（按列算单一统计）

```python
df["age"].sum()         # 求和
df["age"].mean()        # 均值
df["age"].max()         # 最大
df["age"].min()         # 最小
df["age"].std()         # 标准差
df["age"].var()         # 方差
df["age"].median()      # 中位数
df["age"].mode()        # 众数（可能多个）
df["age"].quantile()    # 中位数（默认 0.5 分位）
df["age"].quantile(0.75)  # 75 分位
```

🔥 **第三卡点**：`mean()` 默认 **自动跳过 NaN**——你不用先 dropna。但 NumPy 的 `np.mean()` 会被 NaN 污染（除非用 `np.nanmean`）。**Pandas 在 NaN 处理上比 NumPy 友好**。

### 4.4 计数类

```python
df.count()              # 每列的"非空"数（不含 NaN）
df["age"].nunique()     # 不重复值的个数
df["age"].value_counts()  # 每个值出现几次（自动倒序排）
df.value_counts()       # 整行去重计数（多列组合）
```

**`value_counts` 用法举例**（你做泰坦尼克号见过）：

```python
df["sex"].value_counts()
# male      577
# female    314
```

### 4.5 缺失值

```python
df.isna()               # 元素是否缺失 → 等形 bool DataFrame
df.isna().sum()         # 每列有多少 NaN
df.isnull()             # isna 的别名
df.notna()              # 反过来：是否非空
```

→ 系统讲法见 [[day04_02_缺失值处理教程]]。

### 4.6 去重

```python
df.drop_duplicates()              # 删除完全重复的行
df.drop_duplicates(subset=["id"]) # 只看 id 列重复就删
df["name"].unique()               # 一列的不重复值（ndarray）
```

### 4.7 包含判断

```python
df.isin([101, "李四"])     # 每个元素是否在列表里 → bool DataFrame
df.isin([np.nan])          # 也能检测 NaN

# 实战：选出年龄 ∈ {20, 30} 的行
df[df["age"].isin([20, 30])]
```

### 4.8 排序

```python
# 按 index 排序
df.sort_index()                          # 默认升序
df.sort_index(ascending=False)           # 降序

# 按列的值排序（**最常用**）
df.sort_values(by="age")                          # 升
df.sort_values(by="age", ascending=False)         # 降
df.sort_values(by=["age","id"],                   # 多列排序
               ascending=[True, False])            # 各列方向

# 排序后只取最大/最小 N 行（**实战极常用**）
df.nlargest(3, columns=["age"])         # age 最大的 3 行
df.nsmallest(3, columns=["age"])        # age 最小的 3 行
```

🔥 **常考点**：`nlargest` / `nsmallest` 比 "排序 + head" 更直接、更快——P06_Employee 里找最低/最高薪员工就是用它。

### 4.9 累计运算（时间序列常用）

```python
df3 = pd.DataFrame({'A':[2,5,3,7,4], 'B':[1,6,2,8,3]})

df3.cumsum()           # 累计和（按列）
df3.cumsum(axis=1)     # 累计和（按行）
df3.cummax()           # 累计最大
df3.cummin()           # 累计最小
df3.cumprod()          # 累计积
df3.diff()             # 一阶差分（当前行 - 前一行）
df3.diff(periods=2)    # 二阶差分（当前 - 前 2 行）
df3.diff(axis=1)       # 按行差分
```

**用途**：

- `cumsum` → 算"累计收入"
- `diff` → 算"日增长量"
- `pct_change` → 算"环比增长率"（视频里没讲但很常用）

### 4.10 替换 / 比较

```python
df.replace(np.nan, 88)              # 把 NaN 全换成 88
df.replace({"张三": "张大山"})       # dict 形式批量替换
df1.equals(df2)                     # 两表是否完全相同 → bool
```

---

## 第五部分：布尔索引（**核心动作**）

### 5.1 一行筛选

```python
df = pd.DataFrame(
    {"age":[20,30,40,10], "name":["张三","李四","王五","赵六"]},
    columns=["name","age"],
    index=[101, 104, 103, 102]
)

df[df["age"] > 25]
# 等价两步：
bools = df["age"] > 25
df[bools]
```

### 5.2 多条件组合（**重要**）

```python
# AND 用 &  /  OR 用 |  /  NOT 用 ~
# 每个条件必须用 () 括起来（运算符优先级问题）

df[(df["age"] > 25) & (df["age"] < 40)]              # AND
df[(df["age"] < 20) | (df["age"] > 35)]              # OR
df[~(df["age"] > 25)]                                # NOT
df[df["name"].isin(["张三", "王五"])]                # 多值匹配
```

🔥 **新手 100% 撞的卡点**：

```python
# ❌ 用了 Python 的 and / or 会报错
df[df["age"] > 25 and df["age"] < 40]   # ❌ ValueError

# ✅ 必须用 & | ~，并且每个条件加括号
df[(df["age"] > 25) & (df["age"] < 40)]  # ✅
```

**为什么**：`and / or` 是 Python 的"短路逻辑"，作用于标量；`& | ~` 是"位运算"，作用于 Series 的每个元素。Pandas 必须用后者。

---

## 第六部分：DataFrame 运算

### 6.1 标量运算（广播）

```python
df * 2                # 每个元素 ×2
df["age"] * 2         # 单列每个元素 ×2
df + 100              # 每个元素 + 100
```

### 6.2 DataFrame ↔ DataFrame 运算（**按 index 对位**）

```python
df1 = pd.DataFrame({"age":[10,20,30,40]}, index=[101,102,103,104])
df2 = pd.DataFrame({"age":[10,20,30,40]}, index=[102,103,104,105])

df1 + df2
```

**结果**：

```
     age
101  NaN      ← df2 没有 101
102  30       ← df1[102].age=20 + df2[102].age=10
103  50
104  70
105  NaN      ← df1 没有 105
```

🔥 **第四大卡点（最容易迷糊）**：Pandas 的运算 **按标签对位**——这和 NumPy 完全不同。

| 工具 | 加法行为 |
|---|---|
| NumPy `arr1 + arr2` | 按 **位置** 对位（要求 shape 一致或可广播）|
| Pandas `df1 + df2` | 按 **index / columns 标签** 对位（标签对不上的填 NaN）|

**这是 Pandas 比 NumPy 强大的地方**——再也不用 "记住第 5 行是用户 A" 这种心智负担，直接靠标签自动对齐。

---

## 第七部分：DataFrame 的 **增删改**

### 7.1 修改 index / columns（4 种方法）

#### 方法 A：`set_index` / `reset_index`

```python
df = pd.DataFrame({
    "age": [20,30,40,10],
    "name": ["张三","李四","王五","赵六"],
    "id": [101,102,103,104]
})

# 把 id 列设为行索引
df.set_index("id", inplace=True)
# 此时 df.columns 没有 'id' 了，df.index 是 [101,102,103,104]

# 还原成默认的 0..n
df.reset_index(inplace=True)
# id 又回到 columns 里
```

🔥 **第五卡点**：`set_index("id")` 之后 **id 不在 columns 里**了——不是消失，是变成了 index。要改回去用 `reset_index()`。

#### 方法 B：`rename`

```python
df.rename(
    index={101:"一", 102:"二", 103:"三", 104:"四"},
    columns={"age":"年龄", "name":"姓名"},
    inplace=True
)
```

#### 方法 C：直接赋值

```python
df.index   = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ"]
df.columns = ["年齡", "名稱"]
```

**注意**：赋值要求长度匹配，不匹配会报错。

### 7.2 增删列 / 行

```python
df = pd.DataFrame({...})

# 添加列（直接赋值）
df["phone"] = ["111","222","333","444"]

# 添加列到指定位置
df.insert(0, "phone", ["111","222","333","444"])   # 插到第 0 列

# 修改整列
df["age"] = [200, 300, 400, 100]

# 删除列（3 种写法）
df.drop("phone", axis=1, inplace=True)   # axis=1 表示列
del df["phone"]                          # Python 风格
# df.pop("phone")                        # 删并返回该列

# 删除行
df.drop(3, axis=0, inplace=True)         # axis=0 删行（按 index）
```

🔥 **第六卡点**：`drop` 的 `axis` 参数——`axis=0` 删行、`axis=1` 删列。**和你已经懂的 [[numpy轴的理解]] 一致**：axis 是消失的那个轴。

---

## 第八部分：`inplace=True` —— 修改原表 vs 链式

视频里反复出现 `inplace=True`，这是 Pandas 一个**重要选择**：

```python
# 写法 A：inplace=True，直接改原表，无返回值
df.set_index("id", inplace=True)
# 此后 df 已经被改了

# 写法 B：默认 inplace=False，返回新表，原表不变
df_new = df.set_index("id")
# df 没变，df_new 是新表
```

**怎么选**：

- **新手**：用 `inplace=True`，思路简单（"修改原表"）
- **进阶**：用链式（`inplace=False`），方便组合多个操作

```python
# 链式风格（Pandas 推荐）
result = (df
          .set_index("id")
          .sort_values("age")
          .head(10))
```

> 🔥 **官方趋势**：Pandas 官方 **逐步不推荐 `inplace=True`**（未来可能弃用）——理由是性能没优势、容易隐藏 bug。建议慢慢习惯 **链式写法**。

---

## 卡点汇总（6 大坑预警）

1. **`loc` 闭区间 vs `iloc` 左闭右开** —— 切片差一个元素
2. **`df["列名"]` 是列，`df.loc["行标签"]` 是行** —— 不要混
3. **`mean()` 自动跳 NaN，`np.mean()` 不跳** —— Pandas 更友好
4. **`df1 + df2` 按 index 对位，不是按位置** —— Pandas 比 NumPy 强大的地方，也最容易困惑
5. **`set_index("id")` 后 id 不在 columns 里** —— 是变成 index，不是消失
6. **多条件用 `&|~` 不是 `and/or`** —— 而且每个条件都要 `()`

---

## 速查 API 表

```python
# 创建
pd.DataFrame({...})
pd.DataFrame({...}, columns=[...], index=[...])

# 属性
df.shape / dtypes / ndim / size / index / columns / values / T

# 取值（4 种）
df.loc[行标签, 列标签]                  # 标签（闭区间）
df.iloc[行位置, 列位置]                 # 位置（左闭右开）
df.at[行标签, 列标签]                   # 单值（快）
df.iat[行位置, 列位置]                  # 单值（快）
df["列名"]                              # 取列
df["列名"].values                       # 退化为 ndarray

# 预览
df.head() / tail() / sample()
df.describe() / info()

# 统计
df["col"].sum/mean/min/max/std/var/median/mode/quantile()
df.count()                              # 非空数
df["col"].value_counts() / unique() / nunique()

# 缺失
df.isna() / notna() / isnull()

# 去重 / 包含
df.drop_duplicates(subset=[...])
df.isin([...])

# 排序
df.sort_index()
df.sort_values(by=[...], ascending=[...])
df.nlargest(n, "col") / nsmallest(n, "col")

# 累计
df.cumsum() / cummax() / cummin() / cumprod() / diff()

# 替换 / 比较
df.replace(老值, 新值)
df1.equals(df2)

# 布尔索引
df[df["col"] > x]
df[(df["a"] > 1) & (df["b"] < 5)]
df[df["col"].isin([...])]

# 运算
df * 2 / df + 100 / df1 + df2  # 自动按标签对位

# 增删改
df.set_index("col", inplace=True)
df.reset_index(inplace=True)
df.rename(index={...}, columns={...})
df["new_col"] = [...]
df.insert(位置, "new_col", [...])
df.drop("col", axis=1)
del df["col"]
```

---

## 自测题（请合上笔记复述）

> 给你 `df = pd.DataFrame({"id":[1,2,3,4,5], "name":["a","b","c","d","e"], "age":[20,30,40,10,50]})`，写代码完成：
>
> 1. 把 `id` 设为行索引
> 2. 取出 age > 25 且 age < 45 的行
> 3. 按 age 降序排，取前 2
> 4. 给 df 新增一列 `is_adult`，age >= 18 为 True 否则 False
> 5. 把 columns 重命名为 中文（姓名 / 年龄 / 成年）

<details>
<summary>👇 答案展开</summary>

```python
import pandas as pd

df = pd.DataFrame({"id":[1,2,3,4,5],"name":["a","b","c","d","e"],"age":[20,30,40,10,50]})

# 1. 设 id 为索引
df.set_index("id", inplace=True)

# 2. 多条件过滤
df[(df["age"] > 25) & (df["age"] < 45)]

# 3. 排序取前 2
df.sort_values(by="age", ascending=False).head(2)
# 或者
df.nlargest(2, "age")

# 4. 新增列
df["is_adult"] = df["age"] >= 18

# 5. 重命名
df.rename(columns={"name":"姓名", "age":"年龄", "is_adult":"成年"}, inplace=True)
```
</details>

---

## 配套笔记

- [[pandas理解]] —— Series/DataFrame 全局心法
- [[numpy轴的理解]] —— axis=0/1 概念
- [[day03_00_概念地图]] —— Day03 主题地图
- [[day03_02_导入导出教程]] —— 下一节：CSV/JSON/MySQL
- [[day03_03_日期处理教程]] —— 下一节：`pd.to_datetime` + `.dt`
- [[day04_02_缺失值处理教程]] —— 后续：缺失值的系统化处理

---

## 学完本节你应该能做到

- ✅ 看到 `df.loc[...]` 立刻知道是按标签还是位置
- ✅ 用一行布尔索引代替 for 循环筛行
- ✅ `set_index` / `reset_index` / `rename` 三件套熟练切换
- ✅ 多条件过滤时正确用 `& | ~` + 括号
- ✅ 拿到陌生数据集第一步本能地 `df.head()` + `df.info()`

**这一节学完，Pandas 真正入门了**。接下来 P03 的导入导出 + P04 的日期处理，是把 DataFrame 和"外部世界"连起来的两个接口。
