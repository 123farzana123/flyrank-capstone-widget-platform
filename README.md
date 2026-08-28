# Embeddable Widget & Lead-Capture Platform

A backend platform that lets an authenticated owner create embeddable widgets
(signup forms, CTA popovers), hand out a one-line `<script>` embed snippet,
and safely accept submissions from any website on the public internet —
validated, rate-limited, spam-filtered, geo-enriched, and shown back in a
dashboard.

Built with FastAPI + PostgreSQL, running in Docker.

## Architecture

Three separate request paths, each with a different trust level:

```
Widget Owner (authenticated, JWT via Supabase)
  └─► Widget Management API ─► Widget DB (tenant-isolated) ─► embed snippet

Customer Website (any origin)
  └─ <script src="widget.js?id=123">
  └─► GET /widgets/:id/config (public · cached · CORS)
  └─► render widget

Website Visitor (anonymous, any origin)
  └─► POST /widgets/:id/submissions (public · CORS)
      ├─► honeypot check ── bot? → 204, silently dropped
      ├─► rate limit (5/min per IP) ── flood? → 429, service stays up
      ├─► geo enrichment: Provider A ─(fails)─► Provider B ─(fails)─► store anyway
      ├─► store submission
      └─► confirmation email (best-effort; failure never blocks success)

Widget Owner (authenticated)
  └─► GET /widgets/:id/submissions, /widgets/:id/stats ◄── dashboard
```

**Layering**, same pattern throughout: `routes → service → repository`.
Routes handle HTTP concerns only; services hold business logic (currently
thin, but the seam is there for future rules); repositories hold all raw
SQL. No layer skips another.

**Tenant isolation** is enforced in SQL itself, not just application logic:
every widget query filters `WHERE id = %s AND owner_id = %s`; a mismatch
returns no row → `404`, never `403` — this avoids leaking whether a widget
exists to someone who doesn't own it. Submissions don't store `owner_id`
directly; ownership is enforced via a `JOIN` against `widgets` on every
dashboard query.

## Running it

```bash
cp .env.example .env   # fill in your own Supabase project values
docker compose up --build
```

This starts Postgres (schema auto-applied from `db/schema.sql` on first
boot, persisted in a named volume) and the FastAPI app together. API at
`http://localhost:8000`, docs at `http://localhost:8000/docs`.

### Seeding / trying it out

1. Create a Supabase user (Authentication → Users) to act as a widget owner.
2. Get a JWT for that user via Supabase's password-grant endpoint (see
   `EVIDENCE.md` for the exact command used during development).
3. In Swagger (`/docs`), click **Authorize**, paste the token.
4. `POST /widgets` to create a widget, copy its `id`.
5. Open `customer-site/index.html` (a plain HTML file simulating a
   completely separate website) with that `id` in its `<script>` tag,
   served on a different origin (e.g. VSCode Live Server, port 5500).
6. The widget renders and submits cross-origin — proving CORS, the public
   config endpoint, and the public submission endpoint all work together.

### Running tests

```bash
docker compose exec app pytest tests/ -v
```

## API overview

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/widgets` | owner | create a widget |
| GET | `/widgets` | owner | list owner's widgets |
| GET | `/widgets/{id}` | owner | get one widget (404 if not owned) |
| PUT | `/widgets/{id}` | owner | update (type is immutable — see below) |
| DELETE | `/widgets/{id}` | owner | delete |
| GET | `/widgets/{id}/embed` | owner | get the `<script>` embed snippet |
| GET | `/widgets/{id}/config` | public | cached widget config, for `widget.js` |
| GET | `/widget.js` | public | the embeddable script |
| POST | `/widgets/{id}/submissions` | public | visitor form submission |
| GET | `/widgets/{id}/submissions` | owner | dashboard: list submissions |
| GET | `/widgets/{id}/stats` | owner | dashboard: basic stats |

Full interactive docs at `/docs`.

## Design notes worth knowing

- **Auth**: Supabase Auth, `ES256` JWTs verified against Supabase's public
  JWKS endpoint (not a shared secret — this project's Supabase instance
  uses the newer asymmetric key-pair signing system).
- **`widget_type` is immutable after creation.** Changing it would leave
  `config`'s shape mismatched with the widget's declared type. To change
  type, delete and recreate.
- **Raw SQL, not an ORM** — a deliberate choice to stay consistent with
  patterns already proven out in an earlier project in this track, and to
  keep focus on the genuinely new concepts this capstone introduces (CORS,
  rate limiting, fallback chains) rather than also learning ORM syntax.
- **Honeypot spam control**: `SubmissionCreate` includes an optional
  `website` field that real users never see/fill; if present, the
  submission is silently dropped (`204`, never stored).
- **Geo enrichment fallback chain**: `ip-api.com` → `ipapi.co` → give up
  gracefully. All three outcomes are covered by automated tests (the
  provider calls are mocked for determinism).

## Known limitations

- A malformed (non-UUID) `widget_id` in the submission URL currently
  reaches the database layer before failing, producing a raw DB error
  rather than a clean `4xx`. Caught via testing; not yet fixed given time
  constraints — a good next improvement (validate the path parameter's
  format before it reaches the repository).
- Dashboard stats are computed in Python from the full submission list
  rather than via SQL aggregation (`GROUP BY`) — fine at this scale, would
  need revisiting for a widget with a very large submission count.
- The widget UI rendered by `widget.js` is intentionally minimal (a bare
  form), per the brief's own scope guidance — the grading surface here is
  the backend, not the frontend polish.