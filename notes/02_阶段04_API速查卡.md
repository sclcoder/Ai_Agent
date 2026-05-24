# 阶段04 Numpy / Pandas API 速查卡

> 配合 `01_阶段04_数据分析_精华.md` 使用。
> 这份是「**查询表**」—— 假设你已经懂数据结构基本概念，只列签名和典型用法，不讲原理。
> 写代码忘了某个 API 时 grep 一下就行。

## 📚 官方文档（首选权威来源）

- **Numpy 入门**：https://numpy.org/doc/stable/user/quickstart.html （写给有编程基础的人，正合适）
- **Numpy 完整入门（更慢）**：https://numpy.org/doc/stable/user/absolute_beginners.html
- **Pandas 10 分钟入门**：https://pandas.pydata.org/docs/user_guide/10min.html （**强烈推荐通读一遍**，比看视频快 10 倍）
- **Pandas Cookbook（按场景查）**：https://pandas.pydata.org/docs/user_guide/cookbook.html
- **Pandas API 索引**：https://pandas.pydata.org/docs/reference/index.html

---

## 🟦 Numpy 速查

### 创建 ndarray

```python
import numpy as np

np.array([1, 2, 3])                       # 从列表
np.asarray(lst)                            # 类似 array，但若入参已是 ndarray 则不拷贝（省内存）

np.zeros((3, 4))                           # 全 0
np.ones((3, 4))                            # 全 1
np.empty((3, 4))                           # 未初始化（最快，内容随机）
np.full((3, 4), 7)                         # 全 7
np.eye(3)                                  # 3x3 单位矩阵

np.arange(0, 10, 2)                        # [0 2 4 6 8]，类似 range
np.linspace(0, 1, 5)                       # [0. 0.25 0.5 0.75 1.]，等分 5 个点
np.logspace(0, 3, 4)                       # [1 10 100 1000]，对数等分

np.random.rand(3, 4)                       # [0,1) 均匀
np.random.randn(3, 4)                      # 标准正态
np.random.randint(0, 10, size=(3, 4))      # 整数
np.random.seed(42)                         # 固定随机种子
```

**坑**：`array` vs `asarray` —— 入参是 list 时无差；入参是 ndarray 时 `array` 拷贝，`asarray` 不拷贝。性能敏感场景用 `asarray`。

### 属性

```python
a.shape       # 形状元组
a.ndim        # 维度数
a.size        # 元素总数
a.dtype       # 元素类型
a.itemsize    # 单个元素字节数
a.nbytes      # 总字节数 = size * itemsize
```

### 数据类型转换

```python
a = np.array([1.7, 2.3])
a.astype(np.int32)                         # → [1, 2]，截断不四舍五入
a.astype("float64")                        # 字符串也行
```

常用 dtype：`int8/16/32/64`、`uint8/16/32/64`、`float16/32/64`、`bool_`、`object`、`<U10`（定长字符串）

### 索引与切片

```python
a = np.arange(12).reshape(3, 4)

a[0]              # 第 0 行
a[0, 2]           # 第 0 行第 2 列（推荐写法）
a[0][2]           # 同上，但慢（创建中间数组）
a[:, 1]           # 所有行的第 1 列
a[1:, :2]         # 1 行之后，前 2 列
a[::-1]           # 倒序
a[a > 5]          # 布尔索引
a[[0, 2]]         # 花式索引（取多行）
```

### 基础函数（逐元素）

```python
np.abs(a)         np.sqrt(a)       np.exp(a)        np.log(a)
np.ceil(a)        np.floor(a)      np.rint(a)       np.round(a, 2)
np.sin(a)         np.cos(a)        np.tan(a)
np.add(a, b)      np.subtract(a,b) np.multiply(a,b) np.divide(a,b)
np.where(cond, x, y)        # 类似三元运算符，cond 为真取 x 否则 y
np.isnan(a)       np.isinf(a)      np.isfinite(a)
```

### 统计函数

```python
a.sum()           a.mean()         a.std()          a.var()
a.min()           a.max()          a.argmin()       a.argmax()
a.cumsum()        a.cumprod()      np.median(a)     np.percentile(a, 75)

# axis 方向（最容易搞混的事情）
a.sum(axis=0)     # 沿第 0 轴汇总 —— 「行被压缩」，剩列
a.sum(axis=1)     # 沿第 1 轴汇总 —— 「列被压缩」，剩行
# 记忆法：axis=0 是「向下扫」，axis=1 是「向右扫」
```

### 比较 / 排序 / 去重

```python
np.sort(a)              # 返回新数组
a.sort()                # 原地排序
np.argsort(a)           # 返回排序后的索引
np.unique(a)            # 去重 + 排序
np.unique(a, return_counts=True)   # 同时返回每个值的频次

a == b                  # 逐元素比较，返回布尔数组
np.array_equal(a, b)    # 整体比较，返回单个 bool
```

