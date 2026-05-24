# Matplotlib
import numpy as np
import matplotlib.pyplot as plt  # 导入matplotlib

# 准备x轴数据
x = np.linspace(start=0, stop=10, num=100)
# 准备y轴数据
y1 = np.sin(x)
# 准备y轴数据
y2 = np.cos(x)


# 创建画布   这步不是必须的，我们这里显示创建，可以在创建的时候，传递参数，指定画布的尺寸
plt.figure(figsize=(10, 6))

# 将画布分为2行1列，目前操作的是第一行
plt.subplot(2, 1, 1)
# 设置x轴数据范围
plt.xlim(0, 10)
# 设置y轴数据范围
plt.ylim(-1, 1)
# 设置x轴标签
plt.xlabel('x')
# 设置y轴标签
plt.ylabel('sin(x)')
# 设置子标题
plt.title('sin')
# 绘图
plt.plot(x,y1)


# 将画布分为2行1列，目前操作的是第二行
plt.subplot(2, 1, 2)
# 设置x轴数据范围
plt.xlim(0, 10)
# 设置y轴数据范围
plt.ylim(-1, 1)
# 设置x轴标签
plt.xlabel('x')
# 设置y轴标签
plt.ylabel('cos(x)')
# 设置子标题
plt.title('cos')
# 绘图
plt.plot(x,y2)

plt.show()