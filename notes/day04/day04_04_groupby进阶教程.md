# Day04 · 第四节：groupby 进阶（agg / transform / filter / cut）

> 课程视频 15-18，对应 `P06_Agg_Trans_Filter.ipynb`。深度对标 [[day04_01_表合并教程]] / [[day04_02_缺失值处理教程]] / [[day04_03_apply教程]]。
>
> **前置基础**：你已经把 [[groupby系统理解]] 学透了（split-apply-combine、作用域开关、单/双括号、不补齐组合）。**这一节是在那套基础上叠 4 个"花式工具"**：`cut` / `agg 进阶` / `transform 实战` / `filter`。

---

## 你已经会的部分 vs 这一节新增的部分

| 已会 ✅（来自 [[groupby系统理解]] 或 P05_Weather）| 这一节新增 🆕 |
|---|---|
| 基础聚合 `g.mean()` / `g.sum()` / `g.size()` | `agg` 的"自定义函数"用法 |
| 单/双括号选列 | `agg + dict + rename` 三连 |
| 多列分组 `groupby(["a","b"])` | `pd.cut` / `pd.qcut` 分箱 |
| `as_index=False` 不让分组列变 index | `transform("mean")` 的两个实战（去中心化 + 按组填缺失）|
| `transform` 的"广播回每行" | `filter` 的"按组条件保留/丢弃整组" |
| `apply` 灵活但慢 | 遍历分组 `for k, g in groupby`、`get_group()` |

**核心节奏**：本节不再讲 groupby 是什么（你已经懂），而是补 4 个工具让你处理真实业务场景。

---

## 视频 15：groupby 基础回顾 + 这一节用到的新数据集

### 数据：employees.csv（HR 员工表）

视频 15 切换到了一个新数据集。列名（用得着的）：

```
employee_id  first_name  last_name  email  phone  job_id
salary       commission_pct  manager_id  department_id   hire_date
```

**关键列**：

- `department_id`：部门 id（**最重要的分组键**，10/20/30/.../110 共 11 个部门）
- `job_id`：工种代码（`SA_REP`/`SA_MAN`/`IT_PROG`/...）
- `salary`：工资（数值聚合主战场）
- `commission_pct`：提成比例（**有大量 NaN**——只有销售部门有提成）

> 看到 commission_pct 有大量 NaN 不要慌——这是真实业务里的常态：非销售岗位没有提成。后面 filter 演示就拿它做"过滤掉有 NaN 的组"。

### 视频 15 的 4 个回顾点（你已经会，扫一眼）

```python
df = pd.read_csv("employees.csv")

# 1. 创建分组对象（懒）
dep_group = df.groupby("department_id")

# 2. 查看分组信息
dep_group.groups        # 字典：{部门id: [属于该组的行索引列表]}
dep_group.get_group(50) # 只看 50 部门的所有行  ← 这个用法你之前没用过

# 3. 选列后聚合
df.groupby("department_id")["salary"].mean()

# 4. 遍历每组（调试时很有用）  ← 这个用法你之前没用过
for dept_id, group in df.groupby("department_id"):
    print(f"部门 {dept_id}：{group.shape[0]} 人")
    print(group.iloc[:, 0:3])
    print("---")
```

🆕 **真正没见过的两个动作**：

```python
g.get_group(50)         # 直接取出某一组的 DataFrame
for k, sub_df in g:     # 遍历所有组（k 是分组键，sub_df 是该组的 DataFrame）
```

**`get_group` 的实战意义**：调试时检查"某个组到底有哪些行"——比写 `df[df['department_id']==50]` 更直接。

**遍历的实战意义**：当 `apply / agg / transform` 都不够用，需要写"对每组做完全不同的事"时，**手动 for 循环是最后的逃生通道**。

---

## 视频 15 续：多字段分组 + `as_index=False`

```python
df.groupby(["department_id", "job_id"], as_index=False)[["salary", "commission_pct"]].mean()
```

**结果**：

