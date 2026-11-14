# 游戏视觉分析 · game-visual-analysis

基于 GVF 0.2.0 分析游戏截图、实机录像与项目画面，解释画风构成、视觉层级、一致性与交互反馈，支持作品对比和问题诊断。

这是一份可由 AI 助手加载的独立技能。它要求先检视真实材料，再区分观察、推断、评价与建议。随附 Python 工具只查询本地定义、核对数据快照，不自动分析图片或给画面打分。

## 使用

安装后向支持技能的助手提供截图、录像或可访问的材料，并说明希望了解的问题：

> 使用 $game-visual-analysis，分析这些游戏截图的画风和视觉层级，标明证据、未知项及改进建议。

> 使用 $game-visual-analysis，对比这两个版本中主角与背景的分离效果，说明比较条件和取舍。

> 使用 $game-visual-analysis，检查这段战斗录像中提示、命中和恢复的视觉反馈，以时间码定位证据。

单张截图也可分析；跨场景规律、动态效果和玩家体验需要对应材料，不能从单帧补猜。默认中文，报告格式服从当前任务要求。

## 通过 yts 安装

已接入同一发布者的 [yts](https://github.com/YiTongHu-SC/yts) 时，可直接说：

> 使用 yts 安装并启用 game-visual-analysis。

其他来源的 yts 可指定本仓库。将 `<yts.py>` 替换为本机已安装 yts 的脚本路径；先解析并核对提交，再把返回的 40 位 commit 代入预览和实际安装：

```text
python -B -X utf8 <yts.py> discover https://github.com/YiTongHu-SC/game-visual-analysis.git --ref main
python -B -X utf8 <yts.py> install https://github.com/YiTongHu-SC/game-visual-analysis.git --subdir . --ref <commit> --alias game-visual-analysis --visibility public --enable --dry-run
python -B -X utf8 <yts.py> install https://github.com/YiTongHu-SC/game-visual-analysis.git --subdir . --ref <commit> --alias game-visual-analysis --visibility public --enable
python -B -X utf8 <yts.py> status game-visual-analysis
```

仅在预览没有冲突时执行实际安装。已有同名技能时先保留原件，按 yts 的迁移流程处理。安装依赖 Python 3.11+ 与 Git；本公开仓库无需私人仓库访问权限。

也可将完整仓库放入宿主支持的技能目录，保留根目录 [SKILL.md](SKILL.md)、`references/` 和 `scripts/` 的相对关系；具体发现方式以宿主说明为准。

## 依赖与文件

- 视觉分析需要能查看图片或相关视频片段的助手/宿主，以及用户提供或授权访问的材料。未能打开材料时不能声称已经检视。
- 查询与快照检查使用 Python 3.10+ 标准库，无第三方 Python 包、API 密钥、特定引擎或网络依赖。没有 Python 时可按需读取 JSON。
- 网络只在检索外部作品、来源或下载安装时按任务使用。包内没有上传、遥测或凭据处理。

| 入口 | 内容 |
| --- | --- |
| [SKILL.md](SKILL.md) | 触发条件、分析流程与证据边界 |
| [分析框架](references/analysis-framework.md) | 12 个视觉域、对象、尺度与关系 |
| [证据与测量](references/evidence-and-measurement.md) | ROI、量化、动态证据及格式限制 |
| [输出模式](references/report-patterns.md) | 单作品、对比与诊断报告 |
| [来源与维护](references/provenance.md) | GVF 版本、来源范围及更新方式 |
| [快照清单](references/snapshot.json) | 81 参数、94 术语、51 来源及原字节哈希 |

在仓库根目录可运行：

```text
python -B scripts/query_catalog.py --list-domains
python -B scripts/query_catalog.py --id light.shading_appearance
python -B scripts/query_catalog.py --search 笔触
python -B scripts/query_catalog.py --kind terms --search 视觉风格
python -B scripts/query_catalog.py --kind evidence --id C03
python -B scripts/query_catalog.py --check-snapshot
python -B -m unittest discover -s tests -p "test_*.py" -v
```

从其他工作目录运行时使用脚本绝对路径；数据始终按脚本位置定位。`--check-snapshot` 必须单独使用：退出码 `0` 为内部一致、`1` 为核验失败、`2` 为参数误用。通过仅证明包内一致，不代表外部来源已重新核验或视觉质量验收通过。

## 维护与许可

本仓库是技能唯一维护源。作者模式可用 `yts link` 接入 Git 工作目录，修改、验证及提交后用 `yts refresh game-visual-analysis` 更新宿主副本；不要直接编辑部署目录。

作者：胡一统（yitong）。本项目采用 [MIT 许可证](LICENSE)。第三方来源的标题、链接及归属保留在来源账本中；MIT 不扩展到链接目标、第三方游戏素材或商标。本仓库不包含第三方游戏截图、视频或网页全文。GVF 是操作性分析框架，不是行业统一标准；默认报告不宣称符合原 GVF 的正式交换 schema。
