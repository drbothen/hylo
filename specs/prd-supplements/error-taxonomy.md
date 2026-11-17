---
document_type: prd-supplement-error-taxonomy
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T23:45:00Z
phase: 1a
stage: "3 of 3 (integration)"
inputs: [prd.md]
input-hash: "5c53471"
traces_to: prd.md
---

# Error Taxonomy: hylo P1 statusline

> PRD supplement — extracted from PRD Section 5.
> Referenced by: implementer, test-writer.
> Principle (DI-008): the user-visible render never fails and never exits non-zero.
> Errors are observable as (a) the degraded ladder or (b) one-line grey notices; non-zero
> exits exist only in validate/usage contexts and inside the parity harness.

## Error Categories

| Category Code | Category | Description |
|--------------|----------|-------------|
| REN | Rendering degrade | guard recovery or typed crash-path degrade; the 29-byte line |
| CFG | Configuration | D4-EX-3 invalid `HYLO_*` values (six classes) |
| CLI | Command-line | unknown flags, usage errors |
| VAL | Validation | `config validate` reporting |
| NET | Metrics transport | metrics store unreachable/500/garbage |
| FS  | Filesystem | cache load/save faults, failed replaces |
| HAR | Harness integrity | canary, exclusion machinery, corpus hygiene (harness process only) |

## Error Catalog

| Error Code | Category | Severity | Exit Code | Observable / Message Format |
|-----------|----------|----------|-----------|----------------------------|
| E-REN-001 | REN | broken | 0 | `\e[90mstatusline degraded\e[0m\n` (29 bytes) — BC-1.01.001. Failure of the degraded-line write itself (legacy CP-X03, stdout closed) is the named exclusion `cp-x03` (OD-136): Go swallows the write error and still exits 0, per DI-008 |
| E-REN-002 | REN | broken | 0 | same line, via typed CP-* degrades (overflow/NaN/type confusion) — BC-1.02.026/.027, BC-1.02.020, BC-1.04.014/.015, BC-1.03.015 |
| E-CFG-001 | CFG | degraded | 0 | `\e[90mhylo: config error: <key>=<value> (<reason>)\e[0m\n`; stderr detail `[from <ENVNAME>]` — BC-2.02.001 |
| E-CLI-001 | CLI | degraded | 0 | `\e[90mhylo: unknown flag <flag>\e[0m\n` — BC-4.01.002 |
| E-CLI-002 | CLI | broken | 2 | golden usage text on stderr — BC-4.01.001 |
| E-VAL-001 | VAL | broken | 1 | plain reason lines (no SGR), one per error — BC-2.03.001 |
| E-NET-001 | NET | degraded | 0 | freshness ladder down to the stale suffix — BC-1.04.001/.004 |
| E-FS-001 | FS | degraded | 0 | never-raise caches; failed replace persists nothing — BC-1.06.001/.002 |
| E-HAR-001 | HAR | broken | non-zero | harness FAIL naming the reason (canary, missing table test, glob, id outside closed set) — BC-6.01.003, BC-6.03.004 |

## D4-EX-3 config-error line (E-CFG-001) in detail

Format (BC-2.02.001, OD-102): `\e[90m` + `hylo: config error: ` + `<key>` + `=` +
`<value>` + ` (` + `<reason>` + `)` + `\e[0m` + `\n`. Exactly one line on stdout — the
first error in stable registry order; the full list goes to stderr; a config-error run
writes no caches. `<key>` is the dotted config name (not the env var); `<value>` is
escaped with control bytes and invalid UTF-8 as `\xNN`.

Classes and owner rulings: number-range (BC-2.02.002; OD-114 keeps TTL 0 valid, contra
IM-16), number-grammar (BC-2.02.003), enum (BC-2.02.004), URL (BC-2.02.005), boolean
(BC-2.02.006; OD-140 — dedicated class contract; grammar pinned in BC-2.01.005), theme/SGR
(BC-2.01.003 — reason string `not an SGR parameter list`, named class per OD-134, resolving
PRD OQ-6). The class register is closed at six (OD-114 four + OD-134 + OD-140); a seventh
class needs an owner decision. Unknown-flag precedence: E-CLI-001 is checked before
E-CFG-001.

## Reason Vocabulary (exact strings, BC-2.02.001)

| Reason | Class | Raised by |
|--------|-------|-----------|
| `underscore in numeral` | number-grammar | BC-2.02.003 |
| `non-ASCII digit` | number-grammar | BC-2.02.003 |
| `not a number` / `not an integer` | number-grammar | BC-2.02.003 |
| `not finite` / `negative` / `must be > 0` / `out of range` | number-range | BC-2.02.002/.003 |
| `not a boolean (true\|false\|1\|0\|yes\|no)` | boolean | BC-2.01.005 |
| `unknown value (<v1>\|<v2>\|...)` | enum | BC-2.02.004 |
| `scheme must be http or https` / `not a URL` / `missing host` | URL | BC-2.02.005 |
| `control character` | URL (BC-2.02.005) / theme (BC-2.01.003) | BC-2.02.005, BC-2.01.003 |
| `not an SGR parameter list` | theme | BC-2.01.003 |
| `empty path` / `home directory unknown` | path (BC-2.01.005 grammar; no dedicated class contract) | BC-2.01.005 |
| `exactly one backend entry until P6` | backends (BC-2.01.002 cardinality rule; no dedicated class contract) | BC-2.01.002 |

Reconciliation with the closed register: the six closed classes (OD-114 four + OD-134 +
OD-140) are the classes with dedicated class contracts and D4-EX-3 table tests. The
vocabulary above also contains reasons raised under the same E-CFG-001 surface by other
contracts: the path-grammar reasons (`empty path`, `home directory unknown`) come from
BC-2.01.005 and the backends-cardinality reason from BC-2.01.002 — each maps to its raising
contract, not to a seventh class; `control character` maps to the URL class when raised by
BC-2.02.005 and to the theme class when raised by BC-2.01.003. The class register stays
closed at six.

## Severity Definitions

| Severity | Meaning | Exit Code Impact |
|----------|---------|-----------------|
| broken | Cannot render the requested output | zero exit with the degraded line (statusline), or non-zero in validate/usage/harness contexts |
| degraded | Partial result with stated fallback | zero exit |
| cosmetic | stderr-only detail | zero exit (stderr is never compared by the harness) |

## Crash-path register coverage

Every CP-S/CP-T/CP-N trigger resolves to E-REN-001 or E-REN-002 or a stated widget
fallback; the per-trigger disposition lives in the owning BC (CP-S01..S17 in BC-1.02.x /
BC-1.01.x, CP-T01..T07 in BC-1.03.x, CP-N01/N02 in BC-1.04.x). The import/exit-time triggers
CP-X01/X02 are replaced by D4-EX-3 (BC-2.02.001) and CP-X03 is the named exclusion
`cp-x03` (BC-1.01.001 EC-005, OD-136); CP-X04 (signals) is out of scope. A trigger whose
disposition is neither of those is a spec gap and fails the consistency check.
