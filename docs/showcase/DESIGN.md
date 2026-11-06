# Poster design standard

Status: proposed, 6 November 2026. This file is the standard for the poster and the LinkedIn
image. The [slide-deck standard](slides/DESIGN.md) is separate. Brand tokens are in the
[root DESIGN.md](../../DESIGN.md). Numbers and sources are in the [fact sheet](README.md#fact-sheet).

## Authority

`poster.html` and `linkedin.html` are first drafts from before this standard, and will be
rebuilt to it. Once a poster is converted to Google Slides, the live file becomes the source
of truth, and the HTML is a seed that must not overwrite it. Poster and deck are edited
separately but must never disagree on a claim.

## Intent

Someone with no tech background understands it in a 5-second glance and can explain it after
30 seconds. Clearer hierarchy is the goal: no new measurements or capability claims.

## Reading order

Four numbered sections, about 90 words in total. A one-page poster needs no agenda.

1. **Promise.** Logo bar, then "Say what you crave. Get a meal that fits you." One subtitle:
   one meal sized to your body and goal, plus the shopping list.
2. **Proof.** The Chicken Fried Rice plan card: 629 kcal against a 625 kcal target, macro bars.
   This is the largest element and the only highlighted block.
3. **How it works.** Four numbered steps in one row: Estimate your calories, Find a matching
   recipe, Check the nutrition, Build the shopping list.
4. **Result.** "72 of 72 test meal plans hit their calorie target and healthy macro ranges, up
   from 10", with a short qualifier that this is the project's own benchmark.

Footer: demo QR code, GitHub link, one tech line, "A study project. Not medical advice."

Leave off: test counts, R², tracing, Cloud Run, API keys, the acronym AMDR, class names, and
the intermediate 41 and 47. Those belong to the deck.

## Canvas

| Output | Logical size | Export | Margins |
| --- | --- | --- | --- |
| Poster | 1200 × 1800 px, portrait 2:3 | 2× PNG, plus PDF | 64 px |
| LinkedIn image | 1080 × 1350 px, 4:5 | 2× PNG | 64 px |

The portrait poster suits screens and A3 or A2 prints. Get the exact physical size before a print run.

## Type and colour

Bricolage Grotesque and Inter only, loaded and verified before rendering.

| Role | Poster | LinkedIn |
| --- | --- | --- |
| Headline | 64–76 px, 800 | 76–84 px, 800 |
| Result number | 96–112 px, 800 | 84 px, 800 |
| Section heading | 28–32 px, 700 | not used |
| Body | 16–20 px | 18–22 px |
| Section label, caption | 14 px | 14 px |

`ground` canvas, white cards, one `ink` result panel, `ink` footer. Tomato appears on the logo
and on the words "fits you" only. Macro colours appear on macro bars only. At most four sizes
of body-level text on a surface. Adjust spacing or cut words before shrinking type.

## Components

Follow the deck's card, badge and chip rules: 1 px `line` borders, 16–20 px corners, 24 px
between blocks, no shadows, gradients or edge stripes. Group with spacing, not nested cards.

## Claim rules

The [deck's claim rules](slides/DESIGN.md#charts-figures-and-evidence) apply here. In particular:
never say the model predicts daily burn, never imply plans are USDA-verified, and keep "test"
or "benchmark" next to 72 of 72. Keep the "estimated" badge on the plan card.

## Acceptance

Inspect the whole poster at reduced size for the 5-second read, then full-size crops of the
card and small text. Check everything fits, fonts load, the QR code scans, and each number
matches the fact sheet. Log checks in `docs/5_agent_log.md`.
