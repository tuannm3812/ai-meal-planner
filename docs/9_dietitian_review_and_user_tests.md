# Dietitian review and user tests

The plan for P9's "People" task (`docs/showcase/pending-tasks.md`): first an
accredited dietitian reviews the rules the planner applies, then a small group of
people use the app while we watch. Written 22 November 2026, against `main` at
`060b40c`.

The order matters. The user test shows people plans built from these rules, so a
rule the dietitian wants changed is fixed first. Part A ends with a short list of
must-fix items; Part B starts only when that list is closed or each item is
written up as a known limit.

This is a UTS capstone usability study, not a clinical or dietary trial. No one
follows a plan, and no one's real health record is collected (§B.3).

## Part A. Dietitian review

### A.1 How to run it

- **Who.** An Accredited Practising Dietitian (APD, Dietitians Australia). A UTS
  nutrition lecturer or a clinic dietitian who agrees to an hour is enough.
- **What to send a week ahead.** This Part A, and six sample plans: the
  benchmark's six profiles (`backend/app/evaluation/meal_quality.py`), each with
  one plain craving, one kidney-disease request and one vegan request. Print them
  from the React app or from `uv run python scripts/meal_quality_baseline.py
  --json <file>`. Each plan shows the daily budget, the meal target, portions in
  grams, the macro split and any warnings.
- **The session.** 60 minutes, in person or by video. Walk §A.2 in order; the
  dietitian marks each row **Keep**, **Change** (with what to) or **Remove**.
  Show the app live for 10 minutes at the end so they see the wording people see.
- **Afterwards.** Each **Change** or **Remove** becomes a DEC entry in
  `docs/3_decisions.md` naming the dietitian's advice as its source, with its
  effect on the baseline and the wider check. Record the review itself in
  `docs/5_agent_log.md`. The dietitian's name goes in only with their consent.

### A.2 Checklist

Each row says what the app does today, where it lives, and what to ask.

#### Energy

| # | What the app does | Where | Question | Verdict |
| --- | --- | --- | --- | --- |
| E1 | Daily energy is Mifflin-St Jeor BMR times an activity multiplier: 1.2 sitting, 1.375 light, 1.55 moderate, 1.725 very, 1.9 extra active. | `calorie_expenditure_agent.py`, `frontend/src/features/profile/profile.js` | Are these multipliers and their plain-language labels appropriate? | |
| E2 | Today's workout is added on top, from a trained model (30 minutes at 100 bpm if not given; a rest day adds nothing). | DEC-33 | The activity level already counts a usual week's exercise, so a workout day can count some exercise twice. Is that acceptable for a demo, or should the workout replace part of the multiplier? | |
| E3 | Weight loss is expenditure minus 400 kcal; gain is plus 250 kcal; maintain is expenditure. | `_meal_budget` | Are a 400 kcal deficit and a 250 kcal surplus sensible defaults for every body size? | |
| E4 | A weight-loss budget never goes below 1,200 kcal for women or 1,500 for men, and never above expenditure. A sex the model does not know gets the higher floor. A warning says when the floor applied. | DEC-24 | Are these floors right? Should a small, older person whose expenditure is below the floor be told something more than the warning? | |
| E5 | One meal is 28% of the daily budget, kept between 350 and 850 kcal. A large athlete's meal is about 19% of the day because of the cap. | `_scale_ingredients_to_meal_target` | Is 28% a fair share for one main meal? Is 850 kcal the right cap? | |

#### Macros and portions

