# Day02 · 第四节：Series 入门（P05 + P06 + P07）

> 视频 P05（创建）+ P06（属性）+ P07（方法、布尔索引、运算）。这一节是**进入 Pandas 的第一步**。
>
> **好消息**：你已经把 DataFrame 学透了——**Series 是 DataFrame 的"单列版"**，所有方法几乎一一对应。这一节速通。

---

## 一句话定位

```
Series = "带 index 的一维 ndarray + name 标签"

       ndarray:    [11, 22, 33, 44, 55]
                       ↑
       Series:    a    11
                  b    22
                  c    33    ← name: 'atguigu'
                  d    44
                  e    55
                       ↑
                  每个元素都有标签
```

**和 ndarray 的区别**：

| 项 | ndarray | Series |
|---|---|---|
| 维度 | N 维 | **只能 1D** |
| 标签 | 无（只有位置）| 有 `index`（标签）|
| 名字 | 无 | 有 `name` |
| 类型 | 整数组一个 dtype | 同 |
| 用法 | 数学计算为主 | **数据分析为主** |

**和 DataFrame 的关系**：

```
DataFrame = 多个 Series 拼起来（共享同一个 index）
Series    = DataFrame 的"一列"
```

---

## 第一部分：P05 — Series 的创建（5 种方式）

### 1.1 法 A：从列表造（最简单）

```python
import pandas as pd

s1 = pd.Series([3, 1, 2, 4])
# 0    3
# 1    1
# 2    2
# 3    4
# dtype: int64
```

**默认 index 是 0..n-1**（和 ndarray 一致）。

### 1.2 法 B：指定 index

```python
s2 = pd.Series([3, 1, 2, 4, 5],
               index=['a', 'b', 'c', 'd', 'e'])
# a    3
# b    1
# c    2
# d    4
# e    5
```

`index` 是 Series **最关键的特性**——它让数据从"靠位置"变成"靠标签"。

### 1.3 法 C：指定 index + name

```python
s3 = pd.Series([3, 1, 2, 4, 5],
               index=['a','b','c','d','e'],
               name='numbers')
# a    3
# b    1
# ...
# Name: numbers, dtype: int64
```

**`name` 的用途**：

- Series 转成 DataFrame 时**变成列名**
- 画图时**变成图例**
- 多个 Series 拼接（`concat`）后**区分来源**

### 1.4 法 D：从字典造

```python
s4 = pd.Series({"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
               name="numbers")
# a    1
# b    2
# c    3
# d    4
# e    5
```

**dict 的 key 自动变成 index，value 变成数据**。

### 1.5 法 E：从字典造 + 筛选 index（**精彩**）

```python
dic = {"a": 4, "b": 7, "c": -5, "d": 3}

# 全部：默认按 dict 的 key 当 index
s5 = pd.Series(dic, name="numbers")
# a    4
# b    7
# c   -5
# d    3

# 只取 index=['a','d'] 的部分
s6 = pd.Series(dic, index=["a", "d"], name="numbers")
# a    4
# d    3
```

🔥 **关键认知**：当 `dict` + 显式 `index` 同时给——**Series 会按 index 从 dict 里挑数据**：

- index 在 dict 里有 → 用对应 value
- index 在 dict 里没有 → 填 `NaN`

```python
dic = {"a": 4, "b": 7}
s = pd.Series(dic, index=["a", "x"])
# a    4.0
# x    NaN     ← x 不在 dict 里 → NaN
```

这个特性在 **数据对齐 / 重排** 时极有用。

---

## 第二部分：P06 — Series 的属性 + 取值器

### 2.1 7 个核心属性

```python
arrs = pd.Series([11, 22, 33, 44, 55],
                 name="atguigu",
                 index=["a", "b", "c", "d", "e"])

arrs.index       # Index(['a','b','c','d','e'], dtype='object')
arrs.values      # array([11, 22, 33, 44, 55])  ← ndarray！
type(arrs.values)# numpy.ndarray
arrs.ndim        # 1（永远 1）
arrs.shape       # (5,)
arrs.size        # 5
arrs.dtype       # int64    （或 .dtypes，两者等价）
arrs.name        # 'atguigu'
```

🔥 **`s.values` 返回 ndarray**——这是 Series 和 NumPy 的桥。任何 ndarray 函数都能作用于 `s.values`。

### 2.2 4 种取值器（和 DataFrame 完全一致）

