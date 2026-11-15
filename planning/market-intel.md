---
recommendation: GO
confidence: high
input_level: L3
assessed_at: 2026-11-15T23:20:36Z
assessor: business-analyst + research-agent
scope: P1 (hylo statusline) only
feature: Byte-parity Go port of the prototype's Claude Code status line (P1 of docs/PLAN.md §7)
caveat: Open-source personal/community tool with no revenue model. Market size is treated as
  adoption potential (GitHub stars as the proxy); no TAM/SAM/SOM figures are asserted.
inputs:
  - .factory/specs/research/domain-statusline-landscape-2026-11-15.md
  - .factory/specs/research/domain-hybrid-routing-claude-code-2026-11-14.md
  - .factory/specs/research/peer-tool-lessons-2026-11-14.md
  - docs/PLAN.md
  - docs/STATUSLINE-WIDGETS.md
  - .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md
input-hash: "c0a99b2"
---

# Market Intelligence Assessment — P1 `hylo statusline` (L3 risk check + competitive summary)

## Executive Summary

The Claude Code status line space is crowded and mature — five tools with 1.2k–28.9k stars
already ship the commodity widgets (cost, context %, git, model, 5h/7d windows) — but no
surveyed peer reports a backend telemetry strip, owned-hardware `⛏` cost, or per-lane
percentile-from-history cost colors, and the one existing lane-aware indicator
(model-relay + coralline) is a window-level pill without telemetry (statusline-landscape
§A.4, §A.3). P1 itself carries near-zero market risk: it is the lowest-risk phase of an
owner-approved plan, a port of a prototype in daily use, not a new market entry
(docs/PLAN.md §7; pass-8 synthesis §5 ranks it "lowest operational risk"). **Recommendation:
GO** — proceed to Phase 1 spec work, with the spec hardening the stdin contract against
additive churn and the README positioned on the uncontested differentiators rather than the
commodity widgets.

---

## Research Brief (Step 1 reconstruction)

- **Product/Feature:** `hylo statusline` — a byte-parity Go port (P1) of the prototype's
  two-row Claude Code status line: row 1 session/lane (lane pill, model, git, context
  thermometer, composition, cache hit, lines, timers, token classes, cost, plan limits);
  row 2 backend telemetry (health, queue, KV, throughput, sparkline, TTFT p95, power,
  idle), rendered from stdin JSON + transcript + a Prometheus-compatible metrics store
  (docs/STATUSLINE-WIDGETS.md).
- **Target Audience:** primarily the owner (the prototype is the daily driver); secondary,
  Claude Code users who run their own local inference hardware and want lane/backend visibility.
- **Problem Statement:** existing status lines show cloud-side cost and quota but not which
  lane served the session, whether the local backend is healthy, or what the session actually
  costs on owned hardware (statusline-landscape §A.3, §A.4).
- **Proposed Solution:** port the proven two-row design 1:1 under the parity decision D4,
  then differentiate after cutover (docs/PLAN.md §7, D4).
- **Known Competitors:** claude-hud, ccusage (`statusline`), ccstatusline, CCometixLine,
  claude-powerline; adjacent: model-relay + coralline (lane-aware pair) (statusline-landscape §A.1).
- **Known Constraints:** parity first (D4); public repo hygiene (D2); no "Claude" in names
  (trademark rule); config-over-code (D15); `subagentStatusLine` removed in Claude Code
  2.1.323; ledger/metric names frozen (D7).
- **Input Level:** L3 (plan and architecture exist; risk check + competitive summary depth).

---

## 1. Competitive Landscape (SUMMARY — L3 depth)

Full per-tool survey lives in the research file; this is the headline view
(statusline-landscape §A.1–§A.3).

### Direct competitors (status line tools for Claude Code)

Five dominant tools, all shipping cost, context %, git, model, and 5h/7d plan windows; most
also show prompt-cache state:

