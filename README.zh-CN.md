# Preflight Decks · 发布前体检式幻灯片导演

一个**概念先行的 HTML 幻灯片导演 skill**。它解决的不是「丑」，而是上游
失败：没有观点、三版方案只是同一骨架换色、或者在作者电脑上好看但到投影
仪和手机上就溢出崩版。

本 skill 是一个薄编排层：判断力与机械验收归自己，交付底盘复用
[frontend-slides](https://github.com/zarazhangrui/frontend-slides)（MIT）——
固定 1920×1080 舞台、单文件零依赖、就地编辑、PDF/链接导出、PPTX 转换。


[![CI](https://github.com/MJorgin/preflight-decks/actions/workflows/ci.yml/badge.svg)](https://github.com/MJorgin/preflight-decks/actions/workflows/ci.yml)
## 为什么需要它

Deck skill 大多在卖模板。真正的默认失败模式不是不美观，而是：做得不差
但没观点，或者版式只在作者屏幕上成立。本 skill 把三件事变强制：

1. **概念门（Concept Gate）**：先写出一句话主张和从内容长出的视觉母题，
   并看到三版**结构真正不同**的真实预览，才允许做全片。
2. **评分回路（Critique Loop）**：每一版都基于渲染截图打分；概念不达标
   直接否决，执行再精致也封顶。
3. **防弹底盘**：每份 deck 都是单文件固定舞台 HTML，并用脚本证明它在
   1280×720 与 390×844 下都成立。

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

## 使用

直接让 Agent 做幻灯片（融资 pitch、演讲、内部汇报、PPTX 转网页均可）。
你只会在看到三版真实预览后做选择；验收脚本不通过，流程不算完成。

也可以对任意固定舞台 HTML deck 单独运行验收：

```bash
python3 scripts/verify-deck.py path/to/deck.html
```

产物写入 `.preflight-check/`：逐页截图（720p + 手机）、联系表、
`report.json`。检查项：舞台在手机上等比缩放且保持 16:9、无溢出/出界、
无空白页、无 lorem/占位符，并对通用字体栈给出警告。

## 边界

只做幻灯片：pitch、演讲、教学、内部汇报、PPTX → HTML。不做网站、产品
原型或独立产品宣传片。

## 致谢

本 skill 是站在两个 MIT 项目肩膀上的薄观点层：

- [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides)：
  固定舞台单文件底盘、模板与导出工具。
- [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design)：
  概念先行方法论、评审 rubric 与验收思维，蒸馏在本项目 references 中。

感谢两位作者。本项目为独立社区项目，与上述上游无附属关系。

## 许可证

MIT
