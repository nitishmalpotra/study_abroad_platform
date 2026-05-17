# Codex Migration Prompt Pack

Use these prompts in order. Each prompt is intentionally scoped so the repo stays reviewable and verifiable after every step.

Global rules for every prompt:
- inspect before editing
- do not expand scope beyond the current prompt
- preserve the existing KlassFin visual theme unless the prompt explicitly says otherwise
- run the relevant tests, linting, type checks, and builds before claiming completion
- report exactly what was verified and what was not

## Prompt 1 — Audit the current codebase and produce the migration blueprint

```text
You are working inside my existing study-abroad-platform workspace, which currently contains three separate projects:
1. ai-sop-review-grader
2. graduate-admissions-predictor
3. klassfin-bolt

Do not make implementation changes yet.

Your task is to perform a deep repo audit and produce a migration blueprint for turning this into one public-facing monorepo with:
- a Next.js frontend that preserves the current KlassFin visual theme
- a FastAPI backend
- modular reusable domain services for SOP review and admit prediction
- DeepSeek as the AI provider instead of Gemini
- no user accounts/sign-in
- sensible public rate limits
- Neon Postgres as the production database target
- Vercel Blob for SOP uploads if persisted
- public-repo-grade documentation, security hygiene, testing, CI, and deployment readiness
- frontend support for both real AI calls and mock/demo calls

Inspect the current repos thoroughly before writing anything. Read the existing code, README files, pyproject files, package.json, migrations, app logic, prompt strings, and any historical docs that are still inspectable.

Deliver only:
1. A clear current-state summary
2. A recommended target monorepo architecture
3. A proposed folder tree
4. A phased migration plan
5. A list of technical risks and decisions
6. A checklist of what must be preserved from the current frontend theme
7. A list of acceptance criteria for the entire migration

Do not edit source code. Do not change dependencies. The only file you may create or update is `docs/MIGRATION_BLUEPRINT.md`.

Verification requirements:
- Report which files and folders you inspected.
- Explicitly identify what is implemented today versus what is only implied by docs or missing.
- Call out any contradictions between the current frontend and backend contracts.

Acceptance criteria:
- The plan is concrete enough that a senior engineer could execute it without guessing.
- The plan preserves the current KlassFin theme.
- The plan explicitly covers DeepSeek migration, mock mode, rate limits, docs, security, deployment, and tests.
- The plan distinguishes MVP requirements from later enhancements.

At the end, tell me:
- what you verified
- what you did not verify
- what decisions are now fixed
- what decisions are still open, if any

```

Expected result:
- a design blueprint only
- no code changes

Manual checks:
- confirm the architecture matches your intended product
- confirm no important requirement is missing

## Prompt 2 — Convert the workspace into a clean monorepo shell

```text
Implement the first migration step from the approved blueprint: convert the current workspace into one clean public monorepo shell while preserving all existing code.

Target high-level layout:
- apps/web
- apps/api
- packages/contracts
- services/sop_review
- services/admissions
- docs
- infra
- tests

Requirements:
- Move the existing frontend into apps/web without changing its visual theme or app behavior yet.
- Move the existing Python tool code into appropriate interim locations so nothing is lost.
- Do not yet migrate Vite to Next.js.
- Do not yet replace Gemini.
- Do not yet rewrite application logic.
- Add a root README.md that explains this is now a monorepo in transition and briefly describes the subprojects.
- Add a root .gitignore suitable for a public repo.
- Ensure no secrets, local DB files, logs, .env files, generated artifacts, or personal-machine paths are committed.
- Preserve historical code as cleanly as possible; do not delete working features simply because they will be refactored later.

Acceptance criteria:
- The monorepo has a clear root-level structure.
- Existing frontend and Python app code are still present and understandable.
- No obvious secret-bearing or machine-specific files are tracked.
- Root documentation accurately reflects the repo after the move.
- There are no accidental theme changes in the frontend.

Required verification:
- Inspect the full resulting tree.
- Run git status and verify only intended moves/edits occurred.
- Run Python syntax checks on the moved Python apps.
- Run the existing frontend install/build verification if dependencies are available; if not, say exactly what blocked verification.
- Confirm no .env files or local database files are tracked.

```

