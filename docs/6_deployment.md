# Deployment — Cloud Run

How the hosted API is deployed (DEC-16), and how G6's acceptance is shown
against the real service. The public Streamlit demo is unaffected: it runs on
Streamlit Community Cloud with the backend in-process (DEC-2).

What runs where:

| Piece | Where | Notes |
| --- | --- | --- |
| API image | Artifact Registry | Built from `Dockerfile` by `.github/workflows/deploy.yml` |
| API service | Cloud Run | `HOSTED_MODE=true`, `APP_ENV=production`, port 8000, 0–3 instances |
| `API_KEYS` | Secret Manager | Hashed key records only (README §8.1) |
| Traces | Cloud Trace | `TRACING_EXPORTER=cloud_trace`; allowlisted metadata only (DEC-17) |
| Deploy identity | Workload Identity Federation | No long-lived keys in GitHub |
| Acceptance | `scripts/live_check.sh` | Runs after every deploy; the same script CI runs against its nginx rehearsal |

## 1. One-time setup

Needs: a GCP project with billing enabled, `gcloud` logged in as an owner of it
(`gcloud auth login`), and `gh` authenticated to this repository.

```bash
export PROJECT_ID=<your-project-id>
export REGION=australia-southeast1        # any Cloud Run region
export REPO=tuannm3812/ai-meal-planner
gcloud config set project "$PROJECT_ID"
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')

gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com iam.googleapis.com iamcredentials.googleapis.com \
  sts.googleapis.com telemetry.googleapis.com

gcloud artifacts repositories create ai-meal-planner \
  --repository-format=docker --location="$REGION"
```

### Service accounts

The runtime identity reads the key secret and writes traces, nothing more. The
deploy identity can push images and deploy, and nothing else.

```bash
gcloud iam service-accounts create meal-planner-runtime
gcloud iam service-accounts create meal-planner-deployer
RUNTIME_SA=meal-planner-runtime@$PROJECT_ID.iam.gserviceaccount.com
DEPLOYER_SA=meal-planner-deployer@$PROJECT_ID.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$DEPLOYER_SA" --role=roles/run.admin
gcloud artifacts repositories add-iam-policy-binding ai-meal-planner \
  --location="$REGION" --member="serviceAccount:$DEPLOYER_SA" \
  --role=roles/artifactregistry.writer
gcloud iam service-accounts add-iam-policy-binding "$RUNTIME_SA" \
  --member="serviceAccount:$DEPLOYER_SA" --role=roles/iam.serviceAccountUser
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$RUNTIME_SA" --role=roles/telemetry.tracesWriter
```

### Workload Identity Federation (GitHub → Google, no stored keys)

Only workflows from this repository can act as the deployer.

```bash
gcloud iam workload-identity-pools create github --location=global \
  --display-name="GitHub Actions"
gcloud iam workload-identity-pools providers create-oidc github-oidc \
  --location=global --workload-identity-pool=github \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='$REPO'"
gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER_SA" \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/$REPO"
```

### API keys in Secret Manager

Create one key per client application, plus one for the post-deploy live
check. `scripts/new_api_key.py` prints a raw key, shown once, and the record to
store:

```bash
python scripts/new_api_key.py live-check     # keep "key" for GitHub, below
python scripts/new_api_key.py partner-app    # hand "key" to that client
```

Put every `record` into one JSON list and store it as the secret. Only hashes
leave your machine:

```bash
printf '%s' '[<record>, <record>]' | \
  gcloud secrets create meal-planner-api-keys --data-file=-
gcloud secrets add-iam-policy-binding meal-planner-api-keys \
  --member="serviceAccount:$RUNTIME_SA" --role=roles/secretmanager.secretAccessor
```

### GitHub configuration

```bash
gh variable set GCP_PROJECT_ID --body "$PROJECT_ID"
gh variable set GCP_REGION --body "$REGION"
gh variable set GCP_WIF_PROVIDER \
  --body "projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github/providers/github-oidc"
gh variable set GCP_DEPLOY_SERVICE_ACCOUNT --body "$DEPLOYER_SA"
gh variable set GCP_RUNTIME_SERVICE_ACCOUNT --body "$RUNTIME_SA"
gh secret set MEAL_PLANNER_SMOKE_KEY     # paste the live-check raw key
```

