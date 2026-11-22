# User accounts — design

Status: **draft for Mike's approval**, 2026-11-22. Nothing here is built yet.

Mike chose Firebase on 2026-11-22: Google sign-in through Firebase Auth, saved meals,
ratings and profiles in Firestore, and the React app on Firebase Hosting, all on free
tiers inside the existing GCP project `ai-meal-planner-515508`. Ruled out: Supabase (a
second vendor whose free project sleeps after a week idle), Cloud SQL (about A$15 or
more a month against an A$1 budget), and staying device-only.

## 1. Why the current system can't do this

- **The React app has no way in.** The hosted API accepts only app keys (G4), and a
  public bundle can't hide one, so React only runs against a local open-mode API (DEC-8).
- **The hosted API keeps nothing.** Each Cloud Run instance's SQLite file is lost on
  restart, so hosted mode refuses history with `501 history_disabled_stateless` (DEC-10).
- **A `user_id` is taken on trust** (`docs/4_next_steps.md` §7.7). Anyone who knows an id
  can read that id's history within a client's namespace.
- **The profile lives in the browser** (`aimp.v1`, DEC-36). The server only ever returns
  a built-in default profile (§7.2).

Accounts close all four: a login that gives the browser a token, storage shared by
every instance, and a host for React.

## 2. What the person sees

- The app works signed out, as today: plan, look at the result, keep a profile on this
  device. See §8 question 1 for whether a signed-out visitor can use the hosted app.
- **"Sign in with Google"** sits in the brand bar and on the Profile page.
- On first sign-in, a profile kept on this device moves into the account, unless the
  account already has one; then the account's wins and the person is told.
- Signed in, My meals, Past plans, save and rate all work on the hosted app, on any device.
- The Profile page shows the Google name and photo (from Firebase, in the browser only),
  "Sign out", and **"Delete my account and data"**, which removes every stored record
  after a confirmation.

## 3. Identity

- The browser signs in with the Firebase JS SDK (`firebase/auth`, Google provider, popup)
  and sends the Firebase ID token as `Authorization: Bearer <token>`.
- The API verifies it with `google.oauth2.id_token.verify_firebase_token`, from
  `google-auth`, which is already a dependency. It checks the signature against Google's
  cached public certificates, the audience (the project ID) and the issuer. No
  `firebase-admin` dependency is needed.
- A verified token becomes a `Principal` with `client_id="accounts"`, the new field
  `user_id=<Firebase uid>`, and the three existing scopes. The rate limit keys on the uid.
- For an account principal the server **ignores any `user_id` in the body** and uses the
  uid. A path `user_id` that is not the uid gets `403`. This is what closes §7.7.
- `X-API-Key` keeps working unchanged for Streamlit, scripts and `live_check.sh`. A request
  carrying both is refused as ambiguous.
- The server stores only the uid. It never stores the email, name or photo. A Firebase uid
  is random and opaque, so it meets DEC-18's rule for ids that end up in URLs and logs.
- Production still refuses to start without key records (DEC-8). Account auth is on when
  `FIREBASE_PROJECT_ID` is set.

## 4. Storage

A new `STORAGE_BACKEND=firestore` implements the three existing protocols behind the
DEC-4 boundary, plus one write on `UserProfileStore`. SQLite stays the default for local
development and CI's fast jobs.

```
namespaces/{client_id}/users/{user_id}                profile, location, updated_at
namespaces/{client_id}/users/{user_id}/plans/{request_id}
namespaces/{client_id}/users/{user_id}/feedback/{auto id}
```

- Account records live under `namespaces/accounts/users/{uid}`. Key clients keep their own
  namespace, as in G4, so nothing changes for them.
- `list_for_user` is one ordered query on `saved_at` with a limit, so a Home visit costs
  about 40 document reads.
- **Hosted mode with Firestore stores and serves history.** The DEC-10 refusal stays for
  hosted mode on SQLite, where it is still true.
- `UserProfileStore.save_user_profile(user_id, profile, *, client_id)` is new. Reading a
  profile an account doesn't have raises `ProfileNotFound`, finally closing §7.3.
