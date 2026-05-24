# NumPy & Pandas 必学 vs 可跳清单

> 按 ML / AI 路线优先级排，**不是按官方文档结构**。
> ⭐⭐⭐ = 几乎天天用，必须吃透
> ⭐ = 偶尔用，遇到再查
> 没标 = 一开始可以直接跳过

---

## NumPy

### 一句话定位

> NumPy 是为"批量数值运算"设计的容器。后面 PyTorch 的 tensor 就是它的 GPU 版，API 几乎一样。**把 NumPy 学透，PyTorch 一半的东西免费送你**。

---

### ⭐⭐⭐ 必须吃透（80% 的代码都在用这些）

| 主题 | 核心 API | 为什么重要 |
|---|---|---|
| **创建数组** | `np.array`, `np.zeros`, `np.ones`, `np.arange`, `np.linspace`, `np.random.randn` | 所有数据都得先变成数组 |
| **shape / dtype** | `.shape`, `.dtype`, `.ndim`, `.size` | 地基中的地基（见 [[numpy轴的理解]]） |
| **reshape / transpose** | `.reshape`, `.T`, `.transpose`, `np.newaxis`, `.squeeze` | 换轴顺序、加减维度，PyTorch 里天天写 |
| **索引和切片** | `a[1, 2]`, `a[:, 0]`, `a[1:3, ::2]` | 跟 Python list 类似但更强大 |
| **布尔索引** | `a[a > 0]`, `np.where(...)` | 数据筛选、mask、loss 处理用得极多 |
| **广播** | （见 [[numpy轴的理解]]） | ML 代码的隐形地基 |
| **聚合** | `.sum`, `.mean`, `.max`, `.argmax`，配 `axis=` 和 `keepdims=` | 算 loss、准确率、统计量都靠它 |
| **矩阵乘法** | `A @ B`, `np.matmul`, `np.dot` | 神经网络的本质就是矩阵乘法 |
| **随机数** | `np.random.seed`, `np.random.randn`, `np.random.choice` | 初始化、采样、shuffle |

---

### ⭐ 用到再查

- `np.concatenate` / `np.stack` / `np.vstack` / `np.hstack`（拼接，会一个 `concatenate` 就够了）
- `np.unique`, `np.sort`, `np.argsort`
- `np.linalg.inv`, `np.linalg.norm`, `np.linalg.svd`（线性代数，做 NLP 会用）
- `np.save` / `np.load`（保存 `.npy` 文件）
- `np.einsum`（强大但门槛高，后期再学）

---

### 可以直接跳过

- 高级 `dtype`（结构化数组、record array）
- `np.matrix`（已经被官方弃用，永远用 `ndarray`）
- 大部分 `np.polynomial` / `np.fft` / `np.ma`（专业领域才用）
- C API、ufunc 自定义

---

## Pandas

### 一句话定位

> Pandas = Python 里的 Excel + SQL，用来读数据、清洗、统计、画前置分析。
> 注意：**ML 训练阶段用得越来越少**——大部分数据最后还是要变成 NumPy / Tensor。所以 Pandas 学到"能洗数据"就够了，不用钻到地板下面。

---

### ⭐⭐⭐ 必须吃透

| 主题 | 核心 API | 为什么重要 |
|---|---|---|
| **两种数据结构** | `Series`（一列）vs `DataFrame`（一张表） | 整个库就这俩 |
| **读写文件** | `pd.read_csv`, `pd.read_excel`, `df.to_csv` | 99% 数据从 CSV 进来 |
| **看数据** | `df.head()`, `df.info()`, `df.describe()`, `df.shape`, `df.columns` | 拿到数据第一件事 |
| **选行选列** | `df['col']`, `df[['a','b']]`, `df.loc[行, 列]`, `df.iloc[行号, 列号]` | **`loc` 按名字、`iloc` 按位置**，这个区别必须记牢 |
| **布尔筛选** | `df[df['age'] > 18]`, `df.query('age > 18')` | 数据清洗主力 |
| **缺失值** | `df.isna()`, `df.dropna()`, `df.fillna(...)` | 真实数据全是脏的 |
| **新增/修改列** | `df['new'] = ...`, `df.assign(...)`, `df.drop(...)` | 特征工程基本操作 |
| **groupby + 聚合** | `df.groupby('col').mean()`, `.agg({...})` | 数据分析的灵魂 |
| **类型转换** | `df['col'].astype(...)`, `pd.to_datetime(...)`, `pd.to_numeric(...)` | 经常需要 |
| **和 NumPy 互转** | `df.values` / `df.to_numpy()` / `pd.DataFrame(arr)` | 进模型前必做 |

---

### ⭐ 用到再查

- `merge` / `join` / `concat`（表合并，做特征拼接时用）
- `apply` / `map` / `applymap`（逐元素函数，但**能用向量化就别用 apply**，慢得多）
- `pivot_table` / `melt`（宽表 ↔ 长表）
- `value_counts`, `nunique`, `unique`
- 时间序列：`pd.date_range`, `df.resample`, `.dt` accessor

---

### 可以直接跳过

- 大部分 `MultiIndex` 高级操作（学到就头大，工业界其实用得不多）
- `Categorical` 的深度细节
- `pd.eval` / `df.eval`（性能优化，先不管）
- Styler（HTML 渲染）
- 大部分 `IO` 的小众格式（HDF5、Stata、SAS 等）

---

## 高效学习路线（不要按文档顺序学）

你的状态：已经懂 axis / broadcasting，最难的概念关已经过了。剩下的按**一个真实数据集做一遍分析**的方式串起来：

### 一个练习串起所有核心 API

找一个真实 CSV（比如 Kaggle 的泰坦尼克号、加州房价），从头做：

1. `pd.read_csv` 读进来
2. `df.head() / .info() / .describe()` 看一眼
3. 用 `df.isna().sum()` 找缺失值，用 `fillna` 填上
4. 用布尔筛选挑想要的子集
5. 用 `groupby` 算每组的均值
6. 把数值列 `.to_numpy()` 转成 NumPy 数组
7. 用 NumPy 算 `mean` / `std` 做标准化
8. 用 `reshape` 调成 `(batch, features)` 准备喂模型

**做完这一遍，上面 ⭐⭐⭐ 的 API 你 80% 都摸过了**。比啃文档高效十倍。

---

## 一个判断标准

学某个 API 之前问自己：

> **"它能不能让我把数据变成 `(batch, features)` 这种喂给模型的形状？"**

- 能 → 学
- 不能（比如可视化样式、HTML 输出、奇葩 IO 格式）→ 跳

ML 路线上的 NumPy / Pandas 就是个"**数据搬运工 + 形状整形器**"，别把它当数据库或 BI 工具学。

---

## 相关笔记

- [[numpy轴的理解]] —— 轴、shape、broadcasting 的完整心智模型