| # | What the app does | Where | Question | Verdict |
| --- | --- | --- | --- | --- |
| M1 | A plan "meets the targets" when calories are within 10% of the meal target and protein, carbohydrate and fat sit inside the adult AMDR: 10-35%, 45-65% and 20-35% of energy. The same ranges apply to every goal. | DEC-25 | Is AMDR the right yardstick for one meal rather than a day? Should weight loss or muscle gain use a different protein range? | |
| M2 | "High protein" and other preferences only rank meals; they never change the targets. No recipe is low-carb, because a low-carb meal cannot reach 45% carbohydrate, so the "low carb" preference favours nothing. | DEC-27, DEC-30 | Should low carb be offered at all, given the AMDR targets? | |
| M3 | Portions are first scaled as a whole to the meal target, by 0.65x to 1.6x of the recipe. | `core/portions.py` | Are these bounds sensible? | |
| M4 | Each ingredient is then resized, by 0.5x to 2x of the scaled amount, to land within 5% of the calories and inside AMDR. The meal and its ingredients never change. Amounts round to 5 g. | DEC-26, DEC-28 | Do 0.5x-2x per ingredient give plates a person would recognise and eat? Look at the six sample plans for odd portions. | |
| M5 | Six recipes with no fat source got 10 g of cooking oil; after balancing the oil ships at 5 to 15 g. Eleven recipes got more of a carbohydrate or fat they plausibly hold. | DEC-28, DEC-30 | Are these additions reasonable, and is 15 g of oil in one meal acceptable? | |
| M6 | Nutrition comes from local tables. Fifteen ingredients added with the 76-recipe corpus use typical USDA values not yet checked live, and plans label them "estimated". | DEC-35, P4 | Spot-check a few values in `data/reference/macro_fallbacks.json`. | |

#### Allergens and diets

The rules read a tag table, `data/reference/ingredient_allergens.json`, never the
ingredient's name (DEC-34). An ingredient missing from the table is refused under
any diet rule.

