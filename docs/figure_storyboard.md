# Figure Storyboard

## Figure Type

`Motivated Example` plus `Experimental Results`

## Best Paradigm

Use an animated issue ledger instead of a static benchmark table.

Why:

- it shows temporal updating directly
- it makes stale criticism visible
- it can be reused for both the demo and the paper

## Layout Sketch

Canvas:

- left: review concern cards
- center: author response and revision events on a timeline
- right: model judgment transition

Animation:

- issue cards enter from left
- evidence chips fade into the timeline
- judgment nodes shift color as the model updates

Color roles:

- `fixed`: green
- `partially_fixed`: amber
- `unresolved`: red
- `regressed`: magenta

## Labeling Rules

- every issue card should use concrete issue names
- annotate the exact evidence snippet that supports the final label
- show both gold and predicted labels when possible

## Tool Suggestion

- first draft: the repo's standalone HTML renderer
- paper version: export frames or a static snapshot from the same renderer

## First Three Actions

1. render the smoke timeline end to end
2. replace synthetic cards with real annotated issues
3. design one compact paper-safe static version and one richer demo version
