[![slo-reporting](https://github.com/colenio/slo-reporting/actions/workflows/slo-reporting.yml/badge.svg)](https://github.com/colenio/slo-reporting/actions/workflows/slo-reporting.yml) [![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/slo-reporting)](https://artifacthub.io/packages/search?repo=slo-reporting)

# SLO Reporting

Excel compatible SLO reporting tool for Prometheus.

## Features

## Prerequisites

- Kubernetes cluster with [Prometheus](https://prometheus.io/)-compatible SLO-metrics
- Azure Storage Account with a File Share
- A [Kubernetes Secret](https://learn.microsoft.com/en-us/azure/aks/azure-csi-files-storage-provision#create-a-kubernetes-secret) with the following keys
  - `azurestorageaccountname`: The name of the Azure Storage Account
  - `azurestorageaccountkey`: The key of the Azure Storage Account

See

- [Create and use a volume with Azure Files in Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/azure-csi-files-storage-provision)

## Usage

The helm chart provides a simple way to deploy the tool to a Kubernetes cluster. It consists of a single pod running the tool as a cronjob.

```shell
helm repo add slo-reporting https://colenio.github.io/slo-reporting/
helm install my-slo-reporting slo-reporting/slo-reporting --version 0.1.0 --values my-values.yaml
```

An alternative is to to create a Kubernetes cronjob manually. This allows for more fine-grained control over the output volume.

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
$ python -m pur -r requirements-dev.txt -r requirements-dev.txt
All requirements up-to-date.
```

For updating Python itself, please consider [pyreadiness](https://pyreadiness.org/) with the used dependencies

### Build

Building the container image

```shell
$ docker compose build
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
tests\api\test_readings.py .                                           [100%]

============================= 1 passed in 0.05s =============================
```
