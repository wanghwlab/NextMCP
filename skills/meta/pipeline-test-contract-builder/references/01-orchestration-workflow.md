# Orchestration Workflow

## Goal

Turn one pipeline repository test setup into one final hidden-evaluation-spec bundle without
making the user manually call the classifier, localizer, and converter as separate steps.

## Steps

1. Collect evidence from the standard file order.
2. Classify the test setup.
3. Decide whether localization is needed.
4. If needed, localize remote and repo-local input references into server-local paths.
5. Convert the result into the final evaluation spec.
6. Return `ready`, `blocked`, or `skip`.

## Default behavior

- Prefer `test`, else one small `test_*` profile.
- Prefer one canonical lightweight test setup per pipeline.
- Stop early when the selected setup is clearly unsuitable.
- Keep the final output compact and operational.

## When to bypass this skill

Use the lower-level skills directly only when the user explicitly asks to:

- inspect classification only
- debug localization only
- debug conversion only
