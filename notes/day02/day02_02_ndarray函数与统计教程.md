# Day02 · 第二节：ndarray 函数与统计（P02 + P03）

> 视频 P02（基本函数）+ P03（统计函数）。这一节就是**一长串 API**——挑重点理解 + 速查表带走。

---

## 你已经会的部分

Pandas 的 `df.sum() / mean() / max() / min() / cumsum() / value_counts()` 你都用过。**NumPy 是它们的"出生地"**——Pandas 大量函数底层就调 NumPy。

```python
# 你已经会的 Pandas 写法
df["age"].mean()

# 等价的 NumPy 写法
np.mean(df["age"].values)        # df["age"].values 是 ndarray
```

所以这一节大部分是**"原来 Pandas 的爹长这样"**——快速过一遍即可。

---

## 第一部分：基本函数（P02）

### 1.1 取整三兄弟

```python
arr1 = np.array([[1.3, -2.6, 3.5],
                 [4.7, -5.1, 6.5]])

np.abs(arr1)
# [[1.3, 2.6, 3.5],
#  [4.7, 5.1, 6.5]]               ← 绝对值

np.ceil(arr1)
# [[ 2., -2.,  4.],
#  [ 5., -5.,  7.]]                ← 向上取整（朝 +∞）

np.floor(arr1)
# [[ 1., -3.,  3.],
#  [ 4., -6.,  6.]]                ← 向下取整（朝 -∞）
```

🔥 **第一卡点**：`ceil` 和 `floor` 对**负数**的行为反直觉。

```python
np.ceil(-2.6)      # -2    （朝 +∞ → 比 -2.6 大的最小整数 = -2）
np.floor(-2.6)     # -3    （朝 -∞ → 比 -2.6 小的最大整数 = -3）
```

**记忆**：

- `ceil` = "**c**eiling 天花板" = 朝**上**（更大的方向）
- `floor` = "地板" = 朝**下**（更小的方向）

### 1.2 `np.rint` —— **不是普通四舍五入**（**重点理解**）

```python
np.rint(1.5)       # 2.0
np.rint(2.5)       # 2.0   ← 不是 3！
np.rint(3.5)       # 4.0
np.rint(4.5)       # 4.0   ← 不是 5！
```

视频里特别强调了：

> **"四舍六入五成双"**（**银行家算法 / Banker's Rounding**）：
>
> - 小于 5 → 舍（`1.3 → 1`）
> - 大于 5 → 入（`1.7 → 2`）
> - **恰好 5 → 看前一位**，前一位是**偶数舍、奇数入**（`0.5→0, 1.5→2, 2.5→2, 3.5→4, 4.5→4`）

**为什么这么设计**：

普通"四舍五入"在大量数据上会**系统性偏大**——因为 0.5 永远向上凑成偶。银行家算法让 0.5 一半向上一半向下，**长期统计无偏差**。

🔥 **实战提醒**：

- 想要**普通四舍五入** → 用 `np.round` 或 `int(x + 0.5)`（也有自己的细节坑）
- 不在意精度 → `np.rint` 也行

### 1.3 `np.isnan` —— 判 NaN

```python
arr2 = np.array([[1.3, np.nan, 3.5],
                 [4.7, np.nan, 6.5]])

np.isnan(arr2)
# [[False, True, False],
#  [False, True, False]]
```

🔥 **必须用 `isnan`**——直接用 `==` 永远是 False：

```python
np.nan == np.nan    # False    ← NaN 不等于自己
arr2 == np.nan      # 全是 False
np.isnan(arr2)      # ✅ 正确判断
```

这个坑在 Pandas 那节 [[day04_02_缺失值处理教程]] 你已经踩过——NumPy 这里是它的根源。

### 1.4 元素级 multiply / divide

```python
arr3 = np.array([[1, 2, 3], [4, 5, 6]])
arr4 = np.array([[10, 20, 30], [40, 50, 60]])

np.multiply(arr3, arr4)
# [[10,  40,  90],
#  [160, 250, 360]]               ← 等价于 arr3 * arr4

np.divide(arr4, arr3)
# [[10., 10., 10.],
#  [10., 10., 10.]]
```

🔥 **重要**：`np.multiply` = **元素乘**（不是矩阵乘法！）。矩阵乘法见 [[day02_03_广播与矩阵运算教程]]。

99% 实战直接用算子 `*` `/` `+` `-`，**不会调 `np.multiply` 这种函数**——视频教是为了完整性。

### 1.5 `np.where(cond, x, y)` —— 向量化的 if/else

```python
arr3 = np.array([[1, 2, 3], [4, 5, 6]])

np.where(arr3 > 4, 11, 22)
# [[22, 22, 22],
#  [22, 11, 11]]                  ← 大于 4 的填 11，其他填 22
```

**含义**：`np.where(cond, x, y)` ≈ `[x if c else y for c in cond]`，但**快 100 倍**。

