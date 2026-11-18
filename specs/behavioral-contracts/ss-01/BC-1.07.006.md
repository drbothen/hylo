---
document_type: behavioral-contract
level: L3
version: "1.1.8"
status: draft
producer: product-owner
timestamp: 2026-11-18T08:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md]
input-hash: "8e07087"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_subagent_rows model branch (SL:898-907)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.1.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-010 byte rows (property leg rides VP-028)", "1.1.2 2026-11-18T05:30:00Z: VP-028 v1.1 extends its startswith prefix rule to this contract (adv-p2 sync SC-07); VP row/anchor wording synced", "1.1.3 2026-11-18T07:00:00Z: adv-p3 remediation: goldens re-derived ensure_ascii-escaped (ADV-P3-C01); str() rendering of truthy non-string models specified (ADV-P3-C14); pill bytes sourced from the shared theme/glyph config keys (ADV-P3-C05)", "1.1.4 2026-11-18T08:00:00Z: pass-4 remediation: pill SGR re-anchored to statusline.theme.cyan/magenta, defaults 36/35 = legacy CYAN/MAGENTA SL:906-907, not pill_local/pill_cloud (ADV-P4-C02); strip convention named pyfmt.Strip per BC-1.02.001 PC4 (ADV-P4-C15); stale pill-gate cite corrected (ADV-P4-C12)", "1.1.5 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C03/C06) — lane-tag square pinned to statusline.glyphs.lane (U+25E8) and words to statusline.pill.label_local/label_cloud (OD-173); theme.grey named for the model bit; refactoring note uses pyfmt.Strip, never TrimSpace (OD-170)", "1.1.6 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C12) — frontmatter template conformance: priority P0 added (prd.md S1.07), introduced normalized to the sibling \"0.1\" format", "1.1.7 2026-11-19T21:00:00Z: pass-7 remediation (ADV-P7-C14) — the three prose pseudo-escapes replaced with the source glyph (U+25E8, source bytes e2 97 a8): Description lane-pill clause and EC-003; escaped golden wire forms kept as depict the wire, "1.1.8 2026-11-20T12:00:00Z: pass-8 residual sweep (task 9) — ASSUMP-107-1 capture timing respelled per OD-192: 'before Phase 3' -> 'before Phase 2 writes the S1.07 stories'; body wording only"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.07.006: Model segment carries the model-prefix lane tag

## Description

