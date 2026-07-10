#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from collections import Counter  # FIX: imported to resolve NameError on 'counter = counter()'
from git import Repo  # GitPython library for extracting git metadata
from pathlib import Path
from typing import Any, Dict, List, Optional


class RepoAnalyzer:
    """
    Analyzes a repository to extract metadata for README generation.
    """

    def __init__(self, repo_path: Path):
        """
        Initialize the analyzer with the target repository path.
        """
        self.repo_path = Path(repo_path).resolve()
        self.git_repo = None
        try:
            # attempt to open the directory as a git repository
            self.git_repo = Repo(self.repo_path)
        except Exception:
            # if it fails (no .git folder), we silently ignore
            # the tool still works for non-git directories
            pass

    def analyze(self) -> Dict[str, Any]:
        """
        Run all analysis methods and return aggregated metadata dictionary.
        """
        # extract HTML metadata early so _get_description() can use it as fallback
        html_meta = self._extract_html_meta()
        return {
            "repo_name": self.repo_path.name,
            "description": self._get_description(html_meta),
            "html_title": html_meta.get("title"),
            "primary_language": self._detect_primary_language(),
            "languages": self._detect_languages(),
            "tree": self._get_tree(),
            "has_tests": self._has_tests(),
            "test_framework": self._detect_test_framework(),
            "has_docker": self._has_docker(),
            "has_ci": self._has_ci(),
            "ci_platform": self._detect_ci_platform(),
            "license": self._detect_license(),
            "remote_url": self._get_remote_url(),
            "default_branch": self._get_default_branch(),
            "package_manager": self._detect_package_manager(),
            "install_command": self._get_install_command(),
            "entry_points": self._find_entry_points(),
            "is_website": self._is_website(),
            "has_screenshots_dir": self._has_screenshots_dir(),
            "features": self._get_features(),
            "prerequisites": self._get_prerequisites(),
        }

    def _detect_languages(self) -> Dict[str, int]:
        """
        Detect programming languages by line count and return percentage distribution.
        """
        # map file suffixes to human-readable language names
        extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".html": "HTML",
            ".css": "CSS",
            ".md": "Markdown",
            ".json": "JSON",
            ".yml": "YAML",
            ".yaml": "YAML",
            ".toml": "TOML",
            ".sh": "Shell",
            ".dockerfile": "Dockerfile",
        }
        # FIX: replaced undefined 'counter = counter()' with Counter() from collections
        counter = Counter()
        # folders we never want to count (virtual-envs, caches, build artifacts)
        ignore = {".git", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}

        # recursively walk every file in the repo
        for path in self.repo_path.rglob("*"):
            # skip ignored directories by checking if any part of the path is in ignore set
            if path.is_file() and not any(part in ignore for part in path.parts):
                ext = path.suffix.lower()
                # FIX: files like 'Dockerfile' have no suffix, so we synthesize one from the filename
                if not ext:
                    ext = f".{path.name.lower()}"
                if ext in extensions:
                    try:
                        # count the lines in the file to weight the language distribution
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            lines = len(f.readlines())
                        # add the line count to the matching language bucket
                        counter[extensions[ext]] += lines
                    except Exception:
                        # if a file is unreadable, just skip it
                        pass

        total = sum(counter.values())
        # if there are no tracked files, return empty dict to avoid ZeroDivisionError
        if not total:
            return {}

        # FIX: corrected typo 'counte.most_common()' to 'counter.most_common()'
        # compute percentage for each language, rounded to 1 decimal place
        return {lang: round(count / total * 100, 1) for lang, count in counter.most_common()}

    def _detect_primary_language(self) -> Optional[str]:
        """
        Return the dominant programming language by line count percentage.
        """
        langs = self._detect_languages()
        # return the key with the highest percentage value, or None if no languages were found
        return max(langs, key=langs.get) if langs else None

    def _get_tree(self, max_depth: int = 3) -> str:
        """
        Generate an ASCII directory tree up to a specified depth.
        """
        # directories and artifacts we do not want to show in the tree
        ignore_patterns = {
            ".git",
            "venv",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            "dist",
            "build",
            ".egg-info",
        }
        # start the output list with the root folder name
        lines = [self.repo_path.name + "/"]

        # FIX: moved the recursive helper inside the method as a closure
        # so it can access 'lines', 'ignore_patterns', and 'max_depth' without passing them around
        def _tree(dir_path: Path, prefix: str = "", depth: int = 0):
            """
            Recursive helper to build tree lines.
            """
            # stop recursing once we hit the user-defined max depth
            if depth >= max_depth:
                return

            try:
                # FIX: replaced invalid 'interdir()' with 'iterdir()'
                # list directory entries, filter out ignored names,
                # sort folders first then files alphabetically
                entries = sorted(
                    [e for e in dir_path.iterdir() if e.name not in ignore_patterns],
                    key=lambda e: (e.is_file(), e.name.lower()),
                )
            except PermissionError:
                # if we lack permission to read a directory, skip it gracefully
                return

            for i, entry in enumerate(entries):
                # determine if this is the last child to use the correct corner character
                is_last = i == len(entries) - 1
                connector = "└── " if is_last else "├── "
                # append the file or folder name; append trailing slash for folders
                lines.append(prefix + connector + entry.name + ("/" if entry.is_dir() else ""))

                if entry.is_dir():
                    # choose the indentation string: empty if last child, vertical bar if not
                    extension = "    " if is_last else "│   "
                    # recurse into subdirectory with increased indentation and depth
                    _tree(entry, prefix + extension, depth + 1)

        # kick off recursion from the repository root
        _tree(self.repo_path)
        # join all collected lines into a single ASCII tree string
        return "\n".join(lines)

    def _has_tests(self) -> bool:
        """
        Check if the repository contains test files or directories.
        """
        # common directory names where tests live
        test_dirs = ["tests", "test", "spec", "__tests__"]
        for td in test_dirs:
            # if any of those directories exists, we immediately know tests are present
            if (self.repo_path / td).is_dir():
                return True

        # common filename patterns for test files (Python, JS/TS)
        test_patterns = [r"test_.*\.py$", r".*_test\.py$", r".*\.spec\.(js|ts)$"]
        for pattern in test_patterns:
            # search recursively; if at least one file matches a pattern, return True
            if any(re.search(pattern, p.name) for p in self.repo_path.rglob("*") if p.is_file()):
                return True

        return False

    def _detect_test_framework(self) -> Optional[str]:
        """
        Identify the test framework used in the project.
        """
        # grab all top-level files to avoid deep recursion for framework detection
        files = list(self.repo_path.iterdir()) if self.repo_path.is_dir() else []
        names = {f.name for f in files}

        # Python pytest ecosystem leaves well-known marker files
        if "pytest.ini" in names or "conftest.py" in names:
            return "pytest"
        # also detect pytest if there is a conftest.py nested inside tests/
        if (self.repo_path / "tests" / "conftest.py").exists():
            return "pytest"
        # fallback: if it is a Python project with a tests directory, assume pytest
        python_manifests = {"requirements.txt", "pyproject.toml", "setup.py", "setup.cfg"}
        if any(m in names for m in python_manifests) and (self.repo_path / "tests").is_dir():
            return "pytest"
        # JavaScript / TypeScript
        if "jest.config.js" in names or "jest.config.ts" in names:
            return "jest"
        if "vitest.config.ts" in names or "vitest.config.js" in names:
            return "vitest"
        # Java Maven / Gradle
        if (self.repo_path / "pom.xml").exists():
            return "JUnit (Maven)"
        if (self.repo_path / "build.gradle").exists() or (self.repo_path / "build.gradle.kts").exists():
            return "JUnit (Gradle)"
        # Go and Rust have built-in test commands rather than separate frameworks
        if (self.repo_path / "go.mod").exists():
            return "go test"
        if (self.repo_path / "Cargo.toml").exists():
            return "cargo test"

        return None

    def _has_docker(self) -> bool:
        """
        Check for the presence of Docker-related files.
        """
        # only two common indicators are checked at top-level
        return (self.repo_path / "Dockerfile").exists() or (self.repo_path / "docker-compose.yml").exists()

    def _has_ci(self) -> bool:
        """
        Detect the presence of CI/CD configuration files.
        """
        # list of known CI config paths (folders or files)
        ci_paths = [".github/workflows", ".gitlab-ci.yml", ".circleci", "azure-pipelines.yml", "Jenkinsfile"]
        for ci in ci_paths:
            if (self.repo_path / ci).exists():
                return True

        return False

    def _detect_ci_platform(self) -> Optional[str]:
        """
        Determine which CI/CD platform is configured.
        """
        # each check is ordered from most common to least common
        if (self.repo_path / ".github" / "workflows").is_dir():
            return "GitHub Actions"
        if (self.repo_path / ".gitlab-ci.yml").exists():
            return "GitLab CI"
        if (self.repo_path / ".circleci").exists():
            return "CircleCI"
        if (self.repo_path / "azure-pipelines.yml").exists():
            return "Azure Pipelines"
        if (self.repo_path / "Jenkinsfile").exists():
            return "Jenkins"

        return None

    def _detect_license(self) -> Optional[str]:
        """
        Read the license file and identify the license type.
        """
        # iterate top-level files only; licenses are rarely nested
        for f in self.repo_path.iterdir():
            if f.is_file() and f.name.lower().startswith("license"):
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    # simple substring heuristics to guess the license family
                    if "MIT" in content:
                        return "MIT"
                    if "Apache" in content:
                        return "Apache-2.0"
                    if "GPL" in content:
                        return "GPL"
                    if "BSD" in content:
                        return "BSD"
                    if "All rights reserved" in content or "PROHIBITED ACTIVITIES" in content:
                        return "Proprietary (All Rights Reserved)"
                    # if no known keyword found, fallback to the filename itself
                    return f.name
                except Exception:
                    # if reading fails, at least return the filename so it is not empty
                    return f.name

        return None

    def _get_remote_url(self) -> Optional[str]:
        """
        Return the origin remote URL from git configuration.
        """
        # verify we successfully opened a git repo earlier and it has remotes
        if self.git_repo and self.git_repo.remotes:
            try:
                # 'origin' is the conventional default remote name
                return self.git_repo.remotes.origin.url
            except Exception:
                return None

        return None

    def _get_default_branch(self) -> Optional[str]:
        """
        Get the currently active git branch name.
        """
        if self.git_repo:
            try:
                # in a normal checkout this returns the branch HEAD points to
                return self.git_repo.active_branch.name
            except Exception:
                pass

        return None

    def _detect_package_manager(self) -> Optional[str]:
        """
        Identify the package manager based on manifest files.
        """
        # build a set of top-level filenames for O(1) lookups
        files = {f.name for f in self.repo_path.iterdir() if f.is_file()}

        # map known manifest files to their corresponding ecosystem
        if "requirements.txt" in files or "pyproject.toml" in files or "setup.py" in files:
            return "pip"
        if "package.json" in files:
            return "npm/yarn/pnpm"
        if "Cargo.toml" in files:
            return "cargo"
        if "go.mod" in files:
            return "go mod"
        if "pom.xml" in files:
            return "Maven"
        if "build.gradle" in files or "build.gradle.kts" in files:
            return "Gradle"
        if "Gemfile" in files:
            return "bundler"

        return None

    def _get_install_command(self) -> Optional[str]:
        """
        Return the standard install command for the detected package manager.
        """
        pm = self._detect_package_manager()
        # map each package manager to its idiomatic install/build command
        commands = {
            "pip": "pip install -r requirements.txt",
            "npm/yarn/pnpm": "npm install",
            "cargo": "cargo build",
            "go mod": "go mod download",
            "Maven": "mvn install",
            "Gradle": "gradle build",
            "bundler": "bundle install",
        }

        return commands.get(pm)

    def _get_description(self, html_meta: Dict[str, str] = None) -> Optional[str]:
        """
        Extract a project description from common manifest files or existing README.
        Tries multiple sources in order of reliability.
        """
        # source 1: pyproject.toml [project] description field
        pp = self.repo_path / "pyproject.toml"
        if pp.exists():
            try:
                content = pp.read_text(encoding="utf-8", errors="ignore")
                # simple regex to grab description = "..." or description = '...'
                m = re.search(r'^description\s*=\s*["\'](.+?)["\']', content, re.MULTILINE)
                if m:
                    return m.group(1)
            except Exception:
                pass

        # source 2: package.json description field
        pj = self.repo_path / "package.json"
        if pj.exists():
            try:
                pkg = json.loads(pj.read_text())
                if pkg.get("description"):
                    return pkg["description"]
            except Exception:
                pass

        # source 3: first paragraph of existing README.md (skip the title line)
        readme = self.repo_path / "README.md"
        if readme.exists():
            try:
                text = readme.read_text(encoding="utf-8", errors="ignore")
                lines = text.splitlines()
                for line in lines[1:]:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        return stripped.lstrip("> ").strip()
            except Exception:
                pass

        # source 4: module docstring from __init__.py
        init = self.repo_path / "src" / "__init__.py"
        if not init.exists():
            init = self.repo_path / "__init__.py"
        if init.exists():
            try:
                content = init.read_text(encoding="utf-8", errors="ignore")
                m = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if m:
                    doc = m.group(1).strip().splitlines()[0]
                    return doc
            except Exception:
                pass

        # source 5: HTML meta description (for static websites / portfolios)
        if html_meta and html_meta.get("description"):
            return html_meta["description"]

        return None

    def _extract_html_meta(self) -> Dict[str, str]:
        """
        Parse index.html (if present) to extract <title> and <meta name="description">.
        Used to auto-fill description for static websites and portfolios.
        """
        index = self.repo_path / "index.html"
        if not index.exists():
            return {}
        try:
            content = index.read_text(encoding="utf-8", errors="ignore")
            result: Dict[str, str] = {}
            # extract <title> content (non-greedy, case-insensitive)
            title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
            if title_match:
                result["title"] = re.sub(r"\s+", " ", title_match.group(1).strip())
            # extract <meta name="description" content="...">
            meta_match = re.search(
                r'<meta[^>]*?name=["\']description["\'][^>]*?content=["\'](.*?)["\']',
                content,
                re.IGNORECASE | re.DOTALL,
            )
            if meta_match:
                result["description"] = meta_match.group(1).strip()
            else:
                # try reversed attribute order: content="..." name="description"
                meta_match = re.search(
                    r'<meta[^>]*?content=["\'](.*?)["\'][^>]*?name=["\']description["\']',
                    content,
                    re.IGNORECASE | re.DOTALL,
                )
                if meta_match:
                    result["description"] = meta_match.group(1).strip()
            return result
        except Exception:
            return {}

    def _is_website(self) -> bool:
        """
        Return True if the project looks like a static website (has index.html).
        """
        return (self.repo_path / "index.html").exists()

    def _has_screenshots_dir(self) -> bool:
        """
        Detect common directories that might contain screenshots or preview images.
        """
        candidates = ["images", "img", "assets", "screenshots", "demo", "preview"]
        for c in candidates:
            d = self.repo_path / c
            if d.is_dir():
                # verify the directory actually contains image-like files
                for f in d.iterdir():
                    if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}:
                        return True
        return False

    def _find_entry_points(self) -> Optional[List[str]]:
        """
        Discover project entry points from common conventions.
        """
        entries = []

        # common Python entry points
        if (self.repo_path / "main.py").exists():
            entries.append("main.py")
        if (self.repo_path / "src" / "main.py").exists():
            entries.append("src/main.py")

        # Node.js entry points declared inside package.json
        if (self.repo_path / "package.json").exists():
            try:
                pkg = json.loads((self.repo_path / "package.json").read_text())
                # "main" is the standard CommonJS entry
                if "main" in pkg:
                    entries.append(pkg["main"])
                # "bin" is used for CLI packages
                if "bin" in pkg:
                    entries.append(str(pkg["bin"]))
            except Exception:
                # if package.json is malformed, just ignore it
                pass

        # static website entry point
        if (self.repo_path / "index.html").exists():
            entries.append("index.html")

        # return None instead of an empty list so templates can easily check with 'if entry_points'
        return entries if entries else None

    def _get_features(self) -> List[str]:
        """
        Build a human-readable feature list from everything detected in the repo.
        """
        feats: List[str] = []
        langs = self._detect_languages()
        if langs:
            top = max(langs, key=langs.get)
            feats.append(f"Built primarily with {top}")
        if self._has_tests():
            tf = self._detect_test_framework()
            label = f" ({tf})" if tf else ""
            feats.append(f"Test suite included{label}")
        if self._has_docker():
            feats.append("Docker support")
        if self._has_ci():
            cp = self._detect_ci_platform()
            label = f" via {cp}" if cp else ""
            feats.append(f"CI/CD configured{label}")
        if self._is_website():
            feats.append("Static website / portfolio")
        if self._has_screenshots_dir():
            feats.append("Preview screenshots available")
        ep = self._find_entry_points()
        if ep:
            feats.append(f"Entry point{'s' if len(ep) > 1 else ''}: {', '.join(ep)}")
        lic = self._detect_license()
        if lic:
            feats.append(f"Licensed under {lic}")
        pm = self._detect_package_manager()
        if pm:
            feats.append(f"Package manager: {pm}")
        return feats

    def _get_prerequisites(self) -> Optional[List[str]]:
        """
        Guess runtime prerequisites from the detected package manager / language.
        """
        pm = self._detect_package_manager()
        if not pm:
            if self._is_website():
                return ["Any modern web browser"]
            return None
        prereqs: List[str] = []
        if pm in ("pip",):
            prereqs.append("Python 3.9+")
            if (self.repo_path / "requirements.txt").exists():
                prereqs.append("pip")
        elif pm == "npm/yarn/pnpm":
            prereqs.append("Node.js 18+")
            prereqs.append("npm (or yarn / pnpm)")
        elif pm == "cargo":
            prereqs.append("Rust toolchain (cargo)")
        elif pm == "go mod":
            prereqs.append("Go 1.21+")
        elif pm in ("Maven", "Gradle"):
            prereqs.append("JDK 17+")
            prereqs.append(pm.lower())
        elif pm == "bundler":
            prereqs.append("Ruby 3.0+")
            prereqs.append("Bundler")
        return prereqs if prereqs else None
