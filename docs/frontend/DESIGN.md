# TechGap Frontend Design System

> Purpose: Define the v1 visual language and interaction tone for the TechGap frontend.

## Design Direction

TechGap should feel like a clean guided analytics product: credible enough for faculty and thesis review, but not plain, stale, or overly institutional. The interface should guide students through complex choices while presenting admin analysis with professional clarity.

Design principles:

- Clear first: every screen should make the next action obvious.
- Guided, not playful: use supportive structure and motion without gamified effects.
- Analytical, not cold: data-heavy views should still feel composed and approachable.
- Custom, not default shadcn: shadcn/ui provides accessible primitives, but TechGap owns the visual personality.

## UI Foundation

- Use Tailwind CSS for styling.
- Use shadcn/ui for accessible base primitives such as buttons, dialogs, tabs where needed, popovers, command menus, forms, tooltips, drawers, tables, and alerts.
- Customize shadcn components through TechGap variants, tokens, and composition. Do not ship unstyled default shadcn examples as final UI.
- Use Motion for React for coordinated step transitions, result reveals, expandable evidence panels, roadmap node expansion, and report section entry.
- Use CSS/Tailwind transitions for simple hover, focus, active, color, opacity, and shadow states.

## Visual Tone

Recommended direction: structured studio dashboard.

- Base surfaces should feel warm-neutral rather than stark white.
- Accent colors should be purposeful and limited.
- Panels should use soft borders, subtle shadows, and layered backgrounds.
- Important metrics should use bold numeric hierarchy.
- Roadmap and wizard screens may use more visual guidance than admin report screens.

Avoid:

- Purple-on-white generic SaaS styling.
- Default Material Design or default shadcn visual patterns.
- Overly playful illustrations, bouncing animations, confetti, or mascot-like UI.
- Dense spreadsheet layouts without hierarchy.
- Pure academic report styling for the whole product.

## Color Tokens

Use semantic tokens rather than raw colors in components.

| Token | Suggested Value | Use |
|---|---:|---|
| `bg-page` | `#F7F4EE` | Warm app background. |
| `bg-surface` | `#FFFFFF` | Cards, dialogs, tables, report sheets. |
| `bg-subtle` | `#EEF3F1` | Soft grouped regions and selected panels. |
| `ink` | `#172033` | Primary text and high-emphasis labels. |
| `muted` | `#687385` | Secondary text and helper copy. |
| `border` | `#D9E0E3` | Default borders and separators. |
| `spruce` | `#136F63` | Primary brand/action accent. |
| `spruce-soft` | `#DDEDE9` | Positive and selected backgrounds. |
| `amber` | `#D98C1F` | Warning, partial coverage, and attention states. |
| `coral` | `#D95F4A` | Missing gaps, destructive reset, and high-risk states. |
| `blueprint` | `#2E5E8C` | Evidence, links, and admin analytical accents. |

Accessibility rules:

- Body text must meet WCAG AA contrast.
- Do not rely on color alone for skill categories or score bands.
- Pair color with labels, icons, patterns, or count summaries.

## Typography

Use expressive but readable typography. Avoid default stacks such as Arial, Roboto, Inter, or unstyled system fonts as the final design identity.

Recommended pairing:

- Display/headings: `General Sans` or another geometric sans with strong headings.
- Body/UI: `Source Sans 3` or another highly legible humanist sans.
- Numeric labels: use tabular numbers through CSS features where available.

Type behavior:

- Use large, confident page headings on wizard and dashboard entry states.
- Use compact uppercase labels for metric metadata, not for long copy.
- Keep student explanation copy plain-language and short.
- Keep admin report copy more formal, but still scannable.

## Layout And Spacing

- Use a desktop-first responsive layout.
- Use a max-width content shell for guided student steps.
- Use a wider dashboard grid for admin pages.
- Keep the role selector spacious and visually memorable.
- Use consistent vertical rhythm between headings, helper text, form controls, and actions.
- Reserve dense tables for evidence and reports; use cards for decisions and summaries.

Recommended layout primitives:

- App shell with top brand bar and route-aware secondary actions.
- Student wizard shell with step indicator, content panel, helper rail when useful, and persistent bottom actions on mobile.
- Admin dashboard shell with selected track context, ordered sections, and optional sticky summary on desktop.
- Print report shell with page-like white surface, clear section breaks, and print-specific spacing.

## Motion Language

Use motion to clarify progression and reveal hierarchy.

Motion rules:

- Step transitions: short fade plus slight vertical movement.
- Result reveal: stagger high-level score, categories, then supporting evidence.
- Roadmap nodes: expand with height/layout animation and a soft opacity reveal.
- Evidence panels: slide/fade from the selected job context.
- Report page: minimal motion; prioritize print stability.

Timing defaults:

- Small state changes: 120-180ms.
- Step and panel transitions: 200-280ms.
- Staggered result reveals: 40-70ms between items.

Reduced motion:

- Respect `prefers-reduced-motion`.
- Replace layout movement with instant state changes or simple opacity changes.
- Never make animation required to understand state.

## Data Visualization

Charts should clarify, not decorate.

- Use metric cards for primary scores.
- Use segmented bars for skill categories and Bloom distributions.
- Use compact bar charts for top gaps and demand weights.
- Use tables or evidence cards for source-heavy admin details.
- Use roadmap node diagrams only where prerequisite relationships are meaningful.

Color mapping:

- Present: `spruce`.
- Partial: `amber`.
- Missing: `coral`.
- Future Curriculum Coverage: `blueprint`.
- Low confidence or sparse evidence: amber treatment with explicit label.

## Responsive Behavior

- Desktop is the primary target for admin dashboards and thesis/demo presentation.
- Student wizard must remain comfortable on mobile.
- On mobile, use single-column wizard screens, sticky bottom actions, collapsible evidence, and compact course filters.
- On mobile admin views, preserve content order and collapse dense sections instead of forcing wide tables.

Breakpoints should follow Tailwind defaults unless implementation discovers a concrete need for custom breakpoints.

## Accessibility

- All controls must be keyboard reachable.
- Form controls need visible labels and error messages.
- Step changes must preserve logical focus.
- Dialogs, drawers, popovers, and command menus should use shadcn/Radix accessibility behavior.
- Charts require adjacent text summaries.
- Print report content must be readable without color.
