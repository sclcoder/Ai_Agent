# Pandas 的理解笔记

> 这份笔记的目标：搞清楚 **Pandas 比 NumPy 多了什么**，以及怎么用它。
> 配套阅读：[[numpy轴的理解]]、[[numpy_pandas_重点清单]]。

---

## Pandas 的一句话定位

> **Pandas = NumPy 数组 + 一列"标签"。**

它底层就是 NumPy ndarray，但每一行/每一列多了一个**标签**（叫 index 和 column），这一个改动彻底改变了它的用法：

- **ndarray** 是给"批量计算"用的 → 喂给模型
- **Pandas** 是给"数据分析"用的 → 看、洗、统计

中间会有一步 `.to_numpy()` 把前者转成后者，这是 ML 流程里最常见的衔接。

---

## Pandas 的两个核心结构

```
Series                            DataFrame
（一列带标签的数据）              （多列拼起来 = 表格）

Alice    85                       name    age  score
Bob      92                       Alice   25   85
Carol    78                       Bob     30   92
David    60                       Carol   28   78
                                  David   35   60

= ndarray + index                 = 多个 Series + 共享 index
```

**关键关系**：DataFrame 的每一列就是一个 Series。所以学 Pandas 的顺序是 Series → DataFrame，不能跳。

---

## Pandas 只有 1D 和 2D，没有更高维

> **Series = 1 维，DataFrame = 2 维。没了。**

Pandas **原生不支持 3D 及以上**——这不是工具缺陷，是它**故意**这么设计的。

### 为什么故意只做二维

Pandas 参考的是 **Excel / SQL 数据库**，不是 NumPy 那种"任意维度数组"。现实里你看到的"表"基本都是二维的：

```
姓名   年龄  成绩
Alice  25    85
Bob    30    92
```

没人画三维表格。把自己限制在二维，**换来了更贴合业务的 API**（groupby / merge / pivot 这些都依赖"行 / 列"两个概念）。

### 历史上有过 3D，但已经被砍了

Pandas 早期有个 `Panel` 的 3D 结构，2019 年（0.25 版本）**正式移除**，理由是：

1. 用得太少
2. 3D+ 需求 NumPy 已经做得很好
3. "带分组的二维数据"用 MultiIndex 更优雅

现在的文档**不会再看到 Panel**，知道这段历史就行。

### 想"看起来像 3D"：用 MultiIndex（但不推荐先学）

MultiIndex 让你在二维结构里塞三维数据：

```python
data = pd.DataFrame(
    {'sales': [100, 120, 110, 125]},
    index=pd.MultiIndex.from_product(
        [[2025, 2026], ['Q1', 'Q2']],
        names=['year', 'quarter']
    )
)
#                 sales
# year quarter
# 2025 Q1         100
#      Q2         120
# 2026 Q1         110
#      Q2         125
```

逻辑上三维（年 × 季 × 销售额），物理上还是二维 DataFrame——只是 index 变成了"两级标签"。

**为什么不推荐先学 MultiIndex**：
- 概念绕（"二维结构装三维数据"）
- API 复杂（`xs` / `stack` / `unstack` / `swaplevel`）
- 大部分场景可以用别的方式绕开（比如多搞几个普通列）

工业界很多老手也不爱用，宁可摊平成普通列。

### 真要 3D+，按场景选工具

| 需求 | 工具 |
|---|---|
| 模型张量、批次数据、图片、嵌入向量 | **NumPy** / **PyTorch tensor**（任意维度） |
| 业务表格（用户 / 订单 / 事件） | **Pandas DataFrame**（二维就够） |
| 多维科学数据（气象、地理、医学影像） | **xarray**（带标签的高维数组，"高维版 Pandas"） |

### 一张全景图

```
维度  →    1D            2D              3D+
                                          
NumPy:    1-D ndarray    2-D ndarray     N-D ndarray
                                          
Pandas:   Series         DataFrame       (无原生支持)
                                          ↓ MultiIndex 模拟
                                          ↓ 或转 NumPy
                                          ↓ 或用 xarray

PyTorch:  1-D tensor     2-D tensor      N-D tensor
```

**记法**：追求"任意维度"用 **NumPy 家族**；追求"业务可读"用 **Pandas 家族**。