🔥 **实战中极其常用**——见 [[day04_03_apply教程]] 里的"真向量化"章节，配合多层嵌套替代 apply。

```python
# 嵌套 where 替代多层 if/else
np.where(age < 18, "少年",
np.where(age < 60, "成人", "老人"))
```

---

## 第二部分：统计函数（P03，**和 Pandas 一一对应**）

### 2.1 七大统计

```python
arr = np.array([[1,2,3,4,5],
                [6,7,8,9,10]])

np.mean(arr)            # 5.5         ← 所有元素均值
np.sum(arr)             # 55
np.max(arr)             # 10
np.min(arr)             # 1
np.std(arr)             # 2.87        ← 标准差
np.var(arr)             # 8.25        ← 方差
np.median(arr)          # 5.5         ← 中位数（NumPy 也有）
```

### 2.2 ⭐ `axis` 参数（**核心**）

`axis` 你在 [[numpy轴的理解]] 已经吃透：**axis 是"消失的那个轴"**。

```python
arr = np.array([[1,2,3,4,5],
                [6,7,8,9,10]])
# shape: (2, 5)

np.max(arr)                # 10              ← 整体最大值
np.max(arr, axis=0)        # [6,7,8,9,10]    ← 沿行方向 → 每列的最大值（5 个）
np.max(arr, axis=1)        # [5, 10]         ← 沿列方向 → 每行的最大值（2 个）
```

🔥 **判断 axis 的快速方法**：

- `axis=0` → "纵向"压缩 → **每列一个结果**
- `axis=1` → "横向"压缩 → **每行一个结果**

**或者用"消失的轴"心法**（更稳）：

```
arr.shape = (2, 5)
axis=0 消失第 0 维 → 剩 (5,) → 5 个结果
axis=1 消失第 1 维 → 剩 (2,) → 2 个结果
```

### 2.3 `argmax / argmin` —— 找极值的"下标"

```python
arr = np.array([[1,2,3,4,5],
                [6,7,8,9,10]])

np.argmax(arr)                # 9    ← 整体最大值在"展平后"的位置 9（第 1 行第 4 列）
np.argmax(arr, axis=1)        # [4, 4]    ← 每行最大值的列下标
np.argmin(arr)                # 0
```

**实战场景**：

- **分类问题**：`argmax` 找概率最高的类别下标
- **找最佳超参数**：`argmin` 找 loss 最小的那一组

```python
# ML 经典：神经网络输出 [0.1, 0.7, 0.2] → argmax = 1 → 预测类别 1
probs = np.array([0.1, 0.7, 0.2])
pred = np.argmax(probs)       # 1
```

### 2.4 累计运算

```python
arr = np.array([[1,2,3,4,5],
                [6,7,8,9,10]])

np.cumsum(arr)
# [ 1,  3,  6, 10, 15, 21, 28, 36, 45, 55]
# 拉平后累加（行优先）

np.cumsum(arr, axis=1)
# [[ 1,  3,  6, 10, 15],
#  [ 6, 13, 21, 30, 40]]
# 每行内累加

np.cumprod(arr)
# [1, 2, 6, 24, 120, 720, ...]
# 累计积
```

**实战**：

- `cumsum` → 算"截至今天的累计销售"
- `cumprod` → 算"累计复利"

### 2.5 比较 `any / all`

```python
arr2 = np.array([[1,2,3],[4,5,6]])

np.any(arr2 > 3)    # True     ← 至少一个 > 3
np.all(arr2 > 3)    # False    ← 全部 > 3？不是

np.any(arr2 > 0)    # True
np.all(arr2 > 0)    # True

# 也能配合 axis
np.any(arr2 > 3, axis=0)    # [True, True, True]   每列至少一个 > 3
np.all(arr2 > 3, axis=1)    # [False, True]        每行是否全 > 3
```

🔥 **实战极其常用**：

```python
# 检查数据集有没有 NaN
np.any(np.isnan(arr))

# 检查所有元素都合法
np.all(arr > 0)
```

### 2.6 排序 `sort`

```python
arr3 = np.array([[3,6,4],
                 [2,7,5],
                 [9,8,1]])

# 方式 A：原地排序（修改原数组）
arr3.sort(axis=0)
# arr3 现在变成：
# [[2, 6, 1],
#  [3, 7, 4],
#  [9, 8, 5]]                     ← 每列内排序

# 方式 B：返回新数组
sorted_arr = np.sort(arr3, axis=0)    # arr3 不变
```

🔥 **关键差异**：

| 写法 | 修改原数组吗 | 返回 |
|---|---|---|
| `arr.sort(...)` | ✅ 改 | None |
| `np.sort(arr, ...)` | ❌ 不改 | 新数组 |

**实战建议**：用 `np.sort`——原地排序容易让代码不可预测。

### 2.7 去重 `unique`

