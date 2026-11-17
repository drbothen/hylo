---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "aac2048"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:441-449)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-006
parity_class: byte-exact
confidence: H
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

# Behavioral Contract BC-1.02.001: Lane pill derives from model-prefix startswith match

## Description

The first segment of row 1 is the lane pill: the client-view lane (OD-121) inferred from
stdin `model.id` and the configured backend model prefixes. A case-sensitive `startswith`
match against any prefix gives the local-lane pill; a non-matching id gives the cloud-lane
pill; a missing id or an empty prefix list gives the unknown pill. The pill never claims a
lane it cannot know.

Notation: `\e` is the byte 0x1B; every other character is its UTF-8 encoding.

## Preconditions

1. stdin has been decoded to an object `d` (BC-1.01.002).
2. `model = d.model` if truthy, else `{}`. A truthy non-object `model` is out of contract
   here (see EC-007).
3. `model_id = model.id` if truthy, else `""`.
4. `prefixes` = the configured prefix list `backends[0].model_prefixes` (OD-111, OD-123,
   BC-2.01.002; legacy provenance: env `LOCAL_MODEL_PREFIXES`, SL:444), split on `,`, each
   element stripped of Python Unicode whitespace (NBSP included; `pyfmt.Strip`,
   BC-5.03.002), empty elements dropped, order kept.

## Postconditions

1. `on_local` is computed exactly as:
   - `None` when `prefixes` is empty or `model_id == ""`;
   - otherwise `true` iff some `p` in `prefixes` satisfies `model_id` starts with `p`
     (code-point prefix, case-sensitive, no glob: `*` is a literal character).
2. The pill segment bytes are exactly one of:
   - `on_local == true` → `\e[106;30;1m ◨ DGX \e[0m`
   - `on_local == false` (and `model_id` non-empty) → `\e[105;30;1m ◨ ANTH \e[0m`
   - otherwise → `\e[100;37;1m ◨ ? \e[0m`
3. The pill is always element 0 of row 1 (joined to the next element by the separator,
   BC-1.01.003); it is never omitted.
4. The SGR codes come from the `statusline.theme.*` pill keys (OD-113, BC-2.01.003) and the
   `◨` glyph from `statusline.glyphs.*` (OD-02); with defaults they equal the legacy bytes
   above (SL:130). The words `DGX` / `ANTH` / `?` are legacy output bytes and stay
   unchanged until after cutover (D4, D7); the domain terms are local lane / cloud lane.

## Invariants

1. The pill depends only on `model_id` and `prefixes`; it never reflects the proxy's actual
   routing decision (a server-tool request served by the cloud lane still shows the
   local-lane pill if its id matches; DI-017 is the proxy's concern, not this widget's).
2. No id → never a lane claim (`?` pill).
3. Deterministic: same inputs, same bytes, on every OS.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Prefix list empty (explicit empty value; OD-111 parity cases set it explicitly) | `?` pill even for a `claude-sonnet-*` id |
| EC-002 | Prefix `claude*` with id `claude-sonnet-5-5` | no match (literal `*`) → ANTH pill (while BC-1.02.009 hides limits for the same prefix) |
| EC-003 | Prefix value `" claude-sonnet , claude-opus ,, "` | list `["claude-sonnet","claude-opus"]`; id `claude-opus-5` → DGX pill |
| EC-004 | Case mismatch `Claude-sonnet` vs id `claude-sonnet-5-5` | ANTH pill (case-sensitive) |
| EC-005 | `model` missing, null, `{}` or id `""` | `?` pill |
| EC-006 | `display_name` present, id missing | `?` pill (display name never decides the lane) |
| EC-007 | Truthy non-string id (e.g. `5`) with a non-empty prefix list, or truthy non-object `model` (e.g. `"x"`) | legacy raises AttributeError → whole run degrades to the guard line `\e[90mstatusline degraded\e[0m\n`, exit 0 (BC-1.01.001) |
| EC-008 | Truthy non-string id with an empty prefix list | no exception: `?` pill (the `startswith` call is never reached); the label renders per BC-1.02.021 |

