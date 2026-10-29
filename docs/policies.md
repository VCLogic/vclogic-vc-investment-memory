# Public-source investor policies, version 1.0

New full-export and curated builds produce `policies.json` alongside the readable wiki. It describes **what public sources support**, including where applicability and trade-offs remain unknown. It does not contain historical pitch decisions, calibrated probabilities, model training data, prediction thresholds or numeric policy weights. No prediction-accuracy improvement is claimed.

The [JSON Schema](../wiki_build/policies.schema.json) is the closed, machine-readable contract; [the representative artifact](examples/policies.json) uses a fictional investor quotation. That example deliberately leaves scope unresolved: it is a synthetic excerpt, not an actual investment memory. Its invented text and example.com source metadata are preserved in the [offline fixture](../tests/fixtures/policies/saved_source.json).

## Pipeline and wiki structure

1. **Extract:** review each source packet for identity, exact quotation, attribution, source date, explicit versus inferred support and personal versus fund context. New evidence adds `policy_basis`: kind, relationship classification and seven scope fields. Operating advice remains distinct from investor selection criteria. An effective period must not be invented from a collection date or mistaken for a publication date.
2. **Synthesize:** combine the validated evidence and context ledgers into policy records and supported relationships. Repetition alone establishes no priority. Preserve conflicts and unknown scope. Legacy excerpts lacking policy metadata can support cautious preferences, but cannot establish hard requirements or operative relationships.
3. **Render:** assign content-derived IDs, write `policies.json`, and append a deterministic, cited policy-guidance section to `persona.md`. The model-written persona, theses and portfolio prose retain their existing contracts and may cite the same policy IDs.
4. **Validate and review:** run structural, reference, scope and rendered-guidance checks before publication. Review interpretations against the sources separately; structural success is not semantic verification.

```text
wiki/<investor>/
  README.md
  persona.md                    # Nine dimensions + traceable policy guidance
  theses.md
  portfolio_and_constraints.md
  policies.json                 # New, additive public-source policy contract
  evidence.json                 # Exact quotes, interpretations, source refs, policy_basis
  evidence/*.md
  sources.md
  prepared.json                 # Saved source text and metadata
  _manifest.json                # Includes policies_schema_version for new builds
  validation.json
  context.json, context.md      # Full-export builds: source-reported facts
  inventory.json, source_reviews.json, coverage.json, coverage.md
```

Older wikis without `policies.json` remain valid. A build whose manifest declares the artifact must include it. Existing consumers can continue reading the three Markdown files; consumers interested in policy structure should feature-detect the artifact and check its version. This change does not modify onboarding or assessment installations.

## Records

Top-level fields are `schema_version` (`"1.0"`), `investor_slug`, `policies`, `relationships` and nonempty `limitations`. An empty policy set is allowed when no supportable policies can be extracted; it conveys no rules, not universal acceptance. Empty relationship arrays mean no established ordering or exceptions.

| Policy field | Meaning |
|---|---|
| `id`, `statement` | Content-derived identifier and concise supported claim. |
| `taxonomy_labels` | One or more existing labels from the 44-rationale taxonomy. |
| `type` | `hard_requirement`, `preference`, `conditional_rule`, `descriptive_context`. |
| `decision_effect` | `supports_investment`, `opposes_investment`, `context_dependent`. No automatic opposite rule. |
| `support` | `explicit` or `inferred`. An explicit preference is still a preference. |
| `evidence_refs` | Nonempty references such as `ev:test-0001`; `ctx:` references are context, not sufficient alone for selection policies. |
| `applicability` | Required `investor`, `vehicle`, `period`, `stage`, `sector`, `geography`, `decision_setting` objects. Each has `status` and `value`. |
| `preconditions` | Conditions that must hold before applying the policy. Each gives `condition`, `evidence_needed`, `on_false: "not_applicable"`, `on_unknown: "unresolved"`. |
| `applicability_evidence_needed` | What a downstream agent needs to establish applicability; explicit `not_stated` if absent. |
| `missing_information_effect` | Always `unresolved`; missing pitch information is not negative evidence. |
| `exceptions_status`, `exceptions` | `supported`, `unknown` or `not_stated`; supported exceptions have a statement, nonempty conditions, applicability and direct evidence refs. |
| `uncertainty`, `conflicting_evidence_refs` | Unresolved questions and conflicting evidence, with a substantive explanation when conflicts are cited. |
| `unresolved_applicability` | All scope fields with `unknown` or `not_stated` status. |