Until `GCP_PROJECT_ID` is set, the deploy workflow skips itself, so merging it
deploys nothing. The `production` environment it names can be given required
reviewers in the repository settings, to add a manual approval gate.

## 2. Deploy

```bash
git tag v0.1.0 && git push origin v0.1.0     # or: gh workflow run deploy.yml
```

The workflow then:
1. builds the image and pushes it, tagged with the commit SHA;
2. deploys a new revision;
3. runs `scripts/live_check.sh` against the service URL, failing the run if
   hosted mode is not behaving.

Each deploy is a new revision on fresh instances, so it starts empty
(stateless v1). Hosted mode stores nothing anyway.

## 3. G6 acceptance on the real service

**Two instances.** Run the workflow by hand with two instances kept warm, so
the check's parallel requests reach both:

```bash
gh workflow run deploy.yml -f min_instances=2 -f expect_instances=2
```

Each check (each of the four history and feedback routes, and anonymous calls)
must on its own be answered by at least two distinct `X-Instance-Id` values. A
response without an id counts for none. Each request has 60 seconds
(`REQUEST_TIMEOUT`) to complete. A request that stalls, fails or is cut short
counts as a failure, even if its status and body looked right so far.
This is a sample: it proves that the instances which answered behave correctly,
not that no other instance or revision exists. Afterwards, redeploy normally
(`min_instances` defaults to 0) so idle instances stop billing.

**Revocation** (G4, "a revoked key is refused by every instance"):

1. Generate a replacement with the **same** `client_id`, so the namespace is
   kept.
2. Add its record and remove the old one, then store the list as a new secret
   version:
   `printf '%s' '<new list>' | gcloud secrets versions add meal-planner-api-keys --data-file=-`.
3. Redeploy with two instances, as above. Every instance of the new revision
   reads the new list at startup.
4. Prove the old key is refused by both warm instances:

   ```bash
   MEAL_PLANNER_KEY=<new key> OLD_KEY=<old key> EXPECT_INSTANCES=2 \
     scripts/live_check.sh "$(gcloud run services describe ai-meal-planner-api \
       --region "$REGION" --format='value(status.url)')"
   ```

This requires `min_instances=2` to still be in effect.

## 4. Operations

- **Roll back:**
  `gcloud run services update-traffic ai-meal-planner-api --region "$REGION" --to-revisions=<revision>=100`.
- **Logs:**
  `gcloud run services logs read ai-meal-planner-api --region "$REGION"`.
  Domain errors log their internal detail; responses never carry it.
- **Traces:** in the console, Trace Explorer, service `ai-meal-planner-api`.
  Each request is one trace: a `METHOD /route-template` span with one child per
  stage (`calorie.predict`, `meal.retrieve`, `nutrition.verify`,
  `plan.reconcile`, `supermarket.list`). Spans carry only the allowlisted
  attributes in `backend/app/core/telemetry.py`. Cloud Run limits CPU outside
  requests by default, so batched spans can wait for the next request or for
  shutdown before they are sent. That is acceptable at this traffic level.
- **Retention**, from Google's documentation as of 2026-10-10:
  - Cloud Trace keeps spans for 30 days.
  - Cloud Logging's `_Default` bucket keeps logs for 30 days by default
    (DEC-19). To shorten that:
    `gcloud logging buckets update _Default --location=global --retention-days=<1-3650>`.
    Shortening has a 7-day grace period.
  - Hosted mode stores no meal plans or feedback (DEC-10).
- **What the logs hold.** App log lines name requests by route template, error
  type and code. They never include the request's content, an internal error
  message, or a provider URL. Two things the app does not control:
  - unexpected 500s log a traceback, including that exception's message;
  - Cloud Run's own request log records each full URL, so `user_id` must be
    an opaque id (DEC-18).
- **Rate limit:** `RATE_LIMIT_PER_MINUTE` applies per instance, so with up to
  three instances a client can reach up to three times the limit (README §8.1).
- **Provider keys:** optional. Add `GEMINI_API_KEY`, `USDA_API_KEY` and so on as
  further Secret Manager secrets, and list them under `secrets:` in the
  workflow. Without them, nutrition is estimated and labelled as such (DEC-13).
- **Cost:** with `min-instances=0` the service scales to zero when idle.
- **Render:** `render.yaml` is superseded by this (DEC-16). It also cannot
  start since G4 without `API_KEYS`. Retire it, or fix it as a documented
  fallback.
