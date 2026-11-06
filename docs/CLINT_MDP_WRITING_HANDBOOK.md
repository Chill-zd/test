# Clint 合著 MDP 论文：按段落任务选择的写作手册

本手册从 Chin Pang Ho 合著论文的实际物理段落中提取写法。原句、中文任务解释和带槽位的英文改写分开标示；合著信息不证明某句话由哪位作者执笔。中文说明与英文改写是基于原文的编辑归纳，供选择、再加工或省略，不是统一章节模板。

使用时先确定本段要回答的问题、读者已知对象和前后段的交接，再选择对应卡片。方括号必须用当前稿件已经定义、证明或实测的内容填写；没有依据的比较、保证、因果机制和推广条件应删去。原文中的成本/奖励、极大/极小、策略类及精度条件不能随句式迁移。

每张卡片绑定一个实际段落；某些卡片只讨论该段中的局部任务。段落编号是检索标识，不表示推荐顺序。不同段落的引文从未拼接为一条原文。历史引文与记号在原句中照录；新稿遵循其已有定义及用户指定的引用、加粗规范。

## 导航

| 章节 | 可选择的段落任务 |
|---|---|
| [引言](#introduction) | [开篇定位MDP并引出估计误差敏感性](#introduction-paragraph-01)；[用面向应用的写法引入MDP与参数误差](#introduction-paragraph-02)；[从最坏情形保守性转入分布鲁棒建模](#introduction-paragraph-03)；[回顾矩形性假设并推出局限](#introduction-paragraph-04)；[指出计算瓶颈并铺垫本文贡献](#introduction-paragraph-05)；[先给框架总览，再预告贡献分解](#introduction-paragraph-06) |
| [相关工作](#related_work) | [章首导览:按两条改进思路概括综述范围](#related_work-paragraph-01)；[以应用广度开篇:先交代领域历史与热度](#related_work-paragraph-02)；[由迭代瓶颈引出策略迭代，并限定其代价](#related_work-paragraph-03)；[从集合范围与内层精度比较梯度方法](#related_work-paragraph-04)；[按结构化集合逐类归纳专用算法并突出自身差异](#related_work-paragraph-05)；[类比相关技术:说明相似处再指出差别](#related_work-paragraph-06)；[界定本文范围，再交代模型扩展](#related_work-paragraph-07) |
| [模型设定](#model_setup) | [MDP基本要素的元组式开篇定义](#model_setup-paragraph-01)；[有限空间与无损假设的叙述式设定](#model_setup-paragraph-02)；[在模型定义中解释成本归一化](#model_setup-paragraph-03)；[随机策略的定义与策略集记号](#model_setup-paragraph-04)；[由策略与转移核诱导过程并写出目标函数](#model_setup-paragraph-05)；[以目标句引出分布鲁棒优化，并解释策略变量](#model_setup-paragraph-06)；[现有方法的局限并引出矩形性假设](#model_setup-paragraph-07) |
| [预备知识](#preliminaries) | [有限MDP设定与初始/转移概率的开篇](#preliminaries-paragraph-01)；[奖励设定与WLOG假设](#preliminaries-paragraph-02)；[策略与鲁棒目标的引入](#preliminaries-paragraph-03)；[以NP难为由引入矩形ambiguity set](#preliminaries-paragraph-04)；[定义具体的ambiguity set及其特例](#preliminaries-paragraph-05)；[分布鲁棒MDP的元组定义与数据驱动模型](#preliminaries-paragraph-06)；[说明模型是已有模型的推广](#preliminaries-paragraph-07) |
| [理论结果与解释](#theory) | [方法引入段:说明参数化LP为何适合同伦法](#theory-paragraph-01)；[例子前导段:先说明现象再引出示例](#theory-paragraph-02)；[命题后解读段:按基的类别说明角色](#theory-paragraph-03)；[复杂度小节开头:朴素实现与改进动机](#theory-paragraph-04)；[核心观察段:定义支配并说明可剔除](#theory-paragraph-05)；[证明后收束段:处理并列情形并引出算法](#theory-paragraph-06)；[结果讨论段:与已有工作比较](#theory-paragraph-07) |
| [算法](#algorithm) | [算法描述段：从初始点出发逐基追踪，并交代可行性条件与数值处理](#algorithm-clean-2006-09484v1-1)；[反证法证明段：由上界与选择规则的矛盾推出输出等于真值函数](#algorithm-clean-2006-09484v1-2)；[为非精确子问题定义“δ-精度”并说明为何不求精确解](#algorithm-clean-2205-14202v1-1)；[定义外层迭代的ε-精度并解释为何只求近似](#algorithm-clean-2205-14202v1-2)；[解释定理的归约意义并把计算量与非鲁棒基准对比](#algorithm-clean-2205-14202v1-3)；[章节开篇:先点出代价缺口,再给分解思路与复杂度预告](#algorithm-clean-yu2023wasserstein-1)；[小节开头:汇总各情形总复杂度并与现有方法对比,附证明去向](#algorithm-clean-yu2023wasserstein-2) |
| [数值实验](#experiments) | [实验节开篇:交代对比对象与运行环境](#experiments-paragraph-01)；[实验总览:说明数据类型各自的作用](#experiments-paragraph-02)；[实验设置:合成实例的随机生成流程](#experiments-paragraph-03)；[用两个基准问题的结构差异解释测试价值](#experiments-paragraph-04)；[修改不确定集后，给出具体参数化选择](#experiments-paragraph-05)；[解释Bellman层面加速小于投影子问题的原因](#experiments-paragraph-06)；[从误差曲线及其包络读取收敛趋势](#experiments-paragraph-07) |
| [结论与局部结果收束](#conclusion) | [结论开篇:逐项回顾所提算法及其复杂度](#conclusion-paragraph-01)；[短结论:概述研究对象、贡献与展望](#conclusion-paragraph-02)；[未来工作:分点列出可改进和可推广方向](#conclusion-paragraph-03)；[实验节末：由已测加速收束为规模趋势](#conclusion-paragraph-04)；[结果讨论：解释性能差异并限定比较范围](#conclusion-paragraph-05) |

## 实际来源

| 论文 | 合著作者与署名位置 |
|---|---|
| Partial Policy Iteration for L1-Robust Markov Decision Processes | Chin Pang Ho, Marek Petrik, Wolfram Wiesemann；[原始署名](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:78) |
| Policy Gradient for Robust Markov Decision Processes | Qiuhao Wang, Shaohang Xu, Chin Pang Ho, Marek Petrik；[原始署名](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2410.22114v2/main.tex:65) |
| Fast Bellman Updates for Wasserstein Distributionally Robust MDPs | Zhuodong Yu, Ling Dai, Shaohang Xu, Siyang Gao, Chin Pang Ho；[原始署名](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/yu2023wasserstein/dr_MDP.tex:96) |
| Robust phi-Divergence MDPs | Chin Pang Ho, Marek Petrik, Wolfram Wiesemann；[原始署名](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:58) |
| Efficient Algorithms for Robust Markov Decision Processes with s-Rectangular Ambiguity Sets | Chin Pang Ho, Marek Petrik, Wolfram Wiesemann；[原始署名](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2602.05591v1/main.tex:44) |

<a id="introduction"></a>
## 引言

面向尚未认识模型风险的读者，可比较“标准模型→估计误差→鲁棒模型”和“应用数据→参数误差→策略后果”两种开篇。模型动机已明确时，改从重复求解子问题的计算代价切入。框架总览承担另一任务：先交代适用对象与收益，再分解贡献。

<a id="introduction-paragraph-01"></a>
### 开篇定位MDP并引出估计误差敏感性

**何时选择。** 引言第一段，需要从MDP的价值转到参数不确定带来的风险，并自然引出鲁棒MDP

**原段怎样推进。** 先称MDP是动态不确定决策的通用建模工具；再转折指出解对转移概率和奖励估计误差敏感；再强调强化学习中模型由数据拟合，不确定性天然存在；最后引出RMDP及ambiguity set，并说明合适的集合能降低敏感性

**句间连接。** 第一句的对象是MDP；第二句用Unfortunately, however把MDP的解作为新对象，补上估计误差这一缺陷；第三句借“估计误差”落到强化学习场景；第四句再借“不确定的转移概率”引出RMDP，用允许取值范围替代精确已知

**向后交接。** 以“合适的ambiguity set使解对模型误差不敏感”收尾，下一段可转入rectangularity等具体集合结构

**何时省略或拆开。** 读者很熟悉RMDP，或论文不涉及强化学习，可只保留MDP→敏感性→RMDP三步

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 103 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:103)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:3628`。

原句 1（连续原文；保留原始记号）：

> MDP solutions can be very sensitive to estimation errors in the transition probabilities and rewards

英文改写 1（带槽位的编辑示例，不是引文）：

`[The model solutions] can be sensitive to [the documented source of estimation error].`

原句 2（连续原文；保留原始记号）：

> do not assume that the transition probabilities are known precisely but instead allow them to take on any value

英文改写 2（带槽位的编辑示例，不是引文）：

`[The model] does not assume that [the uncertain parameters] are known precisely but instead allows them to [the specified admissible variation].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="introduction-paragraph-02"></a>
### 用面向应用的写法引入MDP与参数误差

**何时选择。** 目标读者来自决策、金融、医疗或学习领域，需要先给出应用背景再说明鲁棒化动机

**原段怎样推进。** 先说MDP是动态决策与强化学习的基础模型；再指出经典模型假设参数精确已知；再举金融、医疗等应用中参数来自有噪声的有限数据；最后说明估计误差使策略在实践中表现差，并引出RMDP及其worst-case思想

**句间连接。** 从“MDP作为基础模型”过渡到“经典假设参数已知”，再用However转入现实应用，新增数据噪声和策略表现差这一后果，最后由“估计误差”引入RMDP

**向后交接。** 以RMDP在最坏可能转移概率下求最优策略收尾，引向后续对MDP的比较或矩形性假设

**何时省略或拆开。** 论文只面向纯算法读者，可省略应用举例

**实际出处。** [Policy Gradient for Robust Markov Decision Processes，第 98 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2410.22114v2/main.tex:98)；原文段落标识 `arxiv_2410.22114v2:verified-paragraph:3926`。

原句 1（连续原文；保留原始记号）：

> model parameters are estimated from noisy and limited observation data, and these estimation errors may lead to policies that perform poorly in practice

英文改写 1（带槽位的编辑示例，不是引文）：

`[The parameters] are estimated from [the available data], and these estimation errors may lead to [the documented consequence].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="introduction-paragraph-03"></a>
### 从最坏情形保守性转入分布鲁棒建模

**何时选择。** 已说明转移核不确定，需要从最坏情形保护的局限转入采用分布信息的建模动机。

**原段怎样推进。** 先承接转移核不确定性；说明最坏情形的保护作用；再指出它忽略发生可能性；最后引出利用分布信息的模型。

**句间连接。** ambiguous transition kernels→worst-case protection→忽略likelihood的保守性→distributional information

**向后交接。** 下一段可讨论该分布鲁棒模型的集合或计算问题；本段尚未指定Wasserstein集合。

**何时省略或拆开。** 本文未采用分布鲁棒模型，或并未核实该保守性机制时，不套用这条转折。

**实际出处。** [Fast Bellman Updates for Wasserstein Distributionally Robust MDPs，第 146 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/yu2023wasserstein/dr_MDP.tex:146)；原文段落标识 `yu2023wasserstein:verified-paragraph:6317`。

原句 1（连续原文；保留原始记号）：

> robust MDPs are often too conservative because they always adopt the worst possible transition kernels

英文改写 1（带槽位的编辑示例，不是引文）：

`[The baseline] can [the effect documented in this manuscript] because [the identified mechanism].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="introduction-paragraph-04"></a>
### 回顾矩形性假设并推出局限

**何时选择。** 需要交代主流文献的结构假设、其带来的计算好处，以及这些假设仍显局限的原因

**原段怎样推进。** 先说明文献常用的矩形性假设及其状态间独立含义；再指出动态规划可用而一般集合难解；随后从(s,a)-矩形的保守性转入s-矩形，并交代其他扩展及大规模建模中的限制。

**句间连接。** 以“矩形集合”为旧对象，先补充它保留了哪些性质，再对比一般集合的NP-hard，最后用However或such...can be still指出矩形集合在建模上的不足，形成问题缺口

**向后交接。** 以“矩形集合仍然受限”收尾，转到更一般方案或下一类方法的引入

**何时省略或拆开。** 论文只处理一般非矩形设置，且无需交代这段背景时可压缩为对比句

**实际出处。** [Policy Gradient for Robust Markov Decision Processes，第 100 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2410.22114v2/main.tex:100)；原文段落标识 `arxiv_2410.22114v2:verified-paragraph:5352`。

原句 1（连续原文；保留原始记号）：

> This assumption is crucial for RMDPs to maintain traceability, ensuring that an optimal policy

英文改写 1（带槽位的编辑示例，不是引文）：

`This assumption ensures that [the stated computational property holds under the specified conditions].`

原句 2（连续原文；保留原始记号）：

> such rectangular ambiguity sets can be still quite restrictive in modeling ambiguity

英文改写 2（带槽位的编辑示例，不是引文）：

`Such [assumptions] can be restrictive when [the identified modeling limitation arises].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="introduction-paragraph-05"></a>
### 指出计算瓶颈并铺垫本文贡献

**何时选择。** 已介绍鲁棒模型，需要说明求解昂贵，并引出本文新的高效算法

**原段怎样推进。** 先指出集合具有可构造性和多面体结构，可通过线性规划算最坏转移；再用Unfortunately说明每个状态、每步迭代都要解LP；再给出通用LP复杂度；再说明大规模时过于昂贵

**句间连接。** 以“L1集合可计算最坏概率”为旧信息，下一句新增“每次迭代都需求解LP”的计算负担，最后用复杂度近似四次方把负担量化

**向后交接。** 以“对多状态RMDP不可行”收尾，下一段直接用In this paper提出新框架

**何时省略或拆开。** 若论文不比较计算复杂度，可略去具体复杂度句

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 109 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:109)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:5324`。

原句 1（连续原文；保留原始记号）：

> an LP has to be solved for each state and each step of the value or policy iteration

英文改写 1（带槽位的编辑示例，不是引文）：

`[The subproblem] has to be solved for each [unit of the outer computation].`

原句 2（连续原文；保留原始记号）：

> they thus become prohibitively expensive for RMDPs with many states

英文改写 2（带槽位的编辑示例，不是引文）：

`They thus become [the documented computational limitation] for [the relevant problem sizes].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="introduction-paragraph-06"></a>
### 先给框架总览，再预告贡献分解

**何时选择。** 需要在逐项贡献之前说明新框架处理什么、收益来自哪里以及后文如何展开。

**原段怎样推进。** 先提出框架；说明它适用的两种矩形集合及nature的信息差异；再从迭代次数和每次迭代代价解释加速来源；最后预告三个组成部分。

**句间连接。** 框架→适用集合→加速的两个来源→组成部分

**向后交接。** 下一段才逐项展开贡献，不能把尚未出现的贡献细节塞进这一总览。

**何时省略或拆开。** 没有多组成框架时不预告固定数量的组件；不在总览中加入尚未支持的保证。

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 111 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:111)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:6167`。

原句 1（连续原文；保留原始记号）：

> Our framework comprises of three components, each of which represents a novel contribution

英文改写 1（带槽位的编辑示例，不是引文）：

`Our framework comprises [the actual number of components], each of which [its established role in the contribution].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。


<a id="related_work"></a>
## 相关工作

章首可以用计算任务给文献分类，也可以用历史与应用说明研究热度。进入具体工作后，再按集合结构归类，或沿某一明确比较维度逐项对照。这些路径解决不同读者问题，不应机械串成一段。

<a id="related_work-paragraph-01"></a>
### 章首导览:按两条改进思路概括综述范围

**何时选择。** Related Work开头,需要先告诉读者后文按什么维度组织文献时

**原段怎样推进。** 先用一句话说明综述两类工作(减少迭代次数、降低单次迭代复杂度),再补一句说明还会涉及相关机器学习问题,随后进入第一类方法

**句间连接。** 开头没有借前文对象,直接把论文要解决的算法瓶颈拆成(i)(ii)两个维度;第二句在此基础上新增“相关机器学习问题”这一旁支

**向后交接。** 以“We also survey…”收束,下一段即从标准方法(鲁棒价值迭代)讲起,与(i)对应

**何时省略或拆开。** 综述很短、无需分维度组织时

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 132 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:132)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:11829`。

原句 1（连续原文；保留原始记号）：

> We review relevant prior work that aims at (i) reducing the number of iterations needed

英文改写 1（带槽位的编辑示例，不是引文）：

`We review relevant prior work that aims at (i) [the first improvement] and (ii) [the second improvement].`

原句 2（连续原文；保留原始记号）：

> We also survey algorithms for related machine learning problems.

英文改写 2（带槽位的编辑示例，不是引文）：

`We also survey algorithms for [the related problem class].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="related_work-paragraph-02"></a>
### 以应用广度开篇:先交代领域历史与热度

**何时选择。** 需要论证研究对象重要、再引入具体算法文献时

**原段怎样推进。** 先说明该模型自上世纪七十年代就被研究,再用“近年兴趣激增”转折,随后长列举应用领域及引用

**句间连接。** “While…since the seventies”借历史起点,下一分句新增“近期热度+应用清单”,用一长串并列领域承载引用

**向后交接。** 以最后一个应用(近似误差稳健化)结束,下一段转入具体算法实现

**何时省略或拆开。** 篇幅受限或应用动机已在引言充分说明

**实际出处。** [Robust phi-Divergence MDPs，第 114 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:114)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:13179`。

原句 1（连续原文；保留原始记号）：

> While RMDPs have been studied since the seventies

英文改写 1（带槽位的编辑示例，不是引文）：

`While [the topic] has been studied since [the documented period], [the subsequent development].`

原句 2（连续原文；保留原始记号）：

> they have witnessed significant recent interest due to their widespread adoption in applications ranging from

英文改写 2（带槽位的编辑示例，不是引文）：

`[The topic] has witnessed recent interest due to [the documented applications].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="related_work-paragraph-03"></a>
### 由迭代瓶颈引出策略迭代，并限定其代价

**何时选择。** 介绍基线算法并自然引出其改进版本时

**原段怎样推进。** 先指出鲁棒值迭代在折扣因子接近1时需多次迭代；用To alleviate this issue引入策略迭代并解释其交替步骤；最后限定理论速率、实践表现和每次策略评估的大LP代价。

**句间连接。** robust value iteration的代价→policy iteration作为回应→新方法自身的规模限制

**向后交接。** 后文可转入避免这两种代价的方法；本段不承担标准值迭代的完整定义。

**何时省略或拆开。** 读者熟悉基线算法时,可只保留局限与改进两句

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 136 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:136)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:12590`。

原句 1（连续原文；保留原始记号）：

> Unfortunately, robust value iteration requires many iterations and thus performs poorly when

英文改写 1（带槽位的编辑示例，不是引文）：

`[The baseline method] requires [the costly operation] and thus [the documented limitation] when [the relevant condition holds].`

原句 2（连续原文；保留原始记号）：

> To alleviate this issue, \emph{robust policy iteration} alternates between

英文改写 2（带槽位的编辑示例，不是引文）：

`To alleviate this issue, [the alternative method] alternates between [its two actual operations].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="related_work-paragraph-04"></a>
### 从集合范围与内层精度比较梯度方法

**何时选择。** 需沿集合范围、收敛保证或内层求解精度比较相近梯度方法，且已核实各项比较条件。

**原段怎样推进。** 先介绍已有梯度方法并限定其集合范围；再说明本文外层更新与相关方法的关系；随后比较矩形类别、全局收敛和内层容差要求；最后交代相邻actor-critic方法。

**句间连接。** 已有梯度方法→集合范围→与本文更新的关系→保证与内层计算的具体比较

**向后交接。** 比较须保留各方法的集合类别和精度条件；本段没有把所有已有方法归为确定性策略。

**何时省略或拆开。** 缺少直接可比的前作或尚未核实其适用条件时，保留准确介绍，省略优势对比。

**实际出处。** [Policy Gradient for Robust Markov Decision Processes，第 127 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2410.22114v2/main.tex:127)；原文段落标识 `arxiv_2410.22114v2:verified-paragraph:16599`。

原句 1（连续原文；保留原始记号）：

> While this algorithm is compellingly simple, it is limited to the R-contamination set

英文改写 1（带槽位的编辑示例，不是引文）：

`While this algorithm is [its documented strength], it is limited to [its stated scope].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="related_work-paragraph-05"></a>
### 按结构化集合逐类归纳专用算法并突出自身差异

**何时选择。** 综述针对特定歧义集的快速算法,并想强调本文覆盖更广

**原段怎样推进。** 先说明一般情形只能多项式求解、不够快;再列举无权L1的拟线性算法;随后用“In contrast”说明本文同时适用加权版本;再罗列L∞、L2、KL等;最后说明s-矩形集尚无专用算法及原因

**句间连接。** 借“Bellman算子评估”这一对象,依次新增不同范数的已有算法,再转折到本文的加权扩展与s-矩形空白

**向后交接。** 以“not possible to compute the worst transition probabilities independently”说明难点收尾

**何时省略或拆开。** 没有可比的专用算法时

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 142 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:142)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:15585`。

原句 1（连续原文；保留原始记号）：

> Quasi-linear time algorithms for computing Bellman updates for RMDPs with \emph{unweighted} sa-rectangular $L_1$-ambiguity sets have been proposed by

英文改写 1（带槽位的编辑示例，不是引文）：

`[Algorithms with the stated complexity] for [the specified problem class] have been proposed in [the cited studies].`

原句 2（连续原文；保留原始记号）：

> We are not aware of any previous specialized algorithms for s-rectangular ambiguity sets

英文改写 2（带槽位的编辑示例，不是引文）：

`We are not aware of previous [methods of the specified kind] for [the verified scope of the literature search].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="related_work-paragraph-06"></a>
### 类比相关技术:说明相似处再指出差别

**何时选择。** 本文算法与其他领域方法(如LARS、L1球投影、二分法)形似时

**原段怎样推进。** 先用“resembles”指出相似的方法;再补充另一类相似方法;再用“In contrast to those works”说明本文目标函数与可行域的不同

**句间连接。** 借本文算法这一对象,新增相似算法名称,再新增差别(线性vs二次、交集vs整球)

**向后交接。** 以可行域差异收束,下一段接着讲另一技术(二分法)

**何时省略或拆开。** 无明显类比对象

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 144 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:144)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:17181`。

原句 1（连续原文；保留原始记号）：

> Our algorithm for computing the robust Bellman operator over an sa-rectangular ambiguity set resembles LARS

英文改写 1（带槽位的编辑示例，不是引文）：

`Our algorithm for [the stated problem] resembles [the cited related method].`

原句 2（连续原文；保留原始记号）：

> In contrast to those works, our algorithm optimizes a linear function

英文改写 2（带槽位的编辑示例，不是引文）：

`In contrast to those works, our algorithm [the verified difference in objective or feasible set].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="related_work-paragraph-07"></a>
### 界定本文范围，再交代模型扩展

**何时选择。** 收尾时说明本文范围之外但相关的模型

**原段怎样推进。** 先限定本文研究的矩形集合；再列出文献中的其他集合结构与模型扩展。

**句间连接。** 本文对象→文献中超出本文范围的推广

**向后交接。** 用此段说明边界；分布鲁棒研究线需要另有来源的段落承接。

**何时省略或拆开。** 相邻方向与本文关系不大时

**实际出处。** [Robust phi-Divergence MDPs，第 122 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:122)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:17659`。

原句 1（连续原文；保留原始记号）：

> While this paper exclusively studies $s$-rectangular uncertainty sets, alternative generalizations

英文改写 1（带槽位的编辑示例，不是引文）：

`While this paper studies [its actual scope], alternative generalizations [the cited extensions and their relation].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。


<a id="model_setup"></a>
## 模型设定

同样是建立模型，一种实测写法先列元组再解释分量；另一种从状态、动作、时域与随机转移逐步展开。成本归一化是设定段内的论证任务；策略定义、目标陈述则需要各自明确的对象与记号。

<a id="model_setup-paragraph-01"></a>
### MDP基本要素的元组式开篇定义

**何时选择。** 在模型设定起始处，需要一次性交代状态集、动作集、转移、成本和初始分布，读者熟悉MDP但需要对齐符号

**原段怎样推进。** 先给出元组并说明各分量；接着定义有限状态/动作集；再引入转移分布及其汇总成的核；然后给出转移成本；最后交代初始状态分布

**句间连接。** 第一句的元组里的 p、c、ρ 是被后文逐个展开的对象：转移句取元组里的 p，成本句取 c，末句取 ρ，每句只新增一个分量的含义和取值空间

**向后交接。** 以初始分布收尾，下一段自然进入策略的定义

**何时省略或拆开。** 若上文已给出MDP元组，或论文只讨论已定义好的鲁棒模型

**实际出处。** [Policy Gradient for Robust Markov Decision Processes，第 141 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2410.22114v2/main.tex:141)；原文段落标识 `arxiv_2410.22114v2:verified-paragraph:20766`。

原句 1（连续原文；保留原始记号）：

> A nominal MDP is specified by a tuple $\langle\mathcal{S},\mathcal{A},\bm{p},\bm{c}, \bm{\rho}\rangle$, where

英文改写 1（带槽位的编辑示例，不是引文）：

`A [model] is specified by a tuple [the model components], where [the definitions of those components].`

原句 2（连续原文；保留原始记号）：

> The initial state is selected randomly according to the initial state distribution

英文改写 2（带槽位的编辑示例，不是引文）：

`The initial state is selected according to [the specified initial distribution].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="model_setup-paragraph-02"></a>
### 有限空间与无损假设的叙述式设定

**何时选择。** 希望用散文式逐句铺陈设定，并顺带声明无损一般性的简化假设（如动作处处可行、奖励非负）

**原段怎样推进。** 先说明研究对象及有限状态/动作空间；再声明时域设定；接着用 without loss of generality 排除边角情形；然后交代初始状态与转移随机性

**句间连接。** 首句确立 S 和 A，后续句子都借用这两个集合：无损假设借 A 与 S 说明动作可行性，转移句借 s、a 引入 p_sa，每句新增一个设定或简化

**向后交接。** 以不确定集的声明收尾，把读者引向奖励与策略

**何时省略或拆开。** 若不需要任何简化假设，或写作篇幅受限

**实际出处。** [Robust phi-Divergence MDPs，第 128 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:128)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:18844`。

原句 1（连续原文；保留原始记号）：

> We assume an infinite planning horizon, but all of our results immediately extend to a finite time horizon.

英文改写 1（带槽位的编辑示例，不是引文）：

`We assume [the analyzed horizon]; [any justified extension is stated separately].`

原句 2（连续原文；保留原始记号）：

> Without loss of generality, we assume that every action $a \in \mathcal{A}$ is admissible in every state $s \in \mathcal{S}$.

英文改写 2（带槽位的编辑示例，不是引文）：

`Without loss of generality, we assume [the condition whose equivalence has been justified].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="model_setup-paragraph-03"></a>
### 在模型定义中解释成本归一化

**何时选择。** 需要限定成本或奖励取值范围时：读者是偏理论的审稿人则用引用文献给出理由；读者偏应用则只声明非负

**原段怎样推进。** 先明确成本的取值区间；紧接着说明平移和正比例缩放不改变最优策略；随后回到初始分布。

**句间连接。** 成本定义→取值约定→为何不影响最优策略→继续模型设定

**向后交接。** 此处是同一设定段中的局部论证；若归一化不保留研究对象或约束，应另行论证。

**何时省略或拆开。** 取值范围不影响后文结论且读者不关心

**实际出处。** [Policy Gradient for Robust Markov Decision Processes，第 141 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2410.22114v2/main.tex:141)；原文段落标识 `arxiv_2410.22114v2:verified-paragraph:20766`。

原句 1（连续原文；保留原始记号）：

> This is without loss of generality because translating the costs by a constant or multiplying them by a positive scalar does not change the set of optimal policies

英文改写 1（带槽位的编辑示例，不是引文）：

`This is without loss of generality because [the specified transformation] does not change [the relevant solution set].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="model_setup-paragraph-04"></a>
### 随机策略的定义与策略集记号

**何时选择。** MDP要素给出后，需要定义平稳随机策略及其集合

**原段怎样推进。** 先给出策略记号和其逐状态的分布；再用 prescribes 句式说明在状态 s 下以概率 π_sa 选动作；最后用 We use … to denote 引入所有策略的集合

**句间连接。** 借用前文的 S、A 和单纯形记号，新增策略 π 及其分量含义，再新增集合 Π

**向后交接。** 以 Π 收尾，引向给定策略后的随机过程或回报定义

**何时省略或拆开。** 若策略已在前文定义过

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 156 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:156)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:19921`。

原句 1（连续原文；保留原始记号）：

> is a function that prescribes to take an action $a \in \actions$ with the probability $\pi_{s,a}$ whenever the MDP is in a state

英文改写 1（带槽位的编辑示例，不是引文）：

`[The policy] prescribes [the specified action choice] whenever [the relevant state is reached].`

原句 2（连续原文；保留原始记号）：

> We use $\Pi = (\Delta^A)^S$ to denote the set of all randomized stationary policies.

英文改写 2（带槽位的编辑示例，不是引文）：

`We use [the notation] to denote [the explicitly defined policy class].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="model_setup-paragraph-05"></a>
### 由策略与转移核诱导过程并写出目标函数

**何时选择。** 需要把策略选择与随机转移落实为随机过程、期望和鲁棒优化目标。

**原段怎样推进。** 先定义平稳随机策略及其选择动作的概率；再由策略和转移概率引入随机过程与期望；最后把风险偏好落实为折扣最坏期望回报的最大最小目标。

**句间连接。** 借前文的 p∈P 与 π∈Π，先新增随机过程，再新增期望记号，再新增目标式，最后补存在性

**向后交接。** 下一段再论述目标或极值的数学性质；本物理段落尚未给出极值存在的论证。

**何时省略或拆开。** 若这些对象和目标已经明确定义，直接引用前述定义；不要为强调存在性而重复本段。

**实际出处。** [Robust phi-Divergence MDPs，第 132 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:132)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:20454`。

原句 1（连续原文；保留原始记号）：

> The decision maker is risk-neutral but ambiguity-averse and wishes to maximize the worst-case expected total reward under a discount factor

英文改写 1（带槽位的编辑示例，不是引文）：

`The decision maker [the stated preference over uncertainty] and wishes to [the manuscript objective] under [the specified discounting convention].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="model_setup-paragraph-06"></a>
### 以目标句引出分布鲁棒优化，并解释策略变量

**何时选择。** 分布与集合已在前文定义，需要陈述分布鲁棒目标并解释策略变量的含义。

**原段怎样推进。** 先用The goal of陈述最大化最坏期望回报；随后展示目标；最后解释策略向量及逐状态的动作概率。

**句间连接。** 已定义的分布鲁棒模型→目标及优化式→策略分量的操作解释

**向后交接。** 分布与集合的设定来自前文，不应当作本段首次给出的定义。

**何时省略或拆开。** 若当前问题使用另一目标或策略类，应保留自己的对象，仅参考目标句与变量解释的衔接。

**实际出处。** [Fast Bellman Updates for Wasserstein Distributionally Robust MDPs，第 222 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/yu2023wasserstein/dr_MDP.tex:222)；原文段落标识 `yu2023wasserstein:verified-paragraph:26282`。

原句 1（连续原文；保留原始记号）：

> The goal of a distributionally robust MDP is to maximize the worst-case expected return; that is,

英文改写 1（带槽位的编辑示例，不是引文）：

`The goal of [the model] is to [the stated objective]; that is, [the corresponding optimization problem].`

原句 2（连续原文；保留原始记号）：

> the decision variable $\bm{\pi}\in\left( \Delta_A \right)^S$ is called a (randomized) policy where

英文改写 2（带槽位的编辑示例，不是引文）：

`The decision variable [the symbol] is called [the defined object], where [the interpretation of its components].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="model_setup-paragraph-07"></a>
### 现有方法的局限并引出矩形性假设

**何时选择。** 在鲁棒设定中先概述已有算法，再指出它们依赖的结构假设，借此引出自己的处理方式

**原段怎样推进。** 先列举标准方法并概括其共同做法；再指出它们常假设矩形；然后解释矩形的含义；下一段给出具体类别

**句间连接。** 借已有方法的概括，新增它们共同的结构假设，再新增对该假设的解释

**向后交接。** 以矩形解释收尾，转入两类常见不确定集的具体定义

**何时省略或拆开。** 若论文不涉及矩形性或不需要文献综述式铺垫

**实际出处。** [Policy Gradient for Robust Markov Decision Processes，第 214 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2410.22114v2/main.tex:214)；原文段落标识 `arxiv_2410.22114v2:verified-paragraph:30519`。

原句 1（连续原文；保留原始记号）：

> focus on estimating the robust values of policies and selecting policies based on these estimates.

英文改写 1（带槽位的编辑示例，不是引文）：

`[The methods] focus on [the shared computational task].`

原句 2（连续原文；保留原始记号）：

> These method often assume the that the RMDP is rectangular

英文改写 2（带槽位的编辑示例，不是引文）：

`These methods assume that [the stated structural condition holds].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。


<a id="preliminaries"></a>
## 预备知识

可先给模型与记号，也可在已有模型之后以计算困难引入矩形结构。具体集合宜按“定义式→符号含义→直观解释→特例”展开；推广关系宜另用“特定选择→等价模型”解释，不能只说更一般。

<a id="preliminaries-paragraph-01"></a>
### 有限MDP设定与初始/转移概率的开篇

**何时选择。** Preliminaries开头，需要一次性交代状态空间、动作空间、规划期和未知转移概率的ambiguity set

**原段怎样推进。** 先给出有限状态与动作空间；再声明无穷规划期并说明可推广；再用WLOG约定动作可行性；然后引入初始分布；再给转移概率；最后说明转移概率只知属于非空紧ambiguity set。

**句间连接。** 每句只在上一句已定义的对象上加一个要素：先有S和A，再有s、a下的转移分布p_sa，再把p_sa压缩成张量p，最后给p加上ambiguity set约束。

**向后交接。** 以“转移概率只知道位于ambiguity set中”收束，下一段转入奖励的定义。

**何时省略或拆开。** 若模型设定已在引言或前文完整给出，则略去。

**实际出处。** [Robust phi-Divergence MDPs，第 128 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:128)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:18844`。

原句 1（连续原文；保留原始记号）：

> We study RMDPs with a finite state space $\mathcal{S} = \{ 1, \ldots, S \}$

英文改写 1（带槽位的编辑示例，不是引文）：

`We study [the model] with [the stated state and action spaces].`

原句 2（连续原文；保留原始记号）：

> We condense the transition probabilities $\bm{p}_{sa}$ to the tensor

英文改写 2（带槽位的编辑示例，不是引文）：

`We condense [the indexed quantities] into [the defined aggregate object].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="preliminaries-paragraph-02"></a>
### 奖励设定与WLOG假设

**何时选择。** 转移结构已交代，需补充奖励并说明不失一般性的约定

**原段怎样推进。** 先说明转移发生时获得的期望奖励；再类比转移概率，把奖励合并成张量；最后用WLOG声明奖励非负。

**句间连接。** 借前一段的转移概率张量做类比，新增奖励张量及其取值范围。

**向后交接。** 以非负奖励假设结束，之后引入策略集合。

**何时省略或拆开。** 奖励设定无需单独说明时合并进上一段。

**实际出处。** [Robust phi-Divergence MDPs，第 130 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:130)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:20062`。

原句 1（连续原文；保留原始记号）：

> As with the transition probabilities, we condense these rewards to the tensor

英文改写 1（带槽位的编辑示例，不是引文）：

`As with [the previously introduced quantities], we condense [the new quantities] into [the defined object].`

原句 2（连续原文；保留原始记号）：

> Without loss of generality, we assume that all rewards are non-negative.

英文改写 2（带槽位的编辑示例，不是引文）：

`Without loss of generality, we assume [the justified normalization].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="preliminaries-paragraph-03"></a>
### 策略与鲁棒目标的引入

**何时选择。** 设定完整后，要给出策略类、诱导过程和max-min目标

**原段怎样推进。** 先定义平稳随机策略及其选择动作的概率；再由策略和转移概率引入随机过程与期望；最后把风险偏好落实为折扣最坏期望回报的最大最小目标。

**句间连接。** 以前文的p与ambiguity set为基础，新增策略π，二者共同诱导期望，再得到鲁棒目标。

**向后交接。** 下一段再论述目标或极值的数学性质；本物理段落尚未给出极值存在的论证。

**何时省略或拆开。** 若只需简要陈述目标，可省略过程与存在性说明。

**实际出处。** [Robust phi-Divergence MDPs，第 132 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:132)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:20454`。

原句 1（连续原文；保留原始记号）：

> The decision maker is risk-neutral but ambiguity-averse and wishes to maximize the worst-case expected total reward

英文改写 1（带槽位的编辑示例，不是引文）：

`The decision maker [the specified attitude toward uncertainty] and wishes to [the manuscript objective].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="preliminaries-paragraph-04"></a>
### 以NP难为由引入矩形ambiguity set

**何时选择。** 需要论证为何限制ambiguity set的结构

**原段怎样推进。** 先指出一般ambiguity set下内层最小化NP难；再说明因此研究集中在矩形集；再给出s-矩形的形式定义；最后与(s,a)-矩形比较，说明其保守性较低，并提及最优策略可能随机。

**句间连接。** 从前面的鲁棒目标出发，用NP难引出限制，再逐步细化到s-矩形及其优劣。

**向后交接。** 以s-矩形的性质（最优策略可随机化）收束，引向后续算法或具体集合。

**何时省略或拆开。** 若ambiguity set已被限定，无需再论证。

**实际出处。** [Robust phi-Divergence MDPs，第 139 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:139)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:21801`。

原句 1（连续原文；保留原始记号）：

> evaluating the inner minimization in~\eqref{eq:robust_mdp} is NP-hard even if the policy

英文改写 1（带槽位的编辑示例，不是引文）：

`Evaluating [the specified subproblem] is [the established complexity result] even if [the stated restriction holds].`

原句 2（连续原文；保留原始记号）：

> This limits the conservatism of the resulting RMDP

英文改写 2（带槽位的编辑示例，不是引文）：

`This [the documented consequence] for [the stated model or policy class].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="preliminaries-paragraph-05"></a>
### 定义具体的ambiguity set及其特例

**何时选择。** 需要给出本文研究的ambiguity set，并说明其覆盖的已有集合

**原段怎样推进。** 先宣布研究的新类别并给出公式；再逐一解释预算和距离函数；再直观解释该距离；再说明特例覆盖范围并指向表格；最后指出与已有工作的对应关系。

**句间连接。** 借s-矩形的一般形式，新增具体的距离约束，再逐步解释并连接已有研究。

**向后交接。** 以与已有工作的对应收束，引向后续结果。

**何时省略或拆开。** 若集合已在引言完整定义，则略去。

**实际出处。** [Robust phi-Divergence MDPs，第 157 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:157)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:24519`。

原句 1（连续原文；保留原始记号）：

> We study a new general class of $s$-rectangular ambiguity sets that can be expressed as

英文改写 1（带槽位的编辑示例，不是引文）：

`We study a class of [the specified objects] that can be expressed as [the defining formula].`

原句 2（连续原文；保留原始记号）：

> With an appropriate choice of $\phi$, it generalizes other metrics including

英文改写 2（带槽位的编辑示例，不是引文）：

`With an appropriate choice of [the defining parameter], it includes [the verified special cases].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="preliminaries-paragraph-06"></a>
### 分布鲁棒MDP的元组定义与数据驱动模型

**何时选择。** 读者需要正式的模型元组与不确定性来源

**原段怎样推进。** 先给出模型元组；逐一说明空间和有限性；再说明初始分布和转移；再引入折扣因子；最后说明转移核不确定，由未知分布刻画，并属于由历史数据校准的ambiguity set。

**句间连接。** 元组列出对象，随后逐一解释；最后一句增加分布层面的不确定性，是对前面转移核的升级。

**向后交接。** 以符号约定收束，下一段给出目标函数。

**何时省略或拆开。** 若读者熟悉标准MDP，可只保留分布层新增部分。

**实际出处。** [Fast Bellman Updates for Wasserstein Distributionally Robust MDPs，第 220 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/yu2023wasserstein/dr_MDP.tex:220)；原文段落标识 `yu2023wasserstein:verified-paragraph:24714`。

原句 1（连续原文；保留原始记号）：

> A distributionally robust MDP is a tuple

英文改写 1（带槽位的编辑示例，不是引文）：

`A [model] is a tuple [the defined components].`

原句 2（连续原文；保留原始记号）：

> is assumed to be uncertain, and it is governed by an unknown probability distribution

英文改写 2（带槽位的编辑示例，不是引文）：

`[The parameter] is uncertain and is governed by [the specified distributional model].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="preliminaries-paragraph-07"></a>
### 说明模型是已有模型的推广

**何时选择。** 刚给出新模型，需要说明其与标准或鲁棒MDP的关系

**原段怎样推进。** 先声明该公式推广了两类模型；再说明特定选择下等价于鲁棒MDP；再说明退化为单点集合时等价于标准MDP。

**句间连接。** 以刚给出的问题为对象，通过选择ambiguity set逐步缩小到已知模型。

**向后交接。** 以标准MDP的退化情形结束。

**何时省略或拆开。** 若篇幅有限或读者无需此联系。

**实际出处。** [Fast Bellman Updates for Wasserstein Distributionally Robust MDPs，第 228 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/yu2023wasserstein/dr_MDP.tex:228)；原文段落标识 `yu2023wasserstein:verified-paragraph:26979`。

原句 1（连续原文；保留原始记号）：

> It is worth mentioning that the above formulation

英文改写 1（带槽位的编辑示例，不是引文）：

`The above formulation generalizes [the precisely identified models].`

原句 2（连续原文；保留原始记号）：

> is equivalent to the robust MDP with ambiguity set

英文改写 2（带槽位的编辑示例，不是引文）：

`Under [the stated specialization], it is equivalent to [the identified model].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。


<a id="theory"></a>
## 理论结果与解释

性质尚不直观时，可先解释机制或展示例子，再进入正式结果；结果已经陈述时，可按分类解释其对象角色，或与已有复杂度比较。观察→命名→可剔除结论的短段，与结果→条件→比较的讨论段承担不同任务。

<a id="theory-paragraph-01"></a>
### 方法引入段:说明参数化LP为何适合同伦法

**何时选择。** 需要在理论小节开头论证所选算法(如同伦法)与问题结构天然匹配,并引出后续结构分析

**原段怎样推进。** 先断言该方法在此类问题中尤其方便,并给出依据(最优值与最优解分段仿射,附引用)→再用Indeed解释:每个最优基下解仿射,基不可行处出现断点→指出该论证同时推出目标值也分段仿射→描述算法如何从ξ=0出发沿最优基追踪→最后点明效率关键是基的特殊结构

**句间连接。** 首句借用上文已定义的线性规划与参数函数q(ξ)、p*(ξ),新增“分段仿射”这一性质;Indeed句借“最优基”对象,新增断点的成因;This argument句回指前一句论证,新增q(ξ)的结论;Our句把性质转为算法步骤

**向后交接。** 以“The key to its efficiency is ... which we describe next”收尾,预告下一段将刻画基的结构

**何时省略或拆开。** 读者已熟悉参数LP理论,或算法在别处已完整介绍

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 484 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:484)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:59720`。

原句 1（连续原文；保留原始记号）：

> Indeed, the optimal $\b{p}\opt(\xi)$ is affine in $\xi$ for each optimal basis

英文改写 1（带槽位的编辑示例，不是引文）：

`Indeed, [the solution] is [the established property] for each [the stated regime].`

原句 2（连续原文；保留原始记号）：

> This argument also shows that $q (\xi)$ is piecewise affine.

英文改写 2（带槽位的编辑示例，不是引文）：

`This argument also shows that [the further conclusion justified by the same argument].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="theory-paragraph-02"></a>
### 例子前导段:先说明现象再引出示例

**何时选择。** 在给出形式化刻画(命题)之前,先用直观描述和例子展示解路径的行为

**原段怎样推进。** 先声明“正式刻画之前先展示参数行为”→指出所考察的最优解不一定唯一→概括变化规律(恰有两个分量变化)→用总和为1解释一增一减→命名donor与receiver→预告例子展示路径及非均匀权重带来的复杂性

**句间连接。** 借上文已定义的p_B(ξ)与LP中的最优解p*(ξ),新增“两分量变化”的直观规律,再新增donor/receiver术语

**向后交接。** 以“The examples below illustrate ...”收尾,直接衔接后面的图

**何时省略或拆开。** 没有图示例,或术语已在前文引入

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 508 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:508)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:63639`。

原句 1（连续原文；保留原始记号）：

> Before we formally characterize the properties of the optimal bases for different values of $\xi$, we illustrate

英文改写 1（带槽位的编辑示例，不是引文）：

`Before we formally characterize [the property], we illustrate [the behavior relevant to that characterization].`

原句 2（连续原文；保留原始记号）：

> We say that $p_i$ is a \emph{donor} as it donates some of its probability mass

英文改写 2（带槽位的编辑示例，不是引文）：

`We call [the component] [the term] because [its role in the described mechanism].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="theory-paragraph-03"></a>
### 命题后解读段:按基的类别说明角色

**何时选择。** 命题给出导数公式后,需要向读者解释各情形下的含义

**原段怎样推进。** 先读取第一类基的导数,说明谁是receiver、谁是donor→再以on the other hand转到第二类,说明角色取决于权重大小比较→补充相反情形

**句间连接。** 借命题中的导数p-dot和类别(C1)(C2),新增对角色的解释以及对权重的依赖

**向后交接。** 以反向情形的条件结束,随后进入证明

**何时省略或拆开。** 命题自身已写明角色

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 573 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:573)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:69104`。

原句 1（连续原文；保留原始记号）：

> The derivative $\dot{\bm{p}}$ shows that in a basis of class (C1), $i$ is the receiver and $j$ is the donor.

英文改写 1（带槽位的编辑示例，不是引文）：

`[The derivative or other established quantity] shows that, in [the first case], [the corresponding roles].`

原句 2（连续原文；保留原始记号）：

> an inspection of $\dot{\bm{p}}$ reveals that $i$ is the receiver and $j$ is the donor whenever $w_i > w_j$

英文改写 2（带槽位的编辑示例，不是引文）：

`An inspection of [the same quantity] reveals that [the roles] whenever [the condition for the second case holds].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="theory-paragraph-04"></a>
### 复杂度小节开头:朴素实现与改进动机

**何时选择。** 分析算法复杂度,先给基线,再说明为何需要结构性改进

**原段怎样推进。** 先给朴素实现的复杂度及来源(排序所有索引对)→与通用LP求解器的理论复杂度比较,说明已有改进→指出数值上仅与先进求解器相当→预告本节将描述一个结构性质来大幅加速

**句间连接。** 借前文算法(alg:homotopy),新增复杂度数值及其来源,再新增实验观察作为改进动机

**向后交接。** 以“In this section, we describe ... that allows us to ...”结束,引入下一段的核心观察

**何时省略或拆开。** 没有朴素版本与优化版本的对比

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 708 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:708)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:82979`。

原句 1（连续原文；保留原始记号）：

> A naive implementation of \cref{alg:homotopy} has a computational complexity of

英文改写 1（带槽位的编辑示例，不是引文）：

`A naive implementation of [the algorithm] has computational complexity [the proved bound].`

原句 2（连续原文；保留原始记号）：

> we observed numerically that the naive implementation performs on par with state-of-the-art LP solvers

英文改写 2（带槽位的编辑示例，不是引文）：

`We observed numerically that [the implementation] performs [the measured comparison] on [the tested instances].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="theory-paragraph-05"></a>
### 核心观察段:定义支配并说明可剔除