```python
# loc —— 标签（闭区间）
arrs.loc["a":"c"]         # a/b/c 三个
# a    11
# b    22
# c    33

# iloc —— 位置（左闭右开）
arrs.iloc[0:2]            # 前 2 个
# a    11
# b    22

# at —— 单元素，按标签（**最快**）
arrs.at["c"]              # 33

# iat —— 单元素，按位置（**最快**）
arrs.iat[2]               # 33
```

🔥 **你在 DataFrame 已经熟了**——Series 这里**完全一致**：

| 取值器 | 索引方式 | 区间 |
|---|---|---|
| `loc` | 标签 | **闭区间** |
| `iloc` | 位置 | **左闭右开** |
| `at` | 标签 | 单值 |
| `iat` | 位置 | 单值 |

### 2.3 一个小坑：直接 `s["a"]` 也能用

```python
arrs["a"]                 # 11    ← 等价于 arrs.loc["a"]
arrs[0]                   # 11    ← 等价于 arrs.iloc[0]
arrs[0:2]                 # 等价于 arrs.iloc[0:2]
```

**但是不推荐**——当 index 是整数时这两种用法会冲突，**很容易引入隐藏 bug**。**养成永远显式 `loc/iloc` 的习惯**。

---

## 第三部分：P07 — Series 的方法（**和 DataFrame 一一对应**）

### 3.1 9 大类方法（速过）

```python
arrs = pd.Series([11, 22, np.nan, None, 44, 22],
                 index=['a','b','c','d','e','f'])
```

#### 类 1：预览

```python
arrs.head(2)           # 前 2 个
arrs.tail(2)           # 后 2 个
arrs.sample()          # 随机抽 1 个
```

#### 类 2：包含 / 缺失

```python
arrs.isin([11, 44, np.nan])    # 每个元素是否在列表
arrs.isna()                    # 是否 NaN（包括 None / NaN / NaT）
arrs.count()                   # 非空数（忽略 NaN）
arrs.size                      # 总数（含 NaN）
len(arrs)                      # 同 .size
```

#### 类 3：统计九件套

```python
arrs.sum()             # 自动忽略 NaN
arrs.mean()
arrs.min() / max()
arrs.std() / var()
arrs.median()
arrs.mode()            # 众数
arrs.quantile(0.25)
arrs.quantile(0.5, interpolation='midpoint')  # 5 种插值法
```

🔥 **`quantile` 的 `interpolation` 参数**（视频里讲了）：

```python
# 当分位点不在数据点上时，5 种插值方式
arrs.quantile(0.25, interpolation='linear')    # 线性插值（默认）
arrs.quantile(0.25, interpolation='lower')     # 取下界
arrs.quantile(0.25, interpolation='higher')    # 取上界
arrs.quantile(0.25, interpolation='midpoint')  # 取中点
arrs.quantile(0.25, interpolation='nearest')   # 取最近
```

⭐ 默认 `linear` 就行，知道有这参数即可。

#### 类 4：总览 `describe`

```python
arrs.describe()
# count    4.000000      ← 非空数
# mean    25.000000
# std     14.142136
# min     11.000000
# 25%     17.750000
# 50%     22.000000
# 75%     29.500000
# max     44.000000
```

#### 类 5：去重

```python
arrs.unique()                  # ndarray，去重后的值
arrs.nunique()                 # 不重复值的个数（int）
arrs.drop_duplicates()         # 删除重复元素，返回 Series
arrs.value_counts()            # 每个值出现几次（自动倒序）
```

#### 类 6：排序

```python
arrs.sort_index()              # 按 index 排
arrs.sort_values(ascending=False)  # 按值排
```

#### 类 7：替换 / 转换

```python
arrs.replace(22, 66)           # 把 22 替换成 66
arrs.replace({22: 66, 11: 99}) # 多个替换

arrs.to_frame()                # Series → DataFrame
                               # （列名就是 Series 的 name）
```

#### 类 8：比较 / 相关

```python
arr1 = pd.Series([1,2,3])
arr2 = pd.Series([1,2,3,4])
arr1.equals(arr2)              # False（长度不同）

arr3 = pd.Series([3,2,1])
arr1.corr(arr3)                # -1.0（完全负相关）
arr1.cov(arr3)                 # 协方差
```

🔥 **`corr` 解读**（皮尔逊相关系数）：

| 值 | 含义 |
|---|---|
| `1.0` | 完全正相关（一个涨另一个涨）|
| `0` | 无线性相关 |
| `-1.0` | 完全负相关 |

实战场景：分析"气温 vs 冰淇淋销量"、"广告投入 vs 营收"。

#### 类 9：可视化 / 遍历

