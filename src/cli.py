#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path

# when the package is installed via pip, relative imports work automatically
# when running the script directly with `python src/cli.py`, prepend src/ to the path
if __name__ == "__main__" and __package__ is None:
    import sys

    # insert the repo root so `src.analyzer` resolves correctly
    repo_root = Path(__file__).parent.parent
    sys.path.insert(0, str(repo_root))
    from src.analyzer import RepoAnalyzer
    from src.generator import ReadmeGenerator
else:
    from .analyzer import RepoAnalyzer
    from .generator import ReadmeGenerator


def main() -> int:
    """
    CLI entry point: parse arguments, analyze repo, render README, write to disk.
    
    Returns:
        exit code (0 on success, 1 on error).
    """
    parser = argparse.ArgumentParser(
        description="Auto-generate README.md from repository analysis.",
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to the repository to analyze (default: current directory).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="README.md",
        help="Output file path for the generated README (default: README.md).",
    )
    parser.add_argument(
        "-t",
        "--template",
        default="full.md.j2",
        help="Jinja2 template to use (default: full.md.j2).",
    )
    parser.add_argument(
        "--template-dir",
        default=None,
        help="Directory containing Jinja2 templates (default: built-in templates folder).",
    )

    args = parser.parse_args()

    # resolve paths early so relative inputs behave predictably regardless of cwd
    repo_path = Path(args.repo_path).resolve()
    output_path = Path(args.output).resolve()

    # determine the template directory
    if args.template_dir:
        template_dir = Path(args.template_dir).resolve()
    else:
        # default templates live in a 'templates' folder next to this script
        template_dir = Path(__file__).parent / "templates"

    # validate that the target directory actually exists
    if not repo_path.is_dir():
        print(f"Error: '{repo_path}' is not a valid directory.", file=sys.stderr)
        return 1

    # validate that we can locate the Jinja2 templates
    if not template_dir.is_dir():
        print(f"Error: template directory '{template_dir}' not found.", file=sys.stderr)
        return 1

    # step 1: analyze the repository and collect metadata
    analyzer = RepoAnalyzer(repo_path)
    data = analyzer.analyze()

    # step 2: initialize the generator with the chosen template directory
    generator = ReadmeGenerator(template_dir)

    # step 3: render the README content using the selected template
    try:
        readme = generator.generate(data, template_name=args.template)
    except Exception as exc:
        print(f"Error: failed to render template '{args.template}': {exc}", file=sys.stderr)
        return 1

    # step 4: persist the rendered markdown to the output file
    try:
        generator.write(readme, output_path)
    except Exception as exc:
        print(f"Error: failed to write README to '{output_path}': {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    # propagate the return code to the shell so failed runs are detectable
    sys.exit(main())