### 广播规则（必懂）

两个数组运算时，从右向左对齐 shape，每一维要么相等、要么有一个是 1。

```python
np.ones((3, 4)) + np.ones(4)        # ✅ (3,4) + (4,) → (3,4)
np.ones((3, 4)) + np.ones((3, 1))   # ✅ (3,4) + (3,1) → (3,4)
np.ones((3, 4)) + np.ones((4, 1))   # ❌ (3,4) + (4,1) → 报错
```

### 矩阵运算

```python
a @ b                   # 矩阵乘法（推荐，Python 3.5+）
np.dot(a, b)            # 同上
a * b                   # 逐元素乘，不是矩阵乘！
a.T                     # 转置
np.linalg.inv(a)        # 逆矩阵
np.linalg.det(a)        # 行列式
np.linalg.eig(a)        # 特征值/特征向量
np.linalg.solve(A, b)   # 解线性方程组 Ax=b
```

---

## 🟩 Pandas Series 速查

### 创建

```python
import pandas as pd

pd.Series([1, 2, 3])                            # 默认索引 0,1,2
pd.Series([1, 2, 3], index=["a", "b", "c"])     # 自定义索引
pd.Series({"a": 1, "b": 2})                     # 从字典（key 变 index）
pd.Series(5, index=["a", "b", "c"])             # 标量广播
```

### 属性

```python
s.index     s.values     s.shape     s.size
s.dtype     s.name       s.is_unique s.hasnans
```

### 索引（loc 用标签，iloc 用位置）

```python
s.loc["a"]              # 按标签取一个
s.loc[["a", "c"]]       # 按标签取多个
s.iloc[0]               # 按位置取
s.iloc[-1]              # 最后一个
s.at["a"]               # 单值标量（最快）
s.iat[0]                # 单值位置版

s[s > 2]                # 布尔索引
s[s.isin([1, 3])]       # 成员判断
s.between(1, 5)         # 范围判断（含两端）
```

### 常用方法

```python
s.head(5)        s.tail(5)         s.sample(3)
s.value_counts()                   # 频次统计（最常用之一）
s.value_counts(normalize=True)     # 频率（百分比）
s.unique()       s.nunique()       # 唯一值 / 唯一值个数
s.sort_values()  s.sort_index()
s.replace(1, 100)                  # 替换值
s.map({"a": 1, "b": 2})            # 字典映射
s.apply(lambda x: x ** 2)          # 任意函数
s.rename("new_name")
```

### 统计方法

```python
s.mean()  s.median()  s.std()  s.var()  s.sum()
s.min()   s.max()     s.quantile([0.25, 0.5, 0.75])
s.describe()                       # 一次性出所有统计
s.corr(other_series)               # 相关系数
s.cov(other_series)                # 协方差
s.cumsum()  s.cummax()  s.diff()   s.pct_change()
```

### 字符串方法（.str 访问器）

```python
s.str.lower()  s.str.upper()  s.str.strip()
s.str.contains("abc")
s.str.startswith("a")  s.str.endswith("c")
s.str.replace("a", "b", regex=False)
s.str.split(",", expand=True)      # expand=True 拆成多列 DataFrame
s.str.len()
s.str.extract(r"(\d+)")            # 正则提取
```

---

## 🟨 Pandas DataFrame 速查

### 创建

```python
pd.DataFrame({"a": [1, 2], "b": [3, 4]})       # 从字典（最常用）
pd.DataFrame([[1, 3], [2, 4]], columns=["a", "b"])  # 从嵌套列表
pd.DataFrame(np_array, columns=["a", "b"])     # 从 numpy
```

### 属性 / 概览

```python
df.shape    df.columns   df.index    df.dtypes   df.values
df.info()                # 类型 + 非空计数 + 内存
df.describe()            # 数值列统计
df.describe(include="all")          # 所有列（含 object）
df.head(5)  df.tail(5)   df.sample(3)
df.memory_usage(deep=True)
```

### 选列 / 选行

```python
df["col"]               # 单列 → Series
df[["a", "b"]]          # 多列 → DataFrame（注意双层中括号）

df.loc[行标签, 列标签]
df.iloc[行位置, 列位置]
df.loc[:, "a":"c"]      # 切片包含右端（loc 特性）
df.iloc[:, 0:3]         # 切片不含右端（iloc 特性）

df[df["price"] > 100]                      # 布尔筛选
df[(df["a"] > 1) & (df["b"] < 5)]          # 多条件用 &/| 不是 and/or
df.query("a > 1 and b < 5")                # 字符串表达式（更可读）
df.query("col in @some_list")              # 引用外部变量加 @
```