| Cluster | Tools | Stars (verified 2026-11-15) | Relevance to P1 |
|---|---|---|---|
| Large incumbents | claude-hud; ccusage statusline; ccstatusline | 28.9k; 19.4k; 13.6k | Own the commodity widgets; weekly release cadence |
| Mid/small | CCometixLine; claude-powerline | 3.5k; 1.2k | Same widget set, powerline/preset styling |
| Long tail | ~14 smaller tools (Bash, Python, Rust, Go) | 4–646 each (mostly unverified) | Churn bed; feature conveyor for backlog ideas |
| Lane-aware pair | model-relay (router) + coralline (segment) | n/a | Closest peer to the lane pill; no telemetry |

### Adjacent competitors (routers with or without status lines)

claude-code-router (~38k stars) and LiteLLM (~63k) dominate routing but have no lane-aware
status line; every new hybrid router seen this week (claude-spillway, wend-router, leitum,
Toy Models Gate, llm-router, routecall) is a base-URL or hook tool that loses Remote Control
and has no status line (hybrid-routing §1.1; statusline-landscape §B).

### Emerging threats

model-relay is the convergence threat to watch: it already writes a per-session status file
consumed by coralline's `relay` segment, and adding an HTTPS-proxy-mode ledger plus a
metrics strip would close most of the gap (statusline-landscape §C.2).

### Competitive Density Score

**SATURATED — for the commodity widgets.** Five maintained tools with 1k–29k stars, fast
release cadence (ccusage shipped 2026-11-14), and a dozen-plus followers make the
context/cost/git/limits row a commodity; competing on it is pointless
(statusline-landscape §C.2). Within that, however, the specific differentiator cluster —
backend telemetry from a metrics store, owned-hardware cost, percentile-from-history cost
colors — had **no observed occupant** in any surveyed tool (§A.4).

## 2–3. Market Size and Pain — adoption proxy (abbreviated per L3 scope)

- **Market size: not applicable / adoption proxy.** No revenue model (Apache-2.0, D8);
  TAM dollars would be fabricated. The honest proxy is demonstrated demand in the peer
  space: 28.9k + 19.4k + 13.6k stars across the top three status line tools indicates a
  large Claude Code user base actively installing status lines (statusline-landscape §A.1).
- **Pain confirmed: YES (for the differentiated subset).** Demand for status lines broadly:
  incumbent star counts. Demand for the specific missing data — lane, backend health,
  owned-hardware economics — is evidenced by the owner's own daily-driver usage of the
  prototype (9,927 requests analyzed 2026-11-10/13; the tool runs in production windows
  daily; STATUSLINE-WIDGETS "How it runs", lane-pill footnote), which is the only direct
  user signal available for a personal tool. Community peers solving neighboring problems
  (provider detection, quota bars) corroborate appetite for backend visibility, but no
  peer evidence exists for telemetry-strip demand specifically — that remains the owner's
  conviction backed by personal use (statusline-landscape §A.3–A.4, flagged as inference).
- **Pain severity:** inconvenience-to-blocker for the owner's workflow (GPU-box blindness
  during coding), convenience for the wider community.

## 4. Differentiation Opportunities (brief — drives README positioning)

Grounded in statusline-landscape §A.4 ("none" = not found in the READMEs/docs checked):

1. **Backend telemetry strip (row 2) — unique.** Health dot incl. vLLM/LMCache-down
   distinction, queue/preemption, KV gauge + host-tier reuse share, `»mine` vs `▣box`
   throughput, sparkline, TTFT p95 with sample-size dimming, power/temperature/¢/h, idle.
   No surveyed tool reads a Prometheus-compatible store or shows vLLM/LMCache/GPU state.
2. **Owned-hardware `⛏` cost and per-lane p75/p95-from-history cost colors — unique.**
   Peers use fixed dollar thresholds (e.g. $1/$5) or burn-rate visuals; none computes
   personal percentiles from 30-day history, per lane.
3. **Composition `▤❙◈` by bytes and `⌂` window age — unique.** Partly unique: `↻` rebuild
   counter (native `miss_causes` data now exists, a post-cutover alternative).
4. **NOT differentiators — do not claim them:** the lane pill (model-relay + coralline is a
   real window-level lane peer), pace-projected plan-limit coloring (claude-powerline,
   CCometixLine, ccstatusline all ship it), and "single static Go binary" (claudeline and
   felipeelias/claude-statusline are Go; Go is unique only combined with the proxy and
   exporter). Saying "first lane-aware status line" would be inaccurate.