```
   department_id  job_id      salary  commission_pct
0  10.0           AD_ASST     4400.00       NaN
1  20.0           MK_MAN      13000.0       NaN
2  20.0           MK_REP      6000.0        NaN
3  30.0           PU_CLERK    2780.0        NaN
4  30.0           PU_MAN      11000.0       NaN
5  40.0           HR_REP      6500.0        NaN
...
11 80.0           SA_MAN      12200.0       0.30
12 80.0           SA_REP      8396.55       0.21
```

观察 3 个细节：

1. **`["department_id", "job_id"]`** 双字段分组 → 每个"出现过的 (部门, 工种)" 组合就是一组（不补齐没出现的组合，[[groupby系统理解]] 的核心规则）
2. **`as_index=False`** → 分组键不变 index，变成普通列，可以直接 `df1.iloc[:, ...]` 操作
3. **大部分 `commission_pct` 是 NaN** → 因为只有 80 部门（销售）的岗位有提成

> 这个 DataFrame 在视频里反复用，记住它的样子。

---

## 视频 16：`pd.cut` / `pd.qcut` —— 把连续值切成区间（🆕 全新）

### 16.1 一句话定位

```
pd.cut   = "把连续数值按指定的边界切成桶"
pd.qcut  = "把连续数值按分位数切桶（每桶人数相等）"
```

它们是 **"连续 → 离散"的核心特征工程工具**——做 ML、可视化、分组分析时几乎天天用。

### 16.2 `pd.cut` 基础用法

#### 写法 A：指定"切几段"

```python
pd.cut(df.iloc[9:16]["salary"], 3)
```

意思：**自动按 salary 的 (min, max) 区间均匀切成 3 段**。

#### 写法 B：指定"边界"（**实战首选**）

```python
pd.cut(df.iloc[9:16]["salary"],
       bins=[0, 10000, 20000],
       labels=["low", "high"])
```

**结果**：

```
9      low      ← salary 在 [0, 10000]
10     low
11     low
12     low
13     low
14    high      ← salary 在 (10000, 20000]
15     low
dtype: category
Categories (2, object): ['low' < 'high']
```

**关键参数**：

| 参数 | 含义 |
|---|---|
| `bins=[a, b, c, d]` | 边界值，**n 个边界 = n-1 个桶** |
| `labels=['low','high']` | 给每个桶起名，长度必须等于桶数 |
| `right=True/False` | 区间是 `(a, b]`（默认）还是 `[a, b)` |
| `include_lowest=True` | 是否包含最小边界 |

> ⚠️ **第一卡点**：`bins=[0, 10000, 20000]` 只产生 **2 个桶** 不是 3 个——边界 n+1 个，桶 n 个。新手经常写错 labels 长度。

### 16.3 `pd.qcut` —— 按分位数切（每桶人数相等）

```python
pd.qcut(df['salary'], q=4, labels=['低','中低','中高','高'])
# q=4 → 切成 4 等份（25/50/75 分位数为边界）
# 每段大致包含总人数的 25%
```

**`cut` vs `qcut` 对比**：

| 工具 | 桶宽 vs 桶人数 | 适合场景 |
|---|---|---|
| `cut` | **桶宽相等**，人数可能极不平均 | 业务边界明确（"成人/老人"按年龄 18/60 切）|
| `qcut` | **桶人数相等**，桶宽可能极不平均 | 想要"高/中/低三等分位"这种统计意义的分段 |

**例子直观感受**：工资 1k~24k，用 `cut(bins=3)` 切：

- `cut`：桶宽 = 8k，可能 95% 人都落在第一桶（低工资），第三桶只有 CEO 几个人
- `qcut(q=3)`：每桶 33% 的人，但桶宽 ≠ 桶宽

### 16.4 `cut` + `groupby` 的标准组合（**实战核心**）

```python
# 把连续 salary 切成 3 个工资段
df['salary_level'] = pd.cut(df['salary'],
                            bins=[0, 5000, 10000, 30000],
                            labels=['低薪', '中薪', '高薪'])

# 按工资段分组看分布
df.groupby('salary_level').size()
# 低薪    52
# 中薪    35
# 高薪    20

# 再交叉看：每个部门各工资段多少人
df.groupby(['department_id', 'salary_level']).size().unstack(fill_value=0)
```