### 修改

```python
df.rename(columns={"old": "new"}, inplace=True)
df.rename(columns=str.lower)               # 函数应用到所有列名

df.set_index("date")                       # 设索引
df.reset_index()                           # 拆索引回普通列
df.reset_index(drop=True)                  # 直接丢弃原索引

df.drop(columns=["a"])                     # 删列
df.drop(index=[0, 1])                      # 删行
df.drop_duplicates(subset=["a"])           # 去重

df["c"] = df["a"] + df["b"]                # 新增列
df.assign(c=lambda d: d.a + d.b)           # 链式风格新增列（不改原 df）

df.sort_values(by=["a", "b"], ascending=[True, False])
df.astype({"a": "int32"})                  # 类型转换
```

### apply（注意 axis 行为）

```python
df["a"].apply(func)                # Series.apply：func 收到标量
df.apply(func, axis=0)             # axis=0：func 收到每「列」（Series）
df.apply(func, axis=1)             # axis=1：func 收到每「行」（Series）
df.applymap(func)                  # 已废弃，用 df.map(func)（pandas 2.1+）
```

**坑**：`DataFrame.apply` 收到的**永远是 Series 不是标量**。要对每个单元格应用就用 `df.map`（标量级）。

### 读写

```python
pd.read_csv("x.csv", parse_dates=["date"], dtype={"id": "int32"})
df.to_csv("x.csv", index=False)            # index=False 别忘

pd.read_json("x.json")     df.to_json("x.json", orient="records")
pd.read_excel("x.xlsx", sheet_name=0)
df.to_excel("x.xlsx", index=False)

pd.read_parquet("x.parquet")               # 大数据首选（快、压缩好、保留类型）
df.to_parquet("x.parquet")

from sqlalchemy import create_engine
engine = create_engine("mysql+pymysql://user:pwd@host/db")
pd.read_sql("SELECT * FROM t", engine)
df.to_sql("t", engine, if_exists="append", index=False)
```

---

## 🟪 拼接 / 关联

### concat（拼接，要求结构相似）

```python
pd.concat([df1, df2])                       # 默认 axis=0，按行堆叠
pd.concat([df1, df2], ignore_index=True)    # 重置索引（重要！）
pd.concat([df1, df2], axis=1)               # 按列拼（要求 index 对齐）
pd.concat([df1, df2], join="inner")         # 只保留共有列；默认 outer
```

### merge（关联，类 SQL JOIN）

```python
pd.merge(left, right, on="key")                            # 默认 inner join
pd.merge(left, right, on="key", how="left")                # left/right/inner/outer
pd.merge(left, right, left_on="lk", right_on="rk")         # 列名不同
pd.merge(left, right, on="key", suffixes=("_l", "_r"))     # 同名列加后缀
pd.merge(left, right, left_index=True, right_index=True)   # 按索引关联
```

### join（默认按索引，merge 的语法糖）

```python
left.join(right, how="left")               # 按索引拼
left.join(right, on="key")                 # 左表用 key 列、右表用索引
```

### 决策树（怎么选）

```
要按列「值」连接两表 → merge
要按「索引」连接 → join 或 merge(left_index=..., right_index=...)
只是「堆」上去（行列）→ concat
```

---

## 🟧 NaN 处理

### 检测

```python
df.isna()       df.notna()        # = isnull / notnull，完全等价
df.isna().sum()                    # 每列缺失数（最常用）
df.isna().any()                    # 每列是否有缺失
df.isna().sum().sum()              # 全表总缺失数

# NaN 的多种来源
None        # Python 的
np.nan      # numpy 的（最常见，本质是 float）
pd.NA       # pandas 的（新版本，支持 Int/Bool 列保留 NaN）
pd.NaT      # 时间列的 NaN
```

### 删除

```python
df.dropna()                                 # 任一列缺失就删行
df.dropna(how="all")                        # 整行全缺失才删
df.dropna(axis=1)                           # 删列而非删行
df.dropna(subset=["a", "b"])                # 只看这几列
df.dropna(thresh=3)                         # 保留至少有 3 个非空值的行
```

### 填充

```python
df.fillna(0)                                # 全填 0
df.fillna({"a": 0, "b": "unknown"})         # 按列指定
df["a"].fillna(df["a"].mean())              # 用均值填
df.ffill()                                  # 向前填（用前面的非空值）
df.bfill()                                  # 向后填

df.interpolate()                            # 数值列插值（线性等）
df.interpolate(method="time")               # 时间序列按时间间隔插值
```

> **按组填空**见 `01_精华.md` 的 `transform` 章节，那才是生产用法。

---

## 🟫 透视表 pivot_table

