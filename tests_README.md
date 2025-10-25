# Testing Guide

## Running Tests

This project uses pytest for testing. All tests are located in the root directory with the naming pattern `test_*.py`.

### Install Test Dependencies

```bash
pip install pytest pytest-mock
```

Or install all dependencies including test dependencies:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

Or with verbose output:

```bash
pytest -v
```

### Run Specific Test Files

```bash
pytest test_models.py
pytest test_topic_loader.py
pytest test_session_manager.py
```

### Run Specific Test Classes or Functions

```bash
pytest test_models.py::TestTopic
pytest test_models.py::TestTopic::test_topic_creation
```

## Test Coverage

Current test files:

- `test_models.py` - Tests for data models (Topic, Message, Session)
- `test_topic_loader.py` - Tests for topic parsing and loading
- `test_session_manager.py` - Tests for session storage and management

## Test Structure

Each test file follows this pattern:

1. **Setup/Teardown**: Uses pytest's `setup_method` and `teardown_method` for test isolation
2. **Temporary Files**: Tests that require file I/O use temporary directories
3. **Test Classes**: Tests are organized into classes by functionality
4. **Descriptive Names**: Test functions use descriptive names that explain what is being tested

## What's Tested

### Models (`test_models.py`)
- Dataclass creation and validation
- Default values
- Message handling with and without canvas images
- Session state management

### Topic Loader (`test_topic_loader.py`)
- Markdown parsing
- Section extraction (objectives, materials, examples)
- Handling missing or malformed content
- Directory scanning and file filtering
- Error handling for corrupted files

### Session Manager (`test_session_manager.py`)
- Session creation and ID generation
- Saving and loading sessions
- Session listing and sorting
- Error handling for corrupted or missing files
- Message count tracking

## Notes

- Tests use temporary directories and clean up after themselves
- No actual API calls are made during testing
- The UI components (Solara) are not tested as they require a running kernel