**iOS 老兵的直觉类比**：

```swift
// Swift 里你可能这样写：
let level: String
if salary < 5000      { level = "低薪" }
else if salary < 10000 { level = "中薪" }
else                   { level = "高薪" }
```

Pandas 的 `pd.cut` = 一行代码批量完成 10 万行这种 if/else。

### 16.5 `cut` 的常见坑

```python
# 坑 1：labels 长度错
pd.cut(s, bins=[0, 5, 10], labels=['A', 'B', 'C'])
# ❌ bins=3 个 → 桶=2 个，但 labels=3 个 → 报错

# 坑 2：值在 bins 范围外 → 返回 NaN
pd.cut([5, 15, 50], bins=[0, 10, 20])
# [5, 15, NaN]    ← 50 超出 20 → NaN

# 坑 3：区间默认左开右闭 (a, b]
pd.cut([0], bins=[0, 5])
# NaN   ← 0 不在 (0, 5] 内！要写 include_lowest=True
```

---

## 视频 17：`agg` 进阶（🆕 自定义函数 + dict + rename）

### 17.1 你已经会的（来自 [[groupby系统理解]]）

```python
# 单列多统计
df.groupby("department_id")["salary"].agg(["min", "max", "median"])

# 多列各自的统计
df.groupby("department_id").agg({
    "salary":         ["min", "max"],
    "commission_pct": "mean"
})
```

### 17.2 🆕 dict + rename 起中文列名

视频里的真实代码：

```python
df.groupby("department_id").agg({
    "job_id":         "nunique",
    "commission_pct": "mean"
}).rename(columns={
    "job_id":         "工种数",
    "commission_pct": "平均值"
})
```

**结果**：

```
               工种数    平均值
department_id            
10.0             1    NaN
20.0             2    NaN
...
80.0             2    0.225
```

**这个套路在出报表/Excel 时极常用**——业务领导只想看中文表头。

### 17.3 🆕 agg + 自定义函数（**重点**）

视频里给了个很有教育意义的例子：

> "统计每个部门员工 last_name 的首字母集合"

```python
def f(x):                   # x 是什么？ 一个组的 last_name Series
    result = set()
    for i in x:             # 遍历该组的所有 last_name
        result.add(i[0])    # 取首字母
    return result

df.groupby("department_id")["last_name"].agg(f)
```

**结果**：

```
department_id
10.0     {W}
20.0     {F, H}
30.0     {K, C, H, T, B, R}
40.0     {M}
50.0     {E, C, N, W, M, P, B, R, J, S, V, O, A, F, T, ...}
60.0     {A, E, H, P, L}
70.0     {B}
...
```

🔥 **关键认知**：自定义函数 `f` 接收的是 **"该组的一个 Series"**（不是单个元素，也不是整个 DataFrame）。

对照表（这是 apply / agg 学习里最容易混的点）：

| 写法 | func 收到什么 |
|---|---|
| `s.apply(func)` | Series 的**一个元素** |
| `df.apply(func, axis=0)` | DataFrame 的**一整列 Series** |
| `df.apply(func, axis=1)` | DataFrame 的**一整行 Series** |
| `g["col"].agg(func)` | **该组该列的整个 Series**（一组调一次） |
| `g.agg(func)` | **该组的整个 DataFrame** 或 **每列分别调一次** |

> 推荐：第一次写 agg 自定义函数时，**先在函数里 `print(type(x))` 和 `print(x.shape)`** 看清你收到的是啥，免得猜。

### 17.4 自定义函数 vs 字符串名 vs lambda

agg 支持 3 种传法：

```python
# 1. 字符串（内置统计）
g["salary"].agg(["mean", "max"])

# 2. lambda
g["salary"].agg(lambda x: x.max() - x.min())

# 3. 命名函数（复杂逻辑或需复用时）
def salary_range(x):
    return x.max() - x.min()
g["salary"].agg(salary_range)
```

**`agg` 的妙处**：还能在同一次调用里混用！

```python
g["salary"].agg(["mean", "max", lambda x: x.max() - x.min()])
# 列名分别叫：mean / max / <lambda>
```

