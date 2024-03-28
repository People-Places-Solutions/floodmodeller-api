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
The Lint workflow uses `black` for formatting, `ruff` and `pylint` for other best practices, and `mypy` for type checking.
You do not need to install these packages to work on the Flood Modeller API as they run automatically in GitHub Actions.
However, you may wish to install them if you want to check locally that your commits will pass before pushing to the remote.
Install them with 
```shell
pip install black ruff pylint mypy
```

The settings are included in the [`pyproject.toml`](pyproject.toml) file, so the commands are short:
```shell
black .
ruff .
pylint .
mypy .
```
which correspond with those in the [`run_linters.yml`](.github/workflows/run_linters.yml) file.
The package `black` will fix all formating problems and `ruff` will fix some linting problems, while problems raised by `pylint` and `mypy` have to be fixed manually.
Best to run these checks throughout the development process, rather than just at the end.
The packages `black` and `ruff` are also available as extensions for Visual Studio Code.


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
The settings for `pytest` are included in the [`pyproject.toml`](pyproject.toml) file.
Use the command
```shell
pytest . -v
```
which corresponds to the that in the [`run_tests.yml`](.github/workflows/run_tests.yml) file.

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
@pytest.fixture(scope="session")
def test_workspace():
    return Path(os.path.dirname(__file__), "test_data")
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
