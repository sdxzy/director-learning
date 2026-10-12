# 设计说明

这次改的是阅读和导航，不是课文。正文仍是原来的中文；只改了壳子、样式，以及首页里两句已经对不上的使用说明（进度改为手动勾选，并写明可以搜索）。

站点仍然是纯静态文件：没有 CDN、没有构建、相对路径，`file://` 和 GitHub Pages 的 `/director-learning/` 都能打开。

## 参考与对应决定

**VitePress 文档布局**（[默认主题](https://vitepress.dev/reference/default-theme-config)，内容宽度见 [VPDoc.vue](https://github.com/vuejs/vitepress/blob/main/src/client/theme-default/components/VPDoc.vue)）。左侧可折叠目录、中间正文、右侧 “On this page” 大纲，以及页底上一篇 / 下一篇。VitePress 在有侧栏时把正文限制在约 688px。这里用 **720px**，因为正文字号 17px、行高 1.8，汉字是全角，稍宽一点仍大约落在 40 字一行。大纲只收正文里的 `h2` / `h3`（卡片标题不算），并用 `IntersectionObserver` 做 scroll-spy。窄屏时大纲收成正文上方的「本页目录」，避免三栏挤在一起。

**Docusaurus**（[提示框](https://docusaurus.io/docs/markdown-features/admonitions)、[colorMode](https://docusaurus.io/docs/api/themes/configuration)）。四种提示不再共用一条左边线：一句话记住（暖色）、小提示（蓝）、注意（黄）、练一练（绿）。颜色随浅色 / 深色主题变。「练一练」仍是原来的标题文字，由脚本把该标题和紧随的练习段落包进练习框，不改课文。主题默认跟随 `prefers-color-scheme`，只有读者手动切换才写入 `localStorage`；未选择时系统主题变化会跟着变。

**GitBook 提示块**（[Hint](https://gitbook.com/docs/creating-content/blocks/hint)）。同一页上的记住、提示、警告、练习用不同底色、边线和小标签区分，扫读时不用先读完句子才知道是哪一类。

**MDN**。正文用系统字体栈，把苹方、冬青、思源 / Noto、微软雅黑放在西文系统字体前面，这样中文不必下载 webfont。正文行高 1.8，标题级差大约是 2rem / 1.45rem / 1.15rem。链接、辅助文字和提示标签按正文底色分开配色，避免浅灰字落在浅底上。焦点只用 `:focus-visible`，并提供「跳到正文」。

**Stripe 文档**（[docs.stripe.com](https://docs.stripe.com/)）。顶栏保持很轻：半透明、细分割线、搜索是顶栏里的主操作，而不是再做一个大按钮。动效只留侧栏滑入、进度条和悬停边框，大约 160ms；`prefers-reduced-motion: reduce` 时关掉过渡和滚动平滑。

**Nextra 文档主题**。全站搜索做成命令面板：`Ctrl` 或 `⌘` + `K` 打开，方向键选择，Enter 进入，Esc 关闭。索引在 `js/search-index.js` 里，由页面脚本直接加载，不 `fetch`，所以 `file://` 不会被浏览器拦住。术语表页面自己的过滤框仍然只过滤当前表。

**可汗学院一类课程站**。每页底部有「我已学完本页」，记在本机。首页进度和侧栏底部的计数都按勾选计算，不再把「打开过」当成学完。页底上一章 / 下一章做成两张卡片，标明方向和标题。

## 没有做的事

没有引入组件框架、图标字体或搜索服务。目录树仍是原生 `<details>`，键盘和屏幕阅读器不用额外脚本。搜索是标题加正文的包含匹配，34 页足够，不需要分词引擎。