想给 lambda 取名字 → 用 `(列名, 函数)` 元组形式（Python 3.8+ 支持的 **named aggregation**）：

```python
g.agg(
    平均工资 = ("salary", "mean"),
    工资极差 = ("salary", lambda x: x.max() - x.min())
)
```

这是 **Pandas 1.0+ 推荐的写法**——比 rename 二段式优雅得多。

---

## 视频 18 上半场：`transform` 实战（🆕 真正用起来）

### 18.1 你已经会的（来自 [[groupby系统理解]]）

```python
# transform = "聚合后广播回每一行"
df.groupby("month")["temp_max"].transform("mean")
# 输出长度 == df 原长度，不是组数
```

### 18.2 🆕 实战一：去中心化（**ML 特征工程极常用**）

视频里的代码：

```python
df.groupby("department_id")["salary"].transform(lambda x: x - x.mean())
```

**含义**：每个员工的工资 - 他所在部门的平均工资 = "与部门均值的偏差"。

**结果**：

```
0      4666.67    ← 这个人比所在部门均值高 4666
1     -2333.33    ← 这个人比部门均值低 2333
...
```

**为什么这是大杀器**：

- 直接比 salary：跨部门没法比（CEO 和清洁工不能直接比工资）
- 减去组均值后：**"在自己部门里的相对水位"**——这才是有意义的特征

**对应 SQL 的窗口函数**：

```sql
SELECT salary - AVG(salary) OVER (PARTITION BY department_id) AS centered
FROM employees
```

iOS 老兵的角度：Pandas 的 `groupby().transform()` ≈ SQL 的窗口函数 ≈ 数据科学家天天写的"按组归一化"。

### 18.3 🆕 实战二：按组填缺失值（**前面缺失值那节的高级版**）

视频里的完整代码（注释掉了，我替你跑通）：

```python
import numpy as np

# 制造缺失：随机选 30 行 salary 填 NaN
na_index = pd.Series(df.index.tolist()).sample(30)
df.loc[na_index, "salary"] = pd.NA

# 查看每组数据总数 vs 非空数
print(df.groupby("department_id")["salary"].agg(["size", "count"]))
#               size  count
# department_id            
# 10.0             1      1
# 20.0             2      1   ← 2 个人里 1 个缺
# 50.0            45     32   ← 45 个里 32 个非空
# ...

# 按组的平均值填缺失（如果整组都缺 → 兜底填 0）
def fill_missing(x):
    if np.isnan(x.mean()):   # 整组都 NaN → 兜底
        return 0
    return x.fillna(x.mean())

df["salary"] = df.groupby("department_id")["salary"].transform(fill_missing)
```

**为什么用 transform 而不是 apply / agg**：

| 用 | 结果长度 | 能直接 `df["salary"] = ...` 吗 |
|---|---|---|
| `agg(mean)` | **N 行**（一组一行）| ❌ 长度对不上 |
| `apply` | 不固定 | ❌ 可能加层级 |
| `transform(fill_missing)` | **原 df 长度** | ✅ 直接赋值 |

> 这是 transform 真正的杀手锏：**它保证输出和原数据长度一致**，所以能直接当一列赋值回去。

### 18.4 对比一下"全表均值" vs "按组均值"填缺失

```python
# 写法 A：全表均值（粗暴，跨部门混算）
df["salary"].fillna(df["salary"].mean())

# 写法 B：按组均值（精细，部门内填）
df["salary"] = df.groupby("department_id")["salary"].transform(
    lambda x: x.fillna(x.mean())
)
```

**A vs B 的差距**：CEO 缺工资 → A 给他填全公司均值 7k（荒谬），B 给他填总裁组均值 20k（合理）。

**结论**：**有分组信息时，永远优先按组填**。

---

## 视频 18 下半场：`filter` —— 整组保留 / 丢弃

### 18.5 `filter` 一句话定位

```
filter = "对每个组做一个 True/False 判断，True 保留整组、False 丢弃整组"
```

**和 `df[mask]` 的区别**：

```
df[mask]          → 按"每一行"判断 True/False
g.filter(func)    → 按"每一组整体"判断 True/False
```

