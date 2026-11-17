---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md]
input-hash: "d7b0b4e"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-040"
parity_class: byte-exact
confidence: M
lifecycle_status: active
introduced: v0.1.0
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.001: fetch_sample: query, 1.5 s timeout, first-wins

## Description

One metrics-store instant query per fetch turns the backend's metrics into a flat
sample `{series name: float}`. The query string, the URL shape, the proxy bypass, the
per-series skip rule and the first-wins rule reproduce legacy `fetch_sample` exactly;
every failure collapses to "no sample" (never an error, never a crash). Notation: `\e`
is byte 0x1B.

## Preconditions

1. The metrics URL is `backends[0].metrics_url` (OD-123; default `http://192.0.2.10:8428`,
   legacy SL:73), with every trailing `/` stripped (legacy `rstrip("/")`).
2. The query is config key `statusline.telemetry.query`, whose default is
   **byte-identical** to legacy `QUERY` (SL:102-123); the pinned golden is that literal.
3. The timeout is `statusline.telemetry.timeout_s`, default 1.5 s (T-005, rationale
   "~60x the measured ~25 ms LAN RTT and below one 4 s refresh tick", OD-57 E-0).

## Postconditions

1. Exactly one HTTP GET is issued to
   `<url>/api/v1/query?query=<QUERY percent-encoded as Python quote(QUERY, safe='')>`
   (space as `%20`, never `+`; the encoded prefix is
   `%7B__name__%3D~%22vllm%3Anum_requests_running%7C...`).
2. Proxy environment variables are ignored for this request (legacy `ProxyHandler({})`,
   SL:168; Go `Transport{Proxy: nil}`).
3. Result is **no sample** (Go: nil; legacy `None`) when: the status is outside 200-299;
   the body is not decodable JSON (decoded as `json.loads(bytes)`, BC-5.02.003); the
   payload is not an object; `payload["status"] != "success"`; `data`/`result` is
   missing or of a wrong type; any series raises outside the per-series catch; or the
   resulting map is empty.
4. Otherwise, for each element `s` of `data.result`, in array order:
   - `name = s["metric"].get("__name__", "")`; a missing `metric` key or a non-object
     `metric` aborts the **whole** fetch (no sample).
   - `val = float(s["value"][1])` with the Python float grammar (BC-5.01.002). On
     `KeyError`, `ValueError` or `IndexError` that series is skipped. A `TypeError`
     (e.g. `value` is a number, `value[1]` is `null`) is **not** caught per series and
     aborts the whole fetch (no sample).
   - `name == "up"` is rewritten to `"up:" + s["metric"].get("job", "")`.
   - The pair is stored only if `name` is truthy and not already present
     (**first wins**).
5. The function never raises; the render path continues with the result.

## Invariants

1. At most one metrics request per fetch decision (BC-1.04.002 decides whether to fetch).
2. Non-finite strings (`"NaN"`, `"+Inf"`, `"-Inf"`, `"1e400"`) are accepted as floats and
   flow to the renderers and history unchanged (handled by BC-1.04.014/015/016).
3. Ordering of the sample map is insertion order (it is written to the session cache in
   that order, BC-1.04.020).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Two series with the same `__name__` | first in the array kept: `x`=1 then `x`=2 → `{"x": 1.0}` |