### ML 实战里的转换链

```
原始数据                → 整理成表              → 转成数组喂模型
(CSV / Excel)            (Pandas DataFrame)      (NumPy ndarray)
                          2 维                    通常 2 维或 3 维
```

```python
df = pd.read_csv('xxx.csv')              # 2D Pandas
X = df[['age', 'score']].to_numpy()      # 2D NumPy: (N, 2)
X = X.reshape(-1, 1, 2)                  # 3D NumPy: (N, 1, 2) 喂 RNN
```

**Pandas 管"表"的阶段，NumPy 管"张量"的阶段**——两个工具各管一段，不要试图用 Pandas 处理高维张量。

---

## Series：到底比 ndarray 多了什么？

如果只用 Series 的 `.sum()`, `.mean()`, 切片、布尔筛选——和 ndarray 90% 一样，包了一层而已。

**Series 真正的护城河是 index（标签）**。下面 4 个超能力都是 index 带来的。

### 先看清 Series 的"三件套"

一个 Series 由 **3 个部分**组成（不是只有"数据"）：

```
           Name
            ↓
           "A"           ← Series.name        整列的名字
       ┌────────┐
   1   │   1    │
   2   │   2    │
   3   │   3    │
   4   │   4    │
   ↑       ↑
 Index   Values
(标签)   (值)
       
 s.index           s.values / s.to_numpy()
```

| 属性 | 作用 | 例子 |
|---|---|---|
| `s.index` | 每一行的标签 | `Int64Index([1,2,3,4])` 或 `['Alice','Bob',...]` |
| `s.values` / `s.to_numpy()` | 真正的数据（一个 ndarray） | `array([1, 2, 3, 4])` |
| `s.name` | 整个 Series 的名字 | `'A'`（变成 DataFrame 后会成为列名） |

> **关键认知**：Series 不是"数组的别名"，而是"**带标签的数组 + 一个名字**"。
> 把它放进 DataFrame 时，`s.name` 就变成那一列的列名——这是为什么 Series 必须有名字。

### 超能力 1：按"业务名字"查，不靠位置

```python
# ndarray：只能用位置
scores_arr = np.array([85, 92, 78, 60])
scores_arr[0]            # 85，但你得记住 0 是谁

# Series：可以用名字
scores = pd.Series([85, 92, 78, 60],
                   index=['Alice', 'Bob', 'Carol', 'David'])
scores['Alice']          # 85
scores.loc['Alice']      # 85（明确按标签）
scores.iloc[0]           # 85（明确按位置）
```

> **`loc` 按标签，`iloc` 按位置**——这两个 API 必须记牢，是 Pandas 里最常见的混淆来源。

真实数据里你永远是按**业务含义**操作（用户 ID、日期、股票代码），而不是"第几行"。

### 超能力 2：运算按 index 自动对齐（杀手锏）

```python
# ndarray：按位置硬加
a = np.array([1, 2, 3])
b = np.array([3, 2, 1])
a + b                    # [4, 4, 4]

# Series：按 index 对齐
s1 = pd.Series([1, 2, 3], index=['a', 'b', 'c'])
s2 = pd.Series([3, 2, 1], index=['c', 'b', 'a'])  # 顺序反了！
s1 + s2
# a    2     ← 1 + 1
# b    4     ← 2 + 2
# c    6     ← 3 + 3
# 自动按标签配对
```

这个特性在合并不同来源的数据时是救命的——两份数据顺序不同，ndarray 加起来全错位，Series 自动按标签对齐。

### 超能力 3：缺失值是一等公民

```python
# 标签不匹配时自动填 NaN
s1 = pd.Series([1, 2, 3], index=['a', 'b', 'c'])
s2 = pd.Series([10, 20], index=['b', 'd'])
s1 + s2
# a    NaN     ← s2 没有 a
# b     22     ← 两边都有 b
# c    NaN     ← s2 没有 c
# d    NaN     ← s1 没有 d
```

配套的内建 API：

```python
s.isna()       # 哪些是 NaN
s.dropna()     # 删掉 NaN 行
s.fillna(0)    # 把 NaN 填成 0
s.fillna(s.mean())   # 填成均值
```

ndarray 里没有 NaN 概念（数值型只能存数字），缺失值得自己搞 mask。Pandas 全自动。

