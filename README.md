
# Project Development Setup

This project uses a Windows batch script, `dev.bat`, to simplify the management of the Python development environment. The script handles virtual environment creation, dependency management, formatting, and testing.


## Prerequisites

Ensure the following are installed on your machine:

- [Python 3.11](https://www.python.org/downloads/release/python-3110/)
- [Poetry](https://python-poetry.org/docs/#installation) (automatically installed if missing)

## Usage

### 1. Setting up the Development Environment

To create a virtual environment and install the necessary dependencies, including development packages, run:

```bash
dev.bat create-dev
```

This will:
- Create a virtual environment in the `.venv` directory (if not already created).
- Install `poetry` inside the virtual environment (if not available).
- Install all project dependencies as defined in `pyproject.toml`, including the `dev` dependencies.
- run `.venv\Scripts\activate` to activate your env 


### 2. Formatting Code

To automatically format your Python code using `black` and `isort`, run:

```bash
dev.bat format
```

This command applies both formatters across the project codebase.

### 3. Checking Code Formatting

To check if your code adheres to the project's formatting standards without applying changes, run:

```bash
dev.bat format-check
```

This will verify that the code is formatted according to `black` and `isort` rules.

### 4. Checking Dependencies

To check for any potential issues in your project dependencies, such as unused or incorrect packages, run:

```bash
dev.bat dep-check
```

### 5. Updating the Development Environment

To update all the project dependencies to their latest compatible versions, run:

```bash
dev.bat update-dev
```

### 6. Running Tests

To run the test suite with `pytest`, along with coverage reports, run:

```bash
dev.bat test
```

This command generates both terminal and HTML coverage reports, with coverage information for the `./runespreader` directory.

### Available Commands

| Command         | Description                                                              |
|-----------------|--------------------------------------------------------------------------|
| `create-dev`    | Set up the virtual environment and install dependencies                  |
| `format`        | Format the code using `black` and `isort`                                |
| `format-check`  | Check the code formatting without making changes                         |
| `dep-check`     | Check for dependency issues using `deptry`                               |
| `update-dev`    | Update all project dependencies to their latest compatible versions      |
| `test`          | Run the test suite with `pytest` and generate coverage reports           |
