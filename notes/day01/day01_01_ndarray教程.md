# Day01 · 第一节：ndarray 属性 + 创建方式（P02 + P03）

> Day01 的**主菜**——从无到有造出 NumPy 的核心对象 ndarray。学完这一节，你就能用 NumPy 给任何项目"造测试数据"。

---

## 为什么要学 ndarray

iOS 老兵的疑问："Python 不是有 list 吗？为什么还要 ndarray？"

**答**：因为 list **太慢、太占内存、不支持批量运算**。

```python
import numpy as np
import time

# Python list 算 100 万个数 ×2
lst = list(range(1_000_000))
t1 = time.time()
result = [x * 2 for x in lst]
print(f"list: {time.time()-t1:.3f}s")       # 约 50ms

# NumPy ndarray 算同样的事
arr = np.arange(1_000_000)
t2 = time.time()
result = arr * 2                            # 一行搞定
print(f"ndarray: {time.time()-t2:.3f}s")    # 约 1ms
```

**50 倍速度差距**——这就是 NumPy 的存在意义。Pandas / PyTorch / TensorFlow 底层都是 ndarray。

---

## 第一部分：P02 — ndarray 的 5 个属性

### 1.1 视频里的代码

```python
import numpy as np

arr = np.array([[1, 2, 3], [4, 5, 6]])
print(arr.ndim)        # 2
print(arr.shape)       # (2, 3)
print(arr.size)        # 6
print(arr.dtype)       # int64
print(arr.itemsize)    # 8
```

### 1.2 5 个属性详解

#### `ndim` —— 几维？

```python
np.array([1,2,3]).ndim                    # 1（向量）
np.array([[1,2],[3,4]]).ndim              # 2（矩阵）
np.array([[[1],[2]],[[3],[4]]]).ndim      # 3（张量）
```

**记忆**：`ndim = "n-dimension"`，**几层方括号就是几维**。

#### `shape` —— 各维度的大小

```python
np.array([1,2,3]).shape                   # (3,)        ← 注意逗号！
np.array([[1,2],[3,4]]).shape             # (2, 2)
np.array([[1,2,3],[4,5,6]]).shape         # (2, 3)      ← 2 行 3 列
np.zeros((2,3,4)).shape                   # (2, 3, 4)   ← 2 张 3×4 的表
```

🔥 **第一卡点**：1D 数组的 shape 是 `(3,)` 不是 `(3)`。**Python 语法**——`(3)` 等于 `3`，要表示元组必须加逗号 `(3,)`。

```python
type((3))      # <class 'int'>
type((3,))     # <class 'tuple'>     ← 这才是元组
```

#### `size` —— 元素总数

```python
arr.size = arr.shape 各维度乘积

np.zeros((2,3)).size       # 6 = 2 × 3
np.zeros((2,3,4)).size     # 24 = 2 × 3 × 4
```

#### `dtype` —— 元素类型

```python
np.array([1,2,3]).dtype                   # int64（自动推断）
np.array([1.0, 2.0]).dtype                # float64
np.array([1,2,3], dtype="i4").dtype       # int32
```

→ 详细见 [[day01_02_数据类型教程]]。

#### `itemsize` —— 每个元素的字节数

```python
np.array([1,2,3], dtype=np.int64).itemsize    # 8
np.array([1,2,3], dtype=np.int32).itemsize    # 4
np.array([1,2,3], dtype=np.float32).itemsize  # 4
```

**用途**：算数组总内存 = `size * itemsize`。

```python
arr = np.zeros((1000, 1000), dtype=np.float64)
print(arr.size * arr.itemsize / 1024 / 1024)  # 7.63 MB
```

🔥 **实战提醒**：处理大数据时**降低 dtype 精度能省一半内存**——把 `float64` 换成 `float32`，1 GB 数组立刻变 500 MB。

### 1.3 和 Pandas 的对应关系

你已经在 Pandas 里见过类似的：

| Pandas | NumPy ndarray | 含义 |
|---|---|---|
| `df.shape` | `arr.shape` | 形状 |
| `df.dtypes` | `arr.dtype` | 类型（df 每列各有 dtype，ndarray 一个）|
| `df.ndim` | `arr.ndim` | 维度 |
| `df.size` | `arr.size` | 元素总数 |
| `df.values` | `arr`（DataFrame 的底层就是 ndarray）| 数据 |

**关键差异**：DataFrame 每列可以不同 dtype，**ndarray 整体只有一个 dtype**——这是因为 ndarray 是连续内存。

---

## 第二部分：P03 — 9 类创建方式

### 2.1 第 1 类：`np.array` / `np.asarray` —— 从 Python list 造

#### 基本用法

```python
np.array([1, 2, 3])                       # 1D
np.array([[1,2,3], [4,5,6]])              # 2D
```

