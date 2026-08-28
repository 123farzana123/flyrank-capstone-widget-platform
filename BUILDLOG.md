# Build Log — AI Usage

This project was built with Claude as a learning-oriented pair programmer:
concepts were explained before code was written, and I wrote the actual
code myself in almost every case, with Claude reviewing, catching bugs,
and explaining *why* something was wrong rather than just fixing it.

## Where AI helped

- **Explaining new concepts before I wrote code for them** — CORS/preflight,
  JWT verification (including the ES256 vs HS256 distinction, which I hit
  as a real bug against my actual Supabase project, not something I knew
  going in), SQL JOINs, rate limiting, provider fallback patterns, and the
  reasoning behind tenant-isolation-via-query rather than
  application-level checks.
- **Reviewing code I wrote and pointing out specific bugs** — most of this
  project's real debugging time went into things like: a missing comma
  between a SQL string and its values tuple (repeated a few times before
  it stuck), incorrect relative-import dot counts (`.` vs `..` vs `...`)
  as files moved between folders, a return value accidentally wrapped in
  `[...]` making it a list instead of a dict, and an indentation bug where
  `cur.fetchone()` sat outside a `with` block and used an already-closed
  cursor.
- **Writing `widget.js` directly** — the embed script's JavaScript was
  written by Claude given time constraints late in the project; JS was
  outside this course's Python focus and the grading weight here is lower
  than the backend hardening work.
- **Drafting these four documentation files** (README, capstone.yaml,
  EVIDENCE.md, this file) — drafted based on what was actually built and
  tested in conversation, given time pressure near the deadline. I
  reviewed and am submitting them reflecting the real state of the project.
- **PowerShell/curl debugging** — getting a working login request against
  Supabase from Windows PowerShell took real back-and-forth (PowerShell's
  `curl` alias vs real `curl.exe`, quote-escaping, a UTF-8 BOM issue in a
  generated request-body file). This was environment friction, not
  application logic.

## Where AI was wrong / had to be corrected

- An early assumption that Supabase uses a legacy shared-secret (`HS256`)
  JWT scheme turned out to be wrong for this project's Supabase instance,
  which uses the newer asymmetric key-pair (`ES256`) system. This caused
  every login to fail with 401 until diagnosed from the actual token's
  decoded header and fixed by switching to JWKS-based public-key
  verification.

## What I'd do differently with more time

- Fix the known limitation noted in README.md: a malformed `widget_id` in
  the submission URL currently causes a raw DB error instead of a clean
  4xx — needs a format check before the value reaches the repository.
- Move dashboard stats from Python-side aggregation to real SQL
  `GROUP BY` queries.
- Strengthen the oversized-payload test to check the exact configured
  limit rather than just "some large number gets rejected."