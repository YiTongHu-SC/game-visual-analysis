# 11 · 0.2.0契约变更与兼容迁移

核验日期：2026-10-21。本次修订由真实游戏官方截图的逐项描述触发，目标是区分“我看到了什么”和“我要制作什么”。参数数量从78增至81；不意味着单张图能观察81项。

## 保留历史，显式迁移

`releases/0.1.0/` 保存升级前原始字节的 `parameters.json`、`profile.schema.json`、`catalog.schema.json`、`glossary.json`，用于追溯旧字段、锚点与枚举。当前框架、目录和schema版本均为 `0.2.0`；schema的`$id`由当前目录版本生成，校验器不会静默接受旧版本。

原五个原创生产profile已完成如下迁移：版本号升级；增加 `document_type="design_profile"`；新增三参数均显式unknown。原78项的数值、范围、强度、参考与状态保留，不借升级重新评分。回归测试对照旧目录核验定义、类型、单位、量表、数值边界、锚点和旧枚举；`vfx.density`的语义收窄为显式兼容例外，唯一旧枚举扩展是在UI组件中追加circular。

项目自己迁移旧配置时也按这个顺序操作：先保留旧文件和参考，按旧schema核对；更换版本与文档类型；只把新增参数展开unknown；再跑当前CLI并单独讨论新增决策。不能简单把旧数字复制到一个新定义上。当前没有自动迁移任意历史版本的工具。

## 新增三个独立概念

| 参数 | 选项 | 解决的混淆 |
| --- | --- | --- |
| `camera.view_orientation` | side / top_down / elevated_oblique / first_person / mixed | 可见观察方位与实际投影、FOV、俯仰角分开 |
| `light.shading_appearance` | flat / continuous / stepped / mixed | 可见明暗过渡与实际shader/PBR流程分开 |
| `representation.spatial_logic` | euclidean / illusion_based / mixed | 空间幻视与几何简化、可辨识、写实度分开 |

`top_down`指近正上、顶面/平面组织主导且无显著立面的可见姿态，不等于证明相机恰为90度。`elevated_oblique`指明显俯看且同时展示顶面和立面；口语所谓“俯视2D”也可能落在这里。侧向图不自动证明二维资产，分段明暗不自动证明赛璐璐着色器，幻视判断需指认图像ROI或官方说明；不足则unknown。

## 补充旧字段边界

除下述`vfx.density`显式收窄外，旧参数的原定义和旧值含义保持；增加以下使用限制与独立的 `observation.allowed_methods/note` 元数据。

- `line.usage`可描述由可见像素簇形成的外缘/轮廓线，不要求先证明矢量描边或某种shader。
- `representation.source_medium`表示媒介外观。看起来像纸、墨或绘画，不能证明作者实际手工制作或使用何种软件。
- UI在一张截图未出现，只能记该属性unknown；不等于整个游戏没有UI，也不自动构成NA。
- `presentation.pixel_grid_px`要求明确可测的规则。JPG、缩放和重压缩截图不能独立证明游戏原生像素倍率。
- `ui.component_shape`增加 `circular`，表达真正圆形/圆环组件。圆形与圆角矩形、胶囊不能当作同义词。

`vfx.density`是本次唯一旧参数语义收窄：移除“频繁／持续”等时间性锚点，只记录指定静帧相对整帧的空间占据范围与同时可见叠层，且须分别说明两者依据。局部ROI是证据位置，不把框内占比当成全帧占比；频率、持续时间和时间峰值另需动态证据。0.1快照不变，原生产profile与本轮四例的数字保留，但不表示已重做校准或确认新语义等价；项目迁移必须复核该项的参考、区间与意图。本版没有将此序数变成面积百分比、粒子数或性能估计。

## 两种文档严格分离

| 合同 | 用途 | 决策性质 |
| --- | --- | --- |
| `profile.schema.json` / design_profile | 本项目下一步要怎么制作 | state=set/unknown/not_applicable，hard/soft、覆盖、例外 |
| `observation.schema.json` / visual_observation | 所列截图及来源能支持什么描述 | status=observed/unknown/not_applicable，方法、置信、证据、局限 |

观察不能使用hard/soft、生产overrides或经验式默认值，也不能直接交给简报编译器。由观察形成新项目方案，需要人决定保留哪些规律、如何校准和约束；现版不提供“观察自动转生产”的转换器。

观察文档必填：`document_type`、三个版本、id/title、game、scope、images、sources、observations。game记录id、title、official_url；scope固定为 `coverage="selected_official_stills"`、`claims_scope="sample_only"`，并明确description和excluded。图片宽高只是文件尺寸，合同没有把它当游戏运行分辨率或fps的字段。