#### `array` vs `asarray` 的差异（**视频重点演示**）

视频里用 `id(...)` 演示了两者的区别：

```python
import numpy as np

data = [1, 2, 3]
print(f"data 内存地址 → {id(data)}")

# 情况 1：入参是 list（两者无差异）
arr1 = np.array(data)
print(f"arr1 内存地址 → {id(arr1)}")         # 新地址

# 情况 2：入参已经是 ndarray
arr2 = np.array(arr1)                       # ← array 会拷贝
print(f"arr2 内存地址 → {id(arr2)}")         # 新地址（不同）

arr3 = np.asarray(arr1)                     # ← asarray 不拷贝
print(f"arr3 内存地址 → {id(arr3)}")         # 和 arr1 相同地址！
```

**对照表**：

| 入参类型 | `np.array(...)` | `np.asarray(...)` |
|---|---|---|
| Python `list` | 新建 ndarray | 新建 ndarray |
| 已是 `ndarray` | **拷贝一份新的** | **直接复用（不拷贝）** |

**何时用哪个**：

- 想要"**独立的副本**"（修改互不影响）→ `np.array`
- 想要"**省内存**"（明确不会修改）→ `np.asarray`
- 函数入口"**接受 list 或 ndarray 都行**" → `np.asarray`（统一处理）

```python
def process(data):
    arr = np.asarray(data)        # ← 函数内的标准动作：归一化输入
    ...
```

🔥 **第二卡点**：99% 实战直接用 `np.array`——除非明确做性能优化，别管 `asarray`。

---

### 2.2 第 2 类：`zeros` / `ones` —— 全 0 / 全 1

```python
np.zeros((2, 3))         # 全 0，shape (2,3)，默认 float64
np.ones((2, 3))          # 全 1
np.ones((2, 3), dtype=np.int32)   # 全 1 整数
```

**输出**：

```python
np.zeros((2, 3))
# array([[0., 0., 0.],
#        [0., 0., 0.]])
```

🔥 **第三卡点**：注意 `np.zeros(2, 3)` 是 ❌——必须是 `np.zeros((2, 3))`，shape 是**一个元组参数**，不是两个独立参数。

```python
np.zeros(2, 3)          # ❌ TypeError
np.zeros((2, 3))        # ✅
np.zeros([2, 3])        # ✅ 也行（list 也接受）
```

**实战场景**：

- 初始化一个"待填充的数组" → `np.zeros((n, m))` 占位
- ML 里"初始化权重为 0"（虽然 ML 通常不用 zeros 初始化，但占位是常见）

---

### 2.3 第 3 类：`empty` —— 未初始化（**最快**）

```python
np.empty((2, 3))
# array([[2.4e-322, 6.9e-310, 0.0],         ← 内容随机！这是上一次内存的残留
#        [...]])
```

**关键**：`empty` **不清零内存**，里面是"上次该位置的内容"——**全是垃圾**。

**何时用**：

- 知道马上要**覆盖每个元素** → 用 empty 比 zeros 快 30%
- 反例：直接拿 empty 数组的值算东西 → **会得到 NaN / 无穷大 / 任何乱七八糟的数**

```python
# ✅ 正确用法
arr = np.empty((1000, 1000))    # 占位
for i in range(1000):
    arr[i] = compute(i)         # 立刻覆盖

# ❌ 错误用法
arr = np.empty((10,))
print(arr.sum())                # ← 谁知道这是什么数
```

**建议**：新手 99% 场景用 `zeros` 而不是 `empty`——除非性能瓶颈。

---

### 2.4 第 4 类：`full` —— 填指定值

```python
np.full((2, 3), 6)
# array([[6, 6, 6],
#        [6, 6, 6]])

np.full((2, 3), -1.0)             # 用 -1.0 填，dtype 自动推断为 float64
np.full((2, 3), 7, dtype=np.int8) # 显式指定 dtype
```

**实战**：算法中"用某个特定值占位"（如 NaN、-999 表示"未知"）。

---

### 2.5 第 5 类：`_like` 系列 —— 仿 shape 造

```python
arr = np.zeros((2, 3))
np.zeros_like(arr)               # 同 shape 的全 0 数组
np.ones_like(arr)                # 同 shape 的全 1 数组
np.empty_like(arr)               # 同 shape 的未初始化数组
np.full_like(arr, 8)             # 同 shape 的全 8 数组
```

**实战**：写函数时不知道入参 shape，直接 "仿造一个" 当输出：

```python
def my_func(arr):
    result = np.zeros_like(arr)   # ← 输出同 shape，不用关心多少维
    ...
    return result
```

---

### 2.6 第 6 类：`arange` —— 类似 Python range

```python
np.arange(0, 10, 2)
# array([0, 2, 4, 6, 8])     ← 步长 2，左闭右开
```