Expected result:
- one monorepo shell
- existing behavior preserved

Manual checks:
- verify familiar frontend files still exist
- verify old Python tools were preserved
- verify no local secrets were accidentally committed

## Prompt 3 — Add repo standards, documentation scaffolding, and CI baseline

```text
Add the baseline standards expected from a serious public-facing engineering repo.

Implement:
- root CONTRIBUTING.md
- root SECURITY.md
- root CODE_OF_CONDUCT.md only if appropriate for a public OSS-style repo
- docs/architecture.md
- docs/local-development.md
- docs/deployment.md
- docs/security-and-privacy.md
- docs/ai-system-design.md
- docs/evaluation-strategy.md
- .editorconfig
- consistent environment example files
- GitHub Actions CI workflow(s)
- formatting/lint/type-check/test command documentation

Requirements:
- Keep all documentation honest: do not claim features that do not exist yet.
- Public-repo hygiene must be explicit:
  - no committed secrets
  - no local DBs
  - no raw user documents
  - no personal absolute paths
  - no generated runtime logs
- README must eventually include project overview, architecture, local setup, DeepSeek BYO-key setup, mock/demo mode, deployment overview, security/privacy notes, and testing commands. If some features are not implemented yet, label them as planned rather than pretending they exist.
- Preserve the current frontend theme untouched.

Acceptance criteria:
- A new contributor can understand what the repo is, how it is organized, and what the migration target is.
- CI exists and runs useful checks.
- Security posture and public-repo hygiene are documented clearly.
- Documentation is clean, concise, and non-fictional.

Required verification:
- Validate workflow YAML syntax.
- Inspect environment example files for completeness and absence of secrets.
- Confirm CI commands reference scripts that actually exist.
- Run any available documentation or lint checks if configured.
```

Expected result:
- the repo looks professional even before the major refactor

Manual checks:
- read the README and docs as a stranger
- confirm no inflated claims

## Prompt 4 — Extract SOP review logic into modular services

```text
Refactor the SOP review tool out of its current monolithic Streamlit architecture into modular, reusable backend code.

Target modular concerns under services/sop_review:
- schemas
- config
- prompts
- validation
- ingestion/file parsing
- provider-independent service orchestration
- persistence interfaces or adapters
- tests

Requirements:
- Preserve current SOP capabilities:
  - text input
  - file upload parsing support
  - gatekeeping
  - scoring
  - structured outputs
- Do not change frontend theme.
- Do not add a FastAPI route yet unless explicitly required by internal wiring.
- Separate pure business logic from UI logic.
- Keep LLM-provider-specific code out of core domain logic.
- Extract prompts into dedicated, versionable files/modules instead of embedding them inline in UI code.
- Remove dead or misleading assumptions from old code, especially anything docs claim but code does not actually implement.
- Keep Streamlit only as a temporary adapter if retained at all.

Acceptance criteria:
- SOP business logic can be imported and called without Streamlit.
- Prompt templates are isolated and versionable.
- Validation logic is independently testable.
- The new service layer has clear tests.
- Existing SOP behavior is preserved functionally.

Required verification:
- Add and run unit tests for SOP validation and orchestration boundaries.
- Run Python syntax checks.
- Run formatter/linter if configured.
- If the old Streamlit shell remains, verify it still imports correctly.
- Report any behavior intentionally changed and why.
```

Expected result:
- SOP logic is reusable outside Streamlit

Manual checks:
- inspect the new module structure
- confirm the service can clearly be called by a future API

## Prompt 5 — Extract admit predictor logic into modular services

