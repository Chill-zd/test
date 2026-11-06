# 结构层当前状态与历史实现（2026-11-04）

当前源包为 0.3.0；构建不等于安装。四篇语料含 69 个实际章节。八个代表章节已选定，其中五节机械分析完整，Preliminaries 保留表格功能图 partial；共六张待人审卡。Model Setup 十批、Theory 十二批逐单元观察已核验，前者 Sonnet 全节回答因三处 observed transition 缺少原文证据而未通过，后者全节请求因外部余额不足而显式延期，未调用 API、未预留该次调用。二者没有可用全节卡，不能记为八类完成。

共享词库现为 19 个 concept、41 条 scoped phrase（37 个不同 term/phrase 组合），其中 15 条有至少三篇独立目标作者合著论文支持；句型仍为 47 条。以下旧阶段 canonical shared=0 和 2/69 的数字属于历史，不代表当前状态。所有结构语义仍 pending_human，科学内容未核验；未通过 M8 或 Level 3。

合并审查包从原始 v2/v3 路径读取，覆盖全部 69 节并展示缺失项，不复制成另一轮结果、不自造卡或人工批准。Model/Theory 仅有 unit observations 的页面如实展示；Preliminaries 整体来源 sidecar 不补成原功能片段图。16 个离线任务提案对应未来 32 个 full/bare 运行，均未运行；Conclusion 的两个请求共用一个原文段落，重叠已披露。

交付上限明确为 450,000 字符；缺省代码仍为 250,000。超限的完整强制证据不交付，不能当作可引用依据；不截断原文，不拆分 writer 调用。独立 Sonnet 全节输入采用显式 source-only 前置检查及逐字无损共享值编码，原包可精确解码，未开启文本行拆分。原结构核心与历史缓存不变。语言修改通过审查/校验/编译时，继承的科学疑问单独保留；新科学含义或无法忠实表达的歧义仍需单独判断。

详见 [当前状态](IMPLEMENTATION_STATUS.md)、[合并审查与恢复记录](../data/evaluation/structure_expansion_20261104/final_status.md)。

## 历史：初版新增层与试行记录

# 新增结构层：实现与待审范围（2026-11-04）

本轮是独立的**源工作副本新增层**。已安装插件仍为 0.2.0；本轮未改版本、未重新发布/安装，也未将结构观察或新共享候选自动接入日常 writer。原句级知识、既有实验和 active lexicon 不被覆盖。

咨询依据仅为 `data/acceptance/structure_consultation_20261104/04_independent_problem_consultation.json` 与 `05_sonnet_self_clarification.json` 的原始回答；用户纠正前的 01–03 不作试行决策依据。咨询示例没有作为实际提炼结果入库。

## 机器完成的部分

- 实际 section 树按 `input/include` 的逻辑顺序建立，直接源单元和子节占位分别保存，不按 section_type 混并不同真实章节。全库为 4 篇、69 个实际章节、1,242 个源单元：805 个 prose_fragment、400 个 insertion_object、37 个纯 label 元数据单元。这些数字不是自然段数；长段、公式和 include 边界仍可能造成解析碎片。
- 新的逐单元/预算分块观察与全节综合契约独立保存。完整单元上下文和完整本节原文都供模型使用，不以摘要替代。完整请求超出显式预算时保留 pending/异常，不暗中截断原文。每个实际直接项、每个相邻项对均须有有序记录；未知/不适用可以明示，不强迫添加关系或过渡词。
- 所有功能片段、上下文引文和科学保留槽位回查 comment-free 投影，保留 raw/projection 哈希与原文偏移。已分析块须完整覆盖其非空白源文；缺漏、重复、乱序、伪引文或模型自称 approved 均被拒绝。语义判断始终 pending_human。
- 请求/源/提示词与有效参数决定独立缓存；失败、截断、原始应答和可获得的实际 provider 元数据保留。失败不自动重试。统一使用 LLMClient 和 ledger，不另建隐形调用通道。
- 共享审计读取多个已核验 raw 目录，对完整真实语料的各源单元做严格字面回查：Unicode casefold、空白归一化、Unicode 词边界；不去 LaTeX、不合并单复数/连字符/同义词。逐命中保留 span、原文、哈希、章节和真实作者归属；重复 include 的同一物理位置只计一次，arXiv 显式版本号归为同篇。不同标识之间的发表/扩展关系未擅自推断。

新 CLI（不会修改旧句级工件）：