| EC-002 | `value[1]` = `"a5"` next to a good series | `"a5"` skipped (ValueError), `{"y": 7.0}` |
| EC-003 | Every series skipped | no sample (empty map → None) |
| EC-004 | `value` = `5` (TypeError) next to a good series | **no sample** (whole fetch dropped) |
| EC-005 | `value` = `[1, null]` | no sample (TypeError) |
| EC-006 | `value` = `[1]` or key absent | that series skipped (IndexError/KeyError) |
| EC-007 | `value` = `"17"` (a string) | `"17"[1]` = `"7"` → `7.0` |
| EC-008 | `value` = `[1, true]` | `1.0` |
| EC-009 | `value[1]` = `" ١_0 "` (Unicode digit, underscore, spaces) | `10.0` (Python float grammar) |
| EC-010 | `metric` = `{}` | name `""` → series skipped, others kept |
| EC-011 | `metric` key missing on any element | no sample |
| EC-012 | `up` without `job` label | key `"up:"` |
| EC-013 | `__name__` is a number (`5`) | stored under int key 5; later `serving_state` calls `startswith` on it → degraded line (BC-1.01.001) after the session-cache write (JSON key `"5"`) |
| EC-014 | HTTP 500 / 404 | no sample |
| EC-015 | body `not json`; `[1,2]`; `{"status":"error"}`; `result` = `{}` or `"ab"` | no sample |
| EC-016 | body with UTF-8 BOM | accepted (bytes-mode decode) |
| EC-017 | connection refused / timeout | no sample |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `{"status":"success","data":{"result":[{"metric":{"__name__":"vllm:num_requests_running"},"value":[1,"3"]},{"metric":{"__name__":"up","job":"vllm"},"value":[1,"1"]},{"metric":{"__name__":"up","job":"lmcache"},"value":[1,"0"]}]}}` | `{"vllm:num_requests_running": 3.0, "up:vllm": 1.0, "up:lmcache": 0.0}` (this order) | happy-path |
| result with `"NaN"`, `"+Inf"`, `"1e400"` for x, y, z | `{"x": NaN, "y": +Inf, "z": +Inf}` | edge-case |
| result `[{"metric":{"__name__":"y"},"value":[1,"7"]},{"metric":{"__name__":"x"},"value":5}]` | no sample | error |
| HTTP 500 with a valid body | no sample | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030, VP-022 (partial: network edge), VP-022 (frontmatter closure) | For any response bytes, the Go fetch returns the same map (keys, order, float bits) or "no sample" as legacy | fuzz (Tier C differential) + table |
| VP-030, VP-022 (partial: network edge), VP-022 (frontmatter closure) | The function never panics or returns an error to the caller | fuzz |
| VP-030, VP-022 (partial: network edge), VP-022 (frontmatter closure) | Request URL bytes equal legacy's for the default query | manual (golden) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:fetch_sample (SL:158-187); QUERY (SL:102-123); VM_URL/HTTP_TIMEOUT (SL:73, 81) |
| Legacy contract | BC-SL-040 (P3 base + r1 refinement; r5 verified, r8 coverage) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007, DI-008 |
| Decisions | OD-123 (metrics URL under backends[0]), OD-56 (timeout = total deadline), OD-57 E-0 (T-005), D14 (proxy bypass is defense in depth) |
| Architecture Module | `internal/statusline/telemetry.go` (design §2.2; architect to confirm) |
| Stories | TBD (story-writer) |

## Related BCs (Recommended)

- BC-1.04.002 — composes with: decides when this fetch runs and stores its result
- BC-1.04.016 — related to: renders non-finite values this fetch admits
- BC-5.01.002 — depends on: Python float grammar
- BC-5.02.003 — depends on: `json.loads(bytes)` acceptance set
- BC-2.01.002 — depends on: `backends[0].metrics_url`
- BC-2.02.005 — related to: a non-http(s) metrics URL is not fetched at all; it is approved deviation D4-EX-3 (config error line; OD-105 exclusion entry `D4-EX-3`, dedicated test `TestConfigError_D4EX3_URL`), whereas legacy handed any string to urllib (BC-SL-087: a bad URL yields no sample)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#metrics-client` — internal/statusline/telemetry.go (query, total deadline, first-wins) (metrics client and fake-metrics seam) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030, VP-022 — fetch differential equivalence

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:102-123, 158-187) |
| **Confidence** | medium — the per-site catch list (`TypeError` drops the whole sample) is the subtle surface (design §8 row 040) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `except (KeyError, ValueError, IndexError): continue` (SL:179-180); outer `except Exception` (SL:186)
- **inferred**: series order = VictoriaMetrics result order; re-executed against a local fake server on CPython 3.11.7 (2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | network call |
| **Global state access** | reads config |
| **Deterministic** | no — depends on the metrics store |
| **Thread safety** | unknown (single-threaded use) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Split into a `MetricsClient.Query` seam (I/O, `httptest` fake in tests) and a pure
`parseSample(body []byte) (Value, bool)` that carries the catch-list semantics. Timeout
semantics differ by owner ruling OD-56: legacy's 1.5 s is per socket operation, Go's is
a total deadline. The parity corpus never exercises timeouts (fake metrics failure
modes are closed listener, 5xx and garbage), so this is not an output difference and has
no exclusion entry.
