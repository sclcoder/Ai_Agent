# Pandas `groupby` 系统理解

> 给 iOS 老兵的 groupby 速通。**一次搞懂、终身受益**——后面学 transform / agg / apply 都是它的扩展，进入 PyTorch DataLoader / SQL window function 也是同一思维。

---

## 一句话定位

> **`groupby` 是一个「作用域开关」——一旦挂上它，后面的所有操作都自动变成"每组各做一次"。**

```
没有 groupby:                          有 groupby:
df.mean()                              df.groupby("month").mean()
   ↓                                       ↓
"对整张表算一次"                       "对每组算一次"  ← 自动分发
   ↓                                       ↓
返回 1 行                              返回 N 行（N = 组数）
```

`mean` 函数本身没变，**变的是它面对的"数据是什么"**。

---

## 核心机制：Split-Apply-Combine

业界标准三步走（出自 Hadley Wickham 2011 年的论文）：

```
┌─────────────┐    Split        ┌──┐┌──┐┌──┐
│ 整张大表    │    ──────→      │  ││  ││  │   按 key 切成 N 组
└─────────────┘                 └──┘└──┘└──┘
                                  │   │   │
                                  ▼   ▼   ▼     Apply
                                 ƒ   ƒ   ƒ     每组各做一次 ƒ
                                  │   │   │
                                  ▼   ▼   ▼
                                ┌────────────┐
                                │ 拼回结果   │   Combine
                                └────────────┘
```

- **Split** = `groupby(key)` —— 按 key 把表切成多组（**懒**，不真做）
- **Apply** = `.mean()` / `.sum()` / `.agg(...)` —— 每组独立做操作
- **Combine** = Pandas 自动把每组结果拼成一个 DataFrame/Series

---

## 读链子的规则（解决"业务反推"病）

### 错误读法（你最初的本能）

> "按月分组、选两列、求平均"

→ 模糊。"求平均"作用于啥不清楚，只能靠"业务有意义吗？"反推。

### 正确读法

把每个 `.xxx` 当作**独立动作**，每步问一句"**现在面对什么数据**"。

```python
df.groupby("month")[["temp_max","temp_min"]].mean()
```

| 步骤 | 现在面对什么 | 类型 |
|---|---|---|
| `df` | 一张大表 | `DataFrame` |
| `.groupby("month")` | **N 张小桌子**（按月切）| `DataFrameGroupBy`（懒）|
| `[["temp_max","temp_min"]]` | 每张小桌子只看 2 列 | `DataFrameGroupBy`（仍懒）|
| `.mean()` | **每张小桌子各算一次平均** | `DataFrame`（真执行）|

**关键转变在第 2 步**：从"一张大表"变成"N 张小桌子"。后面所有操作**自动作用于每张小桌子**。

---

## 选列：单括号 vs 双括号

和普通 DataFrame 选列规则一致：

```python
g = df.groupby("month")

g["temp_max"]              # 单括号 → SeriesGroupBy → 聚合后返回 Series
g[["temp_max"]]            # 双括号 → DataFrameGroupBy → 聚合后返回 DataFrame
g[["temp_max", "temp_min"]] # 双括号 + 多列 → 聚合后返回 DataFrame
```

| 选法 | 聚合后类型 | 何时用 |
|---|---|---|
| `g["col"]` | `Series`（一列）| 只看一列 |
| `g[["col1", "col2"]]` | `DataFrame`（多列）| 看多列 |
| `g[["col"]]` | `DataFrame`（一列）| 想保持 DataFrame 形态 |

---

## 单列分组 vs 多列分组

### 单列分组

```python
df.groupby("month")  # 按 month 一列 → N 组（N = month 的唯一值个数）
```

### 多列分组

```python
df.groupby(["month", "weather"])  # 按 (month, weather) 元组分组
```

**规则**：按 N 列分组 = **按这 N 列值的"所有不重复组合"分组**。每个出现过的组合就是一组。

---

## 🔥 关键陷阱：`groupby` 不会"补齐"

> **`groupby` 是从数据里"发现"组，不是凭空"枚举"所有可能组合。**
>
> **出现过的组合才有组，没出现的视为不存在**——结果里**根本没那一行**，不是"有但为 0"。

### 例子

假设数据按 (month, weather) 分组：

