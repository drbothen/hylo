---
document_type: architecture-section
level: L3
section: "statusline"
version: "1.18"
status: draft
producer: architect
timestamp: 2026-11-23T10:00:00Z
phase: 1b
inputs: [prd.md, prd-supplements/error-taxonomy.md, semport/hylo-legacy/statusline-target-design.md, behavioral-contracts/BC-INDEX.md]
traces_to: ARCH-INDEX.md
input-hash: "ed463e4"

---

# ARCH-03 — Status line render pipeline (`internal/statusline`)

> The port target. Carries all S1 BCs (BC-1.01..1.07, including the OD-155 subagent
> panel, BC-1.07.001..008). Classification: **mixed, core-dominant** —
> pure widget/parser/format functions plus one ordered effect script. CRITICAL tier
> (statement coverage (the OD-158 gate's 'line coverage') >= 95% for P1; mutation
> kill rate >= 95% is the Phase 6 target,
> OD-135/OD-158).

### Decision: pure widgets plus an ordered effect script (AD-03)

- **Context:** legacy reads back its own writes within one refresh (effective_rl writes
  the session cache; get_sample re-reads and rewrites it; window start re-reads it), so
  the whole refresh cannot be one pure function — an in-memory overlay would get the
  failed-replace persistence semantics wrong (BC-1.06.002: a failed replace persists
  nothing and the next read must see that).
- **Options considered:** (1) one pure render + a final commit block — wrong persistence
  semantics on failed replaces; (2) pure widgets + one orchestrator executing legacy's
  effect order through injected seams.
- **Decision:** option 2 (design doc §3). The orchestrator `Render` executes the step
  script below, calling seams in exactly legacy's order (BC-1.01.009): a crash at step
  k keeps the writes of steps 1..k-1.
- **Rationale:** identical cache states after both happy and degraded runs are a parity
  requirement; only order-preserving effects achieve it.
- **Consequences:** every nondeterminism source is an `Env` interface; the pure renders
  are table-testable without a temp dir; the seams double as harness hooks (ARCH-07).
- **Verification feasibility:** pure renders — **provable-grade** oracle-pinned tables,
  mutation target >= 95% (the Phase 6 target, not a P1 gate; OD-158); the effect order — **testable-only**, order-asserting recording
  fakes plus parity steps (ARCH-07). A widget that needs I/O gets redesigned, not patched
  (iron law).

## Effect-step script (design doc §3.1, normative)

**Ownership of step 0 (ADV-P2-A08):** config resolution is NOT inside `Render`. `Main`
performs step 0: it calls `config.Load` through the injected `EnvVars` seam it is given
(AD-10 amended; ARCH-01), then constructs over the Load-resolved configuration every
seam that reads config at build time (pass-5 A11 — `Query`/`WindowStart` take no
config argument, so pre-built arrivals are impossible):
the `CacheStore` over `paths.cache_dir`, the `MetricsClient` over
`backends[0].metrics_url` and `telemetry.timeout_s`, and the `ProcStarter` over
`window_age.process_name` and `window_age.max_depth`. On a `config.Load` error it prints
the E-CFG-001 line
(first error in registry order, full list to stderr) and returns 0 having written no
caches — `Render` is never entered. A `CacheDir` error at step 0 is NOT a config error
(ADV-P11-A08, pass-11 orchestrator call 9): `Main` wires the load-empty / save-no-op
cache store BC-3.01.001 EC-004 pins and the render PROCEEDS (`Render`'s
`env.Cache != nil` precondition is still satisfied — the no-op store IS a `CacheStore`;
there is no E-CFG-001 and no exit from a directory-resolution failure).
`Env.Loc` is derived exclusively from `platform.LocalZone(env)` (ARCH-05, single zone
seam); LocalZone's error result is non-nil ONLY on the TZ-unset path when OS resolution
fails (BC-3.01.001 PC-6) — on that error `Main` wires `Env.Loc = time.UTC` and the
render proceeds (derived judgment call: never-raise at the orchestrator, DI-008; the
spec family pins no config-error class for a zone failure, so a UTC fallback matching
LocalZone's own empty/unparseable verdicts is the in-family disposition).
`Render`'s precondition is `env.Config != nil &&
env.Cache != nil`
(non-error `*config.Config`), guaranteed by `Main`; the "no cache writes" guarantee
follows because every cache write sits inside `Render`'s step script.

| # | Step | Seams | Degrade? |
|---|---|---|---|
| 0 | config resolved by `Main` (precondition; D4-EX-3 before any write) | `config.Load` (in `Main`) | config-error line |
| 1 | stdin decode (`pyfmt.Decode`, ModeText) | stdin | no — invalid => `{}` (BC-1.01.002/.008) |
| 2 | transcript parse, then mix-cache write | `Files`, `Cache` | D4-EX-2 skip (wrong-shape lines); CP-O06..O08 overflow lines skipped whole, in-flight turn dropped (OD-167); CP-O09 no-write save (the int-to-string breach at the save reproduces legacy's no-write, BC-1.01.009 step 2 — pass-12 B06); CP-S14/S16 degrade sticky (non-string sid at `re.sub` SL:1017; bad `transcript_path` type SL:1010); Windows: a naive timestamp on/before 1970-01-01 or from year ≥ 3001 makes MSVC `localtime_s` raise OSError out of `_iso_ts` (which catches only ValueError) and DEGRADES the whole line (CP-T09; BC-5.04.001 v1.2.3, owner call 8; pass-6 C01 — Windows test vectors derived from the pre-call-8 BCs assert the wrong outcome) |
| 3 | effective_rl (session-cache write iff non-empty rl dict) | `Cache`, `Now` | no catalogued vector; foreign-cache CP-C01/C02 only (the CP-C family, OD-160 — BC-1.01.009 step table) |
| 4 | get_sample when ROWS >= 2: fetch, then session-cache write | `Metrics`, `Cache`, `Now` | no catalogued vector; foreign-cache CP-C03/C04 (the CP-C family, OD-160): a wrong-shape restored sample or `up` bearer raises out of `get_sample` → `errDegraded` (BC-1.04.002 Inv 1; column corrected ADV-P13-C2-02) |
| 5 | row-2 render (width rule) | pure | CP-N01/N02/N03; OD-160 cached-path render degrades borne by the row-2 widgets — freshness ladder (BC-1.04.004 Inv 3), sparkline cached-hist shapes (BC-1.04.009 EC-011, BC-1.04.014 EC-008..010), mine format (BC-1.04.018 PC-1) — each → `errDegraded` (column corrected ADV-P13-C2-02) |
| 6 | window start (may write `proc_start`) | `Proc`, `Cache` | no catalogued vector; foreign-cache CP-C01 only (non-dict cache consulted outside its try) (OD-160) |
| 7a | lane badge/model/project; git segment (git-cache write) | `Files`, `Cache`, `Cwd` | CP-S01..S04; foreign-cache CP-C08 (BC-1.02.005 EC-009/EC-010) (OD-160) |
| 7b | thermometer/composition/cache-hit/limits/lines/timer/⌂/tokens | pure | CP-S05..S13; stdin/metrics-borne OD-156 overflow CP-O01..O05 (E-REN-002) — column widened pass-12 B06 to match BC-1.01.009 step 7b and BC-1.01.001's guarded-site list |
| 7c | record_cost (write), then cost_thresholds | `Cache` (load/save in `statusline`) + `internal/cost` (pure; declared API below, ADV-P13-A02) | CP-S15; unconvertible `usd`/`api_ms` is not recorded (OD-166) — Go skips the record where legacy persisted the raw int, the ruled write-divergence exclusion `OD-166`; history-borne CP-O10/O11 raise HERE in `cost_thresholds` (SL:255; site correction per pass-4 B14, propagated pass-5 A09), owner BC-1.05.005 EC-011 — the bearer (the cost-history cache persisted the value earlier) is unchanged; foreign-cache CP-C09/C10 (the CP-C family, OD-160) per BC-1.01.009's step-7c cell |
| 7d | $, $/h, ⛏ (pure) | pure | CP-O10/O11/O12 (E-REN-002) — O10/O11 disposition only: the history-borne raise sits in step 7c, so the SL:616/623 render sites are unreachable for history-borne values (pass-4 B14); CP-O12 (pass-9 call 4) raises HERE at render on the local lane (SL:633, owner BC-1.02.029, co-owner BC-1.05.003) |
| 8 | trim, surrogate check, single stdout write | stdout | CP-S17 after all writes |

Import-time crash paths CP-X01/X02 are replaced by D4-EX-3 at step 0; CP-X03 (the
degraded-line write failing) is the named exclusion `cp-x03` — Go swallows the write
error and exits 0 (OD-136; per OD-172 the same discipline extends to `--subagent` row
writes: a stdout write failure while printing rows stops writing and exits 0, with no
degraded-line attempt); CP-X04 (signals) is out of scope.

**Typed crash-path register (normative dispositions live in the owning BCs).** The
script's Degrade? column names the CP families; each family id is DEFINED in
error-taxonomy.md's crash-path register — the per-id rows there carry (id, legacy site,
owner BC/EC) for every id, including the six crash paths whose owning ECs name them:
CP-S02, CP-S03, CP-S04, CP-S05, CP-S08 and CP-S10 (pass-11 orchestrator call 14,
ADV-P11-B01) — while the normative disposition per id lives in the owning BC. ARCH-03
cites that register as the definition site of record. The OD-160 foreign-cache crash
class is DEFINED in error-taxonomy.md's separate C register — referred to by the phrase
"the CP-C family (OD-160)", never as a closed id range (the register is extensible;
pass-13 orchestrator call 1), and the script's step cells above name every step whose
owning table cell bears a C-family id, mirroring BC-1.01.009's step table
(ADV-P13-C2-02). Families: CP-S01..S17 (row-1/interaction), CP-T01..T07 + CP-T09
(transcript machine — a family of EIGHT; CP-T08 is a RETIRED id, append-only
numbering; CP-T09 = the Windows MSVC localtime-domain OSError on a naive transcript
timestamp, owner call 8 pass-7 D06/B03), CP-N01..N03 (row-2 telemetry; pass-4 C2-12), **CP-O01..O12** (OD-156 numeric-overflow family:
CP-O01..O05 stdin/metrics-borne at render → E-REN-002, the 29-byte line, exit 0, earlier
writes kept; CP-O06..O08 transcript-borne → the offending line is skipped whole under the
extended D4-EX-2 discipline, no sticky state, and the in-flight turn is dropped
(OD-167); CP-O09 reachable in hylo — two 4,300-digit ints accumulate without meeting a
float and breach CPython's int-to-string limit at the save (ADV-P3-C09; not moot,
disposition per the owning BC); CP-O10/O11
cost-segment overflow — a huge exact int in `usd`/`api_ms` overflowing int→float
conversion in the `cost_thresholds` division at SL:255 (`usd / (api / 3.6e6)`;
OverflowError at \|n\| >= 2**1024−2**970 — an int-to-string reading is WRONG: an int
over ~4,300 digits cannot even load, and the int-to-string breach at the save is
CP-O09's site, not this one; pass-6 A06) (step 7c; the SL:616/623 render sites are unreachable for
history-borne values because `cost_thresholds` raises first — pass-4 B14 site
correction, propagated pass-5 A09), same E-REN-002 disposition, owner BC-1.05.005
EC-011, bearer the cost-history cache), and **CP-O12** cost-pick equivalence
overflow — `tin` and `tout` each below the int→float overflow bound but their
exact-int sum `tot` (SL:626) at or above it enters `tot * dgx_mtok` (SL:633) on the
local lane with a valid basis → OverflowError → the E-REN-002 degraded line
(Surface 1, render-time degrade, like CP-O04; pass-9 call 4; owner BC-1.02.029,
co-owner BC-1.05.003), and **CP-A01..A05** (subagent panel, BC-1.07.008: typed degrades to the 29-byte
line, exit 0; CP-A04/A05 = huge-int `tokenCount`/`startTime` OverflowError paths added
by the pass-3 ruling, owners BC-1.07.007/.008), and **CP-N03** (pass-4 C2-12: the
metrics-borne degrade — a numeric `__name__` key positioned ahead of every `vllm:` key
in the metrics dict's INSERTION order — dicts are not sorted; SL:717 is `any()` over
the dict, corrected pass-7 C2-12 — so `k.startswith` raises AttributeError; owner
BC-1.04.005 EC-007 / BC-1.04.004
(pass-5 A24 correction — the degrade sits in `serving_state`), E-REN-002 disposition).

## Interfaces (design doc §2.2, reused as the contract)

```go
package statusline

// Main runs one refresh and always returns 0. Wiring order (ADV-P4-A06; pass-5 A11):
// step 0 resolves config THROUGH the injected EnvVars seam (AD-10 amended — never a bare
// func(string) string); only then does Main construct, over the Load-resolved
// configuration: the CacheStore (resolved paths.cache_dir), the MetricsClient
// (backends[0].metrics_url + telemetry.timeout_s), and the ProcStarter
// (window_age.process_name + window_age.max_depth). Env.Cache/Metrics/Proc are empty
// before step 0 and filled by Main — the seams do not presuppose the dir/url/pid.
func Main(stdin io.Reader, stdout, stderr io.Writer, env *Env) int

// Render is the orchestrator behind Main (BC-1.01.009 order). On errDegraded the
// caller prints degradedLine; cache writes made before the error persist.
// Preconditions: env.Config != nil && env.Cache != nil, guaranteed by Main.
func Render(stdin []byte, env Env) ([]byte, error)

// Panel is the subagent entry point's body (BC-1.07.001..008), called by
// runStatuslineSubagent after that entry point resolves config itself (OD-168).
// Renders the NDJSON panel rows to stdout; the elapsed-clock widget reads Now
// (BC-1.07.007). Same degrade discipline as Main (typed CP-A01..A05 sites + the
// recover() backstop), and OD-172 row-write discipline: a stdout write failure
// while printing rows stops writing and exits 0.
func Panel(stdin io.Reader, stdout, stderr io.Writer, env *Env) int

const degradedLine = "\x1b[90mstatusline degraded\x1b[0m\n" // 29 bytes, BC-1.01.001
var errDegraded = errors.New("statusline degraded")

type Env struct {
    Now     func() float64        // Python time.time() value; read ONCE per render (IM-14); the panel reads it too (BC-1.07.007). Frozen clock (pass-5 D02/call 7): HYLO_TEST_NOW is parsed to a float64 exactly as Python float() (within the BC grammar) and THAT float IS the time.time() value everywhere — never round-tripped through time.Time nanoseconds (float64 spacing at 1.79e18 ns exceeds the seconds-value ulp; cache bytes would drift); TimeFloat applies only to the real clock (ARCH-06 time.go)
    Loc     *time.Location        // naive transcript timestamps (BC-5.04.001); derived from platform.LocalZone — on its TZ-unset-path error, Main wires UTC and the render proceeds (step 0 above, ADV-P11-A08)
    EnvVar  EnvVars               // AD-10 seam (platform.EnvVars — declared in internal/platform, ARCH-05, single home ADV-P9-A12; Lookup + Names); backs the COLUMNS lookup (BC-1.01.005) and the unknown-HYLO_* sweep (BC-2.01.001 PC-6). The former bare Getenv func(string) string is superseded (ADV-P4-A06)
    Config  *config.Config        // filled by Main at step 0 (D15); Render precondition
    Cache   CacheStore            // constructed by Main after step 0 over the resolved dir (OD-101); a CacheDir error wires the load-empty / save-no-op store, never a config error (step 0 above, BC-3.01.001 EC-004); temp dir in tests
    Metrics MetricsClient         // constructed by Main after step 0 from backends[0].metrics_url + telemetry.timeout_s (pass-5 A11); raw-net.Listener fake in tests (VP-030 transport table; pass-7 C2-05)
    Proc    ProcStarter           // constructed by Main after step 0 from window_age.process_name + window_age.max_depth (pass-5 A11); fake in tests
    Files   FileSystem            // transcript and .git reads; os-backed by default
    Cwd     func() string         // git fallback when no project dir
    // NOTE (ADV-P9-A03): per-flavor absolute-path resolution lives in internal/platform
    // (platform.Abs(cwd, p string) (string, error), ARCH-05) — NOT as an Env seam here;
    // the git walk calls it directly (BC-1.02.004 PC-1), never inside pure pyfmt.
}

// EnvVars is platform.EnvVars (declared once in internal/platform, ARCH-05 —
// single home, ADV-P9-A12): Lookup(name) (string, bool) with ok=false => unset /
// ok=true + "" => set-but-empty, plus Names() []string; consumed here, never
// re-declared.

type CacheStore interface {
    // Depth budgets are PER FILE, not per interface (pass-5 A10): Load decodes and
    // Save encodes with the file's constant from the ARCH-06 depth law, in total
    // JSON nesting depth (the decode convention). Measured END-TO-END on real
    // legacy this burst (pass-5 sweep C: isolated temp HOME+cwd, never the real
    // HOME; python3 -I, CPython 3.11.7):
    //
    //     file          Load(decode)  Save(encode)   reachable from input?
    //     session       991           991            YES — Save re-encodes the stdin-borne rl
    //     mix           991           994            yes — cur.id/cur.out carry input nesting; save failure
    //                                                  unreachable: payload 994 saves / 995 fails, above the
    //                                                  993 transcript decode edge (pass-8 residual sweep)
    //     git           990           990            no — flat legacy-computed payload
    //     cost-history  990           990            no — flat legacy-computed payload
    //
    // One law, both directions (ARCH-06): the encoder boundary is 995 − s for
    // json.dump and 994 − s for json.dumps (s = Python frames at the invoke,
    // invoking frame inclusive), slope exactly 1 slot per frame — a DEEPER stack
    // never has the larger budget, and every cache's Save budget EQUALS its Load
    // budget, so Decode(Save(x)) never rejects what Save produced. MIX IS THE
    // MEASURED EXCEPTION (orchestrator call 1, pass-9, end-to-end): Save 994 >
    // Load 991 — the `_mix_counts` save boundary is the measured exception to the
    // 995 − s law itself (payload 994 saves / 995 fails) — so a saved mix cache
    // nested 992..994 deep is REJECTED on reload: Decode(Save(x)) CAN reject what
    // Save produced there. Measured consequence: a transcript line at decode depth
    // 993 with a deep message.id saves a mix cache of document depth 993; on the
    // next refresh the load fails, legacy treats the cache as absent, re-reads the
    // transcript from offset 0 and rewrites the cache — every refresh while that
    // line remains (file rewritten, no temp leak, exit 0); hylo
    // reproduces this. OWNER OF THE RE-READ LOOP: BC-1.03.021 (PC5/EC-004) —
    // ARCH-06 and BC-5.02.003 cite it by ID, never as owner themselves
    // (ADV-P10-A10/C07). The rewrite is constant-size ONLY while the transcript
    // fits in one read step (524,288 B): above that the re-read from 0 parses one
    // step, saves a shallow cache, then advances step by step until the deep line
    // is saved again, so `size` and totals CYCLE rather than staying constant
    // (ADV-P10-C08; BC-1.03.021 pins the measured loop).
    // Session, git and cost-history keep equality. The real
    // exposure is the stdin side: a rate_limits value nested 991..992 decodes
    // (stdin bound 993) yet breaches the session Save budget 991 — legacy skips
    // the write (SL:307-308), ruled in-band behavior (BC-5.02.006). Git and
    // cost-history Save constants are unreachable from input (flat payloads) but
    // are still named per-file constants (D15), pinned by the same law; the
    // owning-BC gen recipes re-measure and a moved boundary fails table
    // regeneration (measurement recipes: VP-006).
    Load(name string) pyfmt.Value    // never fails: unreadable => empty object
    Save(name string, v pyfmt.Value) error // reports the write outcome to the caller (ADV-P2-A25, VP-018); Render swallows it — DI-008 never-raise at the orchestrator
}
type MetricsClient interface {
    // MINIMAL HTTP/1.1 CLIENT OVER net.Conn (pass-6 C2-02/C2-05, call 4; TLS and
    // framing added pass-7 A11/C2-04/C2-05, orchestrator call 9; PARITY CASES ARE
    // PLAIN http ONLY — OD-181): Go's net/http trims header values
    // (textproto) and url.Parse rejects "%" without two hex digits, while urllib
    // keeps both — so net/http cannot reproduce urllib's targets byte-exactly.
    // The client sends exactly urllib's request headers (request line
    // `GET <selector> HTTP/1.1`, then `Accept-Encoding: identity`, `Host` — the
    // netloc AS WRITTEN, percent-unquoted, with a port only when the URL has one,
    // no default port appended (orchestrator call 10, pass-9) —
    // `User-Agent: Python-urllib/3.11`, `Connection: close` — Accept-Encoding
    // FIRST, the wire order BC-1.04.001 pins, verified against the CPython 3.11.7
    // source; ADV-P8-C2-12a) and parses status line and headers as http.client does (compat32:
    // a header value is value.lstrip(' \t') then rstrip('\r\n') — leading
    // spaces/tabs ARE stripped, inner bytes kept, trailing CR/LF stripped and a
    // trailing space KEPT; verified `Location: \t /x ` parses to `'/x '` —
    // pass-7 C2-02, orchestrator call 9).
    // INTERIM 1xx (orchestrator call 10, pass-9, orchestrator-verified in the
    // CPython 3.11.7 source): only status 100 is skipped (`if status !=
    // CONTINUE`, BC-1.04.001 EC-024); a 101/102/103 response is FINAL — legacy
    // gets NO sample. A client built to skip any 1xx samples obtains a sample
    // where legacy gets none after `103 Early Hints` and diverges (BC-1.04.001
    // EC-025 — the 101/102/103-is-final rows; corrected ADV-P10-C2-03, which
    // had cited EC-024, the header-limits and 100-Continue-skip row).
    // REDIRECT SANITIZATION ORDER (orchestrator call 10, pass-9,
    // orchestrator-verified): urlsplit's own sanitization runs BEFORE the scheme
    // guard and quoting — it strips all leading C0 controls and spaces, deletes
    // every \t \r \n, and lowercases the scheme (`/a<TAB>b` → target `/ab`;
    // `HTTP://` → scheme `http`, which urllib follows) — the guard tests the
    // SANITIZED scheme.
    // RESPONSE BODY FRAMING exactly as http.client (pass-7 C2-01, orchestrator
    // call 9): Transfer-Encoding: chunked de-chunked first, then Content-Length,
    // else read to EOF — the parsed body, never raw chunk-size lines, reaches
    // json.loads (legacy resp.read(), SL:171).
    // HTTPS (pass-7 A11/C2-04, orchestrator call 9): the SAME net.Conn wrapped
    // with crypto/tls — SNI from the URL host, ALPN pinned to http/1.1 only
    // (h2 negotiation would change the framing), certificates verified against
    // the OS trust store (system roots on Linux; macOS/Windows system stores).
    // There is no http.Transport and no proxy consultation. https URLs get a
    // sample when the store answers; PARITY CASES use plain http only (OD-181 —
    // the ruled closed-set exclusion "metrics transport beyond plain http" —
    // covers non-http(s) REDIRECT TARGETS and TLS trust-store differences ONLY
    // (orchestrator call 13, pass-8); a non-http(s) CONFIGURED metrics URL is
    // not OD-181 at all: it is the D4-EX-3 URL class, BC-2.02.005 /
    // BC-1.04.001 (ADV-P8-C2-12b)).
    // MANUAL REDIRECT LOOP: hylo drives the hops itself, so urllib's rules apply
    // exactly: follow `location` then `uri` headers; a present-but-EMPTY Location
    // resolves by urljoin(<URL of the request that received this 3xx>, "") — from
    // the second hop on that is the CURRENT hop's URL, not the first request's
    // (pass-6 C2-02, call 4; supersedes the "redirects to the original URL" rule).
    // An empty fragment is dropped by urlunsplit, so /x# and /x are one loop key.
    // A NON-empty fragment never reaches the wire beyond its LAST segment: urllib's
    // Request splits the URL with _splittag = rpartition('#') — ONLY the text after
    // the LAST '#' is dropped (orchestrator-measured on CPython 3.11.7:
    // Request('http://192.0.2.1:8428/a#b#c').selector is '/a#b';
    // quote(..., safe=string.punctuation) keeps '#'), then _splithost shapes the
    // selector — so a redirect Location '/a#b#c' yields the request line
    // 'GET /a#b HTTP/1.1' — the loop KEY keeps the full fragment text, the REQUEST
    // keeps everything before the last '#' (pass-7 C2-08, call 9; last-'#' selector
    // semantics pinned pass-12 call 13). THE SAME RULE decides the INITIAL selector
    // for a configured metrics URL that contains '#' (BC-2.02.005 admits exactly
    // one): selector = URL text up to the last '#', then _splithost — not a
    // first-# split (urlsplit / Go url.Parse give 'GET /a', a different hop key
    // and a different wire request).
    // After urlunparse, normalize quote(url, encoding="iso-8859-1",
    // safe=string.punctuation), then urljoin (verified in CPython 3.11.7 source).
    // Hop rules are urllib's visited-set/max_repeats/max_redirections limits — 37 is
    // the worst-case chain length, NOT a hop budget (pass-6 C2-03, call 4;
    // BC-1.04.001). The client only ever sees http/https URLs, and the two
    // non-http(s) classes must not be conflated (corrected ADV-P10-C2-04): a
    // CONFIGURED non-http(s) metrics URL never reaches the client — it is the
    // D4-EX-3 config-error line at LOAD, exit 0 (BC-2.02.005; dedicated test
    // `TestD4EX3_URL`), not a sample miss — while a non-http(s) REDIRECT target
    // is the OD-181 exclusion (BC-1.04.001; the HTTPS paragraph above), whose
    // scope is redirect targets and TLS trust only (orchestrator call 13,
    // pass-8; parity cases use plain http only).
    // UserInfo (pass-5 C2-03 ruling OD-180): a metrics URL with userinfo reproduces
    // legacy — NO sample (urllib puts u:p@host into HTTPConnection's host, DNS fails,
    // the dead rung); no exclusion id.
    // Total deadline; proxy-free by construction — a raw net.Conn dialed from the
    // URL host: no http.Transport and no *_proxy consultation (there is no
    // Transport to configure; the D14-(b) precedent in kind — wording updated
    // pass-7 A17). Raw bytes in, no transparent decompression (urllib
    // sends Accept-Encoding: identity and parses the body raw; an auto-gzip response
    // legacy never asked for would give Go a sample where legacy gets none, a
    // spurious VP-030 divergence — the net.Conn design has no auto-gzip by
    // construction, superseding the DisableCompression transport note).
    // TEST SEAM (pass-7 C2-05, orchestrator call 9): VP-030's transport table
    // drives a RAW net.Listener fake — not httptest, whose server canonicalises
    // headers into a map and trims values (textproto.TrimString), so it can
    // neither reproduce urllib's header order nor send `Location: /x `.
    // Reply decode: pyfmt.Decode(b, ModeBytes, depthMetricsReply = 992) (pass-6 A07,
    // call 5 — legacy fetch_sample calls json.loads(resp.read()) on bytes, SL:171,
    // so BOM/UTF-16/32 detection applies; BC-5.02.004).
    Query(ctx context.Context, promql string) ([]byte, error)
}
type ProcStarter interface {
    WindowStart() (start float64, ok bool) // whole seconds, as float64
}
type FileSystem interface {
    Stat(name string) (size int64, regular bool, err error)
    ReadFrom(name string, off int64, max int) ([]byte, error) // transcript window
    ReadFile(name string) ([]byte, error)                     // .git, HEAD — path-unrestricted by type: DI-007's ledger-read prevention is VP-022's static analysis, not the type system (ADV-P9-A13, ARCH-09 rule 3)
}

// ---------- package internal/cost — DECLARED API (ADV-P13-A02 remediation,
// orchestrator call 7) ----------
//
// PURITY BOUNDARY (normative): internal/cost does NO I/O of any kind — no files,
// no clock reads, no env, no network. It exposes PURE FUNCTIONS over values passed
// in (the loaded cost history, the current session's numbers, now) that return the
// new history and the thresholds; internal/statusline loads and saves the
// cost-history file through its CacheStore (budget row above: 990/990, the
// per-file depth constant lives with THAT cache file, not in this package).
// Step 7c therefore reads: load via CacheStore -> RecordCost -> Save via
// CacheStore -> (re)load via CacheStore -> CostThresholds, in legacy's exact
// side-effect order (BC-1.05.004 Description: the record runs before the
// percentile read; BC-1.05.005 Pre 2: the percentile scan loads with the
// BC-1.06.001 load).
//
// Anchor justification: these declarations are the home the cost BCs
// (BC-1.05.004/.005/.006/.009, all CRITICAL-gated) target; until this block no
// section declared cost's API (ADV-P13-A02).
package cost

// SessionCost carries the current session's numbers exactly as decoded
// (BC-1.05.004 PC-1): Sid is the RAW stdin session_id (NOT the nosession
// fallback; numeric sids per BC-1.05.006/OD-30), Lane is the client-view lane
// ("dgx" | "anth" | None), USD is total_cost_usd, APIMs is
// total_api_duration_ms. Ordered plain values, not cache structs (AD-08: no
// cache struct exists anywhere).
type SessionCost struct {
    Sid   pyfmt.Value
    Lane  pyfmt.Value
    USD   pyfmt.Value
    APIMs pyfmt.Value
}

// CostConfig spells the config inputs (D15 registry keys; BC-1.05.005 Pre 3 and
// BC-1.05.004 Pre 2 — every cost key the cost BCs list, none hard-coded):
// WindowS (statusline.cost.window_s), MinUSD (statusline.cost.min_usd),
// MinSessions (statusline.cost.min_sessions), RateMinAPIMs
// (statusline.cost.rate_min_api_ms, the cc/other map), Percentiles
// (statusline.cost.percentiles, the ascending pair), RecordThrottleS
// (statusline.cost.record_throttle_s, the record_cost throttle bound —
// BC-1.05.004 Pre 2/T-022; ADV-P14-A01: the throttle rule now gets its value
// through the declared API).
type CostConfig struct {
    WindowS        pyfmt.Value
    MinUSD         pyfmt.Value
    MinSessions    pyfmt.Value
    RateMinAPIMs   pyfmt.Value
    Percentiles    pyfmt.Value
    RecordThrottleS pyfmt.Value
}

// RecordCost appends this session's cc-tagged entry to the LOADED history and
// returns the NEW history plus whether the throttle appended it. Pure; the
// returned Value is byte-ready for pyfmt.Dumps (BC-1.05.009 exact write format).
// Dispositions:
//   - guard (falsy Sid, Lane not exactly "dgx"/"anth", non-numeric USD) ->
//     (history unchanged, false, nil) (BC-1.05.004 PC-1);
//   - throttle (stored entry src "cc" and now - ts < cfg.RecordThrottleS, the
//     statusline.cost.record_throttle_s config value — strict <; NO hard-coded
//     bound, ADV-P14-A01/ADV-P14-C2-03) -> (history unchanged, false, nil)
//     (BC-1.05.004 PC-3);
//   - OD-166 write-step convertibility skip (either numeric field unconvertible)
//     -> (history unchanged, false, nil) — the caller persists nothing (step 7c;
//     BC-1.05.004 PC-4);
//   - corrupt-history shapes (top level / sessions / an entry not an object;
//     entry ts non-numeric) -> err wrapping errDegraded: CP-C09, and CP-C10 at
//     the record_cost throttle-check site, where the raise precedes save_cache
//     and NOTHING is written (the CP-C family, OD-160; BC-1.05.004 owners).
func RecordCost(history pyfmt.Value, sess SessionCost, cfg CostConfig, now float64) (pyfmt.Value, bool, error)

// CostThresholds scans the LOADED history and returns the two percentile pairs,
// each (p75, p95) by floor-index selection or nil when fewer than
// cfg.MinSessions entries qualify (cold start), excluding the current session's
// own entries (self-exclusion by Sid, BC-1.05.005 Inv 3), entries outside
// cfg.WindowS (strict bound: an entry exactly 30 d old counts, BC-1.05.005
// PC-1) and usd < cfg.MinUSD. Pure function of (history, lane, sid, now,
// config) — BC-1.05.005 Inv 1. Each pair element is a pyfmt.Num carrying the
// RAW history value's exact kind — an exact int stays an exact int (hylo's own
// writer keeps ints as ints, BC-1.05.009 PC-3) — and comparison sites use
// pyfmt.NumCmp (BC-5.01.007: exact cross-kind comparison, never rounds the int
// to float64). float64 is a PARITY BUG here, not a style choice
// (ADV-P14-A02/C2-07): the dollar list holds the raw history usd, and a
// threshold int above 2**53 round-tripped through float64 flips the $
// colour — pinned example, orchestrator-measured on CPython 3.11.7:
// 9007199254740995 >= 9007199254740996.0 is False, while the float64-rounded
// comparison of the same operands is True. The usd / (api_ms / 3.6e6)
// exact-int division (SL:255) lives HERE; its int->float overflow legs
// CP-O10/O11 return err wrapping errDegraded and surface in step 7c (owner
// BC-1.05.005 EC-011); CP-C10's cost_thresholds site faults after the
// record_cost write (BC-1.01.009 step 7c).
func CostThresholds(history pyfmt.Value, sess SessionCost, cfg CostConfig, now float64) (usdPair, ratePair *[2]pyfmt.Num, err error)
```

A `recover()` backstop in `Main` maps any panic to `degradedLine` (mirrors
`except Exception`); typed CP-* sites return `errDegraded` wrappers with per-site catch
lists reproduced exactly (IM-15). One clock read per render; a live-clock minute-straddle
cannot occur (IM-14). File families: `guard.go`, `input.go`, `statusline.go`,
`width.go`, `theme.go`,
`lane.go`, `git.go`, `context.go`, `limits.go`, `session.go`, `tokens.go`, `cost.go`,
`transcript*.go`, `mixcache.go`, `telemetry.go`, `sample.go`, `row2.go`, `sparkline.go`,
`cache.go`, `subagent.go` — one home per S1 subsection (see BC-COMPONENT-MAP.md;
`subagent.go` hosts the OD-155 agent-panel contracts BC-1.07.001..008, dispatched per
ARCH-01; `statusline.go` hosts
the frame-level contracts BC-1.01.003/.009 and BC-1.04.013, ADV-P1-A20).

## Fragment anchors (pass-3 B10/C15; stable targets for BC-body fragment links)

BC bodies link fragments like `architecture/ARCH-03-statusline.md#lane`; the fourteen
anchors below are the complete, closed set — new BC fragment links must target one of
these (twelve plus the pass-12 additions `#input` and `#statusline-frame` for the
`input.go` and `statusline.go` file families, orchestrator call 17 — BC-1.01.002,
BC-1.01.008, BC-1.01.003 and BC-1.01.009 re-anchor to them). Practice note (pass-5
C2-14, call 19): BC bodies additionally link the
auto-generated heading slugs of this section (`#effect-step-script-…`,
`#interfaces-design-doc-22-…`); those resolve and are recognized targets. The ONLY
banned form is the bare line-number pointer (`ARCH-03:NNN`) — never an anchor, always
drifts; line-number pointers in BC bodies are replaced by fragment anchors on sight.

<a id="lane"></a>
<a id="git"></a>
<a id="context"></a>
<a id="limits"></a>
<a id="session"></a>
<a id="statusline-width"></a>
<a id="statusline-guard"></a>
<a id="input"></a>
<a id="statusline-frame"></a>
<a id="transcript"></a>
<a id="telemetry"></a>
<a id="cost"></a>
<a id="caches"></a>
<a id="subagent"></a>

| Anchor | Target |
|---|---|
| `#lane`, `#git`, `#context`, `#limits`, `#session`, `#statusline-width` | row-1 widget file families (`lane.go`, `git.go`, `context.go`, `limits.go`, `session.go`, `width.go`) in the Interfaces paragraph |
| `#transcript`, `#telemetry`, `#cost`, `#caches`, `#subagent` | `transcript*.go`/`mixcache.go`, `telemetry.go`/`row2.go`/`sample.go`, `cost.go` + `internal/cost`, `cache.go` (ARCH-04), `subagent.go` |
| `#statusline-guard` | the 29-byte degraded-line guard (`guard.go`, BC-1.01.001) |
| `#input` | the stdin-decode file family (`input.go` — stdin decode/guard contracts, BC-1.01.002, BC-1.01.008; pass-12 call 17) |
| `#statusline-frame` | the frame-level contracts (`statusline.go` — row rendering/LF join and side-effect order, BC-1.01.003, BC-1.01.009, BC-1.04.013; pass-12 call 17) |

## Mapping

BC-1.01..1.06 subsections -> the file families above (per-row homes in
BC-COMPONENT-MAP.md). Widgets + parser consume `internal/pyfmt` (ARCH-06); metrics
client is the only network edge; caches via ARCH-04.
