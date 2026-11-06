# Slide deck design standard

Status: current living standard, 6 November 2026; colour theme pending. Adapted from the Project 15 and
Text-to-SQL slide standards. Their structure and discipline carry over; their
colours, fonts, logos and claims do not.

## Authority and maintenance

The [live Google Slides deck](https://docs.google.com/presentation/d/1RCroJQywRWTQTnjhNhHvX5xTdKcQ3SD4p8JEYfMENUg/edit)
is the formatting source of truth. Read its current objects before editing and keep
Mike's changes. `../build_deck.js` and the `.pptx` are the first seed only; never
reimport them over the live deck.

| File | Decides |
| --- | --- |
| [BRIEF.md](BRIEF.md) | What each slide says |
| This file | How every slide looks |
| [../../../DESIGN.md](../../../DESIGN.md) | The brand: tokens, voice, logo |
| [../README.md](../README.md) | Links, source files and the fact sheet |
| [design-history.md](design-history.md) | Why a rule changed |

Update a rule here in place. Record the old rule and the reason in design history;
don't append dated sections. Slide-specific content belongs in the brief. Reviews and
checks belong in `docs/5_agent_log.md`. Match slides by native page ID (`p1`, `p2`),
not by page number, because page numbers move.

## Audience, story and language

- This is a reader-oriented portfolio deck. Each slide makes sense with no presenter.
- Separate four things: what it does, what was measured, what that means, what is proposed.
- Short subject titles for context and method slides; supported findings for result slides.
- One scope subtitle on every content slide, preferably one line, not repeating the title.
- Sentence case for titles and prose. Uppercase only for section labels.
- Digits with units and populations: 629 kcal, 72 requests, 34 recipes.
- Prefer spacing and line breaks to decorative dots, bars or dashes.
- Keep a material limitation on the same slide as its claim.
- Put provenance in speaker notes, not on the slide face.

Each slide needs four fields in the brief before any visual work: reader question, main
message, supporting evidence, and what belongs elsewhere. One slide owns each detailed
mechanism. The executive summary may repeat as synthesis; nothing else repeats a diagram.

## Canvas and grid

Canvas 960 × 540 pt (13⅓ × 7½ in), background `ground` #F6F7F2. All positions in points.

| Element | Position and size | Style |
| --- | --- | --- |
| Section label | x 43.5, y 21.7 | Google Sans 10 pt bold uppercase |
| Title | x 43.5, y 48.4; w 873 | Google Sans 24 pt bold |
| Subtitle | x 43.5, y 90.9; w 873 | Google Sans 12 pt, `muted` |
| Content area | x 43.5 to 916.5, y 130 to 486 | Left and right rails are fixed |
| Takeaway column | x 684, y 130; 232.5 × 356 | See Takeaways |
| Takeaway marker | x 668 | Aligned to the rendered heading line |
| Footer mark | x 43.5, y 501; 18 × 18 | Plate mark |
| Footer name | x 68, y 500 | Google Sans 10 pt, `muted`: AI Meal Planner |
| Page number | Right edge at x 916.5, y 500 | Google Sans 10 pt, `muted`, automatic field |

Section label format is one text box: `MAIN SECTION > SUBSECTION`. Main in `ink`, separator
and subsection in `muted`. A standalone section such as EXECUTIVE SUMMARY has no subsection.

Exactly one automatic page number per numbered slide, inherited from the layout. Cover and
close are unnumbered, use the `ink` background, and have their own composition. Footer items
live on the layout, never on a slide. No bars, stripes, rules under titles or decoration.

Default content width beside a takeaway column is x 43.5 to 652. One dominant figure or
diagram leads each content slide. Leave at least 12 pt between neighbouring components.

## Typography

Google Sans for all editable text. Google Sans Code for code spans, filenames and endpoints,
for the span only. Screenshots keep their own type.
No other faces, and no sizes outside these roles.

| Role | Size | Treatment |
| --- | --- | --- |
| Note, qualification, table detail | 8 pt | Regular; bold `Note:` or `Limit:` prefix |
| Figure caption | 9 pt | `muted`; only `Figure N.` bold |
| Section label, footer | 10 pt | Bold uppercase label; regular footer |
| Body, takeaways, table headings, chart labels | 12 pt | Regular; bold for headings |
| Content heading, key value | 16 pt | Bold |
| Slide title | 24 pt | Bold |
| Focal number | 32–54 pt | Bold; one per slide |

Enlarge the owning shape or cut words before reducing type. Never use 8 or 9 pt for a
conclusion. Left-align text; right-align comparable numbers; centre only markers and chips.
Line spacing 110% for body. Emphasise short evidence-bearing phrases in bold; don't colour
whole sentences.

## Colour

**Theme pending Mike's choice from `palette-trials/`.** The roles below are the Kitchen green
values until then.

Colours come from [the brand tokens](../../../DESIGN.md). In the deck their roles are fixed:

| Role | Colour |
| --- | --- |
| Canvas | `ground` #F6F7F2 |
| Cards | `surface` #FFFFFF with 1 pt `line` #DDE3DA |
| Text; step chips; focal panel | `ink` #15291F |
| Secondary text | `muted` #4B5B52 |
| Takeaway markers; the headline's one word on cover | `accent` #C8431F |
| Current or improved result; "On target" | `success-fg` #1B5E3F on `success-bg` #E3EFE6 |
| Baseline or earlier result | `muted` #4B5B52 |
| Limitation strips; estimate badges | #7A4A0C on #FBEBD6 |
| Neutral tracks and reference badges | #ECEFE8 |
| Macro data only | `protein` #2F6FAB, `carbs` #9A6A12, `fat` #7A4E9C |

Most of each slide stays neutral. One `ink` focal panel at most per slide. Colour is never
the only signal. Green is a measured target result, not medical safety. Tomato is
not an error colour.

## Editable components

Use native shapes, text, tables, connectors and bars. Don't flatten a panel to an image or
split wrapped lines into separate boxes. Native PowerPoint charts lose their labels when
converted to Slides, so draw charts from shapes and keep their values in the brief.

| Component | Rule |
| --- | --- |
| Card | White, 1 pt `line`, 12 pt corner radius, no shadow. Text sits inside the shape |
| Padding | 8 pt (0.11 in) on all sides; 12 pt for larger narrative cards |
| Heading and body | One rich-text box: 16 pt heading, 12 pt body, 4 pt gap |
| Step chip | 22 pt `ink` circle, white 10 pt bold number, centred, zero indents |
| Metric card | 16 pt value, 12 pt label, 8 pt caption, 3 pt gaps; repeat one size per slide |
| Focal panel | `ink` fill, focal number, 12 pt `#C9D3CC` label |
| Limit strip | #FBEBD6 fill, 8 pt text, bold #7A4A0C `Limit:` prefix |
| Badge | Short text on tint, never colour alone: `Estimated`, `Reference`, `On target` |
| Table | No outer border, 1 pt `line` row rules, 12 pt headings, right-aligned numbers |
| Arrow | Native connector, 1 pt `muted`, one arrowhead, attached to shape edges |

Arrows show a real sequence or dependency. Don't imply causes the evidence doesn't support.

## Takeaways and markers

Use a takeaway column only when it interprets the evidence on its left: a consequence,
limitation, decision or next test. Don't restate a label. No generic KEY TAKEAWAYS heading.
Omit it on the cover, agenda, executive summary, close, or where the slide already says it.

One native text box, zero internal padding, 12 pt, bold headings, 110% line spacing, 6 pt
after paragraphs, 14 pt before later headings. No fixed point count. Keep the frame fixed;
never shrink the text or stretch the frame to fit.

Number each interpretation in reading order. A marker is one 12 pt `accent` ellipse with a
centred white 8 pt bold number, zero padding. Align it to the centre of its heading's
rendered first line, and repeat the same number beside its evidence, clear of data and text.
Markers are a reference, not a judgment. Use them only in pairs. Step chips are `ink` so the two never read as one system.

Use small `muted` superscripts (¹ ²) for qualifications, restarted per slide, with a matching
8 pt note. With no superscript, use a bold `Note:` or `Scope:` prefix.

## Charts, figures and evidence

| Need | Form | Must show |
| --- | --- | --- |
| Progress across changes | Bars on one zero-based scale | Population (72 requests), each change named |
| Range targets | Band on a 0–100% track | The range and what it is a share of |
| Mechanism | Labelled flow | Sequence and responsibilities |
| Example plan | Authentic screen or rebuilt card | Label it as an example |

- Bars start at zero. No broken axes, dual axes, 3D, gradients, pies or donuts.
- Direct labels over legends. Directly compared items share one scale.
- Figure captions sit 8 pt below their figure, left aligned.
- Screenshots keep their proportions, fit inside the frame and are never recoloured. Label a
  design prototype as a prototype. Use a real capture when one exists.

Project-specific claim rules:

- The trained model predicts **exercise calories**. Its R² and error describe that task, not
  daily expenditure or a meal target. Daily expenditure adds it to a BMR-based estimate.
- 72 of 72 is this project's own offline benchmark. Say so, and that AMDR is a daily
  reference applied here to one meal. It isn't a clinical or user result.
- The benchmark runs without USDA or FatSecret keys, and 68 of 72 plans include an estimated
  ingredient. Never imply those plans were USDA-verified.
- 11 of the 72 are fallback meals, not matches for the craving. 61 of 61 matched plans pass.
- Prices are local estimates. "Checked" means looked up and labelled, not guaranteed.
- A fallback, a refusal or an estimate is a feature to state plainly, not to hide.
- Numbers come from the fact sheet in `../README.md`. A new number goes there first.

## Icons and images

The plate mark is the only icon. Numbered chips do the job of icons. If a diagram needs
pictograms, use Material Symbols Rounded, unfilled, 24 pt, in `ink`, with a text label. No
emoji or clip art. Keep the licence with any asset added. No stock imagery of food or bodies.

## Speaker notes

Each slide: a short opening stating the slide's purpose; natural sentences in the visual's
reading order; `[Point: visible label]` cues on their own lines; limitations with the
claim; a transition. Don't read every number or put editing instructions in the script.
Exact sources go last under `Reference — not read aloud`. Keep notes aligned with the slide.

## Verification and handoff

1. Read the live objects and the slide's brief before editing. One editor at a time.
2. Check question, evidence, takeaways, qualifications and paired markers together.
3. Check fonts, role sizes, colour roles, fit, padding, alignment, image proportions.
4. Recheck every number against the fact sheet, with its population and limits.
5. After text moves, realign markers to the rendered headings.
6. Check one automatic page number per numbered slide, and that links work.
7. Inspect the live deck, then the exported PDF. Local renders substitute fonts, so they
   don't prove fit.
8. Log concrete checks and open concerns in `docs/5_agent_log.md`. Don't commit, push or
   share without instruction.
