# Design standard — AI Meal Planner

The one design standard for everything this project makes: the React app, the
poster, the LinkedIn image, the slide deck and any page or document that shows
the product. If a piece of work departs from this file, change the work or
change this file. Don't let them drift.

The identity is **Kitchen green**, in its "Flat kitchen" edition since 22 November
2026 (DEC-37). Colour values live in
[`frontend/tailwind.config.js`](frontend/tailwind.config.js); if the two ever
differ, that file wins and this one gets fixed. The app's flow and screens are
in [`docs/8_design.md`](docs/8_design.md) (DEC-29) and the kitchen-app spec,
[`docs/superpowers/specs/2026-11-22-react-kitchen-app-design.md`](docs/superpowers/specs/2026-11-22-react-kitchen-app-design.md). What the poster and deck
say is in [`docs/showcase/`](docs/showcase/README.md), which also holds the strict
[slide](docs/showcase/slides/DESIGN.md) and [poster](docs/showcase/DESIGN.md) standards.

## 1. Principles

1. **Lead with the person's task.** Say what it does for them before how it works.
2. **One message per surface.** A slide, a card or a poster block makes one point.
3. **Every number is real.** It comes from the service or from a file in this
   repo, with its unit, and says how it was produced.
4. **Say what is estimated.** Never hide that nutrition or prices are estimates,
   and never imply medical advice.
5. **Quiet page, one loud thing.** Tomato marks the single place the eye should land. The
   logo and paired reference markers on slides don't count toward this.

## 2. Voice

Warm, practical and plain. Not a clinician, not a fitness coach. Never judge
food or bodies. Use sentence case and full sentences. Say "healthy ranges" to a
general audience and keep "AMDR" for technical ones. The short descriptor is
**One meal. Clear nutrition. A shopping list.** The headline is **Say what you
crave. Get a meal that fits you.**

## 3. Colour

Every app colour lives in one file, [`frontend/src/theme/tokens.js`](frontend/src/theme/tokens.js)
(DEC-38). Tailwind maps it to the class names below, and the SVG charts and dish drawings
import it. A guard test (`tokens.test.js`) fails on a raw hex value anywhere else, on
Tailwind's stock colours (`red-50`, `gray-300` and the like), and on a macro colour used
outside the plan feature. The tokens fall into five groups.

| Group | What it is for |
| --- | --- |
| Neutrals | Text, lines and the grounds pages sit on |
| Brand | Tomato for the one call to action; leaf and lime for icons |
| Status | A background and its text for success, estimates and errors |
| Data | Viridis for charts, its three macro stops, and the range band |
| Food | Only inside the dish drawings, never in the interface |

| Token | Hex | Role |
| --- | --- | --- |
| `ground` | #EEF4EF | App page background (light green) |
| `tint` | #DCEEE1 | App section tints and illustration grounds |
| `surface` | #FFFFFF | Cards and readable surfaces |
| `ink` | #15291F | Text, headings, dark panels |
| `ink-raised` | #1F3D2E | The blob shape on an `ink` banner |
| `on-ink-muted` | #C9D3CC | Secondary text on `ink` |
| `muted` | #4B5B52 | Supporting text |
| `line` | #DDE3DA | Borders and dividers |
| `accent` | #C8431F | Tomato: logo, primary action, the one highlight |
| `accent-text` | #B23A17 | Small tomato text on light backgrounds |
| `leaf` | #1B5E3F | Icons and small labels on light grounds; hover rings |
| `lime` | #7AD151 | Icons, focus rings and the saved state on `ink` |
| `success-bg` / `success-fg` | #E3EFE6 / #1B5E3F | Positive result, always with a text label |
| `estimate-bg` / `estimate-fg` | #FBEBD6 / #7A4A0C | Estimate badges and notices |
| `danger-bg` / `danger-fg` | #FBE4DD / #9B2C12 | A failed request or error notice |
| `danger-on-ink` | #FFD2BC | Error text on `ink` |
| `protein` | #440154 | Protein data only (Viridis) |
| `carbs` | #2A788E | Carbohydrate data only (Viridis) |
| `fat` | #22A884 | Fat data only (Viridis) |
| `viridis-1` to `viridis-6` | #440154 #414487 #2A788E #22A884 #7AD151 #FDE725 | Categorical chart series, in order; the calorie ring is `viridis-2` |
| `band` | #C6E3CF | The recommended range behind the balance bars |

Aim for about 70% ground and white, 20% ink, under 10% tomato. Charts use Viridis,
the owner's choice: the macro colours are its three darker stops, each at least 3:1
on white, and a categorical series takes `viridis-1` onward in order, always with a
text label. `viridis-5` and `viridis-6` are fills on `ink` or next to a label, never
text on white. On `ink`, protein uses #B9A3C8 so it stays visible. Macro colours never
mean anything but their macro. Green never means medically safe. Tomato never means an
error; errors use the `danger` pair. Disabled buttons use `line` with `muted` text. The showcase keeps its own palette: #F6F7F2
for slide grounds, #ECEFE8 for neutral tracks and badges, #9AA5A0 for baseline results,
and a white canvas.