**何时选择。** 提出提速所依赖的结构性观察,并在命题前给出直观解释和术语

**原段怎样推进。** 先陈述观察:满足某条件的分量不可能成为receiver→用We call命名为dominated→说明这些分量可被剔除而不影响算法正确性

**句间连接。** 借上一段“提速”目标,新增具体的支配条件(目标系数与权重都更小的另一分量),再新增术语与可剔除结论

**向后交接。** 以“不影响正确性”结束,随后给出严格命题

**何时省略或拆开。** 直接给命题而不需要直观说明

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 710 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:710)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:83657`。

原句 1（连续原文；保留原始记号）：

> Our improvement is based on the observation that a component $i \in \mathcal{S}$ cannot be a receiver

英文改写 1（带槽位的编辑示例，不是引文）：

`Our improvement is based on the observation that [the component cannot play the stated role under the specified condition].`

原句 2（连续原文；保留原始记号）：

> We call such components $i$ \emph{dominated}, and any dominated receivers can be eliminated from further consideration

英文改写 2（带槽位的编辑示例，不是引文）：

`We call such components [the term]; [the justified elimination or simplification].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="theory-paragraph-06"></a>
### 证明后收束段:处理并列情形并引出算法

**何时选择。** 命题证明后补充边界情形(并列),再给出构造最小集合的算法

