# 环境工具速查:Anaconda · conda · Jupyter

> 给 iOS 老兵的速通笔记。一口气讲清三个东西是什么、什么关系、怎么用。

---

## 🟦 Anaconda — "Python 数据科学全家桶"

**是什么:** 一个**发行版**,装上它你就同时得到了:

- Python 解释器
- 250+ 个常用数据科学库(Numpy、Pandas、Matplotlib、scikit-learn... 全部预装)
- conda 这个工具
- Jupyter 这个工具
- 一个图形化的导航器 Anaconda Navigator

**iOS 类比:** 类似 Xcode 安装包——你装一个 Xcode,顺带就有了 Swift 编译器、Instruments、Simulator、各种 SDK。Anaconda 也是"一装全有"。

**它解决的问题:** 新手装 Python + 一堆库太麻烦,Anaconda 一次性搞定。

**注意:** 现在很多人不用完整版 Anaconda(太大,5GB+),改用 **Miniconda** —— 只装 Python + conda,其他库按需安装。如果已经装了 Anaconda 就用着,装了 Miniconda 也完全 OK,体验一样。

---

## 🟩 conda — 包管理 + 环境管理工具

**是什么:** 一个命令行工具,做两件事:

1. **装库**(类似 npm install / pip install)
2. **管理隔离环境**(类似 nvm,可以为不同项目切换不同的 Python 版本和库版本)

**iOS 类比:** 想象 **CocoaPods + rbenv 合体** —— 既能装第三方库,又能为每个项目维护独立的 Python 版本和依赖。

### 最常用命令

```bash
# 创建一个新环境(给"阶段 13 LoRA 微调"专门开一个)
conda create -n lora python=3.10

# 进入这个环境
conda activate lora

# 离开当前环境
conda deactivate

# 在当前环境装库
conda install numpy pandas
# 或者用 pip 也行(混用没问题)
pip install transformers

# 查看所有环境
conda env list

# 删除一个环境
conda env remove -n lora
```

### conda vs pip 的关系

- `conda` 是**包管理 + 环境管理**
- `pip` 只是**包管理**(Python 自带的)
- **实际用法:** 用 `conda` 管环境,装库时 conda / pip 都能用,**优先 conda,装不到的再 pip**

### 为什么要"环境"这玩意儿?

不同项目可能需要不同版本的库——A 项目要 torch 1.x,B 项目要 torch 2.x。环境就是给每个项目造一个独立的"小屋子",互不污染。

后面阶段 13 微调你会深度依赖这个,因为 deepspeed / unsloth / peft 这些库对版本要求很苛刻。

---

## 🟪 Jupyter — 交互式编程环境

**是什么:** 一个能在浏览器里写 Python 的**笔记本式**编程界面。代码可以**一段一段跑**,每段输出(包括图表、表格、图片)直接显示在代码下方。

**iOS 类比:** 类似 **Swift Playground** —— 写一行立刻看到结果,适合"边写边探索"。但 Jupyter 更强,因为它能保留所有中间结果,适合数据分析这种"看一眼数据再决定下一步怎么写"的场景。

**文件格式:** `.ipynb`(JSON 格式,存代码 + 输出 + Markdown 笔记)

### 两个常见名字别搞混

- **Jupyter Notebook** — 老版本,经典界面
- **JupyterLab** — 新版本,像 IDE 一样的多标签界面(推荐)

### 怎么启动

```bash
# 在终端某个目录下
jupyter notebook
# 或
jupyter lab
```

浏览器会自动打开,看到的是当前目录的文件浏览器。

### 为什么数据分析爱用它

- 传统写法:改一行代码 → 重新跑全脚本 → 看结果
- Jupyter:每个 cell 独立跑,改一段只跑一段,数据已经加载在内存里不用重新读
- 对处理几 GB 的 DataFrame 太友好了

---

## 🎯 三者关系图(一句话)

> **Anaconda** 一装,你就有了 **conda**(管环境)和 **Jupyter**(写代码),然后你用 conda 装更多库,在 Jupyter 里把它们组合起来玩。

| 工具 | 角色 | iOS 类比 |
|---|---|---|
| Anaconda | 发行版/全家桶 | Xcode 安装包 |
| conda | 包+环境管理工具 | CocoaPods + rbenv |
| Jupyter | 交互式编程界面 | Swift Playground 加强版 |

---

## 💡 实操建议

1. **现在阶段 04(Numpy/Pandas):** 直接在 Jupyter 里跑课程示例,边写边看输出,体感最好。
2. **后面阶段 06+:** 开始为不同方向建独立 conda 环境,避免后期"我装个 deepspeed,torch 版本被升了,前面的代码跑不了了"这种坑。
3. **不用纠结命名:** 看到 `jupyter notebook` / `jupyter lab` 都启动一下试试,你会自然选出喜欢的。

---

## 🔧 一些大概率会撞到的坑(提前知道)

| 现象 | 原因 | 解决 |
|---|---|---|
| 命令行 `conda: command not found` | conda 没加到 PATH | 重启终端,或手动 `source ~/anaconda3/etc/profile.d/conda.sh` |
| Jupyter 里 import 报错 ModuleNotFoundError,但终端里 pip list 明明有 | Jupyter 用的不是你激活的环境 | 在目标 conda 环境里再装一次 `conda install ipykernel`,然后 `python -m ipykernel install --user --name=lora` |
| 装了一堆库后环境变得混乱、跑不通 | 版本冲突 | 不要硬修,直接删环境重建,5 分钟搞定 |
| `conda install` 巨慢 | 默认走国外源 | 换清华源:`conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/` |
| pip 装包巨慢 | 同上 | `pip install xxx -i https://pypi.tuna.tsinghua.edu.cn/simple` |