```python
df.pivot_table(
    values="price",          # 要聚合的列
    index="zipcode",         # 行维度（可传 list）
    columns="is_renovated",  # 列维度（可传 list）
    aggfunc="mean",          # 聚合函数（可传 list 或 dict）
    fill_value=0,            # NaN 填充
    margins=True,            # 加 All 汇总行/列
)

# 多聚合
df.pivot_table(values="price", index="zip",
               aggfunc=["mean", "max", "count"])

# 不同列用不同聚合
df.pivot_table(index="zip",
               aggfunc={"price": "mean", "bedrooms": "sum"})
```

### pivot_table vs groupby

| 场景 | 用哪个 |
|---|---|
| 一维聚合 | `groupby` 更直观 |
| 二维交叉（行+列两个维度） | `pivot_table` 完胜 |
| 复杂自定义聚合 | `groupby + agg` |
| 同时多种聚合函数 | 都可以，`pivot_table` 表头更整齐 |

---

## 🟥 绘图（matplotlib + pandas + seaborn）

### Matplotlib 中文字体（macOS / Windows）

```python
import matplotlib.pyplot as plt
from matplotlib import rcParams

# macOS
rcParams["font.sans-serif"] = ["PingFang SC", "Arial Unicode MS"]
# Windows
rcParams["font.sans-serif"] = ["SimHei"]

rcParams["axes.unicode_minus"] = False     # 负号正常显示（必加，否则负号显示成方框）
```

### Matplotlib 基础

```python
# 单图
plt.figure(figsize=(10, 6))
plt.plot(x, y, label="line1")
plt.hist(data, bins=30, edgecolor="k")
plt.scatter(x, y, c=color, s=size, alpha=0.5)
plt.bar(x, y)         plt.barh(x, y)        # 竖/横柱
plt.title("标题")     plt.xlabel("x")       plt.ylabel("y")
plt.legend()          plt.grid()
plt.savefig("a.png", dpi=150, bbox_inches="tight")
plt.show()

# 子图（推荐 OO 风格）
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes[0, 0].plot(x, y)
axes[0, 0].set_title("子图1")
axes[1, 1].scatter(x, y)
plt.tight_layout()
```

### Pandas 内置 .plot

```python
df["price"].plot(kind="hist", bins=30)
df.plot(kind="line", x="date", y="price")
df.plot(kind="bar", stacked=True)
df.plot(kind="scatter", x="a", y="b", c="group", colormap="viridis")
df.plot(kind="box")
df.plot(kind="pie", y="value")
```

**何时用**：探索性分析快速出图（一行代码）。**何时不用**：正式报告 → 用 matplotlib 或 seaborn 精雕。

### Seaborn（统计可视化首选）

```python
import seaborn as sns

sns.histplot(data=df, x="price", kde=True, hue="category")
sns.kdeplot(data=df, x="price", hue="group")
sns.scatterplot(data=df, x="a", y="b", hue="cat", size="z", style="cat")
sns.boxplot(data=df, x="cat", y="price")
sns.violinplot(data=df, x="cat", y="price")
sns.heatmap(df.corr(), annot=True, cmap="coolwarm", center=0)    # 相关性矩阵首选
sns.pairplot(df[["a", "b", "c", "d"]], hue="cat")                # 一次出所有两两散点（探索性分析杀器）
sns.lineplot(data=df, x="date", y="price", hue="group")
sns.countplot(data=df, x="cat")                                  # 类别频次柱图
```

Seaborn 的核心优势：**自动用 hue 拆分 + 自动加置信区间 + 默认配色比 matplotlib 顺眼**。

---

## ⚡ 30 秒回忆卡

```python
# Numpy
np.arange / np.linspace / np.random.randn / np.where / a.sum(axis=)
# Pandas IO
pd.read_csv(parse_dates=) / df.to_csv(index=False)
# Pandas 索引
df.loc[label] / df.iloc[pos] / df.query("a > 1") / df[df.a > 1]
# Pandas 变换
df.assign / df.rename / df.sort_values / df.drop_duplicates(subset=)
# 拼接
pd.concat([a, b], ignore_index=True) / pd.merge(a, b, on=, how=)
# NaN
df.isna().sum() / df.fillna({col: val}) / df.dropna(subset=)
# 透视
df.pivot_table(values=, index=, columns=, aggfunc=)
# 画图
sns.heatmap(df.corr(), annot=True) / sns.pairplot / df.plot(kind=)
```

---

## 📎 配套文档

- [01_阶段04_数据分析_精华.md](./01_阶段04_数据分析_精华.md) ← 文档讲不清的进阶模式（transform / 链式去重 / 项目模板）
- [00_环境工具速查_Anaconda_conda_Jupyter.md](./00_环境工具速查_Anaconda_conda_Jupyter.md) ← 环境基础