**原段怎样推进。** 先说明并列情形下可任去其一→由此得到算法→说明算法构造最小接收者集合及其时间复杂度

**句间连接。** 借刚证完的支配命题,新增对完全相等情形的补充,再新增算法与O(S log S)复杂度

**向后交接。** 以引入算法环境的“We thus arrive at ...”结束

**何时省略或拆开。** 没有并列情形或算法

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 742 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:742)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:86549`。

原句 1（连续原文；保留原始记号）：

> One readily verifies that if there are two potential receivers $i$ and $j$ satisfying

英文改写 1（带槽位的编辑示例，不是引文）：

`If [the stated tie condition holds], [the justified treatment of the tied objects].`

原句 2（连续原文；保留原始记号）：

> We thus arrive at \cref{alg:non-dominated}, which constructs a minimal set of receivers

英文改写 2（带槽位的编辑示例，不是引文）：

`We thus arrive at [the algorithm], which constructs [the specified object].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="theory-paragraph-07"></a>
### 结果讨论段:与已有工作比较

**何时选择。** 定理给出收敛速率后,讨论其意义并与文献对比

**原段怎样推进。** 先复述定理的复杂度结论→说明在现有文献中的独特性→介绍此前最早的方法及其速率→指出该方法对规模的依赖→In contrast给出本文改进→补充算法与已有方法的关系

