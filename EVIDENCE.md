# Evidence

One proof per Definition of Done checkbox (§6 of the brief).

## Widget management

**Authenticated CRUD endpoints; requests without valid auth are rejected.**
Verified manually in Swagger: calling `POST /widgets` without an
Authorization header (before clicking Authorize) returns `401 Unauthorized`
via the `HTTPBearer` security scheme on every widget route.

**Full CRUD works.**
```
POST   /widgets                -> 201 (created, e.g. widget id 6f60b48b-5339-49e9-9ce4-9c87b4f332e9)
GET    /widgets                -> 200 (lists owner's widgets)
GET    /widgets/{id}           -> 200
PUT    /widgets/{id}           -> 200 (updated fields reflected)
DELETE /widgets/{id}           -> 204
DELETE /widgets/{id}  (again)  -> 404 (idempotent: retried delete does not error)
```

**Multi-tenant isolation proven: tenant A cannot read/modify tenant B's widgets.**
Enforced in `app/repositories/widget_repository.py` — every widget query
filters `WHERE id = %s AND owner_id = %s` together. A widget belonging to
a different owner produces no row from the query, which the service/route
layer turns into `404`, identical to the widget not existing at all —
deliberately never `403`, so ownership/existence is never leaked to a
caller who isn't the owner.

## Widget delivery

**Embed snippet generated per widget.**
```
GET /widgets/{id}/embed -> 200
{ "snippet": "<script src=\"http://localhost:8000/widget.js?id={id}\"></script>" }
```

**Public config endpoint, small payload, correct cache headers.**
`GET /widgets/{id}/config` returns `200` with `Cache-Control: public,
max-age=60` set via `app/routes/submissions.py`'s `get_widget_config`
route — confirmed via response headers in Swagger.

**Widget JS served as a stable, dedicated URL.**
`GET /widget.js` served via a dedicated FastAPI route
(`app/main.py::serve_widget_js`), returned as `application/javascript`.

**Widget renders on a second-origin page.**
Verified manually: `customer-site/index.html` served via VSCode Live
Server on `http://localhost:5500`, loading
`<script src="http://localhost:8000/widget.js?id=6f60b48b-5339-49e9-9ce4-9c87b4f332e9">`.
The form (title, description, input fields from `config.fields`, submit
button) rendered correctly on the page, and the browser console showed
no CORS errors once a real widget id replaced the initial placeholder
(an earlier attempt with the literal placeholder text correctly produced
a fetch failure, confirming the script's error path too).

## Public submission API

**CORS + preflight work correctly.**
```
tests/test_submissions.py::test_cors_preflight PASSED
```
Checks an `OPTIONS` preflight from `http://localhost:5500` returns `200`
with `Access-Control-Allow-Origin: http://localhost:5500`.

**Malformed/oversized payloads rejected with clean 4xx, never 500.**
```
tests/test_submissions.py::test_invalid_payload_rejected PASSED   (422 on missing `data` field)
tests/test_submissions.py::test_oversized_payload_rejected PASSED (413 via a Content-Length limit middleware, app/main.py::limit_body_size)
```

**Valid submissions stored, linked to the right widget and tenant.**
```
POST /widgets/6f60b48b-5339-49e9-9ce4-9c87b4f332e9/submissions -> 201
{
  "id": 48,
  "widget_id": "6f60b48b-5339-49e9-9ce4-9c87b4f332e9",
  "data": {"name": "Test Visitor", "email": "test@example.com"},
  "ip_address": "172.21.0.1",
  "country": null,
  "city": null,
  "created_at": "2026-08-28T17:47:28.019572"
}
```
(`ip_address` is the real connecting address seen by the server —
Docker's internal network address in local testing; `country`/`city` are
null here because local/internal IPs don't resolve to a real-world
location, which is expected, not a bug — see geo fallback evidence below
for the actual failure-handling proof.)

## Abuse protection

**Rate limiting returns 429 under a burst; legitimate traffic still served after.**
```
tests/test_submissions.py::test_rate_limiting PASSED
```
5 requests/minute per IP, enforced via `slowapi` (`app/rate_limit.py`,
`@limiter.limit("5/minute")` on the submission route). Also manually
verified in Swagger: 5 rapid submissions succeeded, the 6th returned
`429`.

**Honeypot demonstrably blocks a spam submission.**
```
tests/test_submissions.py::test_honeypot_blocks_spam PASSED
```
A submission with the hidden `website` field filled in returns `204`
and is never inserted into the database — confirmed both by the
automated test and manually in Swagger.

## Enrichment & safe side effects

**IP→geo enrichment uses a provider fallback chain (A down -> B answers); both down -> still succeeds without geo.**
```
tests/test_submissions.py::test_geo_fallback_chain PASSED
```
`app/geo.py::get_geo_from_ip` tries `ip-api.com`, then `ipapi.co` on
failure, then returns `{"country": None, "city": None}` if both fail —
the automated test mocks `httpx.get` to always raise, confirming the
fully-degraded path returns cleanly rather than raising.

**A failing confirmation email/webhook does not prevent the submission from being stored.**
Manually verified: temporarily edited `app/email.py::send_confirmation_email`
to unconditionally `raise Exception("Simulated email failure")`, rebuilt
the container, and submitted a normal (non-spam) form. The submission
still returned `201` with the submission correctly stored — the `try/except`
around the email call in `app/routes/submissions.py::create_submission`
swallowed the forced failure without affecting the response. Reverted
`email.py` to its real (console-logging) behavior afterward.

## Owner dashboard

**GET /widgets/{id}/submissions returns submissions for that widget, tenant-scoped via JOIN.**
```
GET /widgets/6f60b48b-5339-49e9-9ce4-9c87b4f332e9/submissions -> 200
[
  {
    "id": 48,
    "widget_id": "6f60b48b-5339-49e9-9ce4-9c87b4f332e9",
    "data": {"name": "Test Visitor", "email": "test@example.com"},
    "ip_address": "172.21.0.1",
    "country": null,
    "city": null,
    "created_at": "2026-08-28T17:47:28.019572"
  }
]
```
Tenant isolation enforced via a SQL `JOIN` against `widgets` in
`app/repositories/submission_repository.py::list_submissions`
(`WHERE s.widget_id = %s AND w.owner_id = %s`) — a widget belonging to a
different owner returns an empty list, not another tenant's data.

**GET /widgets/{id}/stats returns basic aggregated stats.**
```
GET /widgets/6f60b48b-5339-49e9-9ce4-9c87b4f332e9/stats -> 200
{
  "total_submissions": 1,
  "by_country": {"Unknown": 1}
}
```

## Tests & documentation

**Automated tests cover all required scenarios.**
```
tests/test_submissions.py::test_cors_preflight PASSED
tests/test_submissions.py::test_invalid_payload_rejected PASSED
tests/test_submissions.py::test_oversized_payload_rejected PASSED
tests/test_submissions.py::test_honeypot_blocks_spam PASSED
tests/test_submissions.py::test_geo_fallback_chain PASSED
tests/test_submissions.py::test_rate_limiting PASSED
tests/test_submissions.py::test_widget_config_endpoint_structure PASSED
7 passed, 1 warning in 3.96s
```
Run via `docker compose exec app pytest tests/ -v`.

**README + all five submission-pack files present.**
`README.md`, `capstone.yaml`, `EVIDENCE.md` (this file), `BUILDLOG.md`,
`.env.example` — all present at repo root.