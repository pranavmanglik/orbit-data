# Orbit Data: development

The contract package is intentionally dependency-free at runtime. Changes here affect multiple
capability and provider packages, so keep the shared API small, typed, and explicit about its
behavioral guarantees.

## Local setup and checks

From the repository root:

```bash
python -m pip install -e '.[dev]' build
pytest
ruff check src tests
ruff format --check src tests
mypy
python -m build
```

The protocol tests use in-process fixtures and need no database or network service. These checks
verify this package's shape and typing; they do not prove that provider implementations meet the
contract or that transaction behavior is correct against a live database.

## Changing a public contract

Before adding a method or changing a signature, inspect all capability and provider consumers in
the workspace. State which behavioral guarantees are required for every conforming implementation
and which remain implementation-defined. Prefer provider-neutral terms and Python standard types;
do not add driver dependencies here.

Add tests for runtime protocol structure and supported public exports, and coordinate any behavior
change with the affected adapters. Update the README, architecture and operations guides, docstrings,
and release notes when the contract changes. Because this project is alpha, incompatible API
changes are possible, but they still need clear migration guidance for workspace consumers.

## Contribution practices

Follow [CONTRIBUTING.md](../../CONTRIBUTING.md), the code of conduct, and project governance. Keep
examples runnable, explain security-sensitive behavior, and distinguish local validation from
hosted CI or release verification. Do not include real credentials or production data in fixtures.