### 超能力 4：dtype 可以是任何东西

```python
pd.Series(['apple', 'banana'])                    # object（字符串）
pd.Series(pd.date_range('2026-01-01', periods=3)) # datetime64
pd.Series([1, 'two', 3.0])                        # 混合类型
```

字符串、日期、甚至 Python 对象都行。NLP 文本数据、日志数据基本都用 Series 装。

---

## Series 独有的 API（值得专门记的）

ndarray 没有等价物，这些是 Pandas 真正的增量：

| API | 作用 |
|---|---|
| `s.index` | 取出标签 |
| `s.loc[label]` / `s.loc[['a','b']]` | 按标签取 |
| `s.iloc[i]` / `s.iloc[0:3]` | 按位置取 |
| `s.reindex([...])` | 重新按指定的标签顺序排列，缺失补 NaN |
| `s.sort_values()` / `s.sort_index()` | 按值排序 / 按标签排序 |
| `s.value_counts()` | 每个值出现几次（类别统计神器） |
| `s.unique()` / `s.nunique()` | 去重 / 唯一值个数 |
| `s.isna()` / `s.fillna()` / `s.dropna()` | 缺失值三剑客 |
| `s.map(func)` / `s.apply(func)` | 逐元素函数 |
| `s.astype(...)` | 类型转换 |
| `s.str.xxx` | 字符串向量操作（小写、切分、正则） |
| `s.dt.xxx` | 日期向量操作（取年月日、星期） |

其他和 ndarray 重叠的（`.sum`, `.mean`, `.max`, 切片, 布尔筛选）按 NumPy 那套用就行。

---

## DataFrame：本质就是"共享同一个 index 的多个 Series"

```python
df = pd.DataFrame({
    'name':  ['Alice', 'Bob', 'Carol'],
    'age':   [25, 30, 28],
    'score': [85, 92, 78]
})
#       name  age  score
# 0     Alice   25     85
# 1     Bob     30     92
# 2     Carol   28     78

df['age']           # ← 这是一个 Series
type(df['age'])     # pandas.core.series.Series
```

DataFrame 的 **两个轴**：

```
            列标签 (columns)
         ┌──────────────────┐
行       │ name  age  score │
标签     ├──────────────────┤
(index)  │ 0  Alice  25  85 │
         │ 1  Bob    30  92 │
         │ 2  Carol  28  78 │
         └──────────────────┘
```

- **`index`** = 行标签（默认是 0, 1, 2... 但可以换成日期、ID 等）
- **`columns`** = 列标签（一般是字段名）

每一列拎出来 = 一个 Series，共享同一个 `index`。

### 另一个等价视角：DataFrame 是「Series 字典」

```
                Column-1   Column-2   ...   Column-k
              ┌─────────┬─────────┬─────┬─────────┐
   Record 1  │         │         │ ... │         │
   Record 2  │         │         │ ... │         │
     ...     │         │         │ ... │         │
   Record n  │         │         │ ... │         │
              └─────────┴─────────┴─────┴─────────┘
                  ↓         ↓              ↓
               Series    Series    ...   Series
                  └─────────┴───────┬──────┘
                                    │
                            共享同一个 Index
```

可以把 DataFrame 直接看成一个 **`{列名 → Series}` 的字典**：

```python
df.to_dict('series')
# {'name':  <Series 1>,
#  'age':   <Series 2>,
#  'score': <Series 3>}

# 反过来构造也是同一个套路：
df = pd.DataFrame({
    'name':  pd.Series(['Alice', 'Bob']),
    'age':   pd.Series([25, 30]),
    'score': pd.Series([85, 92])
})
```

这个视角解释了 Pandas 很多 API 的设计：

- `df['age']` 像取字典的 value，拿到一个 Series
- 新增列 `df['new'] = ...` 像往字典塞键值对
- `for col in df` 默认遍历的是**列名**（字典 key 的语义），不是行
- 大多数操作（mean、sum、apply）默认是**按列**算的，因为列是一等公民

> **Series 是积木，DataFrame 是积木拼出来的盒子。** 学透 Series → DataFrame 就是顺理成章的事。

---

## DataFrame 的核心操作（按使用频率排）

### 1. 读数据 / 看数据