```python
arrs.hist(bins=5)              # 直方图（需要 matplotlib）

for i, v in arrs.items():      # 遍历 (index, value)
    print(i, v)
# a 11.0
# b 22.0
# ...
```

### 3.2 完整方法对照表（和 DataFrame 一一对应）

| Series 方法 | DataFrame 方法 | 一致吗 |
|---|---|---|
| `s.head() / tail()` | `df.head() / tail()` | ✅ |
| `s.describe()` | `df.describe()` | ✅ |
| `s.isin([...])` | `df.isin([...])` | ✅ |
| `s.isna()` | `df.isna()` | ✅ |
| `s.sum() / mean() / ...` | `df.sum() / mean() / ...` | ✅ Series 一个数，DataFrame 每列一个 |
| `s.value_counts()` | `df["col"].value_counts()` | ✅ 完全等价 |
| `s.unique()` | `df["col"].unique()` | ✅ |
| `s.sort_values()` | `df.sort_values(by="col")` | DataFrame 要指定 `by` |
| `s.drop_duplicates()` | `df.drop_duplicates(subset=[...])` | ✅ |
| `s.replace()` | `df.replace()` | ✅ |
| `s.loc / iloc / at / iat` | `df.loc / iloc / at / iat` | ✅ |

🔥 **掌握 Series 的方法 == 90% DataFrame 单列操作**。

---

## 第四部分：Series 的布尔索引（**核心动作**）

```python
s = pd.Series({"a": -1.2, "b": 3.5, "c": 6.8, "d": 2.9})

bools = s > s.mean()           # mean = 3.0
# a    False
# b     True
# c     True
# d    False

s[bools]                       # 取出 True 的
# b    3.5
# c    6.8
```

🔥 **完全等价的一行写法**（实战首选）：

```python
s[s > s.mean()]
```

这是 [[day03_01_DataFrame教程]] 里 `df[df["age"]>25]` 的**根源**——DataFrame 的布尔索引就是把 Series 的布尔索引"应用到行"。

---

## 第五部分：Series 的运算（按 index 对位）

### 5.1 Series + 标量（广播）

```python
s = pd.Series({"a": -1.2, "b": 3.5, "c": 6.8, "d": 2.9})

s * 10
# a   -12.0
# b    35.0
# c    68.0
# d    29.0
```

### 5.2 Series + Series（**按 index 对位，不是按位置！**）

```python
s = pd.Series([1, 2, 3, 4])                   # index: 0, 1, 2, 3
s1 = pd.Series([10, 20, 30, 40],              # index: 1, 2, 3, 4
                index=[1, 2, 3, 4])

s + s1
# 0     NaN              ← s1 没有 index 0
# 1    12.0              ← s[1]=2 + s1[1]=10 = 12
# 2    23.0
# 3    34.0
# 4     NaN              ← s 没有 index 4
```

🔥 **这是 Pandas 和 NumPy 最大的差异**——你在 [[day03_01_DataFrame教程]] 已经踩过这个坑：

| 工具 | 加法行为 |
|---|---|
| NumPy `arr1 + arr2` | **按位置**（要求 shape 一致或可广播）|
| Pandas `s1 + s2` | **按 index 对位**（标签对不上的填 NaN）|

**这是 Pandas 强大的地方**——你不用记"第 5 行是用户 A"，标签自动对齐。**也是新手最容易困惑的地方**——`s + s1` 怎么多了 NaN？因为 index 没对齐。

---

## 卡点汇总（5 大坑预警）

1. **Series 的 `name` 不是 index 的名字** —— `s.name` 是整个 Series 的名字（转 DataFrame 时变列名）；index 的名字是 `s.index.name`
2. **`s + s1` 按 index 对位** —— 不要以为是按位置（这点和 NumPy 完全不同）
3. **`s["a"]` 和 `s[0]` 在整数 index 时会冲突** —— 永远显式 `loc/iloc`
4. **`s.values` 是 ndarray** —— 想用 NumPy 函数时通过它转
5. **`quantile` 的 `interpolation`** —— 不在数据点上的分位数怎么算（5 种插值法）

---

## Series vs DataFrame 决策表

| 你的数据 | 用什么 |
|---|---|
| 1 列数值（如"工资"列）| **Series** |
| 多列数值（如完整员工表）| **DataFrame** |
| 1 列数值 + 标签（如时间序列）| **Series** + DatetimeIndex |
| 字典 `{key: value}` | 想计算用 Series、想结构化用 DataFrame |

**实战常见**：

```python
df["salary"]                    # 取一列 → Series
df.loc[0]                       # 取一行 → Series（index 是列名）
df.mean()                       # 各列均值 → Series（index 是列名）
df.iloc[0]                      # 第一行 → Series
```