- The runtime service account gets `roles/datastore.user` and nothing broader.
- **Tests.** The repository contract suite gains a Firestore case, run against the
  Firestore emulator in one CI job. Unit tests use a small in-memory fake, so `uv run
  pytest` stays offline.

## 5. API changes

| Route | Change |
| --- | --- |
| every protected route | accepts `Authorization: Bearer` as well as `X-API-Key` |
| `GET /me/profile` | new: the account's profile, or `404` |
| `PUT /me/profile` | new: saves the profile and location |
| `DELETE /me` | new: deletes the account's profile, plans and feedback |
| `/meal-plans/{user_id}`, `/meal-feedback/{user_id}`, `/saved-meals/{user_id}` | `403` unless the path id is the caller's uid |
| `POST /generate-meal-plan`, `POST /meal-feedback` | body `user_id` replaced by the uid |

`docs/openapi.json` is regenerated and declares the bearer scheme. CORS adds the hosting
origins. Health fields still never go in a URL.

Deleting the Firebase sign-in itself happens in the browser (`deleteUser`) after
`DELETE /me` succeeds, so the server needs no admin rights over accounts.

## 6. Hosting and setup

- React builds with `VITE_API_URL` set to the Cloud Run URL and the public Firebase web
  config. That config is not a secret. Firebase identifies the project with it, and the
  authorised-domains list limits where sign-in works.
- A new job in `.github/workflows/deploy.yml` deploys `frontend/dist` to Firebase Hosting
  with the existing Workload Identity Federation, so no new long-lived key is added. The
  address would be `ai-meal-planner-515508.web.app`.
- `live_check.sh` gains a bearer-token check against the emulator in CI. On the real
  service it checks that a bad token gets `401`.
- One-time setup, done once on your Mac and recorded in `docs/6_deployment.md`: add
  Firebase to the GCP project, turn on the Google sign-in provider, create the Firestore
  database in `australia-southeast1`, and grant the two roles.

## 7. Cost

All free tiers, inside the existing budget alert:

| Service | Free allowance | Expected use |
| --- | --- | --- |
| Firebase Auth, Google sign-in | no charge (only phone sign-in is billed, and it isn't used) | a handful of users |
| Firestore | 1 GiB stored; 50,000 reads, 20,000 writes and 20,000 deletes a day | about 40 reads a visit, so about 1,250 visits a day before any charge |
| Firebase Hosting | 10 GB stored, 360 MB a day transferred | about 1 MB a first visit |
| Cloud Run | unchanged, capped at one instance | unchanged |

The one-instance cap still bounds compute cost if someone scripts sign-ins.

## 8. Questions for Mike

1. **Can a signed-out visitor use the hosted app?** Recommended: yes, through Firebase
   anonymous sign-in. The browser gets a uid with no Google account, planning works, and
   signing in with Google later keeps that uid's plans. The other way is to require Google
   sign-in before the hosted app plans anything.
2. **Sign-in methods.** Recommended: Google only for now. Email and password is a later,
   small change.

## 9. Order of work

Each slice is its own PR, merged in order:

1. Bearer-token auth and the account principal, with the `user_id` rules of §3.
2. The Firestore repository, its contract tests on the emulator, and the CI job.
3. `/me/profile` and `DELETE /me`, and hosted mode serving history on Firestore.
4. React: sign-in, profile sync on first sign-in, sign out, delete account.
5. Firebase Hosting deploy, CORS, `live_check.sh`, `docs/6_deployment.md`; then Mike's
   one-time setup and a real sign-in on the live app.

When this is approved, it becomes DEC-39 in `docs/3_decisions.md`, and §7.2, §7.3 and §7.7
of `docs/4_next_steps.md` point here.

## 10. Out of scope

- Unsaving a meal (feedback stays append-only, DEC-37).
- Moving device-only history from a local API into an account. Hosted history was always
  empty, and local history is development data.
- Sharing, households or roles.
- Firebase App Check. Worth adding if the API ever sees abuse.