```python
df = pd.read_csv('xxx.csv')

df.head()         # 前 5 行
df.tail()         # 后 5 行
df.info()         # 列名、类型、非空数量
df.describe()     # 数值列的统计摘要（均值、标准差、分位数）
df.shape          # (行数, 列数)
df.columns        # 列名列表
df.dtypes         # 每列的类型
```

**拿到数据的固定动作**：`info()` 看一眼有什么、有没有缺失，`describe()` 看一眼数值分布。

### 2. 选行选列

```python
# 选列
df['age']                 # 一列 → Series
df[['name', 'age']]       # 多列 → DataFrame

# 选行（按位置）
df.iloc[0]                # 第 0 行 → Series
df.iloc[0:3]              # 前 3 行 → DataFrame
df.iloc[0:3, 1:3]         # 前 3 行的第 1-2 列

# 选行（按标签）
df.loc[0]                 # 标签为 0 的行
df.loc[df['age'] > 25]    # 布尔筛选（最常用）
df.loc[df['age'] > 25, ['name', 'score']]   # 行筛选 + 列筛选
```

> **核心区别再强调一遍**：`loc` 按**标签**，`iloc` 按**位置**。即使标签碰巧是 0,1,2，`loc[0]` 和 `iloc[0]` 含义也不同。

### 3. 布尔筛选（数据清洗主力）

```python
df[df['age'] > 25]                          # 单条件
df[(df['age'] > 25) & (df['score'] > 80)]   # 多条件用 &，单条件必须括号
df[df['name'].isin(['Alice', 'Bob'])]       # 是否在列表里
df.query('age > 25 and score > 80')         # 字符串语法，可读性更好
```

**坑**：多条件必须用 `&` `|` 不是 `and` `or`，每个条件外面必须加括号。

### 4. 缺失值处理

```python
df.isna()                # 每个格子是不是 NaN，返回布尔表
df.isna().sum()          # 每列有几个 NaN（必须掌握）
df.dropna()              # 删掉有 NaN 的行
df.dropna(subset=['age']) # 只看 age 列有 NaN 的行才删
df.fillna(0)             # 全填 0
df['age'].fillna(df['age'].mean(), inplace=True)  # 用均值填
```

### 5. 新增 / 修改 / 删除列

```python
df['new_col'] = df['age'] * 2              # 新建一列
df['age_group'] = df['age'].apply(lambda x: 'young' if x < 30 else 'old')
df = df.drop(columns=['name'])             # 删列
df = df.rename(columns={'age': '年龄'})    # 改列名
```

### 6. groupby + 聚合（数据分析灵魂）

```python
df.groupby('age_group').mean()             # 按 age_group 分组，每组算均值
df.groupby('age_group')['score'].mean()    # 只看 score 的均值
df.groupby('age_group').agg({
    'score': ['mean', 'max', 'min'],
    'age': 'mean'
})
```

**心智模型**：`groupby` 把表按某列拆成多个子表 → 每个子表做聚合 → 把结果拼回来。

### 7. 类型转换

```python
df['age'] = df['age'].astype(int)
df['date'] = pd.to_datetime(df['date'])
df['price'] = pd.to_numeric(df['price'], errors='coerce')  # 错误的转 NaN
```

### 8. 和 NumPy 互转（喂模型前必做）

```python
arr = df.to_numpy()              # DataFrame → ndarray
arr = df[['age', 'score']].to_numpy()  # 只取数值列

df2 = pd.DataFrame(arr,
                   columns=['age', 'score'])  # ndarray → DataFrame
```

---

## 核心 API 速查表（按任务分类）

> **怎么用这一节**：实战时知道"要干什么"，直接到对应小表里找 API。学过一遍后忘 90% 是正常的，回来翻就行。
> 没收进表里的 API 大概率你近期用不到，等真撞到再查。

### 1. 读 / 写文件

| 任务 | API | 示例 |
|---|---|---|
| 读 CSV | `pd.read_csv` | `pd.read_csv('a.csv')` |
| 读 Excel | `pd.read_excel` | `pd.read_excel('a.xlsx', sheet_name='Sheet1')` |
| 读 JSON | `pd.read_json` | `pd.read_json('a.json')` |
| 写 CSV | `df.to_csv` | `df.to_csv('out.csv', index=False)` |
| 写 Excel | `df.to_excel` | `df.to_excel('out.xlsx', index=False)` |

