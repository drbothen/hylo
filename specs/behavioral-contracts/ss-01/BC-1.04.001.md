---
document_type: behavioral-contract
level: L3
version: "1.3.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:11:24Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md]
input-hash: "6f3f463"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:fetch_sample (SL:158-187)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-040"
parity_class: byte-exact
confidence: M
lifecycle_status: active
introduced: v0.1.0
modified: ["2026-11-17 (v1.3) pass-2 remediation ADV-P2-C2-08/09/13/14", "2026-11-18 (v1.3.1) pass-3 remediation ADV-P3-C2-04/05/10 (redirect loop detection; OverflowError catch; 1e400; key identity)", "2026-11-18 (v1.3.2) sync — Verification Properties row relabeled; VP-022 (partial: network edge only) now states its own property (the status line never reads the ledger, DI-007) instead of VP-030's differential-equivalence text", "2026-11-18 (v1.3.3) pass-4 remediation ADV-P4-C2-01/02 (overflow vector >= 2**1024 - 2**970; metric wrapper on the two-key vector), ADV-P4-C2-07 (37-hop worst case; normalized redirect key; rebuilt chain example), ADV-P4-C2-08 (URI header fallback), ADV-P4-C2-09 (Accept-Encoding: identity / DisableCompression), ADV-P4-C2-12 (CP-N03 named on EC-013)", "2026-11-17 (v1.3.4) pass-4 residual sweep — D4-EX-3 table-test name canonicalized to TestD4EX3_* (ADV-P4-D22)"]
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
   `%7B__name__%3D~%22vllm%3Anum_requests_running%7C...`). Transport headers: hylo sends
   what urllib sends — including `Accept-Encoding: identity` (oracle-verified against a
   local listener, CPython 3.11.7, 2026-11-17) — and parses the response body raw, so the
   Go transport sets `DisableCompression: true` (or equivalent): Go's default Transport
   would otherwise send `Accept-Encoding: gzip` and silently decompress, letting Go parse
   a compressed body into a sample where legacy, which never asked for compression, gets
   none (ADV-P4-C2-09). Redirects: the Go client follows HTTP redirects exactly as
   urllib's default `HTTPRedirectHandler` (active because
   `build_opener(ProxyHandler({}))` keeps it, SL:168-171) — a 301/302/303/307/308 is
   followed by GET and the **final** body is parsed; other statuses are not redirected.
   Header read (CPython 3.11.7 `http_error_302`, verified from the 3.11.7 stdlib source
   on 2026-11-17): the target is the first `Location` header, falling back to the first
   `URI` header when `Location` is absent; a 30x carrying neither header is returned
   unhandled (HTTPError → no sample). A redirect naming only `URI:` is therefore followed
   by legacy and must be followed by hylo; a client that reads only `Location` gets no
   sample where legacy gets one (ADV-P4-C2-08). Scheme guard: the scheme of the raw
   (pre-normalization) target must be `http`, `https`, `ftp` or empty (inherit); anything
   else makes urllib raise `HTTPError`. Target normalization (ADV-P4-C2-07): the
   loop-detection key is the target AFTER the raw-header scheme check, the empty-path fix
   (netloc with no path → `/`), percent-encoding of non-ASCII and special bytes
   (`quote(..., encoding="iso-8859-1")`), and resolution to an absolute URL
   (`urljoin(req.full_url, ...)`); a raw `Location: /x` and a `Location: http://<host>/x`
   that resolve to the same absolute URL are ONE key — keying the raw header would split
   them and must not be done. Pinned loop detection: urllib keeps a per-request
   `redirect_dict` keyed by that normalized absolute redirect-target URL (the initial URL
   is never a key) and, before following, refuses iff
   `visited.get(newurl, 0) >= max_repeats (= 4)` **or** `len(visited) >= max_redirections
   (= 10)`; the target's count increments only after the decision to follow. The cap is
   therefore NOT a hop counter: at most 10 distinct targets are ever keyed, a keyed
   target is followed at most 4 times, and the tenth key's single follow exhausts the
   budget — worst case 9×4 + 1 = **37 hops**, after which every further redirect is
   refused. A chain that revisits targets (A→B→A→B…, each visit count < 4) is followed
   while the counts hold, and a distinct-target chain is refused at its 11th redirect
   (len = 10); a Go `CheckRedirect` that counts hops refuses chains urllib follows
   (sample vs no sample). The caps 4/10 are CPython stdlib class constants emulated for
   parity — named constants in hylo with a "why not config" comment, not config keys
   (P16). Normative Go rule: emulate `redirect_dict` exactly — in `CheckRedirect`,
   normalize the response's target the way urllib does, then fail the request (return an
   error, not `ErrUseLastResponse`) iff `count[normalized] >= 4 || len(count) >= 10`;
   otherwise `count[normalized]++` and follow. Hylo must reproduce every refusal mode the
   way urllib does — the fetch fails to "no sample" (outer `except Exception`, SL:186) —
   and must never parse the refused 3xx body.
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
     aborts the whole fetch (no sample). So is an `OverflowError`: Python's `json.loads`
     decodes an integer literal at arbitrary precision, and a JSON integer with
     |value| >= 2**1024 - 2**970 (oracle-verified on CPython 3.11.7, 2026-11-18) raises
     `float(int)` outside the per-series catch (SL:177-180) and aborts the whole fetch
     (no sample, outer `except Exception` SL:186). A JSON **float** literal is not
     subject to that conversion — `1e400` is decoded by `json.loads` itself to +Inf and
     kept. A Go float64 decode maps both literal forms to +/-Inf, so it must
     special-case the oversize integer literal to stay differential-equivalent.
   - `name == "up"` is rewritten to `"up:" + s["metric"].get("job", "")`; a non-string
     `job` makes the concatenation raise `TypeError` — both sites sit outside the
     per-series catch (SL:182-185) — and aborts the whole fetch (no sample).
   - The pair is stored only if `name` is truthy and not already present
     (**first wins**). Membership is dict hashing, so an unhashable non-empty
     `__name__` (list, dict) raises `TypeError` at `name not in out` (SL:183-184) and
     aborts the whole fetch, while an empty list/dict name is falsy and the series is
     skipped. The hashable non-strings `1`, `1.0` and `true` collide under first-wins
     (`True == 1`, equal hash; `1.0 == 1`) and round-trip through the JSON cache write
     as strings. Key identity is Python hash/eq, not text: the string `"5"` and the int
     `5` are **distinct** dict keys, and `json.dump` writes both as the JSON text
     `"5"` (a duplicate-key object, SL:203); a `json.load` of that object keeps the
     **last** one. And the JSON constant `NaN` decodes to one shared float object, so
     two series whose `__name__` is `NaN` collide through dict identity and first-wins
     keeps the first (oracle-verified 2026-11-18). A Go `map[string]float64` model
     diverges on both counts under the VP-030 differential; hylo must carry the
     Python key identity (typed hash/eq key plus the shared-NaN sentinel) through the
     session-cache round trip (BC-1.04.020).