**句间连接。** 借定理的结果,新增文献比较对象DRPG及其速率,再新增本文速率改善的原因和特例联系

**向后交接。** 以特例关系结束,下一段继续比较另一相关工作

**何时省略或拆开。** 没有直接可比的已有结果

**实际出处。** [Policy Gradient for Robust Markov Decision Processes，第 449 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2410.22114v2/main.tex:449)；原文段落标识 `arxiv_2410.22114v2:verified-paragraph:59523`。

原句 1（连续原文；保留原始记号）：

> Theorem~\ref{the:sublinear-dir-para} states that achieving an $\epsilon$-optimal robust policy using DRPMD requires iteration complexity of

英文改写 1（带槽位的编辑示例，不是引文）：

`[The theorem] states that achieving [the specified accuracy] requires [the established complexity under its assumptions].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。


<a id="algorithm"></a>
## 算法

算法对象已建立时，可按初始化→更新或追踪→触发条件解释操作。对象尚未建立时，先说明该节解决什么、所需子问题及暂时假设。命名与两层更新、结构化分解、复杂度小结应按实际读者需求选择，不要求每段齐备。

<a id="algorithm-clean-2006-09484v1-1"></a>
### 算法描述段：从初始点出发逐基追踪，并交代可行性条件与数值处理

**何时选择。** 新稿需要在算法伪代码之后用一段文字说明迭代如何推进，初始解已知，后续中间量（基、斜率、断点）逐步产生，并需要交代退化情形的假设与实现中的精度处理。

**原段怎样推进。** 1) 开头用一句话宣布将描述方法并指向算法编号。2) 给出起点：参数初值、对应的已知最优解及目标值。3) 说明推进规则：沿参数增大追踪当前最优基，直到不可行再换下一个基。4) 用凸性解释为何只需考察斜率不小于已追踪者的基。5) 分类列出各类基的结构及其可行的充要/必要条件，并引用前置引理。6) 补充角色判定规则（谁是接收方、谁是捐出方）。7) 为简化叙述加一条一般性假设（斜率两两不同），并说明扰动即可达成。8) 最后一句交代实现中如何处理浮点误差。

**句间连接。** 方法已由前文结构结果支持→给定初值→沿参数追踪→不可行时换基→分类可行性与数值处理

**向后交接。** 读者知道方法如何推进后，才讨论输出范围或证明；没有路径型算法时不套用追踪叙述。

**何时省略或拆开。** 新稿没有逐步追踪的路径型算法，或没有退化/浮点精度需要说明时，省略假设与实现一句，仅保留起点与推进规则。

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 680 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:680)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:77155`。

