[![slo-reporting](https://github.com/colenio/slo-reporting/actions/workflows/slo-reporting.yml/badge.svg)](https://github.com/colenio/slo-reporting/actions/workflows/slo-reporting.yml) [![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/slo-reporting)](https://artifacthub.io/packages/search?repo=slo-reporting)

# SLO Reporting

Excel compatible SLO reporting tool for Prometheus.

## Overview

Run the tool

```shell
# 1. Have prometheus running on localhost:9090
# 2. Adjust './config/settings.yaml' to your needs or set the environment variables, e.g.
$ export PROMETHEUS_URL=http://localhost:9090
$ export ARCHIVE=./slo-reporting.csv
$ export RUST_LOG=info
# 3. Run the tool
$ cargo run
# Example output
   Compiling slo_reporting v0.1.0
    Finished dev [unoptimized + debuginfo] target(s) in 2.04s
     Running `target\debug\slo_reporting.exe`
[2022-11-02T19:57:12Z INFO  slo_reporting] Started slo_reporting, version dev
[2022-11-02T19:57:12Z INFO  slo_reporting] Read './slo-reporting.csv'
[2022-11-02T19:57:13Z INFO  slo_reporting] Processed 'serviceA-uptime' (goal=98%, rolling=14days, step=1day)
[2022-11-02T19:57:13Z INFO  slo_reporting] Processed 'serviceB-uptime' (goal=98%, rolling=14days, step=1day)
[2022-11-02T19:57:13Z INFO  slo_reporting] Wrote './slo-reporting.csv'
```

Import the CSV into a spreadsheet, e.g. Excel, and create a chart.

## Development

### Prerequisites

Install

- [Rust](https://www.rust-lang.org/tools/install)
- Windows: [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
  - Make sure to select the "C++ build tools" workload
- Linux: `sudo apt install build-essential`

**IDE recommendations:**

- [IntelliJ IDEA](https://www.jetbrains.com/idea/)
  - [Rust bundle](https://plugins.jetbrains.com/bundles/3-rust-bundle)
- [RustRover](https://www.jetbrains.com/rust/)
- [VisualStudio Code](https://code.visualstudio.com/)
  - [Rust extension](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust)

Next run

```shell
rustup update
# Install the required toolchain instrumenting coverage via profiles
rustup install nightly
rustup component add clippy
```

### Build

Building the application is done with `cargo build` or `cargo build --release` for a release build.
Running the test suite is done with `cargo test`.

### Test Coverage

For the coverage, things are slightly more complicated.
We mainly followed [How to collect Rust source-based code coverage](https://marco-c.github.io/2020/11/24/rust-source-based-code-coverage.html)
which is a bit dated, but still works.

First, add `RUSTFLAGS="-Cinstrument-coverage"` to the `profile.dev`.
Note that this requires a nightly toolchain.

```toml
[profile.test]
inherits = "dev"
rustflags = ["-Cinstrument-coverage"]
```

Then, run the tests with `cargo +nightly test --profile=test` which will generate the coverage data.

Alternatively, you can just set `RUSTFLAGS="-Cinstrument-coverage"` in the environment.

Next, we want to generate coverage report (e.g. in HTML format).
**Note** that we need to use the nightly toolchain for this as well and [llvm-tools-preview](https://docs.rs/llvm-tools/latest/llvm_tools/).

```shell
# Install grcov
cargo install grcov
# Install llvm-tools-preview
rustup component add llvm-tools-preview
# Generate the coverage report (lcov format)
grcov . -b target\debug -s . -t lcov --llvm --branch --ignore-not-existing -o lcov.info
# Generate the HTML report
grcov . -b target\debug -s . -t html --branch --ignore-not-existing -o ./coverage/
```

**Note** that most build agents do have the required tools installed, e.g.

- GitHub Actions & Azure DevOps: `ubuntu-22.04`: [Rust Tools](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2204-Readme.md#rust-tools)