5. The function never raises; the render path continues with the result.

## Invariants

1. One fetch decision per refresh (BC-1.04.002 decides whether to fetch); the decision issues the initial GET plus any redirect hops urllib's default handler would also take — a bare single-request `Transport` is not parity-compatible.
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
| EC-013 | `__name__` is a number (`5`) | stored under int key 5; `serving_state`'s `any(k.startswith("vllm:") for k in m)` short-circuits at the first `vllm:` key (SL:717), so the numeric key degrades the line (BC-1.01.001) only when it precedes every `vllm:`-prefixed key (`{5: 1}` alone → degraded; `{"vllm:x": 1, 5: 1}` → renders normally). Metrics-borne degrade, crash id **CP-N03**. After the session-cache write the key round-trips through JSON as the string `"5"`, so later cached-path refreshes never degrade |
| EC-014 | HTTP 500 / 404 | no sample |
| EC-015 | body `not json`; `[1,2]`; `{"status":"error"}`; `result` = `{}` or `"ab"` | no sample |
| EC-016 | body with UTF-8 BOM | accepted (bytes-mode decode) |
| EC-017 | connection refused / timeout | no sample |
| EC-018 | `value[1]` = a bare JSON integer literal with magnitude >= 2**1024 - 2**970 (the smallest magnitude that overflows; e.g. 2**1024 - 2**970 itself. Note 10**308 — also 309 digits — is BELOW DBL_MAX: `float(10**308)` returns `1e+308` without raising, oracle-verified CPython 3.11.7, ADV-P4-C2-01) | `float(int)` raises OverflowError outside the per-series catch (SL:177-180, 186) → **no sample**; a bare float literal `1e400` next to it is kept as +Inf (ADV-P3-C2-05) |
| EC-019 | `value[1]` = `1e400` (bare JSON float literal) | `json.loads` decodes it to +Inf; `float(+Inf)` = +Inf → series stored (`{"x": +Inf}`) |
| EC-020 | two series, `__name__` = string `"5"` and int `5` | both stored (distinct keys, insertion order); `json.dump` emits two `"5"` keys; the cache reload keeps the **last** (ADV-P3-C2-10) |
| EC-021 | two series, both `__name__` = `NaN` | one shared NaN object → dict identity collides → first wins (ADV-P3-C2-10) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `{"status":"success","data":{"result":[{"metric":{"__name__":"vllm:num_requests_running"},"value":[1,"3"]},{"metric":{"__name__":"up","job":"vllm"},"value":[1,"1"]},{"metric":{"__name__":"up","job":"lmcache"},"value":[1,"0"]}]}}` | `{"vllm:num_requests_running": 3.0, "up:vllm": 1.0, "up:lmcache": 0.0}` (this order) | happy-path |
| result with `"NaN"`, `"+Inf"`, `"1e400"` for x, y, z | `{"x": NaN, "y": +Inf, "z": +Inf}` | edge-case |
| result `[{"metric":{"__name__":"y"},"value":[1,"7"]},{"metric":{"__name__":"x"},"value":5}]` | no sample | error |
| result `[{"metric":{"__name__":"x"},"value":[1,1e400]}]` | `{"x": +Inf}` | edge-case |
| result `[{"metric":{"__name__":"y"},"value":[1,"7"]},{"metric":{"__name__":"x"},"value":[1,<2**1024 - 2**970 as a bare JSON integer literal>]}` | no sample (integer-literal OverflowError; the smallest overflowing magnitude, ADV-P3-C2-05 + ADV-P4-C2-01) | error |
| result `[{"metric":{"__name__":"5"},"value":[1,"1"]},{"metric":{"__name__":5},"value":[1,"2"]}]` | two keys stored (distinct keys: string `"5"` then int `5`, insertion order); after a cache round trip one `"5"` key remains holding `2.0` (ADV-P4-C2-02) | edge-case |
| HTTP 500 with a valid body | no sample | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | For any response bytes, the Go fetch returns the same map (keys incl. Python key identity per PC4 — distinct `"5"`/`5`, shared NaN; order; float bits) or "no sample" as legacy | fuzz (Tier C differential) + table |
| VP-022 (partial: network edge only) | The status line never reads the ledger (DI-007): the metrics fetch reads only the VictoriaMetrics HTTP response at the network edge — no ledger/file reads in the render path | static analysis (read-scope absence) |
| VP-030 | The function never panics or returns an error to the caller | fuzz |
| VP-030 | Request URL bytes equal legacy's for the default query | manual (golden) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:fetch_sample (SL:158-187); QUERY (SL:102-123); VM_URL/HTTP_TIMEOUT (SL:73, 81) |
| Legacy contract | BC-SL-040 (P3 base + r1 refinement; r5 verified, r8 coverage) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007, DI-008, DI-012 (metrics-URL D4-EX-3 deviation, BC-2.02.005) |
| Decisions | OD-123 (metrics URL under backends[0]), OD-56 (timeout = total deadline), OD-57 E-0 (T-005), D14 (proxy bypass is defense in depth) |
| Architecture Module | `internal/statusline/telemetry.go` (design §2.2; listed in ARCH-03 §Interfaces, line 114) |
| Stories | TBD (story-writer) |

## Related BCs (Recommended)

- BC-1.04.002 — composes with: decides when this fetch runs and stores its result
- BC-1.04.016 — related to: renders non-finite values this fetch admits
- BC-5.01.002 — depends on: Python float grammar
- BC-5.02.003 — depends on: `json.loads(bytes)` acceptance set
- BC-2.01.002 — depends on: `backends[0].metrics_url`
- BC-2.02.005 — related to: a non-http(s) metrics URL is not fetched at all; it is approved deviation D4-EX-3 (config error line; OD-105 exclusion entry `D4-EX-3`, dedicated test `TestD4EX3_URL`), whereas legacy handed any string to urllib (BC-SL-087: a bad URL yields no sample)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/telemetry.go (query, total deadline, first-wins) (metrics client and fake-metrics seam) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — fetch differential equivalence; VP-022 (partial) — network-edge read scope only

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