```text
Refactor the graduate admissions predictor out of its current monolithic Streamlit architecture into modular, reusable backend code.

Target modular concerns under services/admissions:
- schemas
- config
- prompts
- validation
- provider-independent prediction service
- recommendation post-processing
- persistence interfaces or adapters
- tests

Requirements:
- Preserve current capabilities:
  - profile validation
  - target program handling
  - structured prediction output
  - recommendation logic
  - result alignment
- Separate UI from domain logic.
- Extract prompts into dedicated versionable modules/files.
- Keep provider-specific implementation outside the domain layer.
- Keep or simplify the old Streamlit adapter only if useful during transition.
- Make it possible for a future FastAPI endpoint to call the predictor service cleanly.

Acceptance criteria:
- Admissions prediction logic is callable without Streamlit.
- Validation, schema parsing, and recommendation post-processing are independently testable.
- Prompt templates are isolated and versioned.
- Tests cover important edge cases such as duplicate target programs and invalid score ranges.

Required verification:
- Add and run unit tests.
- Run Python syntax checks.
- Run formatter/linter if configured.
- Verify no frontend theme files changed.
```

Expected result:
- both AI tools now have reusable service layers

Manual checks:
- compare SOP and admissions module boundaries for consistency

## Prompt 5.5 — Checkpoint audit after prompt five

```text
Pause feature work and perform a checkpoint audit of the repo after completion of prompts 1 through 5.

Inspect the current repository against the migration blueprint and answer:
1. Is the repo structurally where it should be after prompt five?
2. Which acceptance criteria from prompts 1 through 5 are fully met, partially met, or not met?
3. Are the SOP and admissions services now genuinely reusable outside Streamlit?
4. Are there any inconsistencies that are harmless now but should be standardized before later phases? Pay particular attention to prompt organization, provider placement, naming, package layout, and docs drift.
5. Is `docs/MIGRATION_BLUEPRINT.md` still the best migration strategy given what has now been implemented, or should it be revised before continuing?

Do not make code changes unless you find a clear defect that blocks continuing. If you recommend changes, separate:
- must fix now
- should fix soon
- acceptable to defer

Required verification:
- inspect the full repo tree
- inspect current docs
- inspect service boundaries
- inspect tests
- run the relevant test suites and checks for prompts 1 through 5
- report exact commands and results

Acceptance criteria:
- the audit is candid and specific
- it distinguishes real blockers from cosmetic inconsistencies
- it gives a clear continue / pause / revise recommendation
- it explicitly evaluates whether prompt organization should be normalized now or later
```

Expected result:
- a go/no-go checkpoint before continuing the migration

Manual checks:
- use this before starting provider migration

## Prompt 6 — Introduce the shared AI runtime and replace Gemini with DeepSeek

```text
Replace Gemini usage with DeepSeek across both AI services while introducing one shared AI runtime that both task-specific domain modules use.

Requirements:
- Create one shared AI runtime location for cross-cutting LLM concerns:
  - provider clients
  - retries and timeout handling
  - response normalization
  - JSON extraction / repair helpers where behavior is genuinely shared
  - logging and redaction helpers
- Keep SOP review and admissions prediction as separate task-specific domain modules that plug into the shared runtime.
- Keep domain service logic separate from provider implementation details.
- Remove direct Gemini dependencies from the core service flow.
- Use environment-based configuration for DeepSeek API credentials and model selection.
- Add .env.example entries for DeepSeek configuration.
- Never expose secrets to the frontend.
- Keep the design flexible enough that another provider could be added later without rewriting domain logic.
- Do not collapse SOP and admissions into one generic service; only centralize behavior that is genuinely shared.
- Update docs honestly to reflect DeepSeek as the chosen provider.
- Remove or deprecate Gemini-specific code only where safe; do not leave confusing dead paths.

Acceptance criteria:
- Both services use DeepSeek through the shared AI runtime.
- Shared retry/timeout/parsing/redaction behavior is not duplicated across both services.
- SOP and admissions remain separate service classes with separate schemas and workflows.
- Domain layers do not import vendor-specific SDKs directly.
- Environment configuration is documented.
- Existing schema validation behavior remains intact.
- Tests cover shared-runtime behavior and provider wiring via mocks/fakes rather than real API calls.

Required verification:
- Run all Python tests.
- Run lint/format/type checks as available.
- Search the repo for remaining Gemini references and classify each as intentional legacy mention or something to remove.
- Confirm no API key appears in source, logs, docs, or fixtures.
```