→ **DataFrame 的所有"取出来的某一维"都是 Series**。

---

## 速查 API 表

```python
# 创建
pd.Series([1,2,3])
pd.Series([1,2,3], index=['a','b','c'], name='x')
pd.Series({'a':1, 'b':2})
pd.Series(d, index=['a','d'])            # dict + 筛选

# 属性
s.index / values / ndim / shape / size / dtype / name
# s.values 是 ndarray，是 Series 和 NumPy 的桥

# 取值
s.loc['a':'c']                           # 标签（闭区间）
s.iloc[0:3]                              # 位置（左闭右开）
s.at['a'] / s.iat[0]                     # 单值

# 预览
s.head() / tail() / sample()
s.describe()

# 包含 / 缺失
s.isin([...]) / isna() / notna()
s.count() / size

# 统计
s.sum() / mean() / min() / max() / std() / var() / median() / mode()
s.quantile(0.5, interpolation='linear')

# 去重
s.unique() / nunique() / drop_duplicates() / value_counts()

# 排序
s.sort_index() / sort_values(ascending=False)

# 替换 / 转换
s.replace(old, new)
s.to_frame()                             # → DataFrame
s.equals(other)

# 相关性
s.corr(other) / cov(other)

# 可视化 / 遍历
s.hist(bins=10)
for i, v in s.items(): ...

# 布尔索引
s[s > s.mean()]

# 运算
s * 2                                    # 广播
s1 + s2                                  # 按 index 对位（对不上填 NaN）
```

---

## 自测题（请合上笔记复述）

> 1. 从 `dic = {"a":1, "b":2, "c":3}` 造一个只包含 a 和 d 的 Series。d 对应什么值？
> 2. `s1 + s2`，s1 的 index 是 `[0,1,2]`，s2 的 index 是 `[1,2,3]`，结果有几个非 NaN 值？
> 3. `s.values` 是什么类型？
> 4. 怎么把一个 Series 转成单列的 DataFrame？列名怎么决定？
> 5. `arr.sum()` 和 `s.sum()` 都会自动跳过 NaN 吗？
> 6. `s.corr(s2)` 返回 `-0.95` 表示什么？

<details>
<summary>👇 答案展开</summary>

1. `pd.Series(dic, index=["a", "d"])` → a 是 1，d 是 NaN（因为 dic 里没有 d）
2. 2 个（index 1 和 2 重合，0 和 3 各自填 NaN）
3. `numpy.ndarray`
4. `s.to_frame()`——列名 = Series 的 `s.name`（没有 name 则列名是 `0`）
5. NumPy 的 `np.sum(arr)` **不会**跳 NaN（结果是 NaN），用 `np.nansum`；Pandas 的 `s.sum()` **会**自动跳
6. 几乎完全负相关——s 增大时 s2 减小

</details>

---

## 配套笔记

- [[day02_00_概念地图]] —— Day02 主题地图
- [[day02_01_ndarray索引切片教程]] —— ndarray 索引
- [[day02_02_ndarray函数与统计教程]] —— NumPy 统计函数
- [[day02_03_广播与矩阵运算教程]] —— 广播（**重头戏**）
- [[day03_01_DataFrame教程]] —— DataFrame（你已学，Series 是它的剥皮版）
- [[pandas理解]] —— Pandas 全局心法

---

## 学完本节你应该能做到

- ✅ Series 的 `loc / iloc / at / iat` 闭眼用
- ✅ 看到 `df["col"]` 立刻意识到这是 Series（不是 DataFrame）
- ✅ 用布尔索引 `s[s > 0]` 而不是手写循环
- ✅ 理解 `s1 + s2` 按 index 对位，知道为什么会出 NaN
- ✅ 把 ndarray 函数和 Series 方法对应起来想

---

**Day02 学完意味着什么**：

NumPy 你已经会"造、用、算"——这是后面所有 ML/DL 框架的底层。

Pandas 你已经会 Series + DataFrame——这是后面所有数据分析的标准对象。

**Day03 教 DataFrame 全套**——你已经学过了，回头扫一眼 [[day03_00_概念地图]] 做个串联即可。

**Day04 教 Pandas 进阶（concat/merge/cleanup/apply/groupby进阶）**——你也已经学过了。

接下来推荐方向：
- **Day05/Day06** 课程剩余的可视化 + 综合实战
- 或直接进入 **阶段05 机器学习**（你之前做过泰坦尼克号，已经摸到 ML 入口）