原句 1（连续原文；保留原始记号）：

> The algorithm starts at $\xi_0 = 0$ with the optimal solution $\bm{p}_0 = \bar{\bm{p}}$ achieving the objective value $q_0 = \bm{p}_0^\top \bm{z}$.

英文改写 1（带槽位的编辑示例，不是引文）：

`The algorithm starts at [the initial parameter] with [the specified initial solution] and objective value [the associated value].`

原句 2（连续原文；保留原始记号）：

> The algorithm subsequently traces each optimal basis as $\xi$ increases, until the basis becomes infeasible and is replaced with the next basis.

英文改写 2（带槽位的编辑示例，不是引文）：

`The algorithm traces [the current object] as [the parameter] increases, until [the stated event] requires [the specified replacement].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="algorithm-clean-2006-09484v1-2"></a>
### 反证法证明段：由上界与选择规则的矛盾推出输出等于真值函数

**何时选择。** 新稿需要证明算法输出与目标函数逐点一致，且已知输出对应可行解（因而是上界），未知的是是否存在被漏掉的更优基。

**原段怎样推进。** 1) 先宣布采用反证法。2) 说明算法每个输出点对应可行解的目标值，所以输出给出上界。3) 假设输出并不逐点等于真值函数。4) 推出必存在某参数值，算法舍弃了斜率严格更小的可行基。5) 指出这与算法选基规则矛盾，收尾。

**句间连接。** 可行输出给出上界→假设严格差距→推出被漏掉的更优可行基→与选基规则矛盾

**向后交接。** 后续正式证明可展开支撑这些步骤的函数或基结构；不要把该算法的可行性结论移给新方法。

**何时省略或拆开。** 若新稿的正确性是直接构造或引用现成定理即可得，无需反证，则省略本段。

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 690 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:690)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:79975`。