## Canonical Test Vectors

All vectors verified against the oracle (`legacy/dgx_statusline.py`, CPython 3.11.7) on 2026-11-15.

| Input | Expected Output | Category |
|-------|----------------|----------|
| prefixes `claude-sonnet`; `{"model":{"id":"claude-sonnet-5-5"}}` | pill `\e[106;30;1m ◨ DGX \e[0m` | happy-path |
| prefixes `claude-sonnet`; `{"model":{"id":"claude-opus-5"}}` | pill `\e[105;30;1m ◨ ANTH \e[0m` | happy-path |
| prefixes `claude-sonnet`; `{}` | pill `\e[100;37;1m ◨ ? \e[0m` | edge-case |
| prefixes `""`; `{"model":{"id":"claude-sonnet-5-5"}}` | pill `\e[100;37;1m ◨ ? \e[0m` | edge-case |
| prefixes `claude*`; id `claude-sonnet-5-5` | pill `\e[105;30;1m ◨ ANTH \e[0m` | edge-case |
| prefixes `" claude-sonnet , claude-opus ,, "`; id `claude-opus-5` | pill `\e[106;30;1m ◨ DGX \e[0m` | edge-case |
| prefixes `Claude-sonnet`; id `claude-sonnet-5-5` | pill `\e[105;30;1m ◨ ANTH \e[0m` | edge-case |
| prefixes `claude-sonnet`; `{"model":{"id":5}}` | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 | error |
| prefixes `claude-sonnet`; `{"model":"x"}` | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | For all string ids and prefix lists, `on_local == any(strings.HasPrefix(id, p))` when both are non-empty, else None | property test (Go `testing/quick`) + table test |
| VP-028 | Pill bytes are one of exactly three constants (with default theme) | table test |
| VP-028 | Go pill bytes equal oracle pill bytes on the Tier A corpus | parity harness (BC-6.03.002) |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:render_lane (SL:441-449); pill SGRs SL:130 |
| Legacy contract | BC-SL-006 (pass-3 broad row; refined in pass-3 deep r1 §A table) |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (degrade on fault), DI-012 (no unnamed deviations) |
| Owner decisions | OD-111 / OD-123 (prefix key and default `claude-sonnet`; empty value expressible), OD-113 (theme keys), OD-121 (client-view lane), OD-05 (no `DGX_*` env) |
| Config keys | `backends[0].model_prefixes`, `statusline.theme.*` (pill codes), `statusline.glyphs.*` |
| Architecture Module | `internal/statusline/lane.go` (design §2.2; BC-COMPONENT-MAP: internal/statusline/lane.go (prefix startswith pill) — ARCH-03) |
| Stories | TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-1.02.002 — composes with (model label is the next segment)
- BC-1.02.009 — related to (same prefix list; reroute-all uses `rstrip("*")`, the pill does not)
- BC-1.02.021 — related to (non-string id rendering)
- BC-2.01.002 — depends on (prefix key, default, single backend entry)
- BC-2.01.003 — depends on (pill SGR theme keys)
- BC-5.03.002 — depends on (Python whitespace strip)
- BC-1.01.001 — depends on (degraded line on fault)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#lane` — internal/statusline/lane.go (prefix startswith pill) (pill, model and project segments) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row-1 lane segments story

## VP Anchors (Recommended)

- VP-028 — pill classification property

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`render_lane`, SL:441-449; constants SL:130) |
| **Confidence** | high (pass-3 HIGH-R, 10 cases; re-run 2026-11-15) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if (prefixes and model_id) else None` (SL:446)
- **inferred**: AttributeError on a non-string id propagates to the module guard (SL:1238-1245)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (config already resolved) |
| **Global state access** | reads resolved config |
| **Deterministic** | yes |
| **Thread safety** | n.a. (single-threaded render) |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed: a pure function of `(model_id, prefixes, theme)`, suitable for
exhaustive table and property tests. The legacy env read inside `render_lane` becomes a
resolved config value passed in (design IM-16).