| 数学上可能 | 实际建组 |
|---|---|
| 48 月 × 5 种天气 = **240 个组合** | 大约 **150 组**（每月平均 3-4 种天气出现）|

如果 2 月**从没下过 drizzle**：
- `(2012-02, drizzle)` 这一组**不存在**
- 结果中**没有这一行**——不是"有但值是 0"

### 想"补齐"成 240 行（缺的填 0）

```python
df.groupby(["month", "weather"]).size().unstack(fill_value=0)
#                                          ↑
#                          把不存在的 (month, weather) 组合填 0
```

或用 `reindex`：

```python
all_combos = pd.MultiIndex.from_product([months, weathers], names=["month","weather"])
result.reindex(all_combos, fill_value=0)
```

**默认行为是"只算存在的组合"**——理解了这条规则后再考虑补齐。

---

## 聚合函数大全（按用途分）

### 1. 单一统计：直接调函数名

```python
g.mean()      # 每列每组的均值
g.sum()       # 每列每组的和
g.max()       # 每列每组的最大值
g.min()       # 每列每组的最小值
g.std()       # 每列每组的标准差
g.var()       # 每列每组的方差
g.median()    # 每列每组的中位数

g.count()     # 每列每组的"非空数"
g.size()      # 每组的"行数"（不分列，整组一个数）
g.nunique()   # 每列每组的"不重复值数"
g.first()     # 每组第一行
g.last()      # 每组最后一行
```

#### `count` / `size` / `nunique` 别搞混

| 函数 | 计什么 | 注意 |
|---|---|---|
| `count()` | 非空值的数量 | 按列算，**忽略 NaN** |
| `size()` | 组的总行数 | 不分列，**含 NaN** |
| `nunique()` | 不重复值的数量 | 按列算 |

### 2. 多种统计同时算：`agg`

```python
g["temp_max"].agg(["mean", "max", "min", "std"])
# 一次输出 4 列：mean / max / min / std
```

```python
g[["temp_max", "temp_min"]].agg(["mean", "max"])
# 多列 × 多统计 → 多级列名
```

#### 不同列做不同统计

```python
g.agg({
    "temp_max": "mean",
    "temp_min": "min",
    "wind":     ["mean", "std"]
})
# 用字典精确指定：哪一列做哪种统计
```

### 3. 保留原 shape：`transform`

> `aggregate` 把每组**压成一行**；`transform` 把结果**广播回每行**。

```python
# 算每月均温
g["temp_max"].mean()
# month
# 2012-01     8.65
# 2012-02    12.34
# → 48 行结果

# 把"该行所在月份的均温"加回每一行
df["month_avg"] = g["temp_max"].transform("mean")
# 原 df 1461 行全保留，多一列每行所在月份的均值
# → 1461 行
```

**经典用法**：算"每行减去所在组的均值"做标准化。

```python
df["temp_max_centered"] = df["temp_max"] - g["temp_max"].transform("mean")
```

### 4. 自定义复杂逻辑：`apply`

```python
def top3_temps(group):
    """返回这组里温度最高的 3 行"""
    return group.nlargest(3, "temp_max")

df.groupby("month").apply(top3_temps)
# 每组各跑一次 top3_temps 函数
```

**`apply` 最灵活但最慢**——能用 `agg` / `transform` 就别用 `apply`。

### 5. 过滤组：`filter`

```python
# 只保留"行数 > 28 天"的月份（剔除短月）
g.filter(lambda x: len(x) > 28)
```

---

## 常见陷阱清单

### 陷阱 1：单括号双括号搞混

```python
g["temp_max"].mean()      # 返回 Series
g[["temp_max"]].mean()    # 返回 DataFrame
```

要做后续合并操作时类型不一致会报错。

### 陷阱 2：分组列变成 index 了

```python
result = df.groupby("month").mean()
result.columns   # 列里没有 'month'！
result.index     # 'month' 变成了 index
```

**修复**：

```python
df.groupby("month", as_index=False).mean()   # 方法 1：不要 index
df.groupby("month").mean().reset_index()      # 方法 2：事后重置
```

### 陷阱 3：以为不存在的组合会被自动补齐

```python
df.groupby(["month", "weather"]).size()
# 如果 (2012-02, drizzle) 不存在 → 结果里没这一行！不是 0
```

要补齐：用 `unstack(fill_value=0)` 或 `reindex`。

