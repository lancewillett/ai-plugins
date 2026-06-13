---
name: js-perf-audit
description: Audit any JS-heavy codebase for performance issues. Checks bundle weight, code splitting, selector memoization, rendering architecture, and performance infrastructure. Produces a findings report with severity ratings and recommendations.
argument-hint: "[path] [--focus area]"
allowed-tools: Read, Bash, Glob, Grep, Task, Write
user-invocable: true
---

# JS performance audit

Automated inspection of a JavaScript-heavy codebase based on the [JS-heavy performance inspection spec](https://sgom.es/posts/2026-02-13-js-heavy-approaches-are-not-compatible-with-long-term-performance-goals/).

## Arguments

- **path** (optional): Path to the codebase to audit. Default: current working directory.
- **focus** (optional): Specific section to audit (e.g., "bundle", "splitting", "selectors", "rendering", "infra"). Default: all sections.

## Workflow

Run all eight audit sections against the target codebase. For each, gather evidence programmatically, then produce a findings report.

### Step 1: Identify the JS architecture

Determine what you're working with:

1. **Build system**: Search for webpack configs, vite configs, rollup configs, gulp files, esbuild configs, tsconfig, package.json build scripts
2. **Framework**: Grep for React, Vue, Angular, Svelte, jQuery, Backbone imports
3. **Entry points**: Find main entry files from build config or package.json `main`/`module`/`browser` fields
4. **Output directory**: Find dist/, build/, out/ directories with built JS

```bash
# Quick architecture scan
find <path> -maxdepth 3 -name "webpack.config*" -o -name "vite.config*" -o -name "rollup.config*" -o -name "gulpfile*" -o -name ".babelrc" -o -name "tsconfig.json" 2>/dev/null | head -20
```

### Step 2: Bundle weight and composition

Measure what ships to users.

1. **Built bundle sizes**:
```bash
# Find and size JS bundles in output directories
find <dist-dir> -name "*.js" -exec ls -lh {} \; | sort -k5 -h -r | head -20
```

2. **Bundle analyzer availability**: Check if webpack-bundle-analyzer, source-map-explorer, or similar is installed
3. **Vendor vs. app code**: Check webpack splitChunks config for vendor chunk separation
4. **Duplicate dependencies**: Look for the same package imported from multiple entry points without shared chunks

**Thresholds:**
- Total initial JS: < 300 KB compressed for content-first, < 500 KB for productivity tools
- Largest single bundle: < 150 KB compressed
- Vendor/framework ratio: app code should be >= 50%

### Step 3: Dependency hygiene

Check for bloat and invisible growth.

1. **Heavy wholesale imports**:
```
Grep for: import .* from ['"]lodash['"]
Grep for: import .* from ['"]moment['"]
Grep for: import .* from ['"]@fortawesome
Grep for: require\(['"]lodash['"]\)
```

2. **CI bundle tracking**: Check `.github/workflows/`, `.circleci/`, CI config for size-limit, bundlewatch, bundlesize, or compressed-size-action
3. **Dependency count**: `npm ls --all 2>/dev/null | wc -l` or check package-lock.json size
4. **Dead dependencies**: Check if installed packages are actually imported in source (e.g., web-vitals installed but never called)
5. **Misplaced dependencies**: Check if test/dev-only packages (`@testing-library/*`, `prettier`, `source-map-explorer`) are in `dependencies` instead of `devDependencies` — they'll ship in production bundles

### Step 4: Code splitting and lazy loading

Check if the codebase loads features on demand.

1. **Dynamic imports**:
```
Grep for: import\(
Grep for: React\.lazy
Grep for: React\.Suspense or <Suspense
```

2. **Feature flag loading pattern**: Search for feature flags/capability checks that guard feature rendering but import the feature statically at the top of the file (anti-pattern)

3. **Store/state registration**: Check if all Redux stores, Vuex modules, or state atoms are registered at boot or lazily

4. **Route-based splitting**: Check router config for lazy-loaded route components

**Red flag:** Zero dynamic imports = zero code splitting. This is the single biggest opportunity in most codebases.

### Step 5: Rendering architecture

Determine how content reaches the user.

1. **SSR detection**:
```
Grep for: renderToString|renderToNodeStream|getServerSideProps|getStaticProps
Grep for: createSSRApp|renderToStream
Check for Next.js, Nuxt, Remix, Astro in dependencies
```

2. **CSR-only detection**: Look for `createRoot`, `ReactDOM.render`, `createApp().mount()` as the primary rendering entry
3. **Content without JS**: Check if main HTML template has meaningful content or just empty div containers
4. **Progressive enhancement**: Does the server deliver readable HTML, or does JS build the DOM?

### Step 6: Runtime performance

Check for patterns that degrade every user interaction. Adapt to the component model found.

**For functional component codebases (hooks):**

1. **Selector memoization rate**: Count selectors using `createSelector`/reselect vs. total selectors
2. **useMemo/useCallback usage**: Zero useMemo = all derived state recalculated every render
3. **React.memo coverage**: What % of presentational components use `memo()`?
4. **Reducer subtree rewrites**: Reducers spreading entire state on every action
5. **Context provider nesting**: Provider components at root with frequently-changing values

**For class component codebases:**

1. **PureComponent vs. Component ratio**: PureComponent provides shallow prop comparison. Count how many extend PureComponent vs. Component
2. **shouldComponentUpdate usage**: Classes without PureComponent or SCU re-render on every parent render
3. **Deprecated lifecycle methods**: `componentWillMount`, `componentWillReceiveProps`, `componentWillUpdate` cause double renders in React 18 strict mode. Count instances
4. **Unmemoized derived data in render()**: `.map()`, `.filter()`, `Object.keys()` in render methods recalculate every render

**For both:**

5. **Inline arrow functions in lists**: `.map()` callbacks creating new function refs in JSX (especially onClick, onChange)
6. **Prop drilling depth**: Trace the deepest prop chain from root to leaf. 5+ levels means state changes cascade re-renders through the entire subtree

### Step 7: Performance infrastructure

Check if the team can detect regression.

| Check | Search for |
|-------|-----------|
| Performance budgets | size-limit config, bundlewatch config, documented budgets |
| RUM | web-vitals library in deps, performance reporting endpoints |
| Synthetic testing | Lighthouse CI config (`.lighthouserc`), Playwright perf tests |
| Realistic throttling | CPU/network throttling in test configs |
| Bundle size in CI | CI workflows referencing bundle size tools |
| CrUX dashboards | Any reference to Chrome UX Report or field data |

### Step 8: Architecture fit

Evaluate whether the JS investment matches the product.

1. **Product type**: Content-first (reading) vs. productivity (editing) vs. hybrid
2. **Interactive surface area**: What % of pages require JS interactivity?
3. **Alternative patterns considered**: Search docs, ADRs, or comments for htmx, Interactivity API, View Transitions, partial hydration
4. **Project lifecycle**: Actively developed, maintenance mode, or deprecated? This changes recommendation severity — maintenance-mode projects may warrant minimal targeted fixes rather than architecture overhauls

## Output format

Write the findings report to a markdown file at the codebase root (or user-specified location).

Structure:

```markdown
# JS performance audit: [product name]

**Date:** [date]
**Codebase:** [path]
**Architecture:** [framework] + [build tool] + [rendering mode]

## Summary

[3-5 sentence overview with the most critical findings]

| Section | Status | Severity |
|---------|--------|----------|
| 1. Bundle weight | Pass/Fail/Partial | Critical/High/Medium/Low |
| 2. Dependencies | ... | ... |
| 3. Code splitting | ... | ... |
| 4. Rendering | ... | ... |
| 5. Runtime | ... | ... |
| 6. Infrastructure | ... | ... |
| 7. Maintainability | ... | ... |
| 8. Architecture fit | ... | ... |

## Findings

[Detailed findings per section with file paths, metrics, and evidence]

## Top 5 recommendations

[Ordered by impact, with specific files and changes]

## Files referenced

[Table of all files mentioned in findings]
```

## Severity guide

| Severity | Definition |
|----------|------------|
| Critical | Mid-tier devices can't use the product effectively |
| High | Measurable negative impact on Core Web Vitals |
| Medium | Contributes to performance debt; will compound |
| Low | Best practice gap; no current user impact |

## Tips

- Use parallel subagents (Task tool with Explore type) for independent audit sections to save time
- For large codebases, focus on entry points and work outward
- Built bundle sizes matter more than source file counts
- Runtime issues (selectors, re-renders) won't show up in bundle metrics — you need both
- When in doubt about severity, test on a throttled connection (Chrome DevTools → Network → Slow 3G, CPU → 4x slowdown)