### 18.6 视频里的例子

```python
df.groupby("department_id").filter(
    lambda x: x["commission_pct"].notnull().all()
)
```

**含义**：对每个部门检查"commission_pct 是否全部非空"——`True` 保留整个部门，`False` 丢弃。

**结果**：只剩 80 部门（销售部）的所有行——因为只有销售员才有提成，其他部门 commission_pct 全是 NaN。

**逐字解读**：

```python
lambda x: x["commission_pct"].notnull().all()
#       │  └─ 该组的某列        └─ 全部非空？
#       └─ x 是该组的整个 DataFrame
```

| 表达式 | 拿到什么 |
|---|---|
| `x` | 一个组的整个 DataFrame |
| `x["commission_pct"]` | 该组该列的 Series |
| `.notnull()` | 等长 bool Series |
| `.all()` | 全部为 True 才返回 True |

### 18.7 `filter` 实战清单

```python
# 1. 只保留人数 > 5 的部门（剔除小部门）
df.groupby("department_id").filter(lambda x: len(x) > 5)

# 2. 只保留平均工资 > 8000 的部门
df.groupby("department_id").filter(lambda x: x["salary"].mean() > 8000)

# 3. 只保留至少有一个高薪的部门
df.groupby("department_id").filter(lambda x: (x["salary"] > 15000).any())

# 4. 剔除有 NaN 的整组
df.groupby("department_id").filter(lambda x: x["salary"].notnull().all())
```

**记住一个核心套路**：`filter` 的 lambda 必须**返回标量 bool**（一组 True/False），不能返回 Series。

---

## agg / transform / filter / apply 一张总图

```
                  groupby 之后能跟的 5 种动作
   ┌─────────────────────────────────────────────────────────┐
   │                                                          │
   │  动作         输出长度       func 返回什么    用途        │
   │  ─────────────────────────────────────────────────────  │
   │  size/mean    N 行          自动              基础统计   │
   │  agg          N 行          标量              多种统计   │
   │  transform    原 df 长度    Series（等长）    每行加列   │
   │  filter       <= 原 df      bool 标量         过滤整组   │
   │  apply        不定          任意              终极后门   │
   │                                                          │
   └─────────────────────────────────────────────────────────┘

   N = 组数
```

**选择决策树**：

```
我想得到什么？
├─ 每组一个数 → agg
├─ 每行都要有结果（同长度） → transform
├─ 整组保留或丢弃 → filter
├─ 上面都搞不定 → apply（性能差，慎用）
```

---

## 性能：再敲一遍向量化的钉子

承接第三节的"性能观"——`groupby + apply` 是性能黑洞：

```python
# ❌ 慢：用 apply 写"按组减均值"
df.groupby("dept")["salary"].apply(lambda x: x - x.mean())

# ✅ 快得多：用 transform
df["salary"] - df.groupby("dept")["salary"].transform("mean")
```

10 万行实测：apply ≈ 500ms，transform ≈ 5ms。**100 倍差距**。

**规则**：

- 能 `agg / transform / filter` 解决 → 不用 apply
- 必须 apply 时 → 接受性能代价、尽量缩小数据规模

---

## 速查 API 表（按视频顺序）

```python
# 视频 15：基础与遍历
g = df.groupby("department_id")
g.groups                      # {组键: 行索引列表}
g.get_group(50)              # 取某一组的 DataFrame
for k, sub in g: ...         # 遍历每组
df.groupby(["a","b"], as_index=False)[["x","y"]].mean()

# 视频 16：cut / qcut
pd.cut(s, bins=3)                                   # 按宽度均分 3 段
pd.cut(s, bins=[0,5000,10000,30000], labels=[...]) # 自定义边界
pd.cut(s, bins=[...], right=False)                  # 改成左闭右开
pd.qcut(s, q=4, labels=[...])                       # 按分位数 4 等分

# 视频 17：agg 进阶
g["col"].agg(["mean","max"])                        # 多统计
g.agg({"col1":"mean", "col2":["sum","max"]})        # 不同列不同统计
g.agg({...}).rename(columns={...})                  # 重命名表头
g["col"].agg(func)                                  # 自定义函数
g.agg(新列名 = ("col","mean"))                      # named aggregation（推荐）

# 视频 18：transform / filter
g["col"].transform("mean")                          # 广播每行
g["col"].transform(lambda x: x - x.mean())          # 去中心化
g["col"].transform(lambda x: x.fillna(x.mean()))   # 按组填缺失
g.filter(lambda x: len(x) > 5)                      # 过滤组
g.filter(lambda x: x["col"].notnull().all())        # 过滤含 NaN 的组
```

