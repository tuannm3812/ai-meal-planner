# Design standard — AI Meal Planner

The one design standard for everything this project makes: the React app, the
poster, the LinkedIn image, the slide deck and any page or document that shows
the product. If a piece of work departs from this file, change the work or
change this file. Don't let them drift.

The identity is **Kitchen green**. Colour values live in
[`frontend/tailwind.config.js`](frontend/tailwind.config.js); if the two ever
differ, that file wins and this one gets fixed. The app's flow and screens are
in [`docs/8_design.md`](docs/8_design.md) (DEC-29). What the poster and deck
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

| Token | Hex | Role |
| --- | --- | --- |
| `ground` | #F6F7F2 | Page and slide background |
| `surface` | #FFFFFF | Cards and readable surfaces |
| `ink` | #15291F | Text, headings, dark panels |
| `muted` | #4B5B52 | Supporting text |
| `line` | #DDE3DA | Borders and dividers |
| `accent` | #C8431F | Tomato: logo, primary action, the one highlight |
| `accent-text` | #B23A17 | Small tomato text on light backgrounds |
| `success-bg` / `success-fg` | #E3EFE6 / #1B5E3F | Positive result, always with a text label |
| `protein` | #2F6FAB | Protein data only |
| `carbs` | #9A6A12 | Carbohydrate data only |
| `fat` | #7A4E9C | Fat data only |

Aim for about 70% ground and white, 20% ink, under 10% tomato. Macro colours
never mean anything but their macro. Green never means medically safe. Tomato
never means an error. Estimate badges use #FBEBD6 with #7A4A0C text. Outside the app,
#ECEFE8 is allowed for neutral tracks and badges, #EEF4EF for panels, #9AA5A0 for baseline
results and #C9D3CC for secondary text on `ink`. The showcase uses a white canvas.

## 4. Type

- **App:** Bricolage Grotesque for headlines and big numbers; Inter for everything read.
- **Showcase (deck, poster, LinkedIn image):** Google Sans, chosen by Mike for a professional
  portfolio look, with Google Sans Code for code spans.
- No other typefaces. Authentic app screenshots keep their own type.

| Role | App |
| --- | --- |
| Title | 32–40 px, 700 |
| Big number | 32–40 px, 700 |
| Section heading | 22–24 px, 700 |
| Body | 16 px |
| Caption or label | 12–14 px |

Slide and poster sizes are in their own standards.

Put units next to numbers (629 kcal, 42 g). Don't write paragraphs in the display face.

## 5. Logo and icons

The project has one icon, the **plate mark**: a tomato ring around a tomato dot
([`logo-mark.svg`](frontend/src/assets/brand/logo-mark.svg)). Put it beside the
name "AI Meal Planner". Use it alone only where space is tiny.

- Don't stretch, rotate, recolour or add effects.
- Leave a quarter of its width clear on every side; never under 24 px.
- Prefer light backgrounds. On ink, check the contrast.

There is no icon set. Numbered ink circles do that job. If a piece truly needs
pictograms, use one outline set, 1.5 px stroke, in ink.

## 6. Layout and components

- Spacing steps: 8, 12, 16, 24, 32, 48 px. Keep related things close.
- Cards: white, a 1 px `line` border, 16–20 px corners, no heavy shadows, no
  gradients, no accent stripes along an edge, no rules under titles.
- Dark `ink` panels carry the one headline number on a surface.
- Badges: short text label, never colour alone.
- Charts: one series colour unless colour means something; label values directly.

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
- [ ] Only the tokens, typefaces and plate mark for that output are used.
- [ ] Tomato marks one focal point per surface, not counting the logo and paired markers.
- [ ] It reads at a glance: headline first, detail second.