Scope examples:

```json
{"status": "stated", "value": "personal angel investments"}
{"status": "not_stated", "value": "not_stated"}
{"status": "unknown", "value": "unknown"}
```

`not_stated` means the sources do not supply the value; `unknown` means applicability is unresolved, including conflicting evidence. Neither means “all vehicles,” “all stages” or “timeless.” A stated policy scope must match the extracted evidence scope exactly. Unsupported specificity is rejected. A quote's numerical example must not be generalized into a cutoff; that interpretive safeguard requires semantic review.

Relationships contain `id`, `from_policy`, `to_policy`, `kind`, `statement`, `support`, `evidence_refs`, `conditions`, `applicability` and `resolution`:

| Kind | Direction and support |
|---|---|
| `priority` | From outweighs to, within supported conditions. Requires an explicit comparative statement. |
| `qualification` | From limits to. Requires explicit qualifying evidence. |
| `exception` | From is an exception to to. Requires explicit exception evidence and conditions. |
| `contradiction` | The two conflict; both sides must be cited. `resolution` remains `unresolved`. |

Separate positive founder and negative market statements do not support a founder override. An investment example with unclear setting is not an exception. Do not resolve disagreement by frequency or recency alone. Relationships and nested exceptions retain their own seven-field applicability. Operative relationships cannot contradict the scope of their target policies. Unknown scope must not be applied universally; conditions must retain any additional limits stated in the comparative quote.

IDs start with `pol-` or `rel-` and include a deterministic content hash. They survive temporary-key changes and evidence ordinal renumbering when source IDs, quotes and policy content stay the same. Changed statements, scope, support or conditions produce new IDs; paraphrasing is not guaranteed to preserve identity. Persist the artifact version or build receipt with IDs and reconcile changed policies on update. These are stable record identifiers, not permanent semantic identities across arbitrary model rewrites.

## Onboarding handoff

- Preserve `policies.json`, evidence/context ledgers and source metadata together. Resolve `ev:` / `ctx:` refs into exact quotes and original sources; do not treat policy IDs alone as evidence.
- Index by policy ID and taxonomy labels. Keep the investor/vehicle and dated scope with each retrieved record. Unknown scope requires clarification or explicitly conditional use, never silent application to the current fund.
- Before using a rule, establish applicability and preconditions. Distinguish a supported negative observation, a false precondition (not applicable), and missing evidence (unresolved).
- Apply an exception only when its stated conditions are established. Respect supported relationship direction and conditions; preserve unresolved contradictions as competing evidence or a clarification request.
- Preserve explicit/inferred status and uncertainty in any downstream representation. Do not convert preferences into gates or these public-source records into numeric weights or prediction thresholds. Onboarding and assessment own any historical behavioral analysis and later evaluation.

## Mechanical enforcement versus model judgment

Offline validation checks schema/version, closed fields, unique and content-derived IDs, reference existence, relationship targets, explicit unknown sentinels, condition outcomes and exception structure. It rejects hard requirements without explicitly classified requirement evidence, operative relationships without explicitly classified comparative evidence, scope mismatches, advice marked as explicit selection, and automatically resolved contradictions. The deterministic persona section must exactly match the structured records; all policy references in the three readable pages must resolve.

These checks depend on extracted classifications being truthful. They cannot prove that “only” constitutes an unconditional gate, that an exception really applies to the target investor, that a quote implies a priority, or that the model has faithfully classified operating advice. They also cannot prove that arbitrary prose outside the deterministic section agrees with the records, or detect every invented numeric threshold embedded in text. A citation's existence is not proof of entailment.

Semantic review should compare each hard requirement, exception and priority with its quote and surrounding source; verify vehicle, period and conditions; inspect contradictory sources; and compare free-form guidance with structured records. The pipeline has no mandatory human approval stage and does not mark structural validation as human review. Record any human review separately; no human or calibration status is fabricated here.

Offline checks (no model calls):

```bash
python -m unittest discover -s tests -v
python -m wiki_build check wiki/investor-slug
```

The test suite builds a temporary wiki from the fictional source and fixture synthesis, checks its policy artifact, and deletes the temporary output. It does not regenerate existing memories or contact Sol.