### 陷阱 4：`apply` 自动加列

```python
df.groupby("month").apply(some_func)
# 结果可能多一层 index（看 some_func 返回什么）
```

不确定时打印 `.head()` 看一眼。

### 陷阱 5：分组聚合后类型变 float

```python
df["x"] = [1, 2, 3, 4]       # int64
df.groupby(...).sum()["x"]    # 可能变 float64
```

**为什么**：含 NaN 列会被升级为 float。需要时 `.astype(int)` 回去。

### 陷阱 6：`mean()` 误算字符串列

```python
df.groupby("month").mean()  # 老版会跳过字符串列；新版可能报错
# 解决：显式选列
df.groupby("month")[["temp_max", "temp_min"]].mean()
```

---

## 跨语言对照表

`groupby + 聚合` 是个普适概念，几乎所有数据处理语言都有：

| 工具 | 写法 |
|---|---|
| **Pandas** | `df.groupby("month").mean()` |
| **SQL** | `SELECT month, AVG(...) FROM t GROUP BY month` |
| **Swift** | `Dictionary(grouping: items, by: \.month).mapValues { ... }` |
| **JS (Lodash)** | `_.chain(items).groupBy("month").mapValues(avg).value()` |
| **Java (Streams)** | `items.stream().collect(groupingBy(Item::month, averagingDouble(...)))` |
| **Python 原生** | `itertools.groupby` + 手动算（不推荐，麻烦）|

**核心思想都一样**：先分桶，再对桶里的数据各做一遍。

---

## 实战速查表（按场景）

| 想做什么 | 写法 |
|---|---|
| 按 A 算每组均值 | `df.groupby("A")["x"].mean()` |
| 按 A 算每组多种统计 | `df.groupby("A")["x"].agg(["mean","max","min"])` |
| 按 A、B 双重分组 | `df.groupby(["A","B"])["x"].mean()` |
| 不同列不同聚合 | `df.groupby("A").agg({"x":"mean", "y":"sum"})` |
| 每行减去组均值（去中心化） | `df["x"] - df.groupby("A")["x"].transform("mean")` |
| 每组取前 3 行 | `df.groupby("A").head(3)` |
| 每组按 score 取最大 1 行 | `df.loc[df.groupby("A")["score"].idxmax()]` |
| 每组数行数（含 NaN） | `df.groupby("A").size()` |
| 每组数非空（按列）| `df.groupby("A").count()` |
| 每组数不重复值 | `df.groupby("A")["x"].nunique()` |
| 每组的累计和 | `df.groupby("A")["x"].cumsum()` |
| 每组的占比 | `df["x"] / df.groupby("A")["x"].transform("sum")` |
| 过滤"组行数 > 10"的组 | `df.groupby("A").filter(lambda g: len(g) > 10)` |
| 把不存在的组合补 0 | `df.groupby([...]).size().unstack(fill_value=0)` |
| 不要分组列当 index | `df.groupby("A", as_index=False)...` |

---

## 进阶模式预览（用到再深入）

```python
# 滚动窗口（每组内做时间序列分析）
g.rolling(window=7).mean()

# 累计/排名（每组内）
g["x"].rank()
g["x"].cumsum()
g["x"].pct_change()

# 偏移（取前一行/后一行的值）
g["x"].shift(1)

# 双分组 + pivot 形成交叉表
df.groupby(["month","weather"]).size().unstack(fill_value=0)
```

后面学时间序列、特征工程时会反复用。**底层全是同一规则**：作用域开关 + apply。

---

## 总结：三层认知

```
第 1 层  会调函数             ── 看课程能学到，能写出 .groupby(...).mean()
第 2 层  懂 split-apply-combine ── 理解机制，知道为什么是"每组一次"
第 3 层  能预测结果 shape      ← 你现在的目标
       和性质（如不补齐）
```

**到达第 3 层后**：

- 看到任何 `groupby` 链能秒答 shape、dtype、index 是什么
- 不再用"业务反推"读代码
- 学 transform / agg / apply / window 时全是这套规则的扩展

---

## 相关笔记

- [[pandas理解]] —— DataFrame / Series 的整体定位
- [[numpy_pandas_重点清单]] —— groupby 在 ⭐⭐⭐ 清单里的位置
- [[numpy轴的理解]] —— axis 概念，理解多级 index 时会用到