```bash
.venv/bin/polishpaper structure inventory
.venv/bin/polishpaper structure plan --paper arxiv_2205.14202v1 --section 'Introduction' --no-recursive
.venv/bin/polishpaper structure analyze --paper arxiv_2205.14202v1 --section 'Introduction' --provider sonnet --max-output-tokens 8192 --max-batch-units 1
.venv/bin/polishpaper structure coverage --analysis-dir data/evaluation/structure_pilot_20261104/analysis
.venv/bin/polishpaper structure audit-phrases --raw-dir data/knowledge/_raw --raw-dir data/evaluation/coverage_expansion_20261104/knowledge/_raw --target-author 'Wolfram Wiesemann'
.venv/bin/polishpaper structure review-pack --analysis-dir data/evaluation/structure_pilot_20261104/analysis --target-author 'Wolfram Wiesemann'
```

`analyze` 是显式模型调用命令，其余上述命令为本地构建/核验。可通过受信任的本地 `--client-factory module:function` 提供 `(config, ledger) -> client` 适配器。协调者本次真实试行用低 effort、关闭 web_search/thinking_display 的显式 Sonnet transport，并保留完整 provider_response；原 config.yaml 未改。实际试行结果已存在，重用时请指定该次 inventory/analysis 路径，不要无故重新推理。完整预算参数与失败重试需显式给出；`--retry-failed` 才授权新的失败后尝试。

## 已有真实试行，不等于语义审定

协调者在 2205 的完整 Introduction、Related Work 上完成 14 次真实 Sonnet 5.5 调用，全部 stop：7 个 Introduction 正文源单元、5 个 Related Work 正文单元，加 1 个不调模型的 label 锚点。形成 50 个连续功能片段与 11 个相邻项检查；两节机械状态 analyzed，语义状态 machine_proposed/pending_human。275 份受保护旧文件哈希未变，详见 `data/evaluation/structure_pilot_20261104/coordinator_verification.json`。

审读限制必须保留：首个 Related Work 正文的 reader_before 只看到邻接 label 窗口，模型把它表述为读者仅知 label；这是局部输入的局限，不能当作完整论文读者状态。整节综合带完整本节原文，但不带前面完整 Introduction。该判断未被机器“修正”为通过。重复记录和出处还造成较大的综合输入：协调者记录 Introduction 综合约 55,895 输入 tokens。当前保证原文不截断，尚未完成效率优化或跨节读者状态建模。

## 共享覆盖与人工尚未完成的部分

独立回查得到 88 个去重候选组合；22 个不同字面 phrase 在至少 3 篇源论文出现，其中 15 个在目标作者参与的 3 篇论文均有字面来源。该工具只接受已核验候选；补充提炼阶段另有 1 条引文不匹配已丢弃并保留失败记录，没有为凑数修饰为通过。既有 canonical shared **仍为 0**：新回查报告没有自动合并 active lexicon。字面出现数不等于概念归类正确、语境适合、作者风格稳定或人工批准；concept、phrase、pattern 的统计始终分开。没有采用形态/LaTeX等归一化、不同作者群门槛或“至少 5 个 term”等额外准入条件。

当前仅 2/69 个实际章节有新机器观察，且只覆盖 Introduction、Related Work 两种类型。原文八类齐全，不等于八类图式已提炼/审定。其余六种主体类型及 appendix/unknown 图式明确 missing，不造卡。两张新卡均是单篇来源观察，人工批准数为 0。

入口为 `data/structure/review_packet/latest_packet.json` 指向的 `index.md`：逐单元原文、reading_task、reader_before/after、功能片段与推进、上下文关系、科学保留项、全节观察/相邻对检查均直接渲染已存 Sonnet 字段；JSON/哈希另作审计链接。共享字面覆盖报告和空的 phrase/section/unit/function 人工 decisions 一并提供。重复生成相同审定包不会覆盖用户 decisions。

仍需用户逐条审定功能解释、上下文理解、适用范围、科学槽位和共享 phrase 的语境；还需扩展其他真实章节/类型并完成全章节图式审定。未自动批准、未完成 M8，也未证明写作质量提高。

## 最终实际交付核验

450,000 字符上限下，六类均交付完整 section map 与所选完整 unit observation 两项：Introduction 418,226、Related Work 74,122、Preliminaries 352,783、Algorithm 171,400、Experiments 151,957、Conclusion 110,319。待人审警告与外部作者归属保留，未调用模型。Theory 实际延期请求重放保持相同请求及工件哈希，ledger 116→116，新增预留 0；不能据此记为已取得 Sonnet 全节回答。最终离线测试 161 项通过。