> **`index=False`** 几乎是写 CSV 的标配——不加会把默认的 0,1,2... 行号也写进文件，造成下次读进来多一列。

### 2. 创建数据

| 任务 | API | 示例 |
|---|---|---|
| 从字典建表 | `pd.DataFrame` | `pd.DataFrame({'a':[1,2], 'b':[3,4]})` |
| 创建 Series | `pd.Series` | `pd.Series([1,2,3], index=['a','b','c'], name='x')` |
| 生成日期序列 | `pd.date_range` | `pd.date_range('2026-01-01', periods=10)` |
| 生成数字范围 | `pd.RangeIndex` | `pd.RangeIndex(10)` |

### 3. 查看 / 检查

| 任务 | API | 备注 |
|---|---|---|
| 前/后 n 行 | `df.head(n)` / `df.tail(n)` | 默认 5 |
| 整体概览 | `df.info()` | 列类型、非空数 |
| 数值统计 | `df.describe()` | mean/std/min/max/分位数 |
| 形状 | `df.shape` | (行数, 列数) |
| 列名 / 行索引 | `df.columns` / `df.index` | |
| 每列类型 | `df.dtypes` | |
| 行数 | `len(df)` | |

### 4. 选行选列

| 任务 | API | 示例 |
|---|---|---|
| 选一列 → Series | `df['col']` | |
| 选多列 → DataFrame | `df[['a','b']]` | |
| 按标签 | `df.loc[行标签, 列名]` | `df.loc[0:3, ['a','b']]` |
| 按位置 | `df.iloc[行号, 列号]` | `df.iloc[0:3, 0:2]` |
| 单元格快取（标签） | `df.at[行, 列]` | 比 loc 快 |
| 单元格快取（位置） | `df.iat[行号, 列号]` | 比 iloc 快 |

> **`loc` 按标签，`iloc` 按位置**。`df[0]` 一般是错的——`df[...]` 只接受列名。

### 5. 筛选（数据清洗主力）

| 任务 | API | 示例 |
|---|---|---|
| 单条件 | `df[条件]` | `df[df['age'] > 18]` |
| 多条件（且） | `df[(a) & (b)]` | `df[(df.a>0) & (df.b<10)]` |
| 多条件（或） | `df[(a) \| (b)]` | |
| 取反 | `df[~条件]` | `df[~df['name'].isin([...])]` |
| 是否在列表 | `s.isin([...])` | `df[df['city'].isin(['北京','上海'])]` |
| 是否在区间 | `s.between(a, b)` | |
| 字符串语法 | `df.query(...)` | `df.query('age > 18 and score > 80')` |

> **坑**：多条件用 `&` `|` 不是 `and` `or`，每个条件外面必须加括号。

### 6. 缺失值

| 任务 | API | 示例 |
|---|---|---|
| 是否 NaN | `df.isna()` / `s.isna()` | |
| 每列缺失数 | `df.isna().sum()` | 拿到表先做一遍 |
| 删 NaN 行 | `df.dropna()` | `df.dropna(subset=['age'])` |
| 填固定值 | `df.fillna(0)` | |
| 用统计量填 | `s.fillna(s.mean())` | 也可以 median / mode |
| 前向 / 后向填充 | `s.ffill()` / `s.bfill()` | 时间序列常用 |

### 7. 排序 / 去重

| 任务 | API | 示例 |
|---|---|---|
| 按值排序 | `df.sort_values('col')` | `ascending=False` 降序 |
| 多列排序 | `df.sort_values(['a','b'])` | |
| 按索引排序 | `df.sort_index()` | |
| 是否重复 | `df.duplicated()` | |
| 去重 | `df.drop_duplicates(subset=['a'])` | |
| 看唯一值 | `s.unique()` / `s.nunique()` | |

### 8. 修改（增删改列、改值）

| 任务 | API | 示例 |
|---|---|---|
| 新增列 | `df['new'] = ...` | `df['x2'] = df['x']*2` |
| 批量新增 | `df.assign(...)` | `df.assign(x2=df.x*2, x3=df.x+1)` |
| 删列 | `df.drop(columns=[...])` | |
| 删行 | `df.drop(index=[...])` | |
| 改列名 | `df.rename(columns={'a':'A'})` | |
| 改值（按条件） | `df.loc[条件, '列'] = 值` | **永远用 loc 改值** |
| 替换值 | `df.replace(old, new)` | `df.replace({-1: np.nan})` |

