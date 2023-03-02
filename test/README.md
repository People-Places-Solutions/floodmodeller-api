# Testing Guidelines
## Overview
The Flood Modeller API uses the [`pytest` framework](https://docs.pytest.org/) for unit tests. 

Writing comprehensive unit tests is an essential part of contributing to the Flood Modeller API. We encourage contributors to acdopt Test Driven Development.

# Running Tests & Coverage Reports

You can run tests from the terminal using `pytest test` add the verbosity flag for more information: `-v`. You can also get a test coverage report using `pytest coverage` (requires `pytest-cov`)


## Automated Testing
The repository uses GitHub Actions to run tests automatically. This is triggered whenever a push is made to any branch and whenever a pull request is made to the `main` branch. Failing tests will prevent merging a PR to `main` unless overrided.

# Writing Tests 

## Best Practice
Where possible, unit tests should isolate a specific unit of functionality.  This gives us clarity on where a bug exists if something fails. 

To learn more about writing unit tests with pytest, refer to their [documentation](https://docs.pytest.org/en/6.2.x/contents.html).

## Directory Structure
The structure of the test directory should mirror the filenames of the source directory `floodmodeller_api` with a test file for each source file. The file names of tests should be preceded with "test_" e.g. `test_dat.py`

 All test files should be at the top level of the directory. This is because of the way `pytest` imports modules.

Here is an example of how the test directory should be structured. If there are duplicate source filenames then preceed them with the module name e.g. `test_units_helpers.py`
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

