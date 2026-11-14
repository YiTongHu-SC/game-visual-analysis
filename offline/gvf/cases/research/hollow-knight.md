# 空洞骑士：三张真实发布图中的分层边缘与变化

核验：2026-10-21。观察合同与参数目录：0.2.0。本案例分析截图，不复刻游戏资产，也不把观察写成可直接生产的profile。

## 样本与来源

采用[官方Steam商店 R01](https://store.steampowered.com/app/367520/?l=english)图库顺序0、1、2，三张均已实际打开查看。原JPEG各1920×1080，URL、SHA256和下载记录见[图像清单](../image-manifest.json)。这是发布方提供的游戏内截图，**不是本次自行录制**；build、拍摄日期与图形设置未知，图库顺序也不表示连续时间。三图不代表全游戏、最新版本或全部资产。

- [HK00：暖光、多层建筑、白色大效果](../images/hollow-knight-00.jpg)
- [HK01：青绿背景、桥栏与不同体型角色](../images/hollow-knight-01.jpg)
- [HK02：红紫环境、观众与低处拖尾外观](../images/hollow-knight-02.jpg)

[Team Cherry产品页 R02](https://www.teamcherry.com.au/games)称其为手绘二维风格。[Unity制作回顾 R03](https://unity.com/made-with-unity/hollow-knight)介绍二维资产在三维环境分层，并以透明柔形处理光照。它支持制作背景，不提供这三帧的确切shader、投影或材质输入。[早期开发介绍 R04](https://www.teamcherry.com.au/blog/introducing-hollow-knight)的“接近单色”概括属于早期阶段，不能覆盖本组三图的青绿、橙光和红紫变化。

## 三图中的一致处与反例

00同时有暖橙光、较冷建筑与高亮白形；01青绿柔光更突出，小型主角和对手轮廓清楚，桥栏同样有密集锐利内线；02以红紫区域色组织环境，中景观众增加纹样密度，大角色清楚，但低处小型深色形象带模糊/拖尾外观。这里的“移动感”只是静态姿势和拖尾暗示，不确定实际速度、阶段或动画采样率。

“角色清楚边线、远背景柔化”是局部成立的观察，不能写成“所有角色永远锐利、所有背景都软、全局描边统一”。00平台、01桥栏和近处树壳、02中景观众仍有明确线条；白色效果和红粉柔形又不服从人物的深色边线方式。应分别描述角色、近景构件、中景装饰、远景、效果、HUD与状态。

## ROI证据

ROI格式为 `[x,y,w,h]`，是相对完整图像的0–1比例，不是线宽或面积测量结果。机器表逐项保留ROI及限度。

| 局部 | ROI | 实际可见内容 | 不能推出什么 |
| --- | --- | --- | --- |
| HK00主角 | 0.414,0.452,0.065,0.140 | 白面、双角、深色身体有清晰边界 | 固定px描边或统一shader |
| HK01桥栏 | 0.180,0.690,0.580,0.100 | 近景构件有密集内线 | 背景都软、都无描线 |
| HK02中景观众 | 0.350,0.480,0.480,0.250 | 重复纹样与轮廓仍清楚 | 全背景低细节 |
| HK02低处形象 | 0.440,0.730,0.200,0.140 | 深色形象和模糊/拖尾外观 | 快门角、冲刺时长、FPS |
| HK00效果 | 0.460,0.300,0.430,0.510 | 大白形、柔光与橙色辉光 | 闪白时长或Bloom实现 |
| 三图HUD | 0.040,0.040,0.370,0.180 | 左上图标/数字随样本变化 | 全部UI、字体文件或对比达标 |

## 逐12域总结

| 域 | 本组观察 | 未知或局部差异 |
| --- | --- | --- |
| 表征与媒介 | 虫形、武器、建筑可辨；侧向分层；官方确认手绘二维资产 | 2D风格不等于无三维环境；hand_drawn没有直接匹配的媒介枚举 |
| 造型与形体 | 大头小身、双角和有机曲线，建筑有尖角和直线 | 不同角色不套同一比例，没有批准尺度表 |
| 线条与边缘 | 人物、平台、桥栏及部分观众有内外线；远景/效果用不同边界 | 按层/对象/状态分工，不要求全屏同宽黑线 |
| 表面与材质 | 简洁人物填色与密集建筑纹样并存；官方支持手绘制作背景 | 不反演PBR、笔刷宽度或全部资产来源 |
| 色彩 | 青绿、暖/冷混合、红紫变化；白色面部和效果较突出 | 无源色板，不填精确L/C/h、色数或面积比 |
| 光照与阴影 | 图形暗部、连续柔光与发光样效果共存 | 可见明暗不同于技术模型；EV、AO、物理一致性未知 |
| 镜头与投影 | 可见观看方向为侧向 | 投影、FOV、俯角、距离和运动未知 |
| 构图与可读性 | 横向行走面、竖向建筑、局部白色焦点；02更拥挤 | 02深色小形象与前景竞争，不声称始终高可读 |
| 运动与动画 | 只有当前姿态与拖尾暗示 | 6个运动字段均unknown；官方传统动画说明不是本帧FPS |
| 特效与反馈 | 白色大效果、青绿亮点、红粉柔形各异 | 无事件时间轴，不验收反馈延迟和技能语义 |
| UI与文字 | 左上圆表计、面具图标、数字组成overlay | 不覆盖地图/菜单/对话，未测字高和对比比率 |
| 输出与处理 | 已知JPEG尺寸，可描述暗边与局部柔化 | 内部分辨率、抗锯齿、颗粒、色差与后期链未知 |

## 覆盖、误判和修订建议

[机器观察表](../observations/hollow-knight.json)包含全81项：35项有可见/官方文档证据，46项unknown，0项not_applicable。新增3个字段使本轮由78项扩为81项。没有把“此帧没看见”写成NA，也没有hard/soft、自动总分或虚构生产参数。

0–100范围只引用目录语义锚点，未制作项目批准校准片，不是实测百分比或官方评分。宽区间反映图与图、对象与对象的差异，不能取中点直接生产。

1. 规则增加视觉角色/深度层范围，区分人物、近景、中景、远景、VFX和HUD；“背景”仍需再细分。
2. 分开边缘形态、边缘可见性、透明度和时间变化。软边可能来自远景、效果或动作外观，一个edge_regularity轴不能包办。
3. 保留shading_appearance与light.model的分工；前者记录可见色块/渐变，后者需要工程来源。
4. 手绘作为明确描述保存，避免强行映射ink或paint；工艺与视觉母题不应混成一个枚举。
5. 官方早期介绍保留日期和范围，不能升级为最终全游戏的永久规则。

仍未验证全部区域、完整动作、完整UI、真实玩家辨识、最低分辨率、性能与AI复现能力。本例检验框架表达缺口，不是完整美术圣经。

`vfx.density`按0.2收窄后的静态空间语义解释：以完整画面比较占据范围和同时可见叠层；ROI只定位证据，不把框内占比当成全帧占比。原粗区间保留但未重新校准，不表示发生频率、持续时间或动态峰值。

## 全81项逐项表

下表与机器JSON同步；证据ROI、方法、置信度和限制以JSON中的逐项记录为准。

| 参数ID | 本组结论 | 观察依据或未知原因 |
| --- | --- | --- |
| `representation.mode` | 2.5d | 依据官方制作背景，符合字典2.5d限定定义。 |
| `representation.recognizability` | 50–75（语义档） | 虫形角色、武器、桥台和建筑部件可辨类别。 |
| `representation.depth_cues` | 50–75（语义档） | 遮挡、明暗、远层柔化和多层重叠提供深度。 |
| `representation.abstraction_strategy` | mixed | 角色简化夸张、背景装饰与图形高亮共存。 |
| `representation.source_medium` | unknown | 官方确认手绘数字资产，但枚举无直接hand_drawn，不能强指定ink、paint或mixed。 |
| `representation.semantic_load` | 25–50（语义档） | 角色外形较直接，资源图标和状态意义依赖约定。 |
| `form.naturalism` | 0–25（语义档） | 小身体、大面部、双角及非自然虫形结构主导角色。 |
| `form.proportion_exaggeration` | unknown | 未指定可复核的现实或设计比例基准；幻想形状本身不足以确定比例夸张档位。 |
| `form.shape_language` | mixed | 圆面/眼、有机壳体与尖角、竖柱、平台直线并存。 |
| `form.edge_roundness` | 50–75（语义档） | 角色多圆滑曲线，角与武器仍尖锐。 |
| `form.silhouette_complexity` | 25–50（语义档） | 主要角色大形较少，以角、披风、肢体提供识别。 |
| `form.scale_consistency` | unknown | 没有同类人物、门、道具的批准尺度表与同条件视图，无法给一致度评分。 |
| `form.anatomy_strategy` | exaggerated | 保留头身肢体线索并显著改变现实比例。 |
| `line.usage` | selective | 角色及近景有内外线；远景、白色效果、柔光采用其他边界。 |
| `line.width_px` | unknown | 未按统一协议沿轮廓法线逐像素取样；JPEG重采样/软边影响线宽，不能凭观看填精确px。 |
| `line.weight_variation` | 25–50（语义档） | 主轮廓、部分内线、近景装饰及HUD有粗细差别。 |
| `line.edge_regularity` | 50–75（语义档） | 角色和桥栏边界连续明确，背景存在柔化和绘画式变化。 |
| `line.color_mode` | mixed | 深色主线、受区域色影响的远景线与高亮边界共存。 |
| `line.inner_density` | 25–75（语义档） | 主角内线少，桥栏、衣褶和观众更密。 |
| `surface.material_physicality` | unknown | 缺少同表面的多视角、多光照与实测材质参照；单帧不能验证反射/透射响应。 |
| `surface.detail_density` | 25–75（语义档） | 简洁人物填色与较密建筑、衣褶、观众并存。 |
| `surface.texture_mode` | hand_painted | 官方文档支持手绘资产的制作背景。 |
| `surface.brush_visibility` | unknown | 不能可靠区分笔触、纹理图案、光照与JPEG压缩；不把全部细节当笔刷痕迹。 |
| `surface.brush_scale_px` | unknown | 没有可稳定辨认并量取的笔触集合；屏幕纹理尺度不等于源笔刷宽度。 |
| `surface.roughness` | unknown | 需要源材质/着色器定义；单帧高光不能唯一反演PBR粗糙度输入。 |
| `surface.metallic` | unknown | 缺少源材质或明确技术资料；颜色和高亮不能唯一确定金属度输入。 |
| `color.palette_mode` | unknown | 未取得源色板及用途分工合同；最终场景色彩关系不能直接等同受控配色策略。 |
| `color.palette_colors` | unknown | 没有原始受控色板；JPEG、光照和渐变中的像素色数不等于色板色数。 |
| `color.saturation` | 25–75（语义档） | 00较柔多色配高亮，01青绿鲜明，02红紫突出。 |
| `color.value_range` | unknown | 没有关键区域遮罩与OKLCH采样协议，也未实际计算明度跨度；不凭观看猜数。 |
| `color.palette_lightness` | unknown | 没有源色板，JPEG亮暗不等于主色板OKLCH L。 |
| `color.palette_chroma` | unknown | 没有源色板和颜色管理条件，鲜艳感不等于主色板OKLCH C。 |
| `color.palette_hue` | unknown | 没有主色选择规则与源色板，三帧区域变化不能压成精确主色相角。 |
| `color.accent_area` | unknown | 未定义强调色掩码、阈值和分母；光晕/渐变/UI未形成面积测量。 |
| `color.temperature_bias` | contextual | 三图分别呈暖/冷混合、青绿和红紫气氛。 |
| `light.physicality` | unknown | 缺少现实光照参照及多条件测试；有阴影/亮光不能证明物理一致性。 |
| `light.model` | unknown | 多种方法能实现相同明暗；没有这些截图使用的着色/灯光配置。 |
| `light.shadow_hardness` | unknown | 暗部混合描线、画入阴影和柔光，未分离出可独立量判的投射阴影过渡。 |
| `light.contrast` | 50–75（语义档） | 白面部和高亮效果对深色前景形成显著明暗组织。 |
| `light.exposure_ev` | unknown | 缺场景曝光基线、色调映射与源HDR数据；JPEG不能提供EV补偿。 |
| `light.emissive_prominence` | 25–100（语义档） | 01亮点局部，00白形和02红粉效果对注意力影响更大。 |
| `light.ambient_occlusion` | unknown | 暗缝/接触暗部可能来自贴图、灯光或后期，不能区分AO贡献。 |
| `camera.projection` | unknown | 不同场景的单视图不能唯一标定投影矩阵；侧看/俯看不等于正交或透视。 |
| `camera.elevation_deg` | unknown | 缺少场景坐标、相机姿态和校准几何，不能给精确俯仰角。 |
| `camera.vertical_fov_deg` | unknown | 没有相机标定、投影类型与参照尺寸，不能推垂直视场角。 |
| `camera.distance_m` | unknown | 没有世界单位、主体尺寸和相机配置，像素占高不能换算米。 |
| `camera.movement` | unknown | 三张不是连续时间序列，无法区分固定、跟随、自由或脚本运动。 |
| `camera.distortion` | unknown | 没有已知直线/成像参照；未见明显畸变不能填0。 |
| `composition.focal_hierarchy` | 50–75（语义档） | 白面、对手与效果成为焦点；02复杂背景增加竞争。 |
| `composition.negative_space` | unknown | 未声明留白/有效视觉空间的遮罩和分母；低细节不等于空白面积。 |
| `composition.depth_layers` | unknown | 虽可见遮挡，但未定义离散层计数协议；可见层不是引擎图层数。 |
| `composition.density` | 50–75（语义档） | 三图有层叠装饰；01上部较疏，02观众与近景更密。 |
| `composition.alignment` | mixed | 水平行走面、竖向建筑、02中央轴线和斜向效果并存。 |
| `composition.subject_separation` | 25–75（语义档） | 00/01白色角色较突出，02深色小形象与近景/效果叠加。 |
| `motion.naturalism` | unknown | 静帧不包含时序、速度、受力与惯性，姿态不能替代运动观察。 |
| `motion.timing` | unknown | 不是连续回放，不能区分插值、保持、跳变或混合时间组织。 |
| `motion.animation_fps` | unknown | 截图没有姿态更新的时间戳序列；交付图尺寸不说明动作/渲染FPS。 |
| `motion.squash_stretch` | unknown | 没有同对象基准形和连续动作，不能证明动态挤压拉伸幅度。 |
| `motion.anticipation_ms` | unknown | 缺主动作及预备阶段的逐帧时间证据，不能填写毫秒。 |
| `motion.secondary_motion` | unknown | 缺主体/附属部件的连续相位关系，不能判断跟随运动显著度。 |
| `vfx.density` | 25–75（语义档） | 静帧中白色攻击样形、红粉效果与光点的全帧空间占据和可见叠层不同；保留粗区间但未重校准，不判断频率或持续时间。 |
| `vfx.bloom` | 25–75（语义档） | 亮区周围有软扩散；00/02较明显，01多局部光点。 |
| `vfx.motion_blur_shutter` | unknown | 条带/软形/拖尾可由绘画、粒子或后期生成，不能反推快门角。 |
| `vfx.screen_shake_px` | unknown | 没有前后帧稳定参照，不包含相机震动位移序列。 |
| `vfx.hit_flash_ms` | unknown | 没有命中事件及前后时间轴，亮白区域不证明受击闪白或时长。 |
| `vfx.semantic_color` | unknown | 单帧不足确定跨技能、阵营和状态的稳定颜色语义映射。 |
| `ui.integration` | overlay | 左上HUD与场景深度/区域底色分开保持位置。 |
| `ui.typography` | serif | 资源数字可见细粗变化与衬线式字形。 |
| `ui.min_font_px` | unknown | 未量可见字身像素高度，也未覆盖所有关键文字，不能报最小字号。 |
| `ui.text_contrast` | unknown | 没有选前景/背景采样对和线性化亮度计算；眼看清楚不是对比比率。 |
| `ui.information_density` | 25–50（语义档） | 常驻信息集中角落，世界画面占大部分。 |
| `ui.component_shape` | mixed | 圆表计、面具状图标、尖弧装饰和数字并列。 |
| `presentation.resolution_strategy` | unknown | JPEG尺寸不是内部渲染、动态分辨率或整数放大策略。 |
| `presentation.pixel_grid_px` | unknown | 没有源逻辑网格与缩放链，最终像素不能反推底层网格。 |
| `presentation.antialiasing` | unknown | 平滑可来自源图、缩放、压缩或多种抗锯齿，没有底层设置资料。 |
| `presentation.grain` | unknown | JPEG噪声、表面信息与绘画痕迹难分，无连续/无压缩参照确认颗粒。 |
| `presentation.chromatic_aberration_px` | unknown | 缺成像标定和通道位移测量；彩色效果边缘不自动等于镜头色差。 |
| `presentation.vignette` | 25–75（语义档） | 周边/前景较暗，01中心亮，02底边深色形体框景。 |
| `camera.view_orientation` | side | 角色和行走面以侧向横截面观看。 |
| `light.shading_appearance` | mixed | 人物色块、结构暗部、背景连续柔光与扩散共存。 |
| `representation.spatial_logic` | euclidean | 本组平台、立柱与遮挡可按常规层叠空间解释。 |
