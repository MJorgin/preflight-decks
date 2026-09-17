# Launch posts — review before posting

Nothing here auto-posts. All drafts are human-review-only. Attach
`assets/hero-deck.gif` (or the MP4 screen recording) and
`assets/demo-previews.png`.

## X / English — main launch

I kept getting decks that were *fine* and said nothing — or overflowed on the projector.

So I built Preflight Decks, an AI skill that refuses to start from a template:

1️⃣ write the one-sentence idea
2️⃣ choose from 3 structurally DIFFERENT real previews
3️⃣ build on a fixed 1920×1080 stage
4️⃣ get scored (weak concept = veto)
5️⃣ Playwright verifies it at 720p AND phone size, 0 errors

Open source, MIT, builds on @zarazhangrui's frontend-slides chassis and the concept-first method from huashu-design.

github.com/MJorgin/preflight-decks

## X / English — alt (maker thread hook)

The best AI slide decks I saw all failed the same two tests:
- swap the logo for a competitor's → deck still works (= no concept)
- open it on your phone → layout breaks

Preflight Decks makes both failures impossible before you design a single slide:

[GIF]

## Hacker News — Show HN

Title: Show HN: Preflight Decks – concept gate + screen verification for AI-made slide decks

Body:
AI coding agents can now produce beautiful slide decks in one prompt. The
failure mode moved: decks are rarely ugly anymore, they are empty (swap the
company name and nothing changes — three "directions" are one skeleton in
three colors) or fragile (perfect on the author's laptop, overflowing on the
projector or a phone).

Preflight Decks is an open-source "director" skill for Codex/Claude Code
that inserts two hard gates into deck generation:

1. A concept gate borrowed from design-studio critique: the deck must state
   its one-sentence argument and a motif grown from the content; the agent
   must render three structurally different preview slides (a safe preset, a
   bold template, a custom wildcard) and the user picks on actual pixels.
2. A mechanical verifier: Playwright opens the deck at 1280×720 and 390×844,
   navigates every slide, and fails on overflow, reflowed (non-16:9) phone
   stages, blank slides, and placeholder text, emitting screenshots and a
   JSON report.

Rendering stays on the excellent frontend-slides fixed-stage chassis (peer
dependency), and the critique methodology is distilled from huashu-design —
both MIT. The repo includes a six-slide example that dogfoods the whole
pipeline, including the three previews.

Would love feedback, especially from people who present weekly.
github.com/MJorgin/preflight-decks

## V2EX / 中文

标题：做了个 Codex Skill：给 AI 做幻灯片加了两道硬门——概念门 + 双屏机械验收

正文：
现在让 AI 做一套幻灯片已经很快了，痛点也变了：不是丑，而是
1）没观点——把 logo 换成竞品名字，整套照样成立；
2）假选择——所谓三版方案其实是同一骨架换三种颜色；
3）只在作者电脑上成立——上投影仪或手机就溢出、重排。

我做了 Preflight Decks，一个「幻灯片导演」skill，在生成流程里插了两道硬门：

- 概念门：必须先写出一句话主张和从内容长出的视觉母题；Agent 要真的渲染出
  三版结构不同的预览页（安全预设 / 大胆模板 / 从内容长出来的 wildcard），
  你看着像素拍板后才允许做全片。
- 机械验收：Playwright 用 1280×720 和 390×844 逐页打开 deck，溢出、手机端
  非 16:9 重排、空白页、占位符直接判红，输出截图和 JSON 报告。

渲染底盘复用了 frontend-slides 的固定舞台单文件方案，方法论蒸馏自
huashu-design，两者都是 MIT。仓库里有一套 6 页示例 deck（就是它自己的
发布 pitch），连同三版预览一起 dogfood 了整条流水线，实测 0 错误。

欢迎每周要做汇报/路演的朋友提反馈：
github.com/MJorgin/preflight-decks

## 即刻 / 中文短帖

AI 做幻灯片的新问题：不是丑，是没观点 + 上投影就崩。

给我的 Codex 加了个「发布前体检」skill：先过概念门（一句话主张 + 三版结构真不同的预览），再用 Playwright 在投影仪和手机尺寸逐页验收，0 错误才交付。开源 MIT，自己的发布 deck 就是它验的。

附 GIF / 链接。

## Reddit candidates

- r/ClaudeAI — "A skill that makes Claude present 3 real deck directions before building"
- r/ArtificialIntelligence (Showcase weekend thread)
- r/webdev — fixed 1920×1080 stage scaling + automated overflow detection

## Awesome-list / directory targets (PR after 24h of feedback)

- Search GitHub for lists matching "claude skills" / "codex skills" /
  "awesome agent skills"; submit under presentation/design categories.
- CoWork, agentskills.io, and similar skill directories if they accept
  community submissions.
- Upstream strategy: open an issue/PR in frontend-slides proposing
  Preflight Decks as a "concept + verification layer" companion (it is a
  peer skill, not a fork).
