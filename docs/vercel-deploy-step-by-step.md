# Deploy to Vercel — Step by Step

A beginner-friendly walkthrough for deploying this monorepo to Vercel using the
**Vercel dashboard** (no command line required). Last verified **May 2026**.

This repo becomes **two Vercel projects from the same GitHub repository**:

1. **API** — the FastAPI backend (`apps/api`)
2. **Web** — the Next.js frontend (`apps/web`)

> Deploy the **API first**, then the **Web**, then come back and tell the API the
> Web's address. That order avoids the most common "it deployed but the tools
> don't work" problem.

For the full reference (every env var, preview/production split, smoke checks),
see [`deployment.md`](deployment.md). This guide is the quick, friendly path.

---

## Before you start: get your accounts and keys

You will need these. Open each in a separate browser tab and keep them handy.

| What | Where to get it | Needed for |
|---|---|---|
| Vercel account | <https://vercel.com/signup> — sign in with GitHub | Hosting both apps |
| GitHub repo access | Your private repo (already pushed) | Vercel imports from here |
| DeepSeek API key | <https://platform.deepseek.com> → API Keys | Live AI answers |
| Neon Postgres database | <https://neon.tech> (free tier is fine) | Saving results + rate limits |
| Supabase project (optional) | <https://supabase.com> | Lead-capture form |

You can deploy and run **demo mode** without DeepSeek, Neon, or Supabase. Those
are only needed for **live AI** and **lead capture**.

### Get your Neon connection string

1. Create a Neon project.
2. On the project dashboard, copy the **connection string** (it looks like
   `postgresql://user:pass@ep-xxxx.neon.tech/dbname?sslmode=require`).
3. Make sure it ends with `?sslmode=require`. Keep this safe — it is a secret.

### Make a rate-limit secret

You also need a random secret called `API_RATE_LIMIT_HASH_SALT`. Generate any
long random string (for example, run `openssl rand -hex 32` in a terminal, or use
a password manager). Use a **different** one for preview vs production.

---

## Part 1 — Deploy the API (`apps/api`)

### Step 1.1 — Import the project

1. Go to <https://vercel.com/new>.
2. Find your repository and click **Import**.
3. Vercel asks for a few settings before the first deploy. Set them as below.

### Step 1.2 — Configure project settings

| Setting | Value |
|---|---|
| **Project Name** | e.g. `study-abroad-api` |
| **Root Directory** | `apps/api` (click **Edit** and pick the folder) |
| **Framework Preset** | Vercel auto-detects **FastAPI** — leave it |
| **Build/Install/Output commands** | Leave on default (the repo already configures them) |

### Step 1.3 — Turn on "include files outside the root" (important)

The API installs shared code from elsewhere in the repo (`packages/` and
`services/`). Vercel must be allowed to see those folders.

1. After import, go to the API project's **Settings → Build and Deployment**.
2. Find **Root Directory**.
3. Turn **ON**: **"Include source files outside of the Root Directory in the
   Build Step."**

If you skip this, the build fails with a "can't find package" / editable-install
error.

### Step 1.4 — Add the API environment variables

Go to **Settings → Environment Variables** and add these. Set the scope to
**Production** (you can repeat for **Preview** later).

Required for live AI:

```
DEEPSEEK_API_KEY      = your_deepseek_api_key
DEEPSEEK_MODEL        = deepseek-v4-flash
```

Required for saving results and production rate limits:

```
DATABASE_URL              = your_neon_connection_string_ending_in_sslmode=require
API_PERSISTENCE_ENABLED   = true
API_RATE_LIMIT_STORE      = postgres
API_RATE_LIMIT_HASH_SALT  = your_long_random_secret
```

CORS (which website is allowed to call this API). For now put a placeholder —
you will fix it in Part 3 once the web app has a URL:

```
API_CORS_ORIGINS = https://example.com
```

> Do **not** add `NEXT_PUBLIC_...`, Supabase, or any web variables here. Keep
> DeepSeek and database secrets on the API project only.

### Step 1.5 — Deploy and check health

1. Click **Deploy** and wait for it to finish.
2. Copy the API's URL (e.g. `https://study-abroad-api.vercel.app`).
3. In your browser, open `https://<your-api-url>/health`.
4. You should see:

```json
{"status":"ok"}
```

If you see that, the API is live. 🎉

### Step 1.6 — Set up the database tables (one time)

The build does **not** create database tables automatically. Run the migration
once from your own computer (you only need the repo and `uv` installed):

```bash
cd apps/api
DATABASE_URL="your_neon_connection_string_with_sslmode_require" uv run python -m app.persistence.migrations
```

Re-run this only when you add a new Neon database.

---

## Part 2 — Deploy the Web (`apps/web`)

### Step 2.1 — Import the same repo again

