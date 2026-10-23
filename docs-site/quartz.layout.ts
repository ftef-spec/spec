// SPDX-FileCopyrightText: 2023 jackyzha0 and Quartz contributors
// SPDX-FileCopyrightText: 2026 FTEF contributors
// SPDX-License-Identifier: MIT
//
// Page layout for the FTEF reading site (adapted from Quartz v4.5.2's default quartz.layout.ts).
import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [],
  footer: Component.Footer({
    links: {
      "Source and issues": "https://github.com/ftef-spec/spec",
      Discussions: "https://github.com/ftef-spec/spec/discussions",
      "Report a security flaw": "https://github.com/ftef-spec/spec/security/advisories/new",
      Licences: "https://github.com/ftef-spec/spec#licence",
    },
  }),
}

export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    Component.ContentMeta({ showReadingTime: false }),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [{ Component: Component.Search(), grow: true }, { Component: Component.Darkmode() }],
    }),
    Component.Explorer({
      title: "Contents",
      // Reading order, not the alphabet: specification, glossary, decisions, then the rest.
      sortFn: (a, b) => {
        const order = ["spec", "glossary", "decisions", "review", "roadmap"]
        const ia = order.indexOf(a.slugSegment)
        const ib = order.indexOf(b.slugSegment)
        if (ia !== -1 || ib !== -1) return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib)
        return a.displayName.localeCompare(b.displayName, undefined, { numeric: true, sensitivity: "base" })
      },
    }),
  ],
  right: [
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
    Component.Graph(),
  ],
}

export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta({ showReadingTime: false })],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [{ Component: Component.Search(), grow: true }, { Component: Component.Darkmode() }],
    }),
    Component.Explorer({
      title: "Contents",
      // Reading order, not the alphabet: specification, glossary, decisions, then the rest.
      sortFn: (a, b) => {
        const order = ["spec", "glossary", "decisions", "review", "roadmap"]
        const ia = order.indexOf(a.slugSegment)
        const ib = order.indexOf(b.slugSegment)
        if (ia !== -1 || ib !== -1) return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib)
        return a.displayName.localeCompare(b.displayName, undefined, { numeric: true, sensitivity: "base" })
      },
    }),
  ],
  right: [],
}
