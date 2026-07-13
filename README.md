
# auto-README

> CLI tool that auto-generates README.md from repository analysis.

**Repository:** https://github.com/Ange2101/auto-README.git

**Primary Language:** Python
**Default Branch:** `main`

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Languages](#languages)
- [Getting Started](#getting-started)
- [Usage Guide](#usage-guide)
- [Development & Tests](#development--tests)
- [License](#license)

---

## Overview

CLI tool that auto-generates README.md from repository analysis.

Clone the repository:

```bash
git clone https://github.com/Ange2101/auto-README.git
cd auto-README
```

---

## Features

- Built primarily with Python
- Test suite included (pytest)
- Licensed under MIT
- Package manager: pip

---

## Project Structure

```
auto-README/
├── auto_README.egg-info/
│   ├── dependency_links.txt
│   ├── entry_points.txt
│   ├── PKG-INFO
│   ├── requires.txt
│   ├── SOURCES.txt
│   └── top_level.txt
├── src/
│   ├── templates/
│   │   ├── full.md.j2
│   │   └── minimal.md.j2
│   ├── __init__.py
│   ├── analyzer.py
│   ├── cli.py
│   └── generator.py
├── tests/
│   └── pyproject.toml
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

---

## Languages

| Language | Percentage |
|----------|------------|
| Python | 81.7% |
| Markdown | 14.1% |
| TOML | 4.2% |

---

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.9+

### Installation

Install dependencies using the detected package manager (`pip`):

```bash
pip install -r requirements.txt
```

---

## Usage Guide

auto-readme is a command-line tool. See below for detailed usage.

### Commands

| Command | Description |
|---------|-------------|
| `auto-readme [repo_path]` |  |

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `-o / --output` | README.md |  |
| `-t / --template` | full.md.j2 |  |
| `--template-dir` | — |  |

### Examples

```bash
auto-readme .
```
Run with default settings in the current directory

```bash
auto-readme . --template minimal.md.j2
```
Use a different template (minimal instead of full)

```bash
auto-readme /path/to/project -o /path/to/project/README.md
```
Analyze another project and write to a custom path


---

## Development & Tests

This project uses **pytest** for testing.

Run the test suite:

```bash
pytest
```

---

## License

This project is licensed under the **MIT** License.
