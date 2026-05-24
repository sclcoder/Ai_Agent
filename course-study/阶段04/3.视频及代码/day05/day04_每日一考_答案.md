1.分别使用内连接、全外、左外、右外连接  连接下面两个df

df1 = pd.DataFrame(

  {"employee": ["Bob", "Jake", "Lisa", "Sue"], "group": ["Accounting", "Engineering", "Engineering", "HR"]}

)

df2 = pd.DataFrame({"name": ["Bob", "Jake", "Lisa", "Sue"], "salary": [70000, 80000, 120000, 90000]})

​	答案见笔记

2.创建一个DataFrame df如下：

| 地区 | 产品 | 销售额 |

|----|----|----|

| 东部 | 苹果 | 100|

| 东部 | 香蕉 | 150|

| 西部 | 苹果 | 120|

| 西部 | 香蕉 | 80|

以地区和产品分组，计算每个地区每种产品的销售额总和。

```python
import pandas as pd
df = pd.DataFrame({    '地区': ['东部', '东部', '西部', '西部'],    '产品': ['苹果', '香蕉', '苹果', '香蕉'],    '销售额': [100, 150, 120, 80]})
df.groupby(["地区","产品"])["销售额"].sum()
```







