# Flood Modeller API Testing Guidelines
## Overview
The Flood Modeller API uses the [`pytest` framework](https://docs.pytest.org/) for unit tests. 

Writing comprehensive unit tests is an essential part of contributing to the Flood Modeller API. We encourage contributors to acdopt Test Driven Development.

# Running Tests
You can run tests from the terminal using pytest test and add the verbosity flag for more information: -v. You can also get a test coverage report using `pytest coverage` (requires pytest-cov). Test coverage reports are important to ensure that all parts of the API are being tested and can help identify areas that need further testing.


## Automated Testing
The repository uses GitHub Actions to run tests automatically. This is triggered whenever a push is made to any branch and whenever a pull request is made to the main branch. Failing tests will prevent merging a PR to main unless overridden.

# Writing Tests 

## Best Practice
When writing unit tests, it's important to isolate a specific unit of functionality as much as possible. This gives us clarity on where a bug exists if something fails. In addition, test names should be descriptive and follow a consistent naming convention. We also recommend avoiding test duplication and using fixtures to set up test data and state.

To learn more about writing unit tests with pytest, refer to their [documentation](https://docs.pytest.org/en/6.2.x/contents.html).

## Test Data
To ensure consistent and reliable testing, we use a variety of test data which is located in the `tests/test_data` folder. 

## Directory Structure
The structure of the test directory should mirror the filenames of the source directory floodmodeller_api with a test file for each source file. The file names of tests should be preceded with "test_" e.g. test_dat.py. All test files should be at the top level of the directory. This is because of the way pytest imports modules.

Here is an example of how the test directory should be structured. If there are duplicate source filenames then preceed them with the module name e.g. test_units_helpers.py
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

# Test Coverage
TBC - aiming to use codecov...