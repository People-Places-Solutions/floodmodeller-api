# Flood Modeller API Contributing Guidelines

## Getting Started
To write code for the Flood Modeller API, first clone or fork the GitHub repository.
Then, use the command
```shell
pip install -e path\to\floodmodeller-api
```
to install the package in editable mode.
This allows you to edit and use the package without having to reinstall it.

To contribute, you should create a new branch, work on it, and then open a Pull Request once you are done.
The repository uses GitHub Actions to run tests and linters automatically.
These are triggered whenever a push is made to any branch and whenever a pull request is made to the main branch.
Failing tests or linters will prevent merging to main unless overridden.

## Linting
Linting ensures that the code meets certain quality standards and can reveal bugs.
The Lint workflow uses `black` for formatting, `isort` for sorting imports, `mypy` for type checking, and `flake8` and `pylint` for other best practices.
You do not need to install these packages to work on the Flood Modeller API as they run automatically in GitHub Actions.
However, you may wish to install them if you want to check locally that your commits will pass before pushing to the remote.
Install them with 
```shell
pip install black isort mypy flake8 pylint
```

If run locally, the packages `black` and `isort` will fix your formatting problems rather than just point them out.
Use the commands
```shell
black . --line-length 100
isort . --profile black --line-length 100
```
to enforce a maximum line length of 100 and ensure that `black` and `isort` do not conflict with each other.

Run `mypy`, `flake8`, and `pylint` with
```shell
mypy . --ignore-missing-imports
flake8 . --ignore E203,E402,E501,W503 --per-file-ignores __init__.py:F401 --builtins __version__ --max-complexity 10
pylint . --disable=all --enable=dangerous-default-value, unneeded-not, no-else-return, no-else-continue, simplifiable-if-statement, simplifiable-if-expression, unnecessary-comprehension, consider-using-in, redefined-builtin, unused-variable, unnecessary-pass, used-before-assignment, superfluous-parens, unnecessary-dunder-call, no-else-raise, consider-iterating-dictionary, raise-missing-from
```
to discover other code quality issues.
Unlike `black` and `isort`, you will have to fix any of these problems manually.
Best to run these checks throughout the development process, rather than just at the end.


## Testing
The Flood Modeller API uses the [`pytest` framework](https://docs.pytest.org/) for unit tests. 

Writing comprehensive unit tests is an essential part of contributing to the Flood Modeller API.
We encourage contributors to adopt Test Driven Development.

Run
```shell
pip install -r requirements.txt
```
to install the packages required for the tests.


### Running Tests
Use
```shell
pytest . -v --cov=floodmodeller_api --cov-fail-under=75
```
to run tests from the terminal, including a coverage report.

Test coverage reports are important to ensure that all parts of the API are being tested and can help identify areas that need further testing.


### Writing Tests 

#### Best Practice
When writing unit tests, it is important to isolate a specific unit of functionality as much as possible.
This gives us clarity on where a bug exists if something fails.
In addition, test names should be descriptive and follow a consistent naming convention. We also recommend avoiding test duplication and using fixtures to set up test data and state.

To learn more about writing unit tests with `pytest`, refer to their [documentation](https://docs.pytest.org/en/6.2.x/contents.html).

#### Naming 

Tests should be given names that clearly describe what is being tested.
Use a consistent approach to naming and follow `snake_case` conventions.
It is okay if this results in a slightly longer function name.


#### Sharing Fixtures Between Tests

Many tests share data which are set up using fixtures.
You should add any fixtures which are shared across multiple tests to `test/conftest.py`.
You must specify the `scope = "session"` parameter:
```python
@pytest.fixture(scope = "session")
def test_workspace():
    return os.path.join(os.path.dirname(__file__), "test_data")
```

#### Test Data
To ensure consistent and reliable testing, we use a variety of test data which is located in the `tests/test_data` folder. 

#### Directory Structure
The structure of the test directory should mirror the filenames of the source directory `floodmodeller_api` with a test file for each source file.
The file names of tests should be preceded with `test_` e.g. `test_dat.py`.
All test files should be at the top level of the directory.
This is because of the way pytest imports modules.

Here is an example of how the test directory should be structured.
If there are duplicate source filenames then preceed them with the module name e.g. test_units_helpers.py
```
floodmodeller_api/
    __init__.py
    dat.py
    ...
    units/
        __init__.py
        helpers.py
        ...
test/
    test_dat.py
    test_helpers.py
    ...
...
```


## Visual Studio Code

If you use Visual Studio Code, here is an example `.vscode/settings.json` file you might find useful when working on the Flood Modeller API:
```json
{
    "python.testing.pytestArgs": [
        "."
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "editor.rulers": [100],
    "black-formatter.args": ["--line-length", "100"],
    "ruff.lint.args": [
        "--select=F,E,W,C,I,N",
        "--ignore=E203,E402,E501",
        "--line-length=100",
    ],
}
```

These settings ensure that the tests can be run from the editor, a ruler appears at the designated line length (100 characters), the `black` and `ruff` plugins function according to this length, and that only certain errors (those that correspond to the implemented GitHub Actions) are checked for.

The `ruff` plugin incorporates many of the linting checks implemented with GitHub Actions, but it runs quickly as you are writing the code.
You need to have the `black` and `ruff` plugins installed to use them as part of the editor, distinct from installing packages with `pip` to use them via the commands listed as described earlier.