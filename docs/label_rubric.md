# Label Rubric

## Core Principle

Label the status of the original concern after revision, not the politeness of the author response.

## Labels

### `fixed`

Use `fixed` when:

- the exact concern is addressed
- the revision contains concrete evidence of the fix
- a reasonable reviewer would no longer keep the issue as an active blocker

Typical evidence:

- new experiments
- newly added tables or figures
- explicit theorem corrections
- newly released implementation details

### `partially_fixed`

Use `partially_fixed` when:

- the authors made real progress
- some part of the concern remains open
- the revision reduces the severity of the issue but does not resolve it

Typical evidence:

- qualitative analysis added, but no full systematic study
- claim softened, but core evidence gap remains
- one missing baseline added, while a stronger one is still absent

### `unresolved`

Use `unresolved` when:

- the issue is still materially present
- the response mostly defers or reframes the problem
- the revision does not supply the evidence needed to resolve the concern

Typical evidence:

- "future work"
- "beyond scope"
- no new experiment despite a direct empirical criticism
- no clarifying detail despite a concrete reproducibility concern

### `regressed`

Use `regressed` when:

- the revision introduces a new issue on the same axis
- the attempted fix weakens the paper
- the paper becomes less reliable, less complete, or less reproducible on this concern

Typical evidence:

- added results expose a stronger failure than before
- revised setup drops previously reported coverage
- a new prompt or training detail reduces reproducibility

## Tie-Breakers

- If the fix exists only in the response but not in the revision, prefer `unresolved` or `partially_fixed`.
- If a concern is softened but not eliminated, prefer `partially_fixed`.
- If the paper changes direction and the original concern no longer applies because the claim is narrowed honestly, prefer `partially_fixed` unless the blocker is truly gone.
- If the attempted fix creates a visibly worse outcome, prefer `regressed`.

## Annotation Discipline

- highlight the exact review sentence that states the concern
- highlight the exact response or revision sentence that supports the label
- store one short note explaining why the neighboring label was rejected