| # | What the app does | Where | Question | Verdict |
| --- | --- | --- | --- | --- |
| D1 | Nine allergen tags: dairy, egg, fish, gluten, peanut, sesame, shellfish, soy, tree nut. | `rag/rules.py` `GROUP_TAGS` | Is anything missing for Australia? FSANZ also lists lupin and separates wheat from gluten. | |
| D2 | Every one of the 65 ingredients is tagged. Ask the dietitian to read the whole table (one page) and flag any wrong tag. | `ingredient_allergens.json` | Is each tag right? | |
| D3 | Rolled oats and oat milk count as gluten (owner's choice: oats are often cross-contaminated). Soy sauce and low-sodium soy sauce count as gluten. | DEC-31 | Agree, for a coeliac request? | |
| D4 | Plant milks, soy yogurt, peanut butter and sunflower seed butter are not dairy. Sunflower seed butter is the peanut swap. | DEC-30 | Agree? Is sunflower seed butter a safe peanut swap given shared processing lines? | |
| D5 | Vegan refuses meat, fish, shellfish, dairy and egg. Vegetarian refuses meat, fish and shellfish, so it allows dairy and egg. | `GROUP_TAGS` | Is lacto-ovo the right reading of "vegetarian"? | |
| D6 | When a meal holds a refused ingredient, the app swaps it only if the swap is safe under every rule in force; otherwise the meal is not served. Swaps keep the grams unless stated: egg to 80 g firm tofu; Greek yogurt or cottage cheese to soy yogurt; wheat bun, bread, tortilla and pasta to gluten-free versions or corn tortilla; soy sauce to coconut aminos; firm tofu to chickpeas; soy milk to oat milk; peanut butter to sunflower seed butter; sesame oil to olive oil; shrimp, salmon or tuna to chicken breast. | `SUBSTITUTION_RULES` | Is each swap sensible? Same grams of chicken for fish loses omega-3; is that worth a note on the plan? | |
| D7 | Allergen safety stops at ingredients. The app says nothing about cross-contact, labels or "may contain". | | What warning should a plan carry for a person with a serious allergy? | |

#### Health conditions

| # | What the app does | Where | Question | Verdict |
| --- | --- | --- | --- | --- |
| H1 | "Hypertension", "high blood pressure" and "low sodium" refuse only ingredients tagged `high_sodium`, which today is soy sauce and low-sodium soy sauce. Both are swapped for coconut aminos. There is no sodium limit in milligrams. | DEC-34 | Should low-sodium soy sauce carry the tag? Is this enough to offer, or should these conditions be removed until there is a real sodium limit? | |
| H2 | Kidney disease refuses ingredients tagged `kidney_caution`: chickpeas, edamame, firm tofu, tempeh, hummus, kidney beans, lentils and both soy sauces. Black beans are allowed. There is no swap, so those meals are not served, and there are no protein, potassium or phosphorus limits. | DEC-34, `4_next_steps.md` §7.13 | Kidney diets depend on the stage and on blood results. Should the app offer kidney disease at all, or only say to follow a renal dietitian's plan? If it stays, which tags are right? | |
| H3 | Recipes also name conditions they are never served for: kidney disease (24 recipes), high cholesterol (13), pregnancy (7), heart disease (5), tree nut allergy (4), shellfish allergy (3), lactose intolerance (2), peanut allergy (2). These were set by hand. | `data/meal_corpus/meals.json` `avoid_conditions` | Are these exclusions sound? Should pregnancy also exclude high-mercury fish, soft cheese and other listeria risks by tag? | |
| H4 | Any health condition adds the warning "Health conditions are used as recommendation constraints only; this is not medical advice." The React app offers only the rules that exist (vegetarian, vegan, dairy-free, gluten-free, peanut allergy, kidney disease); diabetes is not offered. | `profile.js` `AVOID_OPTIONS` | Is the warning enough, and where should it appear? Which conditions should the app decline to plan for? | |

#### Who the app is for, and its wording

| # | What the app does | Where | Question | Verdict |
| --- | --- | --- | --- | --- |
| W1 | The app accepts any age above 0 and any weight from 20 kg. Mifflin-St Jeor and AMDR are adult formulas. | `schemas/requests.py` | What minimum age should the app accept? Should it refuse pregnancy, breastfeeding and a history of eating disorders for weight loss? | |
| W2 | The goal picker says weight loss is "a gentle deficit, never below a safe floor" and gain is "a modest surplus for building". | `profile.js` `GOAL_OPTIONS` | Is "safe floor" a claim the app should make? Suggest wording. | |
| W3 | A plan shows calories, a macro chart, whether it "met the targets" and a portions list. | React plan page | Does any wording read as medical advice or imply more precision than the data has? | |

### A.3 What ends Part A

The review is done when every row has a verdict and each **Change** or **Remove**
is either built (with a DEC entry) or written into `docs/4_next_steps.md` §7 as a
known limit that the user test and the deck state plainly. Must-fix before Part B,
whatever the verdict says: anything the dietitian calls unsafe, and W1's age and
exclusion limits.

## Part B. User tests

### B.1 Goal and questions

Learn whether people can get a meal they would cook from the app, understand why
it was chosen, and notice its limits. Five questions:

1. Can someone new set up a profile and get a plan without help?
2. Would they cook the meal they were given, and if not, why not?
3. Do they understand the daily budget, the meal target and the macro chart?
4. Do they notice and understand the warnings (a fallback meal, an estimated
   ingredient, the floor, "not medical advice")?
5. Is the shopping list useful, and do the prices look believable?

This is a usability test. It does not measure whether the plans change anyone's
diet or health.

### B.2 Participants

- **Five to eight adults, 18 or over.** Five is enough to find most usability
  problems; add up to three more if the first five disagree.
- **A mix:** at least two who cook most days and two who rarely do, at least one
  who follows a diet rule (vegetarian, vegan, dairy-free or gluten-free), and
  ideally one who uses a nutrition app already.
- **Recruit** from classmates, friends and family. No payment is needed; a coffee
  is fine.
- **Exclude** anyone who would follow the plan to manage a medical condition, is
  pregnant, or has a history of an eating disorder. Say this in the invitation.

### B.3 Ethics, consent and data

- **Check with the capstone supervisor first** whether UTS needs a Human Research
  Ethics approval for this study, or whether it counts as a course usability
  activity. If results go into the report or the poster, ask about the low-risk
  route. Record the answer in `docs/5_agent_log.md` before booking anyone.
- **Consent.** A one-page sheet each participant signs: what they will do, that
  it takes 30 minutes, that they can stop at any time, that the app gives general
  ideas and not medical or dietary advice, what is recorded, and how to withdraw
  their notes.
- **No real health data.** Participants may enter approximate numbers or use a
  persona card (§B.5). They should not enter a real medical condition. Notes use
  P1, P2 and so on, never names.
- **Clear the device after each session.** The React app remembers the profile
  and history on the device (DEC-36). Clear the browser's site data and reset the
  local database between participants.
- **Screen recording** only with a tick on the consent sheet, and audio only, or
  the screen only, if that is all they agree to. Delete recordings once the notes
  are written up.

### B.4 Setup

- **Where.** In person, on the facilitator's Mac, running the React app and the
  API locally (`README.md` §6.4), so saving, rating and history work. The
  hosted API cannot serve React with history in v1 (DEC-8). For a remote session,
  use the Streamlit demo once P1's demo mode is on.
- **Before each session.** Start from an empty profile and empty history. Check
  that a plan returns in a few seconds; warm the API with one request.
- **Roles.** One facilitator who reads the script and stays quiet during tasks,
  and, if possible, one note-taker. If alone, record (with consent) and take notes
  after.
- **Version.** Note the commit tested, so findings map to the code.

### B.5 Session script (30 minutes)

1. **Welcome, 3 min.** "We are testing the app, not you. Please think aloud. There
   are no wrong answers." Sign the consent sheet.
2. **Warm-up, 2 min.** How do you decide what to cook on a weeknight? Do you use
   any food or fitness app?
3. **Tasks, 18 min.** Read each task aloud; do not demonstrate. Note where they
   hesitate, what they say, and whether they finish.
   - **T1. Set up.** "Set up the app for yourself, or for this person" (persona
     card). Done when the profile is saved.
   - **T2. Plan.** "You feel like something with chicken and rice tonight. Get a
     meal." Then: "Tell me what you got and why you think it was picked."
   - **T3. Read the plan.** "How much of today's food is this meal? Is it a
     balanced meal? How can you tell?"
   - **T4. A craving it does not have.** "Now ask for pizza." Watch whether they
     see the notice that a standard meal was served instead.
   - **T5. A diet rule.** "Make it vegetarian" (or their own rule). "Is there
     anything in this meal you would not eat?"
   - **T6. Shop.** "Use the shopping list to get what you need. What would it
     cost?"
   - **T7. Save and come back.** "Save a meal you like and rate this one. Find it
     again later."
4. **Questions, 5 min.**
   - Would you cook the meal from T2? Why or why not? (1 to 5)
   - How much do you trust the calorie and nutrition numbers? (1 to 5)
   - What, if anything, worried you or felt like advice you should not follow?
   - The System Usability Scale, ten items, on paper.
5. **Close, 2 min.** Thank them, and repeat that the plans are general ideas, not
   dietary advice.

**Persona cards**, for anyone who prefers not to use their own numbers: the
benchmark's profiles in `backend/app/evaluation/meal_quality.py`, each written as
one line, for example "Sam, 28, 180 cm, 80 kg, exercises 3 to 5 days a week,
wants to keep their weight."

### B.6 What to record

One row per participant per task in a spreadsheet: finished (yes, with help, no),
time, errors, and a one-line quote. Then the four ratings and the SUS score.

| Measure | How | Good result |
| --- | --- | --- |
| Task success | Share of T1-T7 finished without help | At least 80% |
| Time to first plan | T1 start to the T2 plan on screen | Under 3 minutes |
| Would cook it | T2 question, 4 or 5 out of 5 | At least half |
| Warning noticed | T4 fallback notice seen without a prompt | At least 4 of 5 |
| Understood the plan | T3 answered correctly | At least 4 of 5 |
| SUS | Standard scoring | 68 or more (average) |

These are targets for discussion, not pass marks; five people cannot prove them.

### B.7 After the sessions

- Group the notes into findings, each with how many participants hit it and a
  severity: **blocker** (could not finish, or misread a safety message),
  **major** (finished with trouble), **minor** (cosmetic).
- Write them up in a short section added to this file, with the commit tested.
- Fix blockers first; record any product change as a DEC entry.
- Update the deck's "Not tested" step (slide 14, P9 in
  `docs/showcase/pending-tasks.md`) with what was tested, by how many people, and
  the main findings. Say plainly that it was a small usability test.

## Summary of who does what

| Step | Who |
| --- | --- |
| Ask the supervisor about ethics approval | Mike |
| Find a dietitian and book an hour | Mike |
| Print the six sample plans and this checklist | Claude or Mike |
| Run the review and record verdicts | Mike, with the dietitian |
| Build the changes, with DEC entries | Claude |
| Recruit five to eight participants | Mike |
| Run the sessions | Mike |
| Write up findings and update the deck | Claude, from Mike's notes |