---

## 你会撞到的卡点预测

1. **`agg` 的 func 收到什么** —— 是"该组该列的 Series"，不是元素。**`print(type(x))` 一次就破**
2. **`cut` 边界数 vs 桶数** —— `bins=[a,b,c]` 是 2 个桶不是 3 个
3. **`transform` 为什么能直接赋值给一列，`agg` 不行** —— 长度问题，看上面那张总图
4. **`filter` 的 lambda 必须返回 bool 标量** —— 返回 Series 会报错
5. **`cut` vs `qcut` 哪个用哪个** —— 业务边界用 `cut`，统计分位用 `qcut`

撞到任何一个**直接告诉我**，我按 P05_Weather 标准给 `P06_Agg_Trans_Filter.ipynb` 插 Claude 讲解 cell。

---

## 自测题（请合上笔记复述）

> 给你 `employees.csv`（已加载到 `df`），写代码完成：
>
> 1. 把 salary 切成 "低薪 (<5000) / 中薪 (5000-10000) / 高薪 (>10000)" 三档，作为新列 `level`
> 2. 按 `department_id` 分组，输出：每组工资的均值、最大值、岗位种类数
> 3. 给每行加一列 `salary_diff` = 自己的工资 - 所在部门的平均工资
> 4. 只保留"部门人数 > 5 且没有任何 NaN salary"的部门
> 5. 用 `agg + 自定义函数` 输出每个部门的"工资极差"（max - min）

<details>
<summary>👇 答案展开</summary>

```python
# 1. 分箱
df['level'] = pd.cut(df['salary'],
                     bins=[0, 5000, 10000, float('inf')],
                     labels=['低薪', '中薪', '高薪'])

# 2. 多统计
df.groupby('department_id').agg(
    平均工资 = ('salary', 'mean'),
    最高工资 = ('salary', 'max'),
    岗位种类 = ('job_id', 'nunique')
)

# 3. 去中心化
df['salary_diff'] = df['salary'] - df.groupby('department_id')['salary'].transform('mean')

# 4. 过滤
df_filtered = df.groupby('department_id').filter(
    lambda x: len(x) > 5 and x['salary'].notnull().all()
)

# 5. 自定义函数
df.groupby('department_id')['salary'].agg(lambda x: x.max() - x.min())
```
</details>

---

## 配套笔记

- [[groupby系统理解]] —— groupby 全局心法（这一节的基础）
- [[pandas理解]] —— Series/DataFrame 全局
- [[day04_03_apply教程]] —— 自定义函数性能观（apply 慢、transform 快）
- [[day04_02_缺失值处理教程]] —— `fillna` 全局填充；这节是它的"按组细分"升级版
- [[day04_00_概念地图]] —— Day04 主题地图

---

## 学完本节你应该能做到

- ✅ 看到一段 `g.agg({...})` 能立刻说出每列做什么聚合、结果几行几列
- ✅ 区分 `cut` 和 `qcut`，根据场景选对
- ✅ 写出"按组去中心化""按组填缺失"的标准 transform 代码
- ✅ 用 filter 而不是 boolean mask 来按"组整体条件"筛选
- ✅ 看到 `agg(func)` 不再猜 func 收到啥——先 `print(type(x))`

---

**Day04 学完意味着什么**：

Pandas 的 **核心 70%** 你已经摸到——表合并、缺失值、apply/向量化、groupby 进阶。接下来 day05/day06 会是 **数据可视化（matplotlib/seaborn）+ 综合实战**。

到这步可以打开 [[01_数据分析精华]] 自检一下，看哪些点能 30 秒讲清，哪些点还要回这节复习。
