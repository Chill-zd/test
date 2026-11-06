# LaTeX记号参考清单

先保留本稿已经明确定义的记号。需要引入新对象时，优先参考 Yu、Dai、Xu、Gao、Chin Pang Ho 的《Fast Bellman Updates for Wasserstein Distributionally Robust MDPs》（NeurIPS 2023）；该文没有对应对象时，才参考实际含 Chin Pang Ho 作者署名的其他原文。项目显式指定的对象—记号映射优先于来源偏好。这里没有授权整稿换符号。

主参考取自原始 `DR_MDP (1).zip` 的 `dr_MDP.tex`，并核对了[官方论文的题名与作者](https://proceedings.nips.cc/paper_files/paper/2023/file/61779e9b0c26a31c5f36bd3e8c180dcf-Paper-Conference.pdf)。本地作者TeX是单独绑定的版本，不冒称与最终PDF字节相同，也不虚构页码。后备仅四项，来自 Ho、Petrik、Wiesemann 的《Robust φ-Divergence MDPs》，作者由原TeX核对。没有导入旧Paper Supervisor的解释。

- 新写或获授权修改的粗体数学记号用 `\bm{...}`，并确保加载 `bm`；引文用 `\citep{...}`。原始来源LaTeX另存于目录，不为满足偏好改写历史文件。
- 判断的是语义对象、定义域、索引和形状，不是字母外观。未带帽转移核、带帽样本核、核的分布、分布的歧义集、期望核集合必须分清。
- 保留本稿的成本/奖励方向。参考文采用奖励最大化，不因取用符号就把成本改为奖励、把最小化改为最大化、加入矩形性或更换策略类。
- 一旦现有定义、显式映射与候选符号冲突，列为待确认问题；新数学对象没有依据时，不编造定义，也不另造生僻记号。
- 目录是可追溯的来源参考，不是已获批准的语义规则或训练样本。机器只做保守数学片段字面匹配，不能认证对象相同、量词正确、首次定义充分或算法等价。

特别注意：主参考 `\lambda` 是折扣，`\gamma` 是外层二分阈值；`\alpha` 是对偶量，并非策略更新步长；`\kappa` 在主参考是耦合分布，在φ散度后备文中是预算标量；`r_a` 是算法累加量，不是奖励。已有稿若另有明确含义，保留已有定义并另行检查局部碰撞。

下表每一行均有原文行切片、文件哈希和逐字引句保存在目录中。`dr_MDP.tex` 表示主参考；`ho_petrik_wiesemann_phi_original.tex` 表示上述后备。行号来自实际TeX，不是PDF页码。

| 可复制LaTeX | 含义及形状 | 适用范围与来源 |
|---|---|---|
| `[N]` | 从1到N的有限索引集；N个正整数 | i∈[N]；维度N随所索引对象定义；`dr_MDP.tex:L166-L166` |
| `\bm{e}` | 全一向量；上下文决定维度；须在本稿说明 | 与所乘向量维度一致；`dr_MDP.tex:L166-L166` |
| `\bm{e}_j` | 第j个坐标为1、其余为0的向量；与当前向量同维 | j为合法坐标；`dr_MDP.tex:L166-L166` |
| `\Delta_N` | 概率单纯形；{x∈R^N: eᵀx=1,x≥0} | 状态概率用Δ_S；动作概率用Δ_A；`dr_MDP.tex:L166-L166` |
| `P(\mathcal{X})` | 集合X上的全部Borel概率测度；其元素为分布，不是状态概率向量 | X按该对象的样本空间定义；`dr_MDP.tex:L166-L166` |
| `\delta_{\bm{x}}` | 在向量x处的狄拉克分布；质量1集中于x | x的维度由其样本空间确定；`dr_MDP.tex:L166-L166` |
| `\mathcal{S}` | 有限状态集合；{1,…,S} | s,s′∈𝒮；`dr_MDP.tex:L220-L220` |
| `S` | 状态数；\|𝒮\| | 不是状态本身s；`dr_MDP.tex:L220-L220` |
| `\mathcal{A}` | 有限动作集合；{1,…,A} | a∈𝒜；`dr_MDP.tex:L220-L220` |
| `A` | 动作数；\|𝒜\| | 不是动作本身a；`dr_MDP.tex:L220-L220` |
| `\bm{p}_0` | 初始状态分布；Δ_S⊂R^S | s₀按该分布抽取；`dr_MDP.tex:L220-L220` |
| `\bm{p}_{sa}` | 给定状态动作后的下一状态分布；Δ_S；分量索引下一状态 | s∈𝒮,a∈𝒜,s′∈𝒮；`dr_MDP.tex:L220-L220` |
| `\bm{p}_s` | 固定状态下全部动作的转移核块；(Δ_S)^A；有A个S维行/列向量，排列由本稿声明 | a∈𝒜；`dr_MDP.tex:L220-L220` |
| `\bm{p}` | 全部状态动作的转移核；(Δ_S)^(S×A)，坐标结构S×A×S | s,a,s′；`dr_MDP.tex:L220-L220` |
| `r_{sas^{\prime}}` | 状态s执行动作a转到s′的奖励；R；本稿如另有限制须保留 | s,s′∈𝒮,a∈𝒜；`dr_MDP.tex:L220-L220` |
| `\bm{r}_{sa}` | 固定状态动作下按下一状态汇集的奖励；R^S | 分量索引s′∈𝒮；`dr_MDP.tex:L220-L220` |
| `\lambda` | 折扣因子；(0,1) | 时间t=0,1,…；`dr_MDP.tex:L220-L220` |
| `\bm{\pi}` | 随机策略；(Δ_A)^S | s∈𝒮,a∈𝒜；`dr_MDP.tex:L226-L226` |
| `\bm{\pi}_s` | 给定状态的动作分布；Δ_A | a∈𝒜；`dr_MDP.tex:L226-L226` |
| `\pi_{s a}` | 动作概率分量；[0,1]；每个状态的动作概率总和1 | s∈𝒮,a∈𝒜；`dr_MDP.tex:L248-L248` |
| `\bm{v}` | 状态价值向量及其迭代、最优标记；R^S；v_s是分量；星号最优，t为迭代 | s∈𝒮,t=0,1,…；`dr_MDP.tex:L260-L264` |
| `\mathfrak{T}` | 分布鲁棒贝尔曼算子；R^S→R^S；每个分量是一项状态更新 | s∈𝒮；`dr_MDP.tex:L260-L264` |
| `\mu` | 全转移核的未知概率分布；P((Δ_S)^(S×A)) | 随机对象为p，不是单个下一状态；`dr_MDP.tex:L234-L234` |
| `\mu_s` | 状态核块的边际分布；P((Δ_S)^A) | s∈𝒮；`dr_MDP.tex:L236-L236` |
| `\mathbb{M}^q` | 状态矩形的转移核分布歧义集；P((Δ_S)^(S×A))的子集 | q∈[1,∞]，s∈𝒮；`dr_MDP.tex:L234-L234` |
| `\mathbb{M}_{s}^q` | 以Wasserstein球限制状态核分布的集合；P((Δ_S)^A)的子集 | s∈𝒮，q∈[1,∞]；`dr_MDP.tex:L238-L238` |
| `\nu_s` | Wasserstein球中心的参考/经验分布；N个状态核样本上的均匀经验分布 | s∈𝒮，i=1,…,N；`dr_MDP.tex:L240-L246` |
| `N` | 经验分布中的转移核样本数；N≥1 | i∈[N]；`dr_MDP.tex:L246-L246` |
| `\hat{\bm{p}}^i_s` | 第i个状态核样本块；(Δ_S)^A | i∈[N],s∈𝒮；`dr_MDP.tex:L246-L246` |
| `\bm{p}^i_{sa}` | 样本i对应的可选/扰动转移概率；Δ_S | i∈[N],a∈𝒜,s固定；`dr_MDP.tex:L274-L279` |
| `\hat{\bm{p}}^{i}_{sa}` | 第i个样本在状态动作处的转移向量；Δ_S | i∈[N],s∈𝒮,a∈𝒜；`dr_MDP.tex:L274-L279` |
| `\theta` | Wasserstein歧义球的半径；W_q≤θ；有限q预算写θ^q | q∈[1,∞]；`dr_MDP.tex:L238-L238` |
| `q` | Wasserstein阶数及本文地面范数阶数；[1,∞]；具体算法讨论1,2,∞ | 不是Q值或状态动作价值；`dr_MDP.tex:L238-L244` |
| `W_q` | q阶Wasserstein距离；输入为两个状态核分布；q=∞单独按极限定义 | 1≤q<∞，或∞的独立情形；`dr_MDP.tex:L242-L244` |
| `d_q` | 用于构造Wasserstein距离的地面距离；d_q(x,y)=\|\|x-y\|\|_q；x,y为核块 | 维度来自(Δ_S)^A；`dr_MDP.tex:L244-L244` |
| `\kappa` | 两个状态核分布之间的耦合分布；P((Δ_S)^A×(Δ_S)^A) | 边际为μ_s和ν_s；`dr_MDP.tex:L242-L244` |
| `\Gamma` | 给定两边际分布的全部耦合；Γ(μ_s,ν_s) | 两边际保持为μ_s,ν_s；`dr_MDP.tex:L244-L244` |
| `\mathbb{B}_s^q` | Wasserstein分布歧义集导出的期望核集合；(Δ_S)^A的子集；不是分布集合 | s∈𝒮；有限q与∞分别定义；`dr_MDP.tex:L250-L256` |
| `\gamma` | Bellman重构的目标上界与外层二分量；R；下界/上界/中点均为该量 | 固定状态s，动作约束a∈𝒜；`dr_MDP.tex:L274-L279` |
| `\alpha` | 内层约束的非负对偶乘子；0≤α≤barα；动作索引版本见算法 | 固定s,a；二分求解；`dr_MDP.tex:L317-L324` |
| `\bm{b}_{sa}` | 奖励向量加折扣后的当前价值向量；b_sa=r_sa+λv∈R^S | 分量为下一状态s′；`dr_MDP.tex:L290-L290` |
| `\mathfrak{P}` | 固定动作的最小扰动预算子问题；输入样本、b_sa、γ；返回标量最优值 | i∈[N]，固定s,a；`dr_MDP.tex:L283-L290` |
| `\mathfrak{D}_q` | 单样本单动作的内层单纯形子问题；变量p^i_sa∈Δ_S；返回标量 | q有限，i∈[N]，固定s,a；`dr_MDP.tex:L322-L324` |
| `\epsilon_1` | 外层γ二分的停止精度；算法以barγ−underγ≤ε₁停止 | 外层循环；`dr_MDP.tex:L374-L395` |
| `\epsilon_2` | 内层α二分的停止精度；每动作α上下界差≤ε₂ | 内层循环；`dr_MDP.tex:L374-L395` |
| `r_a` | 按动作累加的已计算预算/子问题值；r₀=0；a完成后得r_a，最终比较r_A和θ^q | a=1,…,A；`dr_MDP.tex:L374-L395` |
| `m` | 内层对偶目标的斜率；−hatγ+平均b_saᵀp^{i,*}_sa | 固定当前动作a；`dr_MDP.tex:L385-L386` |
| `\Pi` | 全部平稳随机策略集合；(Δ_A)^S | s∈𝒮,a∈𝒜；`ho_petrik_wiesemann_phi_original.tex:L132-L132` |
| `\mathcal{U}` | 鲁棒MDP的转移核歧义集；核空间的子集；不是分布歧义集M | 保持本稿矩形性/非矩形性假设；`dr_MDP.tex:L228-L228` |
| `\mathcal{P}_s` | φ散度鲁棒模型中的逐状态核歧义集；(Δ_S)^A的子集 | s∈𝒮；动作间共享预算；`ho_petrik_wiesemann_phi_original.tex:L159-L159` |
| `\kappa` | φ散度模型的不确定性预算；R_+；约束总散度≤κ | 动作a∈𝒜共享；`ho_petrik_wiesemann_phi_original.tex:L161-L161` |
| `\phi` | φ散度的凸生成函数；R_+→R_+；凸且φ(1)=0 | 仅φ散度模型；`ho_petrik_wiesemann_phi_original.tex:L165-L165` |

## 接入与局限

来源目录为 `data/knowledge/notation.json`（实际启用由协调流程完成）；来源研究与逐字核验见 `data/evaluation/notation_study_20261105/`。每个条目保留 `original_latex` 与 `preferred_latex`、对象类型、形状、索引范围、使用范围、成本/奖励提醒及碰撞说明。优先级只适用于同一新对象，不自动选择数学假设。

`build_notation_plan` 只生成参考计划，`check_notation` 只报告问题；两者不修改TeX。显式映射形式为 `{对象ID: "精确LaTeX"}`，例如折扣因子ID为 `discount_factor`。两个不同对象映射到同一记号时，进入科学问题栏，不能静默合并。完整来源与目录的哈希改变后，已生成计划不能继续冒用旧绑定。

数学符号扫描只覆盖常用数学环境中的粗体、花体和希腊字母，不是完整TeX解释器；普通单字母、宏展开、同字母跨作用域、张量轴顺序以及未出现于目录的科学对象仍须结合本稿核对。目录不穷举证明里的临时字母。完整稿件的定义优先于局部可见窗口；全稿不可用时必须说明覆盖范围。

没有新建通用宏来占用 `\S`、`\P` 等已有LaTeX命令。`notation_reference.tex` 是全注释的可复制片段清单，不会自动注入稿件，也不应整体取消注释作为正文插入。
