# Routing Matrix

## profile-only

- Classifier: required
- Localizer: run when remote URLs or `projectDir/tests/...` files appear
- Converter: always
- Typical final status: `ready`

## profile-plus-tests-config

- Classifier: required
- Localizer: often required
- Converter: always, with selective merge from `tests/nextflow.config`
- Typical final status: `ready`

## requires-local-cache

- Classifier: required
- Localizer: skip when cache roots already exist and are authoritative
- Converter: always, but keep cache dependency explicit
- Typical final status:
  - `ready` when cache exists
  - `blocked` when cache is missing

## unsuitable-for-generic-smoke

- Classifier: required
- Localizer: skip
- Converter: partial only, enough to explain blockers
- Typical final status: `skip`

## Modifier effects

### localize-remote-inputs

- Force localization planning before final conversion.

### environment-sensitive

- Add adapter notes or blockers when runtime depends on auth, licenses, or cloud assumptions.

### igenome-sensitive

- Record that upstream semantics may differ under current server config.

### snapshot-rich

- Prefer deriving a small stable assertion set from `.snap` and `.nftignore`.
