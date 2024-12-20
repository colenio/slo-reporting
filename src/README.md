# Service Level Objective Reporting

## Development

### Prerequisites

Install

- [Python](https://www.python.org/) (>=3.11)

**IDE recommendations:**

- [PyCharm](https://www.jetbrains.com/pycharm/)
- [IntelliJ IDEA](https://www.jetbrains.com/idea/)
- [VisualStudio Code](https://code.visualstudio.com/)

Next run

```shell
# Install dependencies
$ pip install --user -r requirements.txt -r requirements-dev.txt
Requirement already satisfied: certifi==2021.10.8 in ...
...

# Update dependencies
$ python -m pur -r requirements.txt -r requirements-dev.txt
All requirements up-to-date.
```

For updating Python itself, please consider [pyreadiness](https://pyreadiness.org/) with the used dependencies

### Build

Building the container image

```shell
$ docker compose build slo-reporting
[+] Building 2.5s (11/11) FINISHED
...
Use 'docker scan' to run Snyk tests against images to find vulnerabilities and learn how to fix them
```

### Run

```shell
# Run the app, on Windows use `python -m uvicorn main:app --reload`
$ uvicorn main:app [--reload]
INFO:     Started server process [13728]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

# Tests
$ python -m pytest --mypy --cov --cov-fail-under=75

============================= 1 passed in 0.05s =============================
```