原句 1（连续原文；保留原始记号）：

> the output generated by \cref{alg:homotopy} provides an upper bound on $q (\xi)$

英文改写 1（带槽位的编辑示例，不是引文）：

`The output generated by [the algorithm] provides an upper bound on [the target function under the stated feasibility conditions].`

原句 2（连续原文；保留原始记号）：

> there must be a value of $\xi$ at which the homotopy method disregards a feasible basis that has a strictly smaller derivative than the one selected

英文改写 2（带槽位的编辑示例，不是引文）：

`There must then be [a parameter value] at which [the method] disregards [a feasible object satisfying the contradictory comparison].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="algorithm-clean-2205-14202v1-1"></a>
### 为非精确子问题定义“δ-精度”并说明为何不求精确解

**何时选择。** 当某个子问题（如非线性投影）只能近似求解，而后续复杂度定理需要一个明确的精度概念时使用。

**原段怎样推进。** 1) 先点明子问题在该类模型下通常是非线性的，因此不能期望精确最优；2) 用“为应对这一复杂性”过渡，引入精度定义；3) 对给定的输入参数（已知量），说明什么样的输出（区间对）算作δ-精确解：包含真值且宽度不超过δ；4) 此定义直接衔接下一个以“精度δ下耗时h(δ)”为假设的定理。

**句间连接。** 投影问题→不能假定精确求解→定义包住真值的区间及宽度条件

**向后交接。** 后续复杂度结果可以引用这里定义的精度；新问题需要独立说明为何近似求解及采用何种误差。

**何时省略或拆开。** 若子问题本身有闭式或精确算法（如排序后精确求解），或新稿已在别处定义了精度概念，则省略。

**实际出处。** [Robust phi-Divergence MDPs，第 270 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:270)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:37341`。

原句 1（连续原文；保留原始记号）：

> the projection problem~\eqref{eq:gen_projection} is generically nonlinear and can hence not be expected to be solved to exact optimality

英文改写 1（带槽位的编辑示例，不是引文）：

`[The subproblem] is [the identified computational obstacle]; we therefore specify [the required approximation criterion].`

原句 2（连续原文；保留原始记号）：

> is solved to $\delta$-accuracy by any pair $(\underline{d}, \overline{d}) \in \mathbb{R}^2$ satisfying

英文改写 2（带槽位的编辑示例，不是引文）：

`[The problem] is solved to [the stated accuracy] by [an output satisfying the explicit error conditions].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="algorithm-clean-2205-14202v1-2"></a>
### 定义外层迭代的ε-精度并解释为何只求近似

**何时选择。** 当外层迭代算子（如鲁棒Bellman迭代）的精确值可能无法表示，需要给出误差度量与停机标准，并引入便于后续分析的上界常数时使用。

**原段怎样推进。** 1) 以“给定当前估计”引出已知量；2) 定义满足范数误差不超过ε的任一输出为ε-精确解；3) 用“因为”说明追求近似解的原因（集合非线性，精确迭代值即使输入有理也可能无理）；4) 为简化叙述，再引入一个上界常数并说明它界住哪些量；5) 为下一步复杂度分析作铺垫。

**句间连接。** 当前价值估计→以范数误差定义下一次更新精度→说明近似理由→定义辅助上界

**向后交接。** 精度与辅助常数已明确后，再讨论内层求解成本；不能省略误差的对象与范数。

**何时省略或拆开。** 若新稿的算子可精确计算，或误差度量已在前文定义，则省略。

**实际出处。** [Robust phi-Divergence MDPs，第 268 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:268)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:36567`。

原句 1（连续原文；保留原始记号）：

> the robust Bellman iteration~\eqref{eq:rob_value_it} is solved to $\epsilon$-accuracy by any $\bm{v}^{t+1} \in \mathbb{R}^S$ satisfying

英文改写 1（带槽位的编辑示例，不是引文）：

`[The update] is solved to [the stated accuracy] by any [output satisfying the specified error bound].`

原句 2（连续原文；保留原始记号）：

> We seek $\epsilon$-optimal solutions because our ambiguity sets are nonlinear and hence the exact Bellman iterate

英文改写 2（带槽位的编辑示例，不是引文）：

`We seek [the specified approximate solutions] because [the reason established for this problem].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="algorithm-clean-2205-14202v1-3"></a>
### 解释定理的归约意义并把计算量与非鲁棒基准对比

**何时选择。** 当一个复杂度定理把难问题归约为一系列简单子问题，需要说明其意义、预告后续算法并解释计算开销时使用。

**原段怎样推进。** 1) 概述定理把何种复杂的耦合问题归约为何种结构化子问题，并指出耦合已被解除；2) 预告下一节给出这些子问题的高效求解方案；3) 指出各方案的运行时间汇总于表中；4) 给出非鲁棒基准的复杂度，并据此解释本方法仅多出对数级额外开销，作为鲁棒性的代价。

**句间连接。** 复杂度结果→原来动作间的耦合→归约后的独立投影问题→后文算法及与非鲁棒基准的代价比较

**向后交接。** 接下来可展开各投影的求解方法；新增比较须保持该定理的假设和同一计算单位。

**何时省略或拆开。** 若新稿没有归约定理，或没有可比较的非鲁棒基准，则省略比较部分，仅保留归约说明。

**实际出处。** [Robust phi-Divergence MDPs，第 276 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2205.14202v1/main.tex:276)；原文段落标识 `arxiv_2205.14202v1:verified-paragraph:38464`。

原句 1（连续原文；保留原始记号）：

> to a sequence of much simpler and highly structured projection problems that are no longer coupled across different actions

英文改写 1（带槽位的编辑示例，不是引文）：

`[The original problem] reduces to a sequence of [the specified simpler subproblems].`

原句 2（连续原文；保留原始记号）：

> which implies that our algorithms only incur an additional logarithmic overhead to account for robustness in the transition probabilities

英文改写 2（带槽位的编辑示例，不是引文）：

`This implies that [the method] incurs only [the established additional cost relative to the specified baseline].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="algorithm-clean-yu2023wasserstein-1"></a>
### 章节开篇:先点出代价缺口,再给分解思路与复杂度预告

