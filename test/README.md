# Testing Guidelines
## Overview
The Flood Modeller API uses the `pytest` framework for unit tests. 

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

## Automated Testing
TODO: ...github actions...
