
# auto-README

> CLI tool that auto-generates README.md from repository analysis.

**Repository:** https://github.com/Ange2101/auto-README.git

**Primary Language:** Python
**Default Branch:** `main`

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Languages](#languages)
- [Installation](#installation)
- [Tests](#tests)
- [License](#license)

---

## Overview

CLI tool that auto-generates README.md from repository analysis.

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
| Python | 74.0% |
| Markdown | 21.1% |
| TOML | 4.9% |

---

## Installation

```bash
pip install -r requirements.txt
```

*Package manager detected:* `pip`

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
