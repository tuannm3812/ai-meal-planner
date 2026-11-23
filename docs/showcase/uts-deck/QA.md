# Presentation delivery checklist

Deck and review date __________

Requested outputs and delivery location __________

Kit and engine revisions used __________

Final PDF SHA-256 from output/qa-report.json __________

Tick a step after recording evidence. For a partial delivery or an inapplicable check, record the reason and what the recipient can rely on. Keep prior reviews when revising a deck.

- [ ] **Scope.** Record the audience, objective, duration or reading context, and deliverables in slide-brief.md.
- [ ] **Project.** Confirm the intended pins and local overrides. Identify the baseline for an existing deck.
- [ ] **Evidence.** Record source locators, cutoff, substantive numeric claims, units and limitations. Check asset credits and affiliation where applicable.
- [ ] **Authoring.** Review the reader question, supported message, layout, exact copy, source and presenter notes for each slide. Check that overview point count follows the message, optional next/takeaway blocks add distinct value, and sources/notes/legends have separate roles. Verify bold Source:/Note: labels and matching figure/chart superscripts placed after Note:, equal 20 pt overview gaps, appropriate 40/52 pt horizontal takeaways and actual encoding keys above figures/charts. For an actual project, replace cover/deck-title placeholders and copied sample labels; confirm subject/work label, title and subtitle have distinct roles. In worked examples, verify the input, rule, result, source-note mapping and evidence scope.
- [ ] **Build and export.** Run build, export and final PDF check in order. Record the page count, report locations and PDF hash.
- [ ] **Visual and content review.** List reviewed pages and any corrections. Check palette A section/theme mappings and the independent Viridis data scales. Verify each agenda row against the actual section and its first and last pages in the exported PDF. Check the whole story and inspect all new or changed pages at presentation size.
- [ ] **HTML and sources.** Exercise navigation, notes, source links and PDF download from the delivery copy. Record which files or links were checked.
- [ ] **Handoff.** Open the requested deliverables. Record paths, companion files, outstanding checks and their impact.

See the [agent workflow](https://github.com/tuannm3812/uts-deck-kit/blob/main/AGENT-WORKFLOW.md) in the private kit for the decision paths and commands.

## Review, 23 November 2026: appendix A5 and A6

- **Scope.** Mike asked for the important results of the latest runs in the appendix. Added A5 (workout check, PR #57) and A6 (USDA benchmark, PR #59, DEC-41, §6 of docs/7_meal_quality.md). The dietitian and user-test plan (PR #56) is a plan, not a result, so it is not on a slide.
- **Project.** Kit `uts-deck-kit` 9a6654f (0.6.0 plus the merged HTML counter fix; kit-pin.json updated for `uts_kit/render.py`). Engine: the Mac's `deck-kit` files copied unchanged; every file matches the hashes in kit-pin.json, so the engine commit reads null in build-manifest.json only because the copy had no git history. Built in a cloud session with Chrome and Poppler.
- **Evidence.** New rows in claims-register.md and sources.md (`workouts`, `usda-run`). USDA numbers are from branch `claude/project-thread-u7ncjg` (PR #59, 55f12c5), not yet on main.
- **Authoring.** New layout `mp_bench`: chart left with its key above it, three numbers right, takeaway band. Viridis only: body #3B528B, workout #21918C, removed exercise #440154 outline. Stale lines updated: slide 14 (USDA result, migrations done, body-temperature default), slide 15 (columns, milestones, takeaway), A1 (a stated workout replaces the usual week's exercise).
- **Build and export.** build, export_pdf, check_deck, audit_layout and check_markers: 0 problems, 0 findings, 0 marker findings. 22 pages. PDF SHA-256 `459ab1166a71c082b355f41fb53b6a6007bed55f9ef2caf33b3b914fa31145cf`.
- **Visual review.** Pages 14, 15, 17, 21 and 22 inspected at 110 dpi. Agenda unchanged (the appendix is not on it).
- **HTML.** Arrow-key navigation reaches 22 / 22 in output/deck.html.
