#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


class ReadmeGenerator:
    """
    Generates a README.md file from repository metadata using Jinja2 templates.
    """

    def __init__(self, template_dir: Path):
        """
        Initialize the generator with the directory containing Jinja2 templates.

        Args:
            template_dir: Path to the folder holding .md.j2 templates.
        """
        self.template_dir = Path(template_dir).resolve()

        # set up Jinja2 environment with autoescaping for security
        # autoescape is enabled because we render markdown that may contain user content
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self, data: Dict[str, Any], template_name: str = "full.md.j2") -> str:
        """
        Render a README string from the provided metadata and template.

        Args:
            data: dictionary returned by RepoAnalyzer.analyze().
            template_name: filename of the Jinja2 template to use.

        Returns:
            Rendered markdown as a single string.
        """
        # load the requested template from disk
        template = self.env.get_template(template_name)

        # pass the entire metadata dictionary to the template context
        # templates can access every key directly (e.g. {{ primary_language }})
        return template.render(**data)

    def write(self, content: str, output_path: Path) -> None:
        """
        Write the rendered README to disk.

        Args:
            content: the rendered markdown string.
            output_path: destination file path (usually ./README.md).
        """
        # resolve to absolute path to avoid relative path confusion
        output_path = Path(output_path).resolve()

        # use utf-8 encoding to support all characters (emojis, unicode badges, etc.)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        # optional: print confirmation for CLI feedback
        print(f"README written to {output_path}")
