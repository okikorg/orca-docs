#!/usr/bin/env python3
"""Check the docs' navigation, links, Python syntax, version pins, and route coverage.

The docs describe the Orca server's API, so the version pins and the route
inventory come from the server's contract: a checkout of okikorg/orca-agent-server
at ORCA_SERVER_DIR (default ../orca-agent-server).
"""
import ast
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT
SERVER = Path(os.environ.get("ORCA_SERVER_DIR", ROOT.parent / "orca-agent-server")).resolve()


def main():
    config = json.loads((SITE / "docs.json").read_text())
    versions = json.loads((SERVER / "contract/versions.json").read_text())
    errors = []
    pages = {str(p.relative_to(SITE).with_suffix("")): p for p in SITE.rglob("*.mdx") if "node_modules" not in p.parts}
    texts = {name: path.read_text() for name, path in pages.items()}
    navigation = []

    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "pages":
                    navigation.extend(p for p in child if isinstance(p, str))
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(config["navigation"])
    for name in navigation:
        if name not in pages:
            errors.append(f"Navigation page missing: {name}")
    for name in pages:
        if name not in navigation:
            errors.append(f"Page absent from navigation: {name}")
    for name, text in texts.items():
        frontmatter = re.match(r"^---\n(.*?)\n---", text, re.S)
        if not frontmatter or not all(
            re.search(rf"^{key}: .+", frontmatter[1], re.M)
            for key in ("title", "description")
        ):
            errors.append(f"{name}: missing title/description frontmatter")
        for link in re.findall(r"\]\((/[^)]+)\)|(?:href|src)=\"(/[^\"]+)\"", text):
            target = (link[0] or link[1]).split("#")[0].split("?")[0].lstrip("/")
            if target and target not in pages and not (SITE / target).is_file():
                errors.append(f"{name}: broken local link /{target}")
        for index, code in enumerate(re.findall(r"```python[^\n]*\n(.*?)```", text, re.S), 1):
            try:
                ast.parse(code)
            except SyntaxError as error:
                errors.append(f"{name}: Python block {index}: {error}")
    all_text = "\n".join(texts.values())
    for pin in (f"openai=={versions['python']}", f"openai@{versions['typescript']}"):
        if pin not in texts.get("quickstart", ""):
            errors.append(f"Quickstart is missing client pin: {pin}")
    endpoints = json.loads((SERVER / "contract/endpoints.json").read_text())
    reference = "\n".join(text for name, text in texts.items() if name.startswith("reference/"))
    count = 0
    for group in endpoints.values():
        for endpoint in group:
            count += 1
            method, path = endpoint["method"], endpoint["path"]
            if f"| `{method}` | `{path}` |" not in reference:
                errors.append(f"Missing reference route: {method} {path}")
    upstream = "https://developers.openai.com/api/docs/guides/agents-api/quickstart/"
    if upstream not in all_text or upstream not in json.dumps(config):
        errors.append("Missing upstream quickstart in content or site navigation")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Public docs checks passed: {len(pages)} pages, {count} inventoried routes, "
          "navigation, local links, Python syntax, and client pins.")


if __name__ == "__main__":
    main()
