# Design standard — AI Meal Planner

The one design standard for everything this project makes: the React app, the
poster, the LinkedIn image, the slide deck and any page or document that shows
the product. If a piece of work departs from this file, change the work or
change this file. Don't let them drift.

The identity is **Kitchen green**. Colour values live in
[`frontend/tailwind.config.js`](frontend/tailwind.config.js); if the two ever
differ, that file wins and this one gets fixed. The app's flow and screens are
in [`docs/8_design.md`](docs/8_design.md) (DEC-29). What the poster and deck
say is in [`docs/showcase/README.md`](docs/showcase/README.md).

## 1. Principles

1. **Lead with the person's task.** Say what it does for them before how it works.
2. **One message per surface.** A slide, a card or a poster block makes one point.
3. **Every number is real.** It comes from the service or from a file in this
   repo, with its unit, and says how it was produced.
4. **Say what is estimated.** Never hide that nutrition or prices are estimates,
   and never imply medical advice.
5. **Quiet page, one loud thing.** Tomato marks the single place the eye should land.

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
never means an error. Estimate badges use #FBEBD6 with #7A4A0C text.

## 4. Type

- **Bricolage Grotesque** for headlines, slide titles and big numbers.
- **Inter** for everything read: body, labels, tables, captions.
- No other typefaces. The app bundles both; both are on Google Fonts, so they
  work in Google Slides. On a machine without them, keep the layout and let
  system sans-serif stand in.

| Role | App | Slides (16:9) | Poster (1200 px wide) | LinkedIn (1080 px wide) |
| --- | --- | --- | --- | --- |
| Title | 32–40 px, 700 | 30–32 pt, 700 | 64–76 px, 800 | 76–84 px, 800 |
| Big number | 32–40 px, 700 | 54–66 pt, 800 | 96–112 px, 800 | 84 px, 800 |
| Section heading | 22–24 px, 700 | 18–20 pt, 700 | 28–32 px, 700 | not used |
| Body | 16 px | 14–18 pt | 16–20 px | 18–22 px |
| Caption or label | 12–14 px | 11–12 pt | 14 px | 14 px |

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

| Output | Size | Structure |
| --- | --- | --- |
| Poster | 1200 × 1800 px at 2× (2:3, prints at A3 or A2) | Logo, headline, meal card, four steps, result, footer; about 90 words |
| LinkedIn image | 1080 × 1350 px at 2× (4:5) | Headline, meal card, steps and result side by side, footer |
| Slide deck | 16:9, 12 slides, 10 minutes | Dark title and closing slides, light content slides |
| App | `max-w-6xl` shell, 16 px phone gutter, 24 px wider | You → Craving → Your plan |

**Slides.** A slide title is the slide's point as a sentence, with no full stop.
At most about 30 words on screen; the rest goes in speaker notes. Every slide
has a visual. Content titles sit in the same place on every slide, and the logo
and page number sit on the layout, not on each slide.

## 8. Accessibility

Text keeps at least 4.5:1 contrast, or 3:1 at large display sizes. Nothing relies
on colour alone. Every image has alt text. Focus stays visible in the app, and
the app works by keyboard and screen reader.

## 9. Before you ship

- [ ] Every number traces to the fact sheet in `docs/showcase/README.md` or to the service.
- [ ] Estimates and "not medical advice" are stated where they apply.
- [ ] Only the tokens, typefaces and plate mark above are used.
- [ ] Tomato marks one thing per surface.
- [ ] It reads at a glance: headline first, detail second.