**何时选择。** 新稿某一节要把一个昂贵的核心计算(如鲁棒Bellman更新)拆成小问题,需要在节首说明为何要拆、怎么拆、结果多快、证明放在哪里。

**原段怎样推进。** 1) 先用对比说明通用求解器相对经典情形太贵(给出经典复杂度作参照);2) 说明本节利用问题结构、重构成可分解形式;3) 按情形(q有限/q=∞)预告各小节安排;4) 预告与后续子问题算法结合后得到的总复杂度(对S、A、N的依赖);5) 最后一句交代证明在附录。

**句间连接。** 通用求解器的代价→利用问题结构分解→按模型情形组织后文→复杂度及证明位置

**向后交接。** 节首仅预告方法与结果，具体等价重写和子问题算法由后文给出。

**何时省略或拆开。** 新稿该节无需分解,或没有与基线对比的复杂度结论,或已在引言中交代过路线图时,省略复杂度预告与情形划分。

**实际出处。** [Fast Bellman Updates for Wasserstein Distributionally Robust MDPs，第 266 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/yu2023wasserstein/dr_MDP.tex:266)；原文段落标识 `yu2023wasserstein:verified-paragraph:32548`。

原句 1（连续原文；保留原始记号）：

> we exploit the specific problem structure in \eqref{Bellman_updates} and reformulate the optimization problem to a form that could be decomposed into smaller problems

英文改写 1（带槽位的编辑示例，不是引文）：

`We exploit the structure of [the stated problem] and reformulate it as [the specified equivalent problem].`

原句 2（连续原文；保留原始记号）：

> one can compute $[\mathfrak{T}(\bm{v})]_s$ in time complexity that is quasi-linear in $S$ and linear in $A$ and $N$

英文改写 2（带槽位的编辑示例，不是引文）：

`Under [the result assumptions], [the target quantity] can be computed in [the established complexity].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="algorithm-clean-yu2023wasserstein-2"></a>
### 小节开头:汇总各情形总复杂度并与现有方法对比,附证明去向

**何时选择。** 新稿在转入分情形的子算法前,需要先陈述各情形的总体计算量、与最先进方法的差距,并说明证明和算法细节放在哪里。

**原段怎样推进。** 1) 以'下面将证明'引出各情形的总复杂度,逐情形列出,含精度参数的对数项;2) 紧接着与文献中最先进方法的复杂度作对比,指出低得多;3) 引用对应文献;4) 最后说明命题、定理的证明及算法细节放在附录。

**句间连接。** 前文分解所得复杂度→按不同距离情形汇总→与既有方法比较→证明和算法细节的位置

**向后交接。** 读者已见完整结果后可转入实验或附录；不能把汇总段当作尚未完成的推导。

**何时省略或拆开。** 新稿没有与基线可比的复杂度结论,或各情形结果已在上一段列出,则只保留附录去向一句或全部省略。

**实际出处。** [Fast Bellman Updates for Wasserstein Distributionally Robust MDPs，第 427 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/yu2023wasserstein/dr_MDP.tex:427)；原文段落标识 `yu2023wasserstein:verified-paragraph:50681`。

原句 1（连续原文；保留原始记号）：

> the overall time complexities of our decomposition algorithms are only

英文改写 1（带槽位的编辑示例，不是引文）：

`The overall time complexity of [the method] is [the established bound for each stated case].`

原句 2（连续原文；保留原始记号）：

> The proofs of the following propositions, theorems, and corollaries and the details of the proposed algorithms are relegated to Appendix

英文改写 2（带槽位的编辑示例，不是引文）：

`The proofs of [the stated results] and the algorithmic details are provided in [the actual location].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。


<a id="experiments"></a>
## 数值实验

节首可先说明对比方法及运行环境，也可先说明合成与基准数据分别检验什么。设置段解释如何生成实例；结果段解释测到什么及为何出现差异。后两者的因果链不能互相替代。

<a id="experiments-paragraph-01"></a>
### 实验节开篇:交代对比对象与运行环境

**何时选择。** 实验节第一段,需说明比较哪些算法、对照基线、软硬件与代码获取

**原段怎样推进。** 先用'We now compare...'点明被比较的算法组合及朴素基线;再点名求解器;再说实现语言与并行库;最后给硬件和代码链接

**句间连接。** 首句借前文提出的算法(PPI、同伦法、二分法)作为已知对象,新增'与谁比'(朴素基线+通用LP求解器);后续每句依次新增求解器版本、实现细节、硬件、代码地址

**向后交接。** 以代码仓库链接收尾,下一节转入具体实验设置与测试领域

**何时省略或拆开。** 若环境细节已在附录或后文集中说明则省略硬件句

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 1020 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:1020)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:118317`。

原句 1（连续原文；保留原始记号）：

> We now compare the runtimes of PPI

英文改写 1（带槽位的编辑示例，不是引文）：

`We now compare the runtimes of [the compared methods] on [the stated instances].`

原句 2（连续原文；保留原始记号）：

> All algorithms were implemented in C++, parallelized using the OpenMP library

英文改写 2（带槽位的编辑示例，不是引文）：

`All algorithms were implemented in [the actual language], using [the actual libraries or parallelization].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="experiments-paragraph-02"></a>
### 实验总览:说明数据类型各自的作用

**何时选择。** 需解释为何同时用合成实例与基准实例,并概括对比对象

**原段怎样推进。** 先一句概括研究内容及对比对象(商业求解器与已有方法);再说明实验涵盖哪两类实例;最后分别说明合成实例考察什么、基准实例补足什么

**句间连接。** 首句借本文统一框架作为主语,新增对比对象;第二句借'两类实例'逐一展开各自用途,用whereas对举

**向后交接。** 以基准实例为何不可由合成数据替代收尾,随后进入运行环境与实现说明

**何时省略或拆开。** 只有单一类型实验时省略

**实际出处。** [Efficient Algorithms for Robust Markov Decision Processes with s-Rectangular Ambiguity Sets，第 1121 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2602.05591v1/main.tex:1121)；原文段落标识 `arxiv_2602.05591v1:verified-paragraph:132365`。

原句 1（连续原文；保留原始记号）：

> We study the empirical performance of our unified solution framework

英文改写 1（带槽位的编辑示例，不是引文）：

`We study the empirical performance of [the method] for [the stated problem class].`

原句 2（连续原文；保留原始记号）：

> The synthetic instances enable us to investigate how runtimes scale with the number of states

英文改写 2（带槽位的编辑示例，不是引文）：

`The synthetic instances enable us to investigate how [the measured quantity] scales with [the varied dimensions].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="experiments-paragraph-03"></a>
### 实验设置:合成实例的随机生成流程

**何时选择。** 读者需要复现随机实例,需逐项说明参数分布

**原段怎样推进。** 先说明规模取值范围;再说支撑集与概率的采样方式;再给奖励、初始分布、折扣因子;

**句间连接。** 首句给出规模参数,随后每句借上句的实例对象新增一个被采样的量及其分布

**向后交接。** 以折扣因子等固定常数收尾,下一段转入不确定集的设定

**何时省略或拆开。** 实例来自公开基准而非随机生成时省略

**实际出处。** [Efficient Algorithms for Robust Markov Decision Processes with s-Rectangular Ambiguity Sets，第 1129 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2602.05591v1/main.tex:1129)；原文段落标识 `arxiv_2602.05591v1:verified-paragraph:134309`。

原句 1（连续原文；保留原始记号）：

> we generate synthetic instances with

英文改写 1（带槽位的编辑示例，不是引文）：

`We generate synthetic instances with [the specified sizes and sampling scheme].`

原句 2（连续原文；保留原始记号）：

> the corresponding transition probabilities are drawn from a symmetric Dirichlet distribution

英文改写 2（带槽位的编辑示例，不是引文）：

`The corresponding [parameters] are drawn from [the stated distribution].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="experiments-paragraph-04"></a>
### 用两个基准问题的结构差异解释测试价值

**何时选择。** 需要简洁说明两个基准的计算结构为何不同，以及这种不同对本实验有什么意义。

**原段怎样推进。** 先点名实验中的两个领域；再从动作空间、转移概率或问题结构说明计算挑战。

**句间连接。** 基准名称→各自结构→测试为什么有意义

**向后交接。** 需要复现实例时另段给出生成参数；本段不替另一篇论文展开状态、动作和成本。

**何时省略或拆开。** 若结构差异与评测目的无关，省略对比；完整模型定义另行给出。

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 1024 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:1024)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:119113`。

原句 1（连续原文；保留原始记号）：

> Our experiments involve two problems from different domains with a fundamentally different structure.

英文改写 1（带槽位的编辑示例，不是引文）：

`Our experiments involve [the benchmark problems], whose structures differ in [the relevant computational features].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="experiments-paragraph-05"></a>
### 修改不确定集后，给出具体参数化选择

**何时选择。** 实验修改了前文的不确定集，需要解释修改目的，并给出实际预算与权重设定。

**原段怎样推进。** 先解释为何修改原有集合；给出本实验使用的集合及预算设定；再说明权重选择。

**句间连接。** 实验目的→集合修改→具体预算与权重

**向后交接。** 对照方法的其他超参数应在其对应设置段说明。

**何时省略或拆开。** 集合没有变化时，省略修改理由；没有使用的预算或权重选项不要列入。

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 1036 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:1036)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:123264`。

原句 1（连续原文；保留原始记号）：

> The ambiguity sets are modified slightly in this section to ensure a more realistic evaluation.

英文改写 1（带槽位的编辑示例，不是引文）：

`We modify [the experimental construction] to [the stated purpose of the evaluation].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="experiments-paragraph-06"></a>
### 解释Bellman层面加速小于投影子问题的原因

**何时选择。** 已分别测量投影子问题与Bellman计算，需解释两个层面的加速幅度为何不同。