### 9. 类型转换

| 任务 | API | 示例 |
|---|---|---|
| 改 dtype | `s.astype(int)` | `astype(str)`、`astype(float)` |
| 转日期 | `pd.to_datetime` | `pd.to_datetime(df['date'])` |
| 转数字 | `pd.to_numeric` | `errors='coerce'` 失败填 NaN |

### 10. 聚合统计

| 任务 | API | 备注 |
|---|---|---|
| 求和 | `df.sum()` | 默认按列；`axis=1` 按行 |
| 均值 / 中位数 | `df.mean()` / `df.median()` | |
| 最值 | `df.max()` / `df.min()` | |
| 标准差 / 方差 | `df.std()` / `df.var()` | |
| 计数（非空） | `df.count()` | |
| 类别频次 | `s.value_counts()` | 类别分析神器 |
| 累计 | `df.cumsum()` / `df.cumprod()` | |
| 相关系数 | `df.corr()` | 数值列之间的相关性 |

### 11. groupby（数据分析灵魂）

| 任务 | API | 示例 |
|---|---|---|
| 分组 | `df.groupby('col')` | 此时不会立即计算 |
| 分组求均值 | `.mean()` / `.sum()` | `df.groupby('city').mean()` |
| 多种聚合 | `.agg({...})` | `groupby('a').agg({'b':'mean','c':['min','max']})` |
| 每组大小 | `.size()` | |
| 保留原 shape 的变换 | `.transform(...)` | 用于"减去组内均值"这种 |
| 按多列分组 | `df.groupby(['a','b'])` | |

### 12. 合并 / 拼接

| 任务 | API | 说明 |
|---|---|---|
| 按行拼（上下叠） | `pd.concat([df1, df2])` | |
| 按列拼（左右贴） | `pd.concat([df1, df2], axis=1)` | |
| 按 key 合并（SQL JOIN） | `df1.merge(df2, on='id')` | |
| 左 / 右 / 外连接 | `merge(..., how='left'|'right'|'outer')` | |
| 按 index 合并 | `df1.join(df2)` | |

### 13. 字符串操作（`s.str.xxx`）

| 任务 | API | 示例 |
|---|---|---|
| 大小写 | `s.str.lower()` / `s.str.upper()` | |
| 包含子串 | `s.str.contains('AI')` | 返回布尔 Series |
| 切分 | `s.str.split(',')` | |
| 取片段 | `s.str[:3]` | |
| 替换 | `s.str.replace('a','b')` | |
| 长度 | `s.str.len()` | |

### 14. 日期操作（`s.dt.xxx`）

| 任务 | API | 示例 |
|---|---|---|
| 取年 / 月 / 日 | `s.dt.year` / `.month` / `.day` | |
| 星期 | `s.dt.dayofweek` | 0=周一 |
| 格式化字符串 | `s.dt.strftime('%Y-%m')` | |
| 日期差（天） | `(s2 - s1).dt.days` | |

### 15. 和 NumPy 互转（喂模型前必做）

| 任务 | API | 备注 |
|---|---|---|
| DataFrame → ndarray | `df.to_numpy()` | 推荐 |
| 旧写法 | `df.values` | 还能用，但官方推荐 `to_numpy` |
| ndarray → DataFrame | `pd.DataFrame(arr, columns=[...])` | |
| 单列 → ndarray | `df['col'].to_numpy()` | |

---

## 一份完整 ML 数据预处理流水线（套用上面所有 API）

把上面这些 API 串成一个真实场景，一次性见到所有"主角":