## Prompt 7 — Redesign the SOP prompt for quality-first feedback

```text
Audit and redesign the SOP review prompt for best possible practical output quality.

The goal is not more text. The goal is better judgment.

Prompt-design requirements:
- prefer quality over quantity
- be specific, evidence-based, and admissions-relevant
- avoid generic filler, motivational fluff, and vague praise
- require concise but high-signal feedback
- distinguish academic fit, university specificity, career clarity, narrative coherence, and language/tone
- require criticism when criticism is warranted
- avoid pretending certainty where there is none
- keep outputs schema-valid and easy to render
- preserve a stable response contract for the API/frontend
- version the prompt and document its rationale
- keep prompt files under the normalized versioned layout

Implement:
- improved prompt(s)
- any needed few-shot examples only if they materially improve behavior
- prompt version metadata
- eval fixtures / golden examples for strong, average, weak/generic, and invalid non-SOP inputs
- tests that verify schema adherence and expected qualitative tendencies where practical

Acceptance criteria:
- The prompt is clearly more rigorous than the old one.
- The prompt has an explicit quality philosophy.
- It is versioned and documented.
- The eval strategy can detect obvious regressions.
- It does not overproduce text just to appear helpful.

Required verification:
- Run all SOP tests and eval-related checks.
- Document what can be verified automatically and what still needs human review.
- If live API testing is not possible without a key, state that clearly and provide a manual evaluation checklist.
```

## Prompt 8 — Redesign the admissions prompt for quality-first reasoning

```text
Audit and redesign the graduate admissions predictor prompt for best possible practical output quality.

Prompt-design requirements:
- prefer quality over quantity
- be careful, calibrated, and non-hypey
- do not imply false precision
- avoid generic recommendations
- use the applicant's actual profile in the reasoning
- distinguish clearly between safe, target, reach, and unrealistic
- give concise, useful reasons rather than long filler
- preserve structured, schema-valid output
- version the prompt and document its rationale
- keep prompt files under the normalized versioned layout

Implement:
- improved prompt files/modules
- prompt version metadata
- eval fixtures / golden examples for strong, borderline, weak, and unrealistic-target profiles
- regression/eval tests where practical

Acceptance criteria:
- The prompt avoids vague admissions-coach language.
- The result schema stays stable.
- Outputs are useful, concise, and appropriately cautious.
- The prompt version is tracked and documented.
- There is a clear eval plan for future improvements.

Required verification:
- Run all admissions tests and eval-related checks.
- Document what is automatically tested versus what needs manual live-model review.
- If live provider tests are skipped, say so explicitly.
```

## Prompt 9 — Build the FastAPI backend

```text
Create the FastAPI backend app under apps/api.

Required API surface for the first public release:
- GET /health
- POST /api/v1/sop/review
- POST /api/v1/sop/review/mock
- POST /api/v1/admissions/predict
- POST /api/v1/admissions/predict/mock

Requirements:
- Use the extracted modular services rather than duplicating business logic.
- Use the shared AI runtime rather than adding route-local provider code.
- Use shared schemas/contracts wherever appropriate.
- Keep secrets server-side only.
- Add structured validation and safe error responses.
- Add sensible public rate limiting for live endpoints.
- Mock endpoints must return deterministic representative data without calling DeepSeek.
- Live endpoints must call DeepSeek through the shared AI runtime.
- Add tests for health, validation errors, happy-path mock responses, rate limiting, safe error handling, and no live-model dependency in tests.

Acceptance criteria:
- The API app runs independently.
- All endpoints are covered by tests.
- Mock endpoints do not call the provider.
- Live endpoints are wired but testable with fakes/mocks.
- API docs are understandable from generated schema plus repo docs.

Required verification:
- Run backend tests.
- Run lint/format/type checks.
- Start the API locally if possible and verify /health.
- Inspect OpenAPI output if generated.
- Confirm no secret leaks in error payloads.
```

