# Contributing

Thanks for contributing to the Spreadsheet Schema Manager test suite.

## How to contribute

- Open an issue for any proposed change or bug before starting larger work.
- Keep changes focused and scoped to a single feature or fix.
- Update the relevant test coverage and documentation when behaviour changes.

## Pull request process

1. Create a branch from the main branch.
2. Add or update tests for the behaviour you are changing.
3. Run the relevant test subset locally before submitting.
4. Open a pull request with a clear summary and test evidence.
5. Update the README if the test workflow, environment assumptions, or commands change.

## Test expectations

- Prefer deterministic, isolated tests.
- Avoid depending on state left behind by previous tests.
- Keep page-object and fixture logic clear and reusable.
- If a test is flaky, fix the root cause rather than weakening assertions.

Please also review our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [SECURITY.md](SECURITY.md).