```python
arr1 = np.random.randint(0, 5, (3, 3))
# [[2, 2, 3],
#  [1, 1, 1],
#  [0, 2, 4]]

np.unique(arr1)
# [0, 1, 2, 3, 4]                 ← 自动排序 + 去重
```

`np.unique` 还能返回更多信息：

```python
unique, counts = np.unique(arr1, return_counts=True)
# unique: [0, 1, 2, 3, 4]
# counts: [1, 3, 3, 1, 1]          ← 每个值出现的次数
```

→ Pandas 的 `value_counts()` 底层用的就是这个。

---

## 第三部分：NumPy 函数 vs Pandas 对应表

| 功能 | NumPy | Pandas | 备注 |
|---|---|---|---|
| 均值 | `np.mean(arr)` | `s.mean()` / `df.mean()` | Pandas 自动跳 NaN |
| 求和 | `np.sum(arr)` | `s.sum()` | |
| 最值 | `np.max / min` | `s.max() / min()` | |
| 标准差 | `np.std(arr)` | `s.std()` | |
| 最值下标 | `np.argmax` | `s.idxmax()` | Pandas 返回 **index 标签**，NumPy 返回**位置**|
| 累计 | `np.cumsum / cumprod` | `s.cumsum() / cumprod()` | |
| 去重 | `np.unique` | `s.unique() / value_counts()` | |
| 排序 | `np.sort` | `s.sort_values()` | Pandas 还能 sort_index |
| 判 NaN | `np.isnan` | `s.isna()` | Pandas 自动识别 NaN/None/NaT |
| 三元运算 | `np.where(c,x,y)` | `s.where(c, y)` / `np.where(c,x,y)` | 用法略不同 |
| any/all | `np.any / all` | `s.any() / all()` | |

🔥 **核心结论**：**Pandas 是 NumPy 的"加了 index 标签的版本"**——同样的统计函数大都在两边都有。

---

## 卡点汇总（4 大坑预警）

1. **`np.rint` 是"四舍六入五成双"** —— `2.5 → 2` 不是 3
2. **`np.isnan` 是唯一判 NaN 的方式** —— `arr == np.nan` 永远 False
3. **`axis=0/1` 容易写反** —— 心法："消失的那个轴"
4. **`arr.sort()` 原地改、`np.sort(arr)` 返回新数组** —— 不留意会改坏原数据

---

## 速查 API 表

```python
# 基本函数
np.abs(arr)
np.ceil(arr) / floor(arr)
np.rint(arr)                          # 四舍六入五成双
np.round(arr, decimals=2)             # 普通四舍五入（保留 N 位）
np.isnan(arr)
np.where(cond, x, y)                  # 向量化 if/else

# 统计
np.mean / sum / max / min / std / var / median(arr, axis=)
np.argmax / argmin(arr, axis=)
np.cumsum / cumprod(arr, axis=)
np.any / all(arr, axis=)

# 排序去重
arr.sort(axis=)                       # 原地（改原数组）
np.sort(arr, axis=)                   # 新数组
np.unique(arr, return_counts=True)
np.argsort(arr)                       # 排序后的"下标"

# 元素级（用 算子 更常用）
np.multiply / divide / add / subtract
arr1 * arr2 / arr1 / arr2             # ← 实战首选
```

---

## 自测题（请合上笔记复述）

> 1. `np.rint(2.5)` 是几？为什么？
> 2. `arr = np.array([[1,2],[3,4]])` 求每行最大值的代码
> 3. 把 `arr` 里所有大于 2 的元素替换成 99，小于等于 2 的保持
> 4. 检查 `arr` 有没有 NaN（一行代码）
> 5. `arr.sort()` 和 `np.sort(arr)` 有什么区别？

<details>
<summary>👇 答案展开</summary>

1. `2`——四舍六入五成双；`2.5` 前一位是偶数 2，所以舍去 5 → 2
2. `np.max(arr, axis=1)`
3. `np.where(arr > 2, 99, arr)`
4. `np.any(np.isnan(arr))`
5. `arr.sort()` 原地修改原数组并返回 None；`np.sort(arr)` 返回新数组、原数组不变

</details>

---

## 配套笔记

- [[day02_00_概念地图]] —— Day02 主题地图
- [[day02_01_ndarray索引切片教程]] —— 上一节
- [[day02_03_广播与矩阵运算教程]] —— 下一节：广播（**重头戏**）
- [[day02_04_Series教程]] —— Series 入门
- [[numpy轴的理解]] —— axis 心法
- [[day04_02_缺失值处理教程]] —— `isna` 的 Pandas 版

---

## 学完本节你应该能做到

- ✅ 看到 `np.mean(arr, axis=0)` 立刻心算出输出 shape
- ✅ 用 `np.where(cond, x, y)` 写出向量化的 if/else
- ✅ 处理 NaN 时本能用 `np.isnan` 而不是 `==`
- ✅ 找极值"位置"用 `argmax` 而不是 `max` 再查找
- ✅ 知道 `arr.sort()` 和 `np.sort(arr)` 的区别