1. Go to <https://vercel.com/new> again.
2. Import the **same** repository (Vercel allows multiple projects from one repo).

### Step 2.2 — Configure project settings

| Setting | Value |
|---|---|
| **Project Name** | e.g. `study-abroad-web` |
| **Root Directory** | `apps/web` |
| **Framework Preset** | Auto-detects **Next.js** — leave it |
| **Build/Install/Output** | Leave on default |

Leave the "include files outside root" toggle **OFF** for the web project — it
does not need it.

### Step 2.3 — Add the Web environment variables

Go to **Settings → Environment Variables** (scope **Production**).

Point the frontend at your API from Part 1:

```
NEXT_PUBLIC_STUDY_ABROAD_API_URL = https://your-api-url.vercel.app
```

Optional — only if you want the lead-capture form to save leads:

```
NEXT_PUBLIC_SUPABASE_URL      = https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = your_supabase_anon_key
```

> Everything starting with `NEXT_PUBLIC_` is visible in the browser. Never put
> secret keys (DeepSeek, database, salt) here.

### Step 2.4 — Deploy

1. Click **Deploy**.
2. Copy the web URL (e.g. `https://study-abroad-web.vercel.app`).
3. Open it — the site should load with the KlassFin look (purple theme, Poppins
   font).

---

## Part 3 — Connect them (fix CORS)

Right now the API still has the placeholder CORS value, so the live tools on the
website will be blocked by the browser. Fix it:

1. Go to the **API** project → **Settings → Environment Variables**.
2. Edit `API_CORS_ORIGINS` and set it to your **web** URL exactly (no trailing
   slash):

```
API_CORS_ORIGINS = https://study-abroad-web.vercel.app
```

3. Environment variable changes need a redeploy to take effect: go to the API
   project's **Deployments** tab → open the latest → **Redeploy**.

---

## Part 4 — Test it

On your live website:

1. Open `/tools/sop-review` and click **Demo Review**. You should get sample
   output labelled **"Demo output"** (this works even without a DeepSeek key).
2. Open `/tools/admit-predictor` and click **Demo Prediction**. Same idea.
3. If you set a DeepSeek key + database, try a **live** request on each tool.
4. If you hit the rate limit, you'll see a friendly "try again later or use demo
   mode" message — that's expected.

If demo works but live fails, it's almost always one of: missing `DEEPSEEK_API_KEY`,
`API_CORS_ORIGINS` not matching the web URL, or you forgot to redeploy the API
after changing a variable.

---

## Preview vs Production (optional but recommended)

Vercel automatically builds a **Preview** deployment for every branch/PR and a
**Production** deployment for your main branch.

- Use a **separate Neon database/branch** and a **separate**
  `API_RATE_LIMIT_HASH_SALT` for Preview so test traffic never touches
  production data.
- In Vercel, add the same variables again but choose the **Preview** scope, with
  preview-specific values.
- Point the Preview web's `NEXT_PUBLIC_STUDY_ABROAD_API_URL` at the Preview API
  URL, and add the Preview web URL to the Preview API's `API_CORS_ORIGINS`.

---

## Quick reference

**API project**
- Root Directory: `apps/api`
- Include files outside root: **ON**
- Health check: `GET /health` → `{"status":"ok"}`
- Secrets: `DEEPSEEK_API_KEY`, `DATABASE_URL`, `API_RATE_LIMIT_HASH_SALT`
- Other: `API_PERSISTENCE_ENABLED=true`, `API_RATE_LIMIT_STORE=postgres`,
  `API_CORS_ORIGINS=<web url>`

**Web project**
- Root Directory: `apps/web`
- Include files outside root: **OFF**
- `NEXT_PUBLIC_STUDY_ABROAD_API_URL=<api url>`
- Optional: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Golden rules**
- Deploy API first, then Web, then set the API's CORS to the Web URL.
- Any env var change requires a **redeploy** to take effect.
- Secrets live only on the API project. `NEXT_PUBLIC_` values are public.
- Run database migrations yourself; the build never does.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| API build fails: "No module named ai_runtime / sop_review" | "Include source files outside of the Root Directory" is OFF — turn it ON, redeploy |
| `/health` works but live tools fail in the browser console with a CORS error | `API_CORS_ORIGINS` doesn't match the web URL exactly; fix it and **redeploy the API** |
| Live AI returns an error but demo works | `DEEPSEEK_API_KEY` missing/invalid on the API project |
| "rate limit exceeded" message | Expected after several live calls; wait, or use demo mode. Tune `API_LIVE_RATE_LIMIT_COUNT` if needed |
| Results don't persist / DB errors | `DATABASE_URL` missing, missing `?sslmode=require`, or migrations not run |
| Changed a variable but nothing changed | You must redeploy after editing environment variables |
| Site loads but font/theme looks wrong | Hard refresh; confirm the Web project deployed the latest commit |
