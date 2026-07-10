# auto-README

> CLI tool that auto-generates README.md from repository analysis.

**Repository:** https://github.com/Ange2101/auto-README.git

**Primary Language:** Python
**Default Branch:** `main`

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Types](#project-types)
- [Limitations](#limitations)
- [Project Structure](#project-structure)
- [Languages](#languages)
- [Tests](#tests)

---

## Overview

`auto-readme` is a command-line tool that analyzes a repository and generates a complete `README.md` file automatically. It detects languages, test frameworks, CI/CD, Docker, package managers, entry points, and license information by inspecting files in the project.

---

## Features

- **Language detection** by line-count percentage
- **ASCII directory tree** generation (up to depth 3)
- **Test framework detection** (pytest, jest, vitest, JUnit, go test, cargo test)
- **CI/CD platform detection** (GitHub Actions, GitLab CI, CircleCI, Azure Pipelines, Jenkins)
- **Docker support** detection
- **Package manager & install command** inference
- **License identification** (MIT, Apache-2.0, GPL, BSD)
- **Git metadata** extraction (remote URL, default branch)
- **Two templates:** `full.md.j2` (comprehensive) and `minimal.md.j2` (quick overview)

---

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/Ange2101/auto-README.git
cd auto-README
pip install -e .
```

*Package manager detected:* `pip`

---

## Usage

### Basic usage

Analyze the current directory and generate a full README:

```bash
auto-readme . --template full.md.j2
```

Generate a minimal README:

```bash
auto-readme . --template minimal.md.j2
```

Analyze another repository:

```bash
auto-readme /path/to/project --output /path/to/project/README.md
```

### CLI options

| Option | Description |
|--------|-------------|
| `repo_path` | Path to the repository (default: current directory) |
| `-o, --output` | Output file path (default: `README.md`) |
| `-t, --template` | Template to use: `full.md.j2` or `minimal.md.j2` |
| `--template-dir` | Custom directory containing Jinja2 templates |

---

## Project Types

### Python projects

For Python projects, `auto-readme` extracts the description from:
1. `pyproject.toml` (`[project]` → `description`)
2. `package.json` (`description`) *(if present)*
3. Existing `README.md` first paragraph
4. `__init__.py` module docstring

If your project has a `tests/` directory, pytest will be detected automatically.

### Node.js / JavaScript projects

Description is read from `package.json`. Test framework is inferred from config files (`jest.config.js`, `vitest.config.ts`, etc.).

### HTML / CSS portfolios and static sites

**Important:** Static sites (HTML, CSS, JS) usually do **not** contain a manifest file with a description. The generated README will therefore miss:
- Project description
- Demo link
- Screenshots
- Feature list

**Workaround:** Create a minimal `package.json` at the root:

```json
{
  "name": "my-portfolio",
  "description": "Personal portfolio website built with HTML and CSS."
}
```

Then run:

```bash
auto-readme . --template full.md.j2
```

After generation, manually add:
- A **Live Demo** link
- **Screenshots** (`![Screenshot](screenshot.png)`)
- A **Features** section

### Java / Maven / Gradle

Test framework is inferred from `pom.xml` or `build.gradle`. Install command is mapped to `mvn install` or `gradle build`.

### Go / Rust

Install commands (`go mod download`, `cargo build`) and test commands (`go test ./...`, `cargo test`) are auto-detected from `go.mod` and `Cargo.toml`.

---

## Limitations

- **Description extraction** requires a manifest file (`pyproject.toml`, `package.json`) or an existing `README.md`. Projects without these will have an empty overview.
- **Remote URL** requires the target directory to be a git repository with an `origin` remote.
- **Entry points** are detected from common conventions (`main.py`, `package.json` `main` / `bin`). Custom entry points may be missed.
- **Templates** are Jinja2-based. Advanced custom formatting requires editing the `.j2` files directly.

---

## Project Structure

```
auto-README/
├── src/
│   ├── templates/
│   │   ├── full.md.j2
│   │   └── minimal.md.j2
│   ├── __init__.py
│   ├── analyzer.py
│   ├── cli.py
│   └── generator.py
├── tests/
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Languages

| Language | Percentage |
|----------|------------|
| Python | 83.0% |
| Markdown | 10.8% |
| TOML | 6.2% |

---

## Tests

Framework: **pytest**

Run the test suite with:

```bash
pytest
```

---

## License

This project is licensed under the **MIT** License.