**原段怎样推进。** 先指出Bellman层面的加速趋势与投影问题一致但幅度较小；再用Indeed解释对照求解器采用了结构化重写；最后回到差距缩小但仍有加速这一观测。

**句间连接。** 投影问题的结果→Bellman层面的差异→对照求解器的结构利用→回扣观测

**向后交接。** 适合解释两个计算层面的实测差异；本段不是完整RMDP求解器的加速结论。

**何时省略或拆开。** 没有这两个层面的可比结果，或未核实对照方法的结构利用方式时，省略该解释。

**实际出处。** [Efficient Algorithms for Robust Markov Decision Processes with s-Rectangular Ambiguity Sets，第 1171 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2602.05591v1/main.tex:1171)；原文段落标识 `arxiv_2602.05591v1:verified-paragraph:140099`。

原句 1（连续原文；保留原始记号）：

> The speedups observed at the level of the robust Bellman operator closely track those

英文改写 1（带槽位的编辑示例，不是引文）：

`The speedups observed for [the complete computation] track those for [the constituent subproblem], but [the observed difference].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="experiments-paragraph-07"></a>
### 从误差曲线及其包络读取收敛趋势

**何时选择。** 需要解释重复实验中的相对差距曲线、样本分位包络，以及它与预期收敛的关系。

**原段怎样推进。** 先说明随机重复或误差统计；再读取图中相对差距的衰减；最后把观测趋势与预期收敛行为联系起来。

**句间连接。** 所画误差与包络→曲线变化→与预期的关系

**向后交接。** 这是收敛图的局部解读，不是另一实验中鲁棒策略表现的论证。

**何时省略或拆开。** 没有重复实验时不写分位包络；曲线未支持极限或理论保证时，只报告实际观测。

**实际出处。** [Policy Gradient for Robust Markov Decision Processes，第 1064 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/corpus/raw/arxiv_2410.22114v2/main.tex:1064)；原文段落标识 `arxiv_2410.22114v2:verified-paragraph:135574`。

原句 1（连续原文；保留原始记号）：

> As expected, the relative difference decreases to zero as the number of iterations increases

英文改写 1（带槽位的编辑示例，不是引文）：

`The [measured difference] decreases [as observed in the plotted results] as [the experimental axis increases].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。


<a id="conclusion"></a>
## 结论与局部结果收束

短结论可在一段内回顾研究对象、方法、已证实结果和开放方向；多项方法则可逐项回顾后另段列未来工作。实验节的局部总结和性能解释仍保留其局部范围，不能直接当作全文贡献结论。

<a id="conclusion-paragraph-01"></a>
### 结论开篇:逐项回顾所提算法及其复杂度

**何时选择。** 结论第一段,需要向读者重申方法贡献,并说明各算法适用的集合类型与时间复杂度

**原段怎样推进。** 先用一句话总括提出了几种新算法及其适用问题;再逐个说明homotopy算法适用于sa-rectangular及其quasi-linear复杂度;再说bisection借用homotopy处理s-rectangular;然后说明两者可与PPI结合;最后用数值结果收尾。

**句间连接。** 第二句借第一句的“三种新算法”,逐一展开成“Our homotopy algorithm…”;下一句用“utilizes the homotopy algorithm”把bisection与前一算法联系起来,新增s-rectangular场景。

**向后交接。** 以“Both algorithms can be combined with PPI”引入组合方法,再以数值加速结论收尾,为后文未来工作做铺垫。

**何时省略或拆开。** 若论文只有一种算法,无需逐项回顾。

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 1113 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:1113)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:134540`。

原句 1（连续原文；保留原始记号）：

> We proposed three new algorithms to solve robust MDPs over $L_1$-ball uncertainty sets.

英文改写 1（带槽位的编辑示例，不是引文）：

`We proposed [the contributions] for [the stated problem class].`

原句 2（连续原文；保留原始记号）：

> Our bisection scheme utilizes the homotopy algorithm to compute the robust Bellman operator over s-rectangular

英文改写 2（带槽位的编辑示例，不是引文）：

`[The outer scheme] uses [the inner algorithm] to compute [the stated quantity].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="conclusion-paragraph-02"></a>
### 短结论:概述研究对象、贡献与展望

**何时选择。** 篇幅有限或会议论文,结论只需用几句话交代工作、结果和后续方向

**原段怎样推进。** 先说明研究的问题;再说明提出的快速算法;再概括理论和实验上优于已有方法;最后一句指出未来可拓展方向。

**句间连接。** 第二句借第一句中的“distributionally robust MDPs”,新增“fast algorithms”这一贡献;第三句借“proposed algorithms”新增比较结果。

**向后交接。** 以“Future work could address…”结束,直接给出后续研究方向。

**何时省略或拆开。** 若需要逐项回顾多个算法,改用详细回顾写法。

**实际出处。** [Fast Bellman Updates for Wasserstein Distributionally Robust MDPs，第 574 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/yu2023wasserstein/dr_MDP.tex:574)；原文段落标识 `yu2023wasserstein:verified-paragraph:61954`。

原句 1（连续原文；保留原始记号）：

> We show that the proposed algorithms outperform other existing methods in both theory and experiments.

英文改写 1（带槽位的编辑示例，不是引文）：

`We show [the precise theoretical and empirical comparisons established in the paper].`

原句 2（连续原文；保留原始记号）：

> Future work could address the extensions to approximate dynamic programming

英文改写 2（带槽位的编辑示例，不是引文）：

`Future work could address extensions to [the identified setting beyond the present results].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="conclusion-paragraph-03"></a>
### 未来工作:分点列出可改进和可推广方向

**何时选择。** 结论后半部分,需要列出多个相互独立的后续研究问题

**原段怎样推进。** 先用总起句说明研究开辟了若干方向;再以First说明算法实现上的改进;再以Second说明推广到其他不确定集;再说明值得做的实现与实证比较;最后以Finally提出与函数逼近的结合。

**句间连接。** 每个方向借用前文已出现的对象(如homotopy方法、L1球、PPI),并增加一个新的改进或推广对象。

**向后交接。** 以Finally引出最后一个方向并结束,无需再引出后续内容。

**何时省略或拆开。** 若没有明确后续工作,可以不写。

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 1115 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:1115)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:135308`。

原句 1（连续原文；保留原始记号）：

> Our research opens up several promising avenues for future research.

英文改写 1（带槽位的编辑示例，不是引文）：

`This study suggests [the specific directions for future work].`

原句 2（连续原文；保留原始记号）：

> we believe that the techniques presented here can be adapted to other uncertainty sets

英文改写 2（带槽位的编辑示例，不是引文）：

`The techniques presented here may be adapted to [the proposed extension not established in this paper].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="conclusion-paragraph-04"></a>
### 实验节末：由已测加速收束为规模趋势

**何时选择。** 实验讨论结束时,需要把多组结果归纳为一个总体加速结论,并说明规模扩展趋势

**原段怎样推进。** 先总结实测中的组合算法加速；明确集合类别和对照方法；再谨慎说明大规模实例中的潜在优势。

**句间连接。** 实测比较→对照范围→对更大规模的预期

**向后交接。** 适合实验结果收束；不能直接替代整篇论文结论。

**何时省略或拆开。** 若实验结果只有一组,或没有与基线比较,无需此归纳。

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 1109 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:1109)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:133931`。

原句 1（连续原文；保留原始记号）：

> our empirical results show that our proposed combination of PPI and the homotopy or bisection method achieves a speedup

英文改写 1（带槽位的编辑示例，不是引文）：

`Our empirical results show that [the tested method] achieves [the measured comparison under the stated conditions].`

原句 2（连续原文；保留原始记号）：

> their advantage is likely to only increase with larger problems

英文改写 2（带槽位的编辑示例，不是引文）：

`Its [the documented scaling behavior] suggests [the qualified expectation beyond the tested sizes].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

<a id="conclusion-paragraph-05"></a>
### 结果讨论：解释性能差异并限定比较范围

**何时选择。** 需要解释某方法为何在不同问题上表现不同,并提醒读者结果取决于实例。若读者更关心原因,用“依赖”式解释;若关心可靠性,用“强调理论保证相同”式限定

**原段怎样推进。** 先提出实验中的重要观察；说明两类迭代的相对表现如何依实例与不确定集改变；再将观测与理论速率的关系分开。

**句间连接。** 实验观察→实例与集合差异→适用范围

**向后交接。** 保留具体实验对象；用于结果讨论或结论中的限制说明，而非一般性优势声明。

**何时省略或拆开。** 若各方法差异不大或没有对比结果,可省略。

**实际出处。** [Partial Policy Iteration for L1-Robust Markov Decision Processes，第 1107 行起](/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/data/evaluation/m8_sources_20261105/corpus/raw/arxiv_2006.09484v1/faster_a.tex:1107)；原文段落标识 `arxiv_2006.09484v1:verified-paragraph:132394`。

原句 1（连续原文；保留原始记号）：

> The improvement margin depends on the relative complexity of policy improvements and evaluations.

英文改写 1（带槽位的编辑示例，不是引文）：

`The improvement depends on the relative computational cost of [the two identified operations].`

原句 2（连续原文；保留原始记号）：

> its performance relative to the robust value iteration and RMPI will depend on the specific problem instance

英文改写 2（带槽位的编辑示例，不是引文）：

`Its performance relative to [the specified baselines] depends on [the instance features and parameter settings].`

使用边界：槽位中的事实、条件与比较必须来自当前稿件。先检查上一句是否已给出本句的旧信息，再检查末句是否完成本段任务并给下一段留下明确对象。

## 核验与适用边界

目录中的每个连续原句均在对应物理段落的无注释投影中核验，段落保留源文件绝对路径、全文件哈希、原始偏移和行号，署名另由真实原文件核验。无法在同一请求的真实原文中定位的建议被舍弃；若建议混合了两个段落，按实际选中的段落重新收窄中文说明。

各节最初的专家阅读同时包含多篇论文，所读论文全部保留在生成来源中。它们可以供人工查阅，但不能因为最终引用了另一篇论文，就声称该建议与被排除论文完全独立。独立单篇阅读形成的卡片另有完整请求记录；评估时按全部生成输入与实际引文来源共同排除。

这些材料验证的是来源与可追溯性，不等于已经测得写作质量提升，也不替代数学和文献事实核查。