```python
import pandas as pd
import numpy as np

# 1. 读数据 (§1)
df = pd.read_csv('data.csv')

# 2. 看一眼 (§3)
print(df.shape, df.dtypes)
df.head()
df.describe()

# 3. 检查缺失值 (§6)
print(df.isna().sum())

# 4. 清洗 (§6, §9, §8)
df['age'] = df['age'].fillna(df['age'].mean())     # 用均值填
df['date'] = pd.to_datetime(df['date'])             # 转日期
df = df.dropna(subset=['target'])                   # 目标列缺失直接删
df = df.drop_duplicates()                           # 去重

# 5. 特征工程 (§8, §14)
df['year'] = df['date'].dt.year
df['is_adult'] = df['age'] >= 18
df = df.assign(age_bucket=pd.cut(df['age'], [0,18,40,100]))

# 6. 筛选感兴趣的子集 (§5)
df = df[(df['score'] > 0) & (df['country'].isin(['CN','US']))]

# 7. 按组统计（探索性分析） (§11)
print(df.groupby('country')['score'].agg(['mean','std','count']))

# 8. 选特征 + 转 NumPy (§4, §15)
features = df[['age', 'score', 'year']].to_numpy()    # (N, 3)
labels   = df['target'].to_numpy()                     # (N,)

# 9. 调形状准备喂模型（NumPy 接力）
X = features.reshape(-1, 3)
y = labels
print(X.shape, y.shape)
```

**这一个流程跑通，你 80% 的核心 API 都用过一遍了。** 后面学具体模型时，前面的"准备数据"环节永远是这套。

---

## 什么时候用 ndarray、什么时候用 Pandas？

| 你的数据 | 用哪个 |
|---|---|
| 纯数值、不需要标签、要喂模型 | **ndarray** |
| 有业务标签（日期、ID、名字）、要分析 | **Series / DataFrame** |
| 从 CSV / Excel 读进来 | **DataFrame** |
| 神经网络层之间传的张量 | **ndarray / tensor** |
| 文本、日期、混合类型 | **Series**（ndarray 装这些很别扭） |

**口诀**：
- 要**分析数据** → Pandas
- 要**喂给模型** → NumPy / Tensor
- 中间用 `.to_numpy()` 衔接

---

## 几个最容易踩的坑

### 坑 1：`loc` 和 `iloc` 弄混

```python
df = pd.DataFrame({'a': [10, 20, 30]}, index=[100, 200, 300])
df.loc[100]    # ✅ 取标签为 100 的行 → 10
df.iloc[100]   # ❌ 越界，因为只有 3 行
df.iloc[0]     # ✅ 第 0 行 → 10
```

**永远显式写 `loc` 或 `iloc`，不要直接 `df[0]`**（行索引用 `df[...]` 是错的，会被当成列名找）。

### 坑 2：链式赋值 (chained assignment)

```python
df[df['age'] > 25]['score'] = 0    # ❌ 可能不生效，会有 SettingWithCopyWarning
df.loc[df['age'] > 25, 'score'] = 0  # ✅ 正确写法
```

要修改子集，永远用 `df.loc[行条件, 列名] = 值`。

### 坑 3：`inplace=True` 不返回值

```python
df2 = df.fillna(0, inplace=True)    # df2 是 None！
df.fillna(0, inplace=True)          # ✅ 直接改 df
df = df.fillna(0)                   # ✅ 也行，重新赋值
```

社区现在更推荐**不用 inplace**，直接重新赋值，逻辑更清晰。

### 坑 4：多条件筛选忘了括号

```python
df[df['a'] > 0 & df['b'] > 0]        # ❌ 优先级错乱
df[(df['a'] > 0) & (df['b'] > 0)]    # ✅ 每个条件外面加括号
```

### 坑 5：`apply` 慢——能向量化就别用

```python
df['x'] = df['age'].apply(lambda v: v * 2)   # 慢
df['x'] = df['age'] * 2                       # 快得多（向量化）
```

只有逻辑真的没法向量化时才用 apply。

---

## 学习建议

1. **不要按官方文档顺序读**——一开始就遇到 MultiIndex、PeriodIndex 会绝望
2. **找一个真实数据集做一遍完整分析**——读、看、洗、统计、转 ndarray
3. **遇到不会的 API 再查**——记忆里只要保留"大概有这么个东西"就够了
4. **重点理解 Series 和 index 的关系**——这是和 NumPy 唯一的本质差别，理解了它，剩下的 API 都是糖

---

## 相关笔记

- [[numpy轴的理解]] —— axis / shape / broadcasting 的基础
- [[numpy_pandas_重点清单]] —— 必学 vs 可跳的 API 清单