## Prompt 10 — Add shared contracts between backend and frontend

```text
Create a shared contracts layer so the frontend and backend use one explicit source of truth for request/response structures.

Requirements:
- Define schemas for SOP review request/response, admissions prediction request/response, and common API error shape.
- Keep names aligned with backend domain models.
- Keep contracts aligned to the separate SOP and admissions workflows even though they share AI infrastructure.
- Generate or maintain TypeScript types for frontend use.
- Document the contract philosophy and versioning strategy.
- Remove contract drift, including the current SOP rubric mismatch between the frontend mock page and backend grading schema.
- Ensure mock responses exactly match live response shape.

Acceptance criteria:
- Frontend and backend use matching field names.
- SOP criteria shown in the frontend match the backend rubric.
- Mock payloads conform to the same schemas as live payloads.
- A future schema change would be obvious and testable.

Required verification:
- Run schema/contract tests.
- Run backend tests.
- Run frontend type-checking after integrating generated/static types.
- Search for stale old rubric names and remove or document them.
```

## Prompt 11 — Migrate the frontend from Vite to Next.js without changing the theme

```text
Migrate the current frontend from the Vite React app into a Next.js app under apps/web while preserving the existing KlassFin look and feel as closely as possible.

Non-negotiable requirement:
- Do not redesign the visual theme.

Requirements:
- Recreate existing routes/pages in Next.js.
- Preserve current pages: home, destinations, destination detail, universities, tools, EMI calculator, SOP review, resources, blog, and blog post.
- Preserve existing lead-capture UX behavior unless a necessary backend change is explicitly called out.
- Use the shared contracts layer for future API integrations.
- Keep the code modular and idiomatic for Next.js.
- Document any routing or asset changes caused by the migration.

Acceptance criteria:
- The website renders the same visual design and content as before.
- All existing routes work in Next.js.
- Build, type-check, and lint pass.
- No unapproved redesign occurred.

Required verification:
- Run install/build/typecheck/lint commands.
- Use browser/manual visual verification if available.
- Compare representative pages before/after if possible: home, tools, SOP review, blog post.
```

## Prompt 12 — Wire real SOP review and mock SOP review into the frontend

```text
Replace the current mocked SOP frontend behavior with a proper API-driven implementation while preserving the existing visual theme.

Requirements:
- Add a real SOP review submission flow and a mock/demo SOP review button.
- Live mode sends user input to the real API and handles loading, success, validation errors, rate-limit responses, and server errors.
- Mock mode does not call DeepSeek and clearly communicates that it is demo output.
- Reuse shared contracts.
- Keep SOP-specific UX and response handling separate from admissions-specific behavior; shared AI infrastructure stays behind the API boundary.
- Align displayed rubric with the backend SOP criteria.
- Preserve the current design language and page layout.

Acceptance criteria:
- The page no longer uses hardcoded fake scoring as its only behavior.
- Live and mock modes both render valid response shapes.
- Error handling is clear and safe.
- No theme regression occurs.
- The frontend never exposes the DeepSeek key.

Required verification:
- Run frontend tests/typecheck/lint/build.
- Run backend tests.
- Manually verify short invalid SOP text, mock flow, successful live flow if a key is available, API failure state, and rate-limit state if practical.
```

## Prompt 13 — Build the Admit Predictor frontend page with real and mock modes

```text
Add the missing public Admit Predictor page to the Next.js frontend and integrate it with the API.

Requirements:
- Create the route and page for the admit predictor.
- Update the tools page so Admit Predictor is no longer “Coming Soon.”
- Build a clean form for applicant profile and target programs.
- Add real prediction and mock/demo buttons.
- Render target predictions, chance categories, probabilities, reasoning, strengths, weaknesses, roadmap, and recommendations.
- Handle loading, validation errors, rate limiting, and server failures.
- Use shared contracts.
- Keep admissions-specific UX and response handling separate from SOP-specific behavior; shared AI infrastructure stays behind the API boundary.
- Preserve the existing KlassFin theme.

Acceptance criteria:
- Admit Predictor is a first-class public tool in the frontend.
- It works in both live and mock modes.
- It uses the backend contracts exactly.
- It looks native to the existing site.

Required verification:
- Run frontend typecheck/lint/build.
- Run backend tests.
- Manually verify mock flow, validation failures, one-program case, multiple-program case, and live flow if credentials are available.
```

