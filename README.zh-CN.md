# Preflight Decks · 概念先行的幻灯片导演

[![CI](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Preflight Decks 社交卡片](./assets/social-card.png)

**概念先行的 HTML 幻灯片导演 skill。** 它解决的不是「丑」，而是上游失败：
没有观点、三版方案只是同一骨架换色、或者只在作者电脑上好看，到投影仪和
手机上就溢出崩版。

本 skill 是一个薄编排层：判断力与机械验收归自己，交付底盘复用
[frontend-slides](https://github.com/zarazhangrui/frontend-slides)（MIT）——
固定 1920×1080 舞台、单文件零依赖、就地编辑、PDF/链接导出、PPTX 转换。

## 看它工作

同一个简介，产出三版**结构真正不同**的真实预览——不是同一骨架换三种颜色。
你在像素上拍板，只有被选中的方向才会被做成完整 deck：

![三版概念门预览：安全预设、大胆模板、自定义 wildcard](./assets/demo-previews.png)

被选中的 wildcard 方向——一套「发布前飞行手册」——扩成 6 页 pitch deck。
下面这个 GIF 就是用仓库里的真实示例文件渲染的：

[![6 页示例 deck](./assets/hero-deck.gif)](./examples/preflight-decks-pitch.html)

每份 deck 随后都要通过 Playwright 在投影仪和手机尺寸下的机械验收。示例
deck 的成绩是 **6 页、0 错误、0 警告**：

![1280x720 与 390x844 双视口验收联系表](./assets/verification-contact-sheet.png)

30 秒体验：用浏览器打开
[`examples/preflight-decks-pitch.html`](./examples/preflight-decks-pitch.html)
（方向键翻页）。三版概念门预览在 [`examples/previews/`](./examples/previews/)。然后运行：

```bash
python3 scripts/verify-deck.py examples/preflight-decks-pitch.html
```

## 为什么需要它

Deck skill 大多在卖模板。真正的默认失败模式不是不美观，而是：做得不差但
没观点，或者版式只在作者屏幕上成立。本 skill 把三件事变强制：

1. **概念门**：先写出值得一讲的主张和从内容长出的视觉母题，并在全 deck
   之前看到三版结构真正不同的真实预览。
2. **评分回路**：每一版都基于渲染截图打分；概念不达标直接否决，执行再精致
   也救不回来。
3. **防弹底盘**：每份 deck 都是单文件固定舞台 HTML，由自动截图检查证明它
   在 1280×720 与 390×844 下都成立。

## 流程

```
0 需求清点   真实内容清单 + 演讲型/阅读型密度
1 概念门     一句话主张 → 三版真实预览 → 用户拍板 → Gate 文件
2 制作       基于 frontend-slides 固定舞台生产全 deck
3 评分回路   六维打分 → 修改 → 复评（达标线 7.5，无单项低于 6）
4 机械验收   scripts/verify-deck.py 零硬错误
5 交付       单个 HTML（可选 PDF / 在线链接）
```

## 安装

```bash
# 交付底盘（必需的 peer skill）
git clone https://github.com/zarazhangrui/frontend-slides \
  ~/.codex/skills/frontend-slides

# 本 skill
git clone https://github.com/MJorgin/preflight-decks \
  ~/.codex/skills/preflight-decks

# 验收脚本依赖
python3 -m pip install playwright pillow
python3 -m playwright install chromium
```

## 验收脚本

可对任意固定舞台 HTML deck 单独运行：

```bash
python3 scripts/verify-deck.py path/to/deck.html
```

产物写入 `.preflight-check/`：逐页截图（720p + 手机）、联系表、
`report.json`。检查项：舞台在手机上等比缩放且保持 16:9、无溢出/出界、
无空白页、无 lorem/占位符，并对通用字体栈给出警告。

退出码：`0` 通过（允许警告）、`2` 存在硬错误、`1` 工具错误。

## 边界

只做幻灯片：pitch、演讲、教学、内部汇报、PPTX → HTML。不做网站、产品原型
或独立产品宣传片。

## 致谢

站在两个 MIT 项目肩膀上的薄观点层：

- [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides)：
  固定舞台单文件底盘、模板与导出工具。
- [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design)：
  概念先行方法论、评审 rubric 与验收思维，蒸馏在本项目 references 中。

同作者另一个项目：[github-launch-studio](https://github.com/MJorgin/github-launch-studio)，
面向开源仓库发布就绪度的 Codex skill。本项目为独立社区项目，与上述上游无
附属关系。

## 许可证

MIT