**3 个参数**：`arange(start, stop, step)`——和 Python 内置 `range` 完全一样。

| 写法 | 结果 |
|---|---|
| `np.arange(5)` | `[0, 1, 2, 3, 4]` |
| `np.arange(2, 8)` | `[2, 3, 4, 5, 6, 7]` |
| `np.arange(0, 10, 2)` | `[0, 2, 4, 6, 8]` |
| `np.arange(0, 1, 0.1)` | `[0, 0.1, 0.2, ..., 0.9]` （浮点也行）|

🔥 **第四卡点**：`arange` **左闭右开**——不包含 stop。`np.arange(0, 10)` 是 `0..9`，没有 10。

---

### 2.7 第 7 类：`linspace` —— 等差等分点

```python
np.linspace(0, 10, 5)
# array([ 0. ,  2.5,  5. ,  7.5, 10. ])   ← 在 [0,10] 切 5 个等分点

np.linspace(0, 10, 5, endpoint=False)
# array([0., 2., 4., 6., 8.])             ← 不包含末尾，等价于 arange(0,10,2)
```

**3 个参数**：`linspace(start, stop, num)`——`num` 是**点的个数**，不是步长。

| `arange` | `linspace` |
|---|---|
| 指定**步长** | 指定**点数** |
| 左闭右开（默认）| **闭区间**（默认 endpoint=True）|
| 容易出现浮点误差（步长 0.1 时）| 精确分点 |
| 整数序列首选 | 浮点序列首选 |

🔥 **实战记忆**：

- 想要 `[0, 0.1, 0.2, ..., 1.0]` 这种"切 N 个点"的浮点序列 → **永远用 `linspace`**
- 想要 `[0, 1, 2, ..., 9]` 这种整数步长 → 用 `arange`

**典型场景**：画图的 x 轴。

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 2*np.pi, 100)    # 在 [0, 2π] 切 100 个点
y = np.sin(x)
plt.plot(x, y)                       # 平滑的正弦曲线
```

---

### 2.8 第 8 类：`logspace` —— 等比数列

```python
np.logspace(start=2, stop=5, num=4, base=2)
# array([ 4.,  8., 16., 32.])
```

**含义**：在 `base ** start` 到 `base ** stop` 之间，**指数等差**地取 num 个点。

逐步拆解：

```
start=2, stop=5, base=2
↓
2^2 = 4, 2^5 = 32, 取 4 个点
↓
指数：[2, 3, 4, 5]
↓
结果：[2^2, 2^3, 2^4, 2^5] = [4, 8, 16, 32]
```

**实战场景**：

- ML 的**学习率搜索**：`logspace(-5, -1, 5)` → `[1e-5, 1e-4, 1e-3, 1e-2, 1e-1]`
- 频域分析、对数坐标轴

⭐ 用到再查。

---

### 2.9 第 9 类：`np.random` —— 随机数（**ML 必备**）

#### 4 个核心方法

```python
np.random.rand(2, 3)
# array([[0.37, 0.95, 0.73],
#        [0.60, 0.16, 0.06]])   ← [0, 1) 均匀分布

np.random.randint(low=0, high=5, size=(2, 3))
# array([[1, 4, 0],
#        [3, 2, 4]])              ← [0, 5) 整数

np.random.uniform(low=0, high=5, size=(2, 3))
# array([[2.3, 0.7, 4.1],
#        [3.5, 1.8, 0.2]])        ← [0, 5) 均匀浮点

np.random.randn(2, 3)
# array([[-1.99,  1.35,  0.59],
#        [ 1.17,  0.95,  1.42]])  ← 标准正态（均值 0，标准差 1）
```

#### 一句话区分 4 个

| 方法 | 分布 | 范围 | 用途 |
|---|---|---|---|
| `rand(2,3)` | 均匀 | `[0, 1)` | 通用随机 |
| `randint(0,5,(2,3))` | 均匀 | `[0, 5)` 整数 | 模拟离散事件、类别 |
| `uniform(0,5,(2,3))` | 均匀 | `[0, 5)` 浮点 | 任意范围连续随机 |
| `randn(2,3)` | **标准正态** | 实数（约 ±3 内）| **ML 权重初始化** |

#### 🔥 `np.random.seed` —— 固定随机种子

```python
np.random.seed(42)
np.random.rand(3)
# array([0.37, 0.95, 0.73])      ← 这个结果固定不变

np.random.seed(42)
np.random.rand(3)
# array([0.37, 0.95, 0.73])      ← 再跑一次，结果一样
```

**实战必备**：

- 调试时**结果可复现**——同事看到的和你看到的一样
- ML 训练时**实验对比**——别因为随机数不同得出错误结论

```python
# 实验开头一律加这两行
np.random.seed(42)
# (如果用 PyTorch 也加 torch.manual_seed(42))
```

---

### 2.10 第 10 类（番外）：`np.matrix` —— **几乎不用**

```python
aa = np.matrix("1,2;3,4")          # 用字符串造矩阵
# matrix([[1, 2],
#         [3, 4]])