**Positioning consequence for the README:** differentiate as "the status line that knows
your own hardware — lane, backend health, and owned-hardware cost", never "first/only",
and credit model-relay + coralline in an Alternatives list (statusline-landscape §Implications 6).

## 5. Risk Signals (FULL)

| Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|
| **R1. statusLine stdin contract churn breaks byte-parity output without any code change.** Additive field arrival is the norm (2.1.80 → 2.1.295) and historic breakage of status line *data* exists (`current_usage` zeros, 2.1.8–2.1.14) (statusline-landscape §C.1). | MED | HIGH | Defensive parsing (every object optional) as a spec'd contract; golden stdin corpus per tested Claude Code version, including absent/null objects and the newer optional fields; record the stdin `version` for diagnosis (owner question 2); per-release changelog review (`area:statusline`) as a P5 checklist item (statusline-landscape §C.1). |
| **R2. Commodity-widget saturation erases discoverability.** Row 1 basics are indistinguishable from five entrenched peers with weekly cadence; a parity-faithful port competes on none of them (statusline-landscape §C.2). | MED | HIGH | README leads with the §A.4 differentiator cluster; honest Alternatives section; adopt peer-inspired backlog items (warm-cache countdown, config-driven model aliases) only after cutover (§A.5). |
| **R3. Byte-semantics parity friction is the dominant delivery risk.** 137 of 232 BCs are byte-exact and depend on Python behavior Go lacks (banker's rounding, `json.dumps` separators/`ensure_ascii`, code-point lengths, NaN ordering, arm64 FMA; 22 pitfalls); the status line is the largest byte-exact surface (103 BCs) (pass-8 §1 finding 1, §5 rank 2). | MED | HIGH (known gaps, documented) | Helper packages (`pyfmt`, `pyjson`, `pystr`, `pytime`) with CPython-generated tables before any widget code; row/cost-color/trim goldens; table tests per fixed review rule (pass-8 §8.2). |
| **R4. Competitive convergence from model-relay.** Already pairs a router with a status segment; a proxy-mode ledger + metrics strip there would be the closest overlap (statusline-landscape §C.2). | MED | LOW–MED | Watch model-relay releases; the differentiators rest on infrastructure peers lack (proxy ledger, metrics store with vLLM/LMCache/DCGM series, owned-hardware cost rules) — replication needs the backend, not just a widget. |
| **R5. Removal/mods precedent on the status line surface.** `subagentStatusLine` went documented → inert in one release (2.1.323) with no warning, and mods gained status-line render sites (2.1.287+); a `statusLine` removal is not signaled but is conceivable (statusline-landscape §C.1). | MED | LOW | Stay on `statusLine` for P1 (documented, first-class `/statusline`, still gaining fields); do not port `--subagent`; add "mods status line" as a P7 watch item; never exit nonzero (blank-line degradation preserves UX on contract changes). |
| **R6. Cost-basis skew under managed `modelPricing`.** For managed-pricing users, `cost.total_cost_usd` reflects contracted rates, which would mix bases in the 30-day p75/p95 history (statusline-landscape §B stdin facts). | LOW | LOW–MED | Doc-only treatment: note the caveat in the D15 cost rationale; no behavior change pre-cutover (D4); cannot be set by hylo's launcher either way (managed scope only). |
| **R7. Trademark/policy exposure — low for P1.** hylo's status line reads only stdin, transcript, caches and its own metrics store; several popular peers instead read the Claude.ai OAuth token from the keychain to call `/api/oauth/usage`, sitting closer to the "intermediate … session tokens" clause; hylo's naming is already the conservative pattern (statusline-landscape §C.3; hybrid-routing §4.1). | LOW | LOW | Keep current naming/disclaimer pattern; keep glyphs/colors original; do not adopt OAuth-usage-API widgets (reject A.5 idea 8); the heavier policy questions belong to P3, not P1. |

## 6. Implications for Spec Work (concrete P1 spec inputs)

The recommendation is GO, so: the spec should emphasize contract hardening and honest
positioning, and must NOT change the parity target (D4) or reopen settled decisions D1–D16.
Concrete inputs:

1. **Golden stdin corpus must include the newer optional fields.** Fixtures carrying
   `output_style.name`, `pr.kind`, `workspace.repo.{host,owner,name}`,
   `prompt_cache.last_miss_cause`/`miss_causes`, and `rate_limits.spend_limit` (with and
   without the dollar fields) prove additive fields do not perturb byte-parity output.
   All synthetic — public-repo hygiene (statusline-landscape §Implications 2; §B stdin facts).
2. **Keep `--subagent` out of P1.** Confirm removal (2.1.323 changelog quoted in
   statusline-landscape §B; consistent with PLAN §3's non-goal). Do not copy
   CCometixLine's still-documented-but-inert `subagentStatusLine` example (§A.1, §Implications 3).
3. **README positioning as a spec deliverable:** "lane-aware with backend telemetry and
   owned-hardware cost", not "first/only"; Alternatives section crediting model-relay +
   coralline (§Implications 6; §A.4 positioning line).
4. **Doc-wording obligations (no behavior change):** ⏱ gains "accumulates across resumes;
   excludes time the session isn't running" at its next edit; the `$` widget rationale
   (D15) notes list-price-unless-managed-`modelPricing`; cost-history percentile doc notes
   the mixed-basis possibility (§Implications 4–5, §B).
5. **Degradation contract as a spec'd BC:** every code path exits 0 with output — never
   nonzero, never a blank line from an internal error — matching the observed
   "shown only on exit 0" rule (statusline-landscape §C.1 mitigations; STATUSLINE-WIDGETS "How it runs").
6. **Watch list into the spec's risk register:** model-relay releases (R4), Claude Code
   mods status-line render sites (R5), issue #109446 (any `subagentStatusLine` successor),
   and the `7d_oi` = Fable-only claim, verifiable locally only (§Implications 8, §C.1).
7. **Unchanged:** parity target, phase scope, D1–D16, the ledger, and the fixture-scrubbing
   regime. Nothing in the 2026-11-15 freshness delta invalidates a legacy behavior
   (statusline-landscape §Implications 1).

### Assumptions Made

- **Adoption potential is proxied by GitHub stars;** no usage analytics exist for any peer
  or for hylo. Stars are a lagging, popularity-skewed proxy (flagged throughout).
- **Long-tail star counts and versions are single-pass survey data,** not re-verified on
  repo pages; coralline and two Go peers have no verified star figure
  (statusline-landscape §A.2, §Inconclusive).
- **"None found" uniqueness claims are absence-of-evidence** over the READMEs/docs checked
  on 2026-11-15 — not proof that no peer has the feature (§A.4 framing).
- **The `7d_oi` Fable-only allowance rests on one community source** (claude-spillway
  README); treat as unverified until checked against local `anth_ratelimit` captures (§B).
- **Community adoption is a secondary goal** after the owner's own use; if the owner's goal
  weighting differs, the R2 discoverability risk changes weight accordingly (goal assumption — owner to confirm).
- **Managed `modelPricing` is rare among plausible community users** (it is managed-scope
  only), so R6 is minor; no frequency data was found either way (§B).

## Questions for owner review

1. **README positioning.** Adopt "lane-aware with backend telemetry and owned-hardware
   cost" as the lead claim, and name model-relay + coralline (plus the incumbents) in an
   honest Alternatives section — comfortable naming peers, including the one real
   lane-aware predecessor?
2. **Record stdin `version` in the session cache** for per-release diagnosis (the research's
   C.1 mitigation 2)? It is a behavior/format change over `legacy/`, so under D4 parity-first
   it must either land as an additive key excluded from the parity diff, or wait until after
   parity — approve the former, or defer it?
3. **`7d_oi` = Fable-only:** worth a local check against `anth_ratelimit` ledger captures the
   next time a Fable request occurs (local verification only), or leave the watch-item note as is?
4. **Goal weighting:** is community adoption a real objective for P1 (which elevates R2 and
   the README work), or is the owner's own daily use the success criterion for this phase?

---

*Assessment prepared by business-analyst + research-agent, 2026-11-15. Source of record for
all factual claims: the four research files listed in the frontmatter, cited by section above;
assessment depth L3 (risk check + competitive summary) per the market-intelligence-assessment
skill. The final GO/CAUTION/STOP call rests with the owner (Step 4 review gate).*