## 4. Type

- **App:** Bricolage Grotesque ExtraBold (800) for headlines and big numbers; Inter for
  everything read.
- **Showcase (deck, poster, LinkedIn image):** Google Sans, chosen by Mike for a professional
  portfolio look, with Google Sans Code for code spans.
- No other typefaces. Authentic app screenshots keep their own type.

| Role | App |
| --- | --- |
| Title | 40–58 px, 800 |
| Big number | 28–40 px, 800 |
| Section heading | 22–26 px, 800 |
| Body | 16 px |
| Caption or label | 12–14 px |

Slide and poster sizes are in their own standards.

Put units next to numbers (629 kcal, 42 g). Don't write paragraphs in the display face.

## 5. Logo and icons

The mark is the **plate on a calendar**: a green calendar outline around a tomato plate
([`logo-mark.svg`](docs/showcase/slides/assets/logo-mark.svg), and a white-outline
[dark version](docs/showcase/slides/assets/logo-mark-dark.svg)). Mike chose it on
6 November 2026 for the showcase. The app still uses the earlier plate mark
([`logo-mark.svg`](frontend/src/assets/brand/logo-mark.svg)) until a separate app change.

Put it beside the name "AI Meal Planner". Use it alone only where space is tiny.

- Don't stretch, rotate, recolour or add effects. Use the dark version on `ink`.
- Leave a quarter of its width clear on every side; never under 24 px.
- It stands for a planned meal, not a weekly calendar feature, so don't imply one.

**Icons:** the app uses one outline set, [`lucide-react`](https://lucide.dev) (ISC),
always through the `Icon` component in `frontend/src/components/icons/` (DEC-38). It
fixes the rest:

- One stroke, 1.75, with round caps and joins.
- Three sizes: `sm` 20 px inside buttons and links, `md` 24 px for navigation, field
  labels and notices, `lg` 32 px beside section headings, list headings and stars.
- Colour comes from the surface, never from the meaning: `light` is `leaf` on ground,
  tint and white cards; `ink` is `lime` on the dark banners and top bar; `current` takes
  the text colour inside a button or notice. Never a macro colour, never tomato.
- No tile or circle behind an icon. An icon sits next to a word unless the control has
  an accessible name, and it is hidden from screen readers.

The guard test fails on a Lucide import outside that folder and on a hand-set icon
size or stroke. Slides and posters keep numbered ink circles.

**Illustrations:** flat food drawings, one for each kind of dish (rice bowl, stir fry,
noodles, pasta, curry, soup, salad, taco or wrap, eggs and toast, oats, plate, bowl).
They use no outlines and no gradients, and they are hidden from screen readers. They
stand for a kind of dish, never a photo of the meal; the service has no photos. One
soft blob shape may sit behind a banner illustration.

## 6. Layout and components

- Spacing steps: 8, 12, 16, 24, 32, 48 px. Keep related things close.
- Cards: white with no border on the green ground in the app (a 1 px `line` border on
  the showcase's white canvas), 24 px corners, no heavy shadows, no gradients, no
  accent stripes along an edge, no rules under titles.
- Dark `ink` banners open each app page and carry its headline; dark `ink` panels carry
  the one headline number on a surface.
- Badges: short text label, never colour alone.
- Charts: one series colour unless colour means something; label values directly. The
  app's plan page draws a calorie ring, a macro donut, range bars over a green band and a
  stacked bar of where the calories come from, all plain SVG.

## 7. Output specs

| Output | Standard |
| --- | --- |
| App | `max-w-6xl` shell, 16 px phone gutter, 24 px wider; [`docs/8_design.md`](docs/8_design.md) |
| Slide deck | [`docs/showcase/slides/DESIGN.md`](docs/showcase/slides/DESIGN.md) |
| Poster and LinkedIn image | [`docs/showcase/DESIGN.md`](docs/showcase/DESIGN.md) |

## 8. Accessibility

Text keeps at least 4.5:1 contrast, or 3:1 at large display sizes. Nothing relies
on colour alone. Every image has alt text. Focus stays visible in the app, and
the app works by keyboard and screen reader.

## 9. Before you ship

- [ ] Every number traces to the [fact sheet](docs/showcase/README.md#fact-sheet) or to the service.
- [ ] Estimates and "not medical advice" are stated where they apply.
- [ ] Only the tokens, typefaces and mark for that output are used.
- [ ] Tomato marks one focal point per surface, not counting the logo and paired markers.
- [ ] It reads at a glance: headline first, detail second.
