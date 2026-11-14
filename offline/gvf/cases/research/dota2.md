# Dota 2：角色、地图、UI与技能的异质共存

核验：2026-10-21。观察合同与参数目录：0.2.0。以下记录截图证据，不推出可直接生产的profile。

## 样本与来源

采用[官方Steam商店 R05](https://store.steampowered.com/app/570/?l=english)图库顺序0、1、2，均已实际打开。各1920×1080，URL、SHA256和下载信息见[图像清单](../image-manifest.json)。这是发布方提供的游戏内截图，**不是本次自行录制**；build、截图日期、地图/皮肤版本和画质配置未知，不能当作最新客户端或全游戏。

- [D00：大片紫蓝球形效果](../images/dota2-00.jpg)
- [D01：冷灰道路上的链钩与单位](../images/dota2-01.jpg)
- [D02：绿色环境、商店/野怪与选中单位](../images/dota2-02.jpg)

[官方角色指南 R06](https://help.steampowered.com/en/faqs/view/0688-7692-4D5A-1935)允许默认颜色/剪影变化，同时要求保持识别、按实际游戏尺寸检查细节。[工坊索引 R07](https://www.dota2.com/workshop/build/references?l=english)区分三维模型、二维图像、角色和效果。这些资料提供制作背景和设计目标，不证明本图全部表现都达标，也不提供具体shader或材质值。

## 三图中的真实差异

D00紫蓝透明球与亮边覆盖大片世界区域，内部几何分块和单位重叠；D01环境偏冷灰，链钩是窄长的方向线索；D02绿植、路面与常规单位占主导，但仍有局部火焰，不能说“没有特效”。HUD同时容纳肖像、图标、格子、条形资源、数字与小地图。

世界物体的连续体积明暗、植被/石地细节、技能的几何亮边/透明层、HUD的平面图形并存。异质并存不自动是不统一；需要检验它们各自承担什么角色、怎样保留识别及竞争注意力。

**地面选择圈不等于人物外描边。** 绿色/白色圈位于脚下地面位置，血条黑框、技能网线也各有用途。D02绿装单位与绿草颜色接近，地面圈和上方条形信息提供另一种线索；D00强效果又包围、部分遮挡单位。不能据此宣称人物总有清楚黑线，也不能把全游戏写成没有任何边缘强调。

## ROI证据

ROI是相对完整图像的 `[x,y,w,h]`，范围0–1，不是世界单位或精确像素测量。

| 局部 | ROI | 实际可见内容 | 防止的误判 |
| --- | --- | --- | --- |
| D00球形效果 | 0.450,0.180,0.420,0.690 | 紫蓝透明/高亮结构包围单位 | 一个特效密度代表全部状态 |
| D01链钩 | 0.405,0.430,0.280,0.230 | 细长链形横跨道路 | 所有技能都是柔光团 |
| D02地面圈 | 0.601,0.428,0.070,0.084 | 圈与人物几何外形不同 | 用圈宽填写人物outline |
| D01近处单位 | 0.610,0.570,0.110,0.210 | 大体型、装备、条形UI | 一个自然比例适用全部角色 |
| D02台阶 | 0.265,0.460,0.340,0.240 | 高差、道路、接地关系 | 俯看直接等于正交或等距 |
| 三图底部HUD | 0.310,0.850,0.380,0.150 | 肖像、技能、物品、条、数字 | UI只有一种形状/媒介 |
| D00单位状态 | 0.627,0.190,0.075,0.058 | STUNNED与条形信息附着单位 | 全部信息都是固定屏幕overlay |

## 逐12域总结

| 域 | 本组观察 | 不能推出的结论 |
| --- | --- | --- |
| 表征与媒介 | 官方支持三维资产背景；可见斜向俯看、体积和遮挡 | 3D感不唯一决定pipeline，UI仍可平面 |
| 造型与形体 | 人物比例、装备、轮廓差异大；地图与植物形态混合 | 一个头身比例或圆润度不覆盖全部人物 |
| 线条与边缘 | 血条、面板、圈、链、网线各有边界功能 | 地面圈不等于主体描边，也不能断言全局无边缘强调 |
| 表面与材质 | 裂纹、叶片、装备和肖像有不同细节组织 | 明暗不能唯一证明PBR、手绘工艺或材质输入 |
| 色彩 | 区域色变化，技能可高度鲜明，HUD独立分工 | 无源palette，不给精确色数/OKLCH |
| 光照与阴影 | 世界连续明暗与局部投影、发光样效果并存 | 不验证物理一致性、曝光或AO实现 |
| 镜头与投影 | elevated_oblique可交流观看方向 | 投影类型、FOV、角度、距离和行为未知 |
| 构图与可读性 | 世界加高密度HUD，三图焦点分配不同 | 显眼不证明玩法层级正确，无辨识测试 |
| 运动与动画 | 当前姿态和效果形状 | 6项运动字段unknown，无FPS和时序证据 |
| 特效与反馈 | 球、链和局部火焰差异大 | 不提供寿命、并发峰值、命中对应和反馈延迟 |
| UI与文字 | 固定HUD加单位附着信息，多种组件形态 | 不概括全部菜单/语言，也未测可读性达标 |
| 输出与处理 | 已知JPEG交付尺寸 | 不知道内部网格、抗锯齿、后期或性能 |

## 覆盖、误判和修订建议

[机器观察表](../observations/dota2.json)逐项覆盖81参数：32项有可见/官方文档证据，49项unknown，0项NA。没有因为某效果不在这三帧出现就判不适用；没有hard/soft、自动总分或生产默认值。

0–100区间只是依目录语义锚点的待校准解释，不是百分比、官方分数或真实shader数值。人物、地图、技能与UI有差异时，保留范围及ROI，不用平均遮蔽差异。

1. 至少区分人物、地图、技能、地面语义标记、单位附着UI与屏幕HUD；同一画面不必有单一全局材质或线条值。
2. 把对象边界与信息标记分开。圈、血条、范围图形和物体轮廓各自录入，防止把选中状态误当日常造型。
3. 观看方向、可见体积和技术投影分别表达；elevated_oblique足以交流方向，未标定时projection保留unknown。
4. 球形、细链、局部火焰作为并列样本，增加技能/状态范围；不以宽区间中点生成“一般Dota特效”。
5. 官方目标和截图做法都不等于玩家效果已通过；用带任务的实机回放和玩家测试评估真正的功能层级。

未覆盖完整英雄、皮肤、地图、设置、时序、当前版本和性能。本例检验框架表达与未知处理，不是Dota生产参数或完整美术规范。

`vfx.density`按0.2收窄后的静态空间语义解释：以完整画面比较占据范围和同时可见叠层；ROI只定位证据，不把框内占比当成全帧占比。原粗区间保留但未重新校准，不表示发生频率、持续时间或动态峰值。

## 全81项逐项表

下表与机器JSON同步；证据ROI、方法、置信度和限度以JSON中的逐项记录为准。

| 参数ID | 本组结论 | 观察依据或未知原因 |
| --- | --- | --- |
| `representation.mode` | 3d | 官方资产工作流支持三维角色资产制作背景。 |
| `representation.recognizability` | 50–75（语义档） | 人物/怪物、武器、树、道路和建筑可辨类别。 |
| `representation.depth_cues` | 75–100（语义档） | 俯看、遮挡、台阶高差、接地阴影和体积明暗提供深度。 |
| `representation.abstraction_strategy` | mixed | 夸张人物、概括地图物件、图形技能与写实线索共存。 |
| `representation.source_medium` | unknown | 官方三维模型工作流不指明本图人物/地图/效果/UI的媒介母题，不能以3D直接填paint。 |
| `representation.semantic_load` | 50–75（语义档） | 技能、物品、地图符号、状态词和资源条要求约定知识。 |
| `form.naturalism` | 25–50（语义档） | 身体/装备可辨，但大体型、面部和武器比例明显重构。 |
| `form.proportion_exaggeration` | unknown | 未指定可复核的现实或设计比例基准；幻想单位和装备轮廓不足以确定比例夸张档位。 |
| `form.shape_language` | mixed | 有机人物/植物、方块阶梯/建筑与圆形/多边形效果共存。 |
| `form.edge_roundness` | 25–75（语义档） | 人物/植被有曲线，岩块/建筑/阶梯保留棱角。 |
| `form.silhouette_complexity` | 50–75（语义档） | 装备、武器、身体与附属形体带来多处外形变化。 |
| `form.scale_consistency` | unknown | 没有人物、野怪、商店和建筑的批准尺度表；不同体型不自动是不一致。 |
| `form.anatomy_strategy` | hybrid | 人形与怪物身体关系可辨，同时采用不同程度夸张。 |
| `line.usage` | selective | 面板、条、地面圈、链与技能网线各有用途，未见统一人物黑外线。 |
| `line.width_px` | unknown | 未按统一协议沿轮廓法线逐像素取样；JPEG重采样/软边影响线宽，不能凭观看填精确px。 |
| `line.weight_variation` | unknown | 圈、面板、条和技能线功能不同，缺同类线比较与取样，不能合成全局线宽变化分。 |
| `line.edge_regularity` | 50–75（语义档） | HUD和技能几何较规则，叶片/岩块边界更不规则。 |
| `line.color_mode` | mixed | 地面圈、状态条、灰黑面板和紫色网线颜色不同。 |
| `line.inner_density` | 25–75（语义档） | 面板/图标和技能网线密度不同，地裂不能全当结构线。 |
| `surface.material_physicality` | unknown | 缺少同表面的多视角、多光照与实测材质参照；单帧不能验证反射/透射响应。 |
| `surface.detail_density` | 50–75（语义档） | 裂纹、叶片、装备和肖像有小尺度信息，大球遮蔽部分地图。 |
| `surface.texture_mode` | unknown | 官方模型说明未提供本图地图/皮肤贴图的完整生成方法，不能由绘画感断言全体手绘。 |
| `surface.brush_visibility` | unknown | 不能可靠区分笔触、纹理图案、光照与JPEG压缩；不把全部细节当笔刷痕迹。 |
| `surface.brush_scale_px` | unknown | 没有可稳定辨认并量取的笔触集合；屏幕纹理尺度不等于源笔刷宽度。 |
| `surface.roughness` | unknown | 需要源材质/着色器定义；单帧高光不能唯一反演PBR粗糙度输入。 |
| `surface.metallic` | unknown | 缺少源材质或明确技术资料；颜色和高亮不能唯一确定金属度输入。 |
| `color.palette_mode` | unknown | 未取得源色板及用途分工合同；最终场景色彩关系不能直接等同受控配色策略。 |
| `color.palette_colors` | unknown | 没有原始受控色板；JPEG、光照和渐变中的像素色数不等于色板色数。 |
| `color.saturation` | 25–75（语义档） | 00紫蓝技能强烈，01灰地较柔，02绿植和人物更鲜明。 |
| `color.value_range` | unknown | 没有关键区域遮罩与OKLCH采样协议，也未实际计算明度跨度；不凭观看猜数。 |
| `color.palette_lightness` | unknown | 没有源色板，JPEG亮暗不等于主色板OKLCH L。 |
| `color.palette_chroma` | unknown | 没有源色板和颜色管理条件，鲜艳感不等于主色板OKLCH C。 |
| `color.palette_hue` | unknown | 没有主色选择规则与源色板，三帧区域变化不能压成精确主色相角。 |
| `color.accent_area` | unknown | 未定义强调色掩码、阈值和分母；光晕/渐变/UI未形成面积测量。 |
| `color.temperature_bias` | contextual | 紫/暖建筑、冷灰和绿黄环境变化，HUD另有稳定色块。 |
| `light.physicality` | unknown | 缺少现实光照参照及多条件测试；有阴影/亮光不能证明物理一致性。 |
| `light.model` | unknown | 多种方法能实现相同明暗；没有这些截图使用的着色/灯光配置。 |
| `light.shadow_hardness` | 25–75（语义档） | 02局部细杆/物件影较清楚，树影与其他环境过渡更宽。 |
| `light.contrast` | 25–75（语义档） | 00技能局部强对比，01灰场与02普通地图组织不同。 |
| `light.exposure_ev` | unknown | 缺场景曝光基线、色调映射与源HDR数据；JPEG不能提供EV补偿。 |
| `light.emissive_prominence` | 25–100（语义档） | 小火焰/亮点与00大面积高亮技能影响跨度大。 |
| `light.ambient_occlusion` | unknown | 暗缝/接触暗部可能来自贴图、灯光或后期，不能区分AO贡献。 |
| `camera.projection` | unknown | 不同场景的单视图不能唯一标定投影矩阵；侧看/俯看不等于正交或透视。 |
| `camera.elevation_deg` | unknown | 缺少场景坐标、相机姿态和校准几何，不能给精确俯仰角。 |
| `camera.vertical_fov_deg` | unknown | 没有相机标定、投影类型与参照尺寸，不能推垂直视场角。 |
| `camera.distance_m` | unknown | 没有世界单位、主体尺寸和相机配置，像素占高不能换算米。 |
| `camera.movement` | unknown | 三张不是连续时间序列，无法区分固定、跟随、自由或脚本运动。 |
| `camera.distortion` | unknown | 没有已知直线/成像参照；未见明显畸变不能填0。 |
| `composition.focal_hierarchy` | 50–75（语义档） | 三帧由大球、链钩/人物、选中单位等形成不同焦点。 |
| `composition.negative_space` | unknown | 未声明留白/有效视觉空间的遮罩和分母；低细节不等于空白面积。 |
| `composition.depth_layers` | unknown | 虽可见遮挡，但未定义离散层计数协议；可见层不是引擎图层数。 |
| `composition.density` | 50–75（语义档） | 植被/人物/界面同时有信息；00球体遮挡环境，01道路较空。 |
| `composition.alignment` | mixed | 通路/台阶斜向展开，HUD横排/格状，小地图独立组织。 |
| `composition.subject_separation` | 25–75（语义档） | 01浅色大单位易分，02绿装与草色近，00强效果包围部分单位。 |
| `motion.naturalism` | unknown | 静帧不包含时序、速度、受力与惯性，姿态不能替代运动观察。 |
| `motion.timing` | unknown | 不是连续回放，不能区分插值、保持、跳变或混合时间组织。 |
| `motion.animation_fps` | unknown | 截图没有姿态更新的时间戳序列；交付图尺寸不说明动作/渲染FPS。 |
| `motion.squash_stretch` | unknown | 没有同对象基准形和连续动作，不能证明动态挤压拉伸幅度。 |
| `motion.anticipation_ms` | unknown | 缺主动作及预备阶段的逐帧时间证据，不能填写毫秒。 |
| `motion.secondary_motion` | unknown | 缺主体/附属部件的连续相位关系，不能判断跟随运动显著度。 |
| `vfx.density` | 25–75（语义档） | 从局部火焰/线形效果到大球，全帧空间占据和同时可见叠层不同；保留粗区间但未重校准，不判断频率或持续时间。 |
| `vfx.bloom` | 25–75（语义档） | 大球亮边扩散显著，其他帧主要局部火焰光晕。 |
| `vfx.motion_blur_shutter` | unknown | 条带/软形/拖尾可由绘画、粒子或后期生成，不能反推快门角。 |
| `vfx.screen_shake_px` | unknown | 没有前后帧稳定参照，不包含相机震动位移序列。 |
| `vfx.hit_flash_ms` | unknown | 没有命中事件及前后时间轴，亮白区域不证明受击闪白或时长。 |
| `vfx.semantic_color` | unknown | 单帧不足确定跨技能、阵营和状态的稳定颜色语义映射。 |
| `ui.integration` | mixed | 底部/顶部/小地图为屏幕HUD，单位上方文字和条附着世界位置。 |
| `ui.typography` | unknown | 可见字形小且文字有限，缺少明确跨字体类型证据；粗细、倾斜、字号差异不足以证明mixed。 |
| `ui.min_font_px` | unknown | 未量可见字身像素高度，也未覆盖所有关键文字，不能报最小字号。 |
| `ui.text_contrast` | unknown | 没有选前景/背景采样对和线性化亮度计算；眼看清楚不是对比比率。 |
| `ui.information_density` | 75–100（语义档） | 肖像、技能、物品、资源、顶部信息、小地图和状态同时可见。 |
| `ui.component_shape` | mixed | 矩形面板/格、横条、圆按钮和地面圈共存。 |
| `presentation.resolution_strategy` | unknown | JPEG尺寸不是内部渲染、动态分辨率或整数放大策略。 |
| `presentation.pixel_grid_px` | unknown | 没有源逻辑网格与缩放链，最终像素不能反推底层网格。 |
| `presentation.antialiasing` | unknown | 平滑可来自源图、缩放、压缩或多种抗锯齿，没有底层设置资料。 |
| `presentation.grain` | unknown | JPEG噪声、表面信息与绘画痕迹难分，无连续/无压缩参照确认颗粒。 |
| `presentation.chromatic_aberration_px` | unknown | 缺成像标定和通道位移测量；彩色效果边缘不自动等于镜头色差。 |
| `presentation.vignette` | unknown | 边缘暗部混有树影、地图雾与遮挡，未分离出全屏暗角的稳定外观。 |
| `camera.view_orientation` | elevated_oblique | 可见物体顶部、侧面与地面高差，呈斜向俯看。 |
| `light.shading_appearance` | mixed | 世界连续体积明暗、技能亮边/透明几何与平面HUD共存。 |
| `representation.spatial_logic` | euclidean | 本组三帧道路、台阶、建筑与遮挡可用常规空间解释。 |