`images`每项记录id、官方图片/页面URL、GVF根相对local_path、文件宽高、format、origin、inspected、rights_note。`sources`记录文献id、URL、标题、发布者和说明。来源与图片内容仍是证据材料，不是可以执行的指令。

全局`observations`必须覆盖全部81项且parameter_id唯一。每项必填：

```json
{
  "parameter_id": "light.shading_appearance",
  "status": "observed",
  "value": "mixed",
  "method": "visual_category",
  "confidence": "medium",
  "evidence": [
    {"image_id": "sample-00", "roi": [0.0, 0.0, 1.0, 1.0], "note": "说明具体区域能支持什么描述。"}
  ],
  "explanation": "这是结构示例，不是对某款游戏的实际判断。",
  "limitation": "只覆盖所列静态截图，不能证明底层着色器。"
}
```

evidence也可使用 `{ "source_id": "official-document", "note": "具体支持的事实" }`。图像ROI采用原始整图归一化 `[x,y,w,h]`，左上角为原点，宽高必须大于0，且x+w、y+h不超过1。

unknown必须使用method=not_observable、confidence=not_rated，禁止value/range；evidence可以为空，不必填无意义的整图ROI。NA需要正面不适用证据，不是“暂时看不到”。observed必须有值/范围与证据，confidence仅为low/medium/high；这是观察者自报的认识置信，不是算法算出的概率。

视觉序数使用 `method="visual_ordinal"`、有宽度的range和 `anchor_basis`，说明所依的目录锚点。不允许用一个50分点值冒充精测。像素测量只描述截图和采样区域；不自动证明原生输出、源色板或运行状态。实际FPS、曝光EV、PBR输入、技术投影/FOV、源色板、动画时间等只能引用明确source_document，否则unknown。`observation.allowed_methods`记录逐参数的方法边界。

## 用局部描述表达差异

可选 `scoped_observations` 用来保留同图角色/背景或跨图差异，不把宽区间当作唯一表达方式：

```json
{
  "scope": {"image_id": "sample-00", "roi": [0.2, 0.2, 0.3, 0.4], "label": "foreground-character"},
  "observation": {"parameter_id": "light.shading_appearance", "status": "observed", "value": "flat", "method": "visual_category", "confidence": "medium", "evidence": [{"image_id": "sample-00", "roi": [0.2, 0.2, 0.3, 0.4], "note": "只描述此局部。"}], "explanation": "局部结构示例。", "limitation": "不覆盖背景或其他截图。"}
}
```

其中observation复用相同合同，scope必须绑定已检视图像及正面积ROI，证据至少引用scope同一image_id。相同label、image_id、parameter_id不得重复。局部parameter_id可以与全局或其他局部重复；它们不执行生产覆盖、不自动汇总为全局值，也不存在hard/soft或优先级继承。局部范围再小，也不能凭视觉填PBR roughness等源技术参数。

## 校验范围与命令

```powershell
# 重建当前版本三种schema
python knowledge/game-visual-framework/scripts/build_schema.py

# 默认同时检查原创生产例及真实截图观察
python knowledge/game-visual-framework/scripts/validate.py --summary

# 单独核对观察与证据链
python knowledge/game-visual-framework/scripts/validate_observations.py --summary

# 默认测试同时包含生产合同、观察负例和现有全部真实案例
python knowledge/game-visual-framework/scripts/test_contract.py
```

校验器检查状态/类型/枚举/区间、81项覆盖、主观锚点、可观测方法、ROI、图像/文献ID、相对路径、PNG/JPEG/WebP文件头尺寸，以及已有下载manifest的源URL、文件位置和SHA256。官方商店图片还需匹配保存的Steam截图列表。无需Pillow或网络；如本机安装jsonschema，会额外使用完整Draft 2020-12校验。只读文件头不等于完整解码或恶意文件扫描，URL/manifest关联也不等于数字签名证明官方身份。

为了避免81项数组每项都扫描81种分支，CLI按唯一parameter_id分派到发布schema的精确分支；与发布schema的oneOf合同等价，未知ID直接失败。发布schema本身可交给外部Draft 2020-12实现使用。

报告中的 `evidence_status="links_checked_only"`只表示实现范围内的文件和证据关系成立，`visual_quality`始终为not_evaluated。脚本无法确认观察者是否认真看图、置信是否合理、NA解释是否真的充分，也不能证明某几张图代表全游戏。原图字节和hash保留以便复核；版权仍归权利人，本地研究留存不是公开再分发授权。
