## Intro

- Started off by cloning files from the [Original SDK](https://github.com/surge-ai/surge-python)
- Converted (almost) all the i/o blocking functionality to use Python's asyncio.

## Improvements & Changes

### Async support

- Most of the I/O blocking operations are now converted to async. This guarantees better performance when the library is
  used in an async environment.
- `httpx` replaces requests for making network calls: This makes network calls async with minimal changes from the
  `requests` api.
- File processing now happens using
  `aiofiles` which provides async alternatives to stdlib file processing tools.
- The `urllib` usage to download reports is now migrated to
  `httpx` streaming response mode.

### Dependency Management

- Dependencies are now managed using `uv`. uv enables faster dependency resolution & installs and provides deterministic
  locking.
- Development related dependencies are now added to an optional group (`dev`). They won't get installed into package
  users systems.

### Better Testing

- Developers can locally test the library across all the supported Python versions using `tox` command. Tox config is
  added in `pyproject.toml`
- For CI testing, Github test matrix + uv is added to parallely run tests across all supported Python versions on push.
- More tests: The number of test case is (almost) doubled.

### Code quality & formatting

- Added black for formatting the code. It is now added as a pre-commit hook.
- To set-up automated formatting: `pre-commit install` command should be run after initial project setup.

### New Dependencies

- tox: For local testing across the supported python versions
- aiofiles: Provides async equivalent of the stdlib file handlers.
- aiocsv: For async csv task processing
- httpx: For async network requests; compatible with requests api.
- pytest-asyncio: Plugin to support async test functions
- pytest-httpx: For mocking network calls.

### New Test Cases

- Added test_teams.py - To test the `teams.py` functionality using `pytest-httpx` plugin.
- test_reports.py - Added to test the report download & save functionality which was converted to use `aiofiles` and
  asyncio.
- test_utils.py - Test added for csv task processing (`load_tasks_data_from_csv()`), which now runs as a coroutine

## Breaking Changes

- The library drops support for Python versions prior to 3.9, which reached EOL.

## Future Improvements

- Automated releases & publishing to Pypi