When a task carries a truthy `model`, the row gains a second bit: the optional lane pill (cyan `◨DGX`
`\e[36m` when `model` starts with any configured prefix, magenta `◨ANTH` `\e[35m` otherwise — only when
the configured prefix list yields at least one non-empty entry) followed by the model id in grey `\e[90m`.
The same prefix rule as the main lane pill (BC-1.02.001) so a Haiku subagent inside a DGX session shows
it is served by Anthropic (review 2026-11-13 #21.4).

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 2 writes the S1.07 stories (OD-192).
2. `prefixes` = the configured prefix list `backends[0].model_prefixes` (OD-111, OD-123, BC-2.01.002;
   legacy provenance: env `LOCAL_MODEL_PREFIXES`, SL:898-907), read through internal/config — hylo never
   reads the legacy env name (OD-05; the parity harness translates legacy env to `HYLO_*` per case,
   ASM-003). Comma-separated; each entry stripped of Python Unicode whitespace (NBSP included;
   `pyfmt.Strip`, BC-5.03.002 — the BC-1.02.001 PC4 convention); empty entries dropped; order kept.

## Postconditions

1. `model` falsy or missing → no segment at all (no pill, no grey model).
2. Truthy `model` that is a string → `<lane><GREY><model><RESET>`; the GREY model bit is the shared theme colour key `statusline.theme.grey` (default `90`, OD-113); the pill bytes are
   `\e[36m` + U+25E8 + `DGX\e[0m ` (prefix hit) or `\e[35m` + U+25E8 + `ANTH\e[0m ` (miss), each
   followed by `\e[90m<model>\e[0m`.
   A truthy non-string `model` with empty prefixes renders through Python f-string `str()`
   coercion (`pyfmt.Str`): `True`, `1.0`, `['x']`, `{'a': 1}` display as exactly those literals
   (verified). With prefixes configured, any non-str truthy `model` is the CP-A03 degrade (EC-002).
3. Prefix hit test: case-sensitive `strings.HasPrefix` against any entry (same semantics as
   BC-1.02.001's startswith rule).
4. `prefixes` empty (explicit empty value; parity cases set it explicitly, OD-111) → lane pill omitted;
   grey model bit still appended.

## Invariants

1. The pill is omitted entirely (not neutral-grey) when no prefixes are configured — an unknown lane
   must not be asserted (mirrors BC-1.02.001's unknown-pill rule from the other direction).
2. Exactly one of {local pill (U+25E8 + `DGX`), cloud pill (U+25E8 + `ANTH`)} when prefixes exist;
   case-sensitive startswith; first matching entry wins (outcome identical either way).
3. The segment appears after the opening glyph bit and before token/clock/status bits.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `model` missing / `""` / `0` / `False` | No segment |
| EC-002 | `model = 123` with prefixes configured | AttributeError site in legacy — degraded line (CP-A03, BC-1.07.008); in Go the Num coercion must NOT occur: route non-str truthy models to the degraded predicate |
| EC-003 | `model = 123`, prefixes empty | Grey segment `123` via `str()` coercion (same rendering for `True`, `1.0`, `['x']`, `{'a': 1}`), no crash, no pill |
| EC-004 | Prefixes with spaces (`" claude-sonnet , foo "`) | Entries trimmed of Python Unicode whitespace (`pyfmt.Strip`, NBSP included); whitespace-only entries dropped |
| EC-005 | Model `Claude-Sonnet-5-5` vs prefix `claude-sonnet` (case mismatch) | No hit → ◨ANTH (case-sensitive) |

## Canonical Test Vectors

| Input (task dict + config) | Expected Output (content bits) | Category |
|---|---|---|
| `{"id":"a1","name":"explore","status":"running","model":"claude-sonnet-5-5","tokenCount":12345,"startTime":<now-125000>}`, `model_prefixes = [claude-sonnet]` | `{"id": "a1", "content": "\u001b[33m\u00bb explore\u001b[0m \u00b7 \u001b[36m\u25e8DGX\u001b[0m \u001b[90mclaude-sonnet-5-5\u001b[0m \u00b7 \u001b[36m12.3k tok\u001b[0m \u00b7 \u001b[90m02:05\u001b[0m"}` | happy-path |
| `{"id":"a2","label":"explor\u00e9","status":"completed","model":"claude-haiku-5","tokenCount":2500000}`, same config | `{"id": "a2", "content": "\u001b[32m\u2714 explor\u00e9\u001b[0m \u00b7 \u001b[35m\u25e8ANTH\u001b[0m \u001b[90mclaude-haiku-5\u001b[0m \u00b7 \u001b[36m2.50M tok\u001b[0m \u00b7 \u001b[90mcompleted\u001b[0m"}` | happy-path |
| `{"id":"a7","status":"running","model":123}`, `model_prefixes = []` | `{"id": "a7", "content": "\u001b[33m\u00bb ?\u001b[0m \u00b7 \u001b[90m123\u001b[0m"}` (no pill, no crash) | edge-case |
| `{"id":"a7b","status":"running","model":"gpt-9"}`, `model_prefixes = [claude-sonnet]` | `{"id": "a7b", "content": "\u001b[33m\u00bb ?\u001b[0m \u00b7 \u001b[35m\u25e8ANTH\u001b[0m \u001b[90mgpt-9\u001b[0m"}` | edge-case |
| any truthy str model, `model_prefixes = []` (parity cases set it explicitly) | `\e[90m<model>\e[0m` with no pill | happy-path |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`): rows 1, 2, 3, 4 byte-reproduced; goldens
re-derived escaped after the adv-p3 C01 escape-decoding incident; pill square = U+25E8
(source UTF-8 e2 97 a8); pill wire forms `\u001b[36m\u25e8DGX\u001b[0m ` /
`\u001b[35m\u25e8ANTH\u001b[0m ` confirmed (see the escaped vectors).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-010 | Python-written goldens pin the lane-pill byte rows on committed cases; the startswith property leg is pinned by VP-028 (rule extended to this contract, VP-028 v1.1) | Tier B golden comparison (Python oracle writes; Go matches) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (CP-A03 degrade), DI-012 (byte parity) |
| Architecture Module | `internal/statusline` (model segment; shares the prefix table with the row-1 lane pill) |
| Config keys | `backends[0].model_prefixes`; pill SGR from the shared theme colour keys `statusline.theme.cyan` (default `36`, hit) and `statusline.theme.magenta` (default `35`, miss) — defaults equal to legacy CYAN/MAGENTA (SL:906-907) — and the pill square from `statusline.glyphs.lane` (U+25E8, 1 code point/1 column; the pass-5 call-1 registry completion member, shared with the row-1 lane pill — BC-2.01.004 owns the closed registry). The tag words DGX/ANTH are NOT constants: they come from the OD-173 keys `statusline.pill.label_local`/`label_cloud` (defaults `DGX`/`ANTH`; BC-1.02.001 is the row-1 consumer) — hard-coding them would violate D15/OD-173 (ADV-P5-C03). NOT the row-1 inverted pills `statusline.theme.pill_local`/`pill_cloud` (defaults `106;30;1`/`105;30;1`): building from those anchors breaks byte parity (ADV-P4-C02) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py: model branch (SL:898-907); pill bytes SL:127-133 |
| Legacy contract | BC-SL-097 (P3r2 §A7; prefix rule shared with BC-SL-006) |
| Decisions | OD-155, D4 (byte parity); review 2026-11-13 #21.4 (lane tag rationale) |

## Related BCs (Recommended)

- BC-1.02.001 — related to (same startswith prefix rule, row-1 pill)
- BC-1.07.004 — composes with (framing)
- BC-1.07.008 — related to (CP-A03 non-str model + prefixes → degraded line)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — segment builder; prefix table read once per render

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-010 (lane-pill byte rows; startswith property leg pinned by VP-028 v1.1)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:898-907) |
| **Confidence** | high (pinned runs 2026-11-18) |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **assertion**: pinned runs for hit/miss/no-prefix/empty cases
- **guard clause**: `if model:` truthy gate (SL:899); `if prefixes:` pill gate (SL:905); pill bytes (SL:906-907)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | legacy reads `os.environ["LOCAL_MODEL_PREFIXES"]`; hylo receives `backends[0].model_prefixes` from internal/config (OD-05) |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use |
| **Overall classification** | pure function of (task, prefixes) |

#### Refactoring Notes

Go: take `backends[0].model_prefixes` from internal/config (OD-123), parse (split on `,`, strip each
entry with `pyfmt.Strip` — Python Unicode whitespace, NBSP included; **never** `strings.TrimSpace`:
Go's `unicode.IsSpace` leaves U+001C..U+001F which Python's `str.strip()` removes, so a prefix with a
leading U+001F would match differently from legacy — OD-170; ADV-P5-C06; PC2/EC-004 convention),
drop empties) once per render, then
`slices.ContainsFunc(prefixes, func(p string) bool { return strings.HasPrefix(model, p) })`. Take the
tag words from `statusline.pill.label_local`/`label_cloud` (OD-173), the
pill SGR from `statusline.theme.cyan`/`statusline.theme.magenta` (defaults 36/35 = legacy CYAN/MAGENTA,
SL:906-907), and the square glyph from `statusline.glyphs.lane` (ADV-P3-C05 disposition, corrected by
ADV-P4-C02: not `statusline.theme.pill_local`/`pill_cloud`, whose inverted-pill defaults
`106;30;1`/`105;30;1` differ), not from constants, so byte parity stays auditable next to
PILL_DGX/PILL_ANTH defaults.
