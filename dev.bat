@echo off
setlocal

REM Check if virtual environment exists, if not create it
if not exist ".venv\Scripts\activate" (
    echo "Creating virtual environment..."
    py -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Install poetry if it's not already installed
where poetry >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo "Installing Poetry..."
    pip install poetry==1.4.2
)

REM Parse the first argument to decide the command
if "%1" == "create-dev" (
    echo "Setting up development environment..."
    poetry install --with dev
    echo "Development environment setup complete!"
) else if "%1" == "format" (
    echo "Formatting code..."
    poetry run black .
    poetry run isort .
) else if "%1" == "format-check" (
    echo "Checking code formatting..."
    poetry run black --check .
    poetry run isort --check .
) else if "%1" == "dep-check" (
    echo "Checking dependencies..."
    poetry run deptry .
) else if "%1" == "update-dev" (
    echo "Updating development environment..."
    poetry update
) else if "%1" == "test" (
    echo "Running tests..."
    poetry run pytest --cov-report term --cov-report html --cov=./runefumbler .
) else (
    echo "Invalid command. Available commands: create-dev, format, format-check, dep-check, update-dev, test"
)