np.matrix([[1, 2], [3, 4]])         # 用 list 造
```

🔥 **重要提醒**：**`np.matrix` 已被 NumPy 官方标记为"不推荐使用"**——未来可能弃用。

**原因**：

- 限制为 2D（不支持高维）
- 和 ndarray 行为不一致（`*` 在 matrix 是矩阵乘法，在 ndarray 是元素积）
- 容易引起混淆

**结论**：**永远用 `ndarray`**，矩阵乘法用 `@` 或 `np.matmul`：

```python
a = np.array([[1,2],[3,4]])
b = np.array([[5,6],[7,8]])

a @ b          # 矩阵乘法（推荐）
np.matmul(a, b)  # 等价
a * b          # 元素积（不是矩阵乘法！）
```

视频里讲了 matrix 是为了**完整性**，**实战中你应该忘记它**。

---

## 卡点汇总（5 大坑预警）

1. **`shape` 是元组、1D 数组 shape 是 `(5,)` 不是 `(5)`** —— 加不加逗号差别巨大
2. **`np.zeros(2, 3)` 不对** —— shape 必须是元组：`np.zeros((2,3))`
3. **`array` vs `asarray`** —— list 入参无差，ndarray 入参 array 拷贝、asarray 不拷贝
4. **`arange` 左闭右开 vs `linspace` 闭区间** —— 切点 5 个用 linspace、步长 2 用 arange
5. **`np.matrix` 不要用** —— 一律 `ndarray` + `@`

---

## 速查表

```python
# 属性
arr.ndim / shape / size / dtype / itemsize

# 从 list 造
np.array(lst)
np.asarray(lst)             # 入参是 ndarray 时不拷贝

# 全 0 / 全 1 / 全指定值
np.zeros((2, 3))
np.ones((2, 3))
np.full((2, 3), 6)
np.empty((2, 3))            # 未初始化，最快

# 仿 shape 造
np.zeros_like(arr) / ones_like / empty_like / full_like(arr, 8)

# 等差 / 等比
np.arange(start, stop, step)
np.linspace(start, stop, num, endpoint=True)
np.logspace(start, stop, num, base=10)

# 随机
np.random.seed(42)
np.random.rand(2, 3)                  # [0,1) 均匀
np.random.randint(0, 5, (2, 3))       # 整数 [0,5)
np.random.uniform(0, 5, (2, 3))       # 浮点 [0,5)
np.random.randn(2, 3)                 # 标准正态（ML 必备）

# 矩阵（不要用！）
# np.matrix(...) ← 忘掉它
```

---

## 自测题（请合上笔记复述）

> 1. 写出生成"2 行 4 列的全 0 整数数组"的代码
> 2. 用 `linspace` 生成 `[0, 0.25, 0.5, 0.75, 1]`
> 3. 用 `arange` 生成 `[0, 2, 4, 6, 8]`
> 4. 生成"100 个标准正态分布的随机数"，且**可复现**（每次跑结果一样）
> 5. 一个 ndarray `arr.shape == (3, 4)`、`dtype` 是 `float64`，它占多少字节？

<details>
<summary>👇 答案展开</summary>

```python
# 1.
np.zeros((2, 4), dtype=np.int64)
# 或
np.zeros((2, 4), dtype="i8")

# 2.
np.linspace(0, 1, 5)
# 或 np.linspace(0, 1, 5, endpoint=True)

# 3.
np.arange(0, 10, 2)
# 注意：stop=10 是 ✅；stop=9 也行因为左闭右开

# 4.
np.random.seed(42)
np.random.randn(100)

# 5.
# size = 3 × 4 = 12
# itemsize = 8 (float64)
# 总字节 = 96
```
</details>

---

## 配套笔记

- [[day01_00_概念地图]] —— Day01 主题地图
- [[day01_02_数据类型教程]] —— 下一节：dtype 详解
- [[numpy轴的理解]] —— 学完本节再看（理解 axis）
- [[pandas理解]] —— Pandas 全局（你已学）

---

## 学完本节你应该能做到

- ✅ 闭眼写出"造 (2,3) 全 0 数组"、"造 100 个 [0,1) 随机数"
- ✅ 区分 `arange` vs `linspace` 的使用场景
- ✅ 设置 `np.random.seed` 让实验可复现
- ✅ 知道 `np.matrix` 是历史遗物，一律用 ndarray + `@`
- ✅ 看到 `arr.shape == (1000, 1000)` + `float64` 能立刻心算占多大内存（8MB）
