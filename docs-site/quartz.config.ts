// SPDX-FileCopyrightText: 2023 jackyzha0 and Quartz contributors
// SPDX-FileCopyrightText: 2026 FTEF contributors
// SPDX-License-Identifier: MIT
//
// Quartz configuration for the FTEF reading site (adapted from Quartz v4.5.2's default quartz.config.ts).
// Copied into the pinned Quartz checkout by docs-site/build.sh. No analytics, no web fonts, no CDN at runtime.
import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

const config: QuartzConfig = {
  configuration: {
    pageTitle: "FTEF",
    pageTitleSuffix: " | FTEF",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "en-US",
    baseUrl: "ftef.vdhome.be",
    ignorePatterns: [],
    defaultDateType: "modified",
    theme: {
      // "local": nothing is fetched; Inter is used when installed, else the system sans-serif.
      fontOrigin: "local",
      cdnCaching: false,
      typography: {
        header: "Inter",
        body: "Inter",
        code: "JetBrains Mono",
      },
      // Colours: brand/BRAND.md. Link colour (secondary) reaches 4.5:1 on the paper in both themes.
      colors: {
        lightMode: {
          light: "#F5F7FA",
          lightgray: "#DDE3EA",
          gray: "#5E6B7A",
          darkgray: "#3A4A5C",
          dark: "#0B2545",
          secondary: "#0E7C74",
          tertiary: "#0B2545",
          highlight: "rgba(18, 159, 149, 0.12)",
          textHighlight: "rgba(242, 165, 65, 0.35)",
        },
        darkMode: {
          light: "#1B2533",
          lightgray: "#2C3A4C",
          gray: "#9AA8B8",
          darkgray: "#C9D3DF",
          dark: "#F5F7FA",
          secondary: "#2CC4B8",
          tertiary: "#5B8BD0",
          highlight: "rgba(44, 196, 184, 0.14)",
          textHighlight: "rgba(247, 185, 85, 0.35)",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({ priority: ["frontmatter", "filesystem"] }),
      Plugin.SyntaxHighlighting({
        theme: { light: "github-light", dark: "github-dark" },
        keepBackground: false,
      }),
      // mermaid off: Quartz loads it from a CDN at runtime.
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false, mermaid: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents({ maxDepth: 3 }),
      Plugin.CrawlLinks({ markdownLinkResolution: "absolute" }),
      Plugin.Description(),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.ContentIndex({ enableSiteMap: true, enableRSS: false }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
    ],
  },
}

export default config