## Prompt 14 — Add production persistence with Neon Postgres and optional Vercel Blob storage

```text
Add production-grade persistence architecture for the public platform.

Requirements:
- Use Neon Postgres as the production database target.
- Add a clean persistence layer and migrations for SOP review submissions, admissions predictions, and any minimal rate-limit tracking needed.
- Do not force a shared persistence model merely because the tools share AI infrastructure; share only what is genuinely common.
- Keep local development simple.
- Add environment-variable-based configuration.
- If SOP uploaded files are persisted, use Vercel Blob for file storage and store references/metadata in Postgres.
- If full file persistence is not needed for the first release, explicitly design for temporary processing and document that choice instead of overbuilding storage.
- Do not store more sensitive information than necessary.
- Add retention/privacy notes to docs.

Acceptance criteria:
- Database schema is versioned through migrations.
- Persistence is modular and testable.
- Local dev instructions are documented.
- Production configuration is clear.
- Data minimization is intentional and documented.

Required verification:
- Run migration tests or migration application locally where practical.
- Run persistence unit/integration tests.
- Verify environment examples.
- Verify that no raw secrets or local DB artifacts are tracked.
```

## Prompt 15 — Add sensible public rate limiting and secure-by-default behavior

```text
Implement secure-by-default public access controls for both live AI tools.

Requirements:
- No sign-in required.
- Add sensible backend-enforced public rate limits.
- Separate live AI endpoints from mock/demo endpoints where appropriate.
- Add request validation, safe error responses, CORS configuration, secret redaction, structured logging, upload constraints, content-size limits, shared-runtime timeout handling, and clear AI disclaimers where appropriate.
- Document the threat model and security posture for a public repo/public app.

Acceptance criteria:
- A user cannot bypass the real rate limit simply by hiding frontend UI.
- Errors do not reveal secrets.
- Oversized or invalid requests fail safely.
- Mock mode remains usable and does not incur model cost.
- Security docs match actual implementation.

Required verification:
- Add and run tests for rate limiting, validation failures, safe errors, oversize payloads, and provider failures.
- Run lint/type/test suites.
- Review logs and error payloads for accidental secret leakage.
```

## Prompt 16 — Finish the README and public documentation set

```text
Bring the public-facing documentation to final quality.

Update the root README so that a stranger can understand and run the project.

The README must include:
- what the project is
- who it is for
- what the tools do
- architecture overview
- monorepo structure
- tech stack
- local setup
- how to run the web app
- how to run the API
- how to create a .env file
- how to bring your own DeepSeek API key
- how mock/demo mode works
- how to run tests
- deployment overview
- security/privacy notes
- known limitations
- roadmap

Update supporting docs as needed:
- architecture
- deployment
- local development
- security/privacy
- AI system design
- prompt/evaluation methodology

Acceptance criteria:
- A new developer can clone the repo and know exactly what to do.
- The BYO DeepSeek API workflow is obvious.
- The repo looks intentionally designed for public consumption.
- Docs match the actual code.

Required verification:
- Cross-check docs against real scripts, ports, env vars, and commands.
- Search for personal paths, stale names, and false claims.
- Run documentation linting if configured.
```

## Prompt 17 — Add comprehensive tests, CI hardening, and final verification

```text
Perform the final engineering hardening pass for the whole monorepo.

Goals:
- maximize confidence before public release
- remove obvious dead code and stale migration artifacts
- make CI meaningful
- verify the integrated platform end to end

Requirements:
- Ensure coverage exists for shared AI runtime behavior, backend services, API routes, prompt/schema behavior, frontend rendering and API integration, mock mode, validation errors, and rate limiting.
- Ensure CI runs formatting/lint checks, type checks, tests, and builds.
- Add integration tests where they provide real value.
- Add smoke-test instructions for manual release verification.
- Remove obsolete code/docs that are no longer part of the final architecture, but do not delete useful historical context without reason.
- Confirm the old Streamlit apps are either intentionally retained as internal tools and documented as such or removed after migration is complete.

Acceptance criteria:
- All intended automated checks pass.
- CI is coherent and not ceremonial.
- The repo has no obvious stale references to the old architecture.
- The integrated product is testable in both mock and live configurations.
- Any remaining limitations are explicitly documented.

Required verification:
- Run the full test suite.
- Run full lint/type/build checks across the monorepo.
- Run backend smoke tests.
- Run frontend smoke tests.
- If possible, run one end-to-end mock flow for SOP and admissions.
- If live DeepSeek testing is skipped, say so clearly and explain why.
```

## Prompt 18 — Prepare Vercel deployment for web and API

```text
Prepare the monorepo for deployment on Vercel.

Requirements:
- Configure the web app and API app so they can be deployed cleanly from the same monorepo.
- Provide exact deployment instructions for apps/web and apps/api.
- Configure environment variable expectations for DeepSeek, Neon Postgres, optional Vercel Blob, CORS, and frontend API URL.
- Document preview vs production environment setup.
- Ensure health checks and build commands are documented.
- Add any required Vercel config only if necessary; prefer simple, conventional setup.
- Do not put secrets into the repo.

Acceptance criteria:
- A developer can deploy both projects from the monorepo with minimal ambiguity.
- Required env vars are documented.
- Build commands are correct.
- The deployed frontend knows how to reach the deployed backend.
- The architecture remains public-repo safe.

Required verification:
- Validate local production builds.
- Validate documented commands against actual package/scripts/config.
- Inspect deployment docs for completeness.
- If possible, run a local production-like build for both apps.
```

## Prompt 19 — Final public-release audit

```text
Perform a final public-release audit of the entire repository.

Do not make broad feature changes unless needed to resolve a real release blocker.

Audit for:
- secret leakage
- local paths
- private docs
- stale references
- outdated architecture claims
- broken links
- dead code
- inconsistent naming
- unclear setup instructions
- untested behavior
- deployment gaps
- accessibility issues
- mock/live UX clarity
- rate-limit clarity
- security/privacy gaps
- AI limitation disclosures
- theme regressions

Required deliverables:
1. Release readiness scorecard
2. List of blockers
3. List of non-blocking improvements
4. Final recommended README edits, if any
5. Final recommended launch checklist
6. Explicit statement of whether the repo is public-release ready

Acceptance criteria:
- The audit is candid.
- It distinguishes blockers from polish.
- It does not hide unverified areas.
- It gives a clean final go/no-go answer.

Required verification:
- Re-run full checks if needed.
- Re-inspect the repo tree.
- Search for secrets, stale names, and old architecture residue.
- Confirm docs match implementation.
```

## Suggested commit sequence

```text
chore(repo): create monorepo shell
docs(repo): add public project documentation baseline
refactor(sop): extract reusable service modules
refactor(admissions): extract reusable service modules
feat(ai): add shared runtime and deepseek provider
feat(api): expose sop and admissions endpoints
feat(web): migrate frontend to nextjs
feat(web): integrate sop review api
feat(web): add admit predictor tool
feat(data): add postgres persistence
feat(security): add public rate limiting and safe errors
docs(readme): finalize public setup guide
test(repo): harden ci and release checks

```

## Scope-control prompt

Use this if a future Codex run starts expanding too far:

```text
Pause. Re-evaluate the current task against the agreed target state and this prompt only. Do not perform adjacent refactors, redesigns, or speculative improvements. Tell me what is strictly necessary for this step, what is optional, and what you recommend doing now versus later.

```
