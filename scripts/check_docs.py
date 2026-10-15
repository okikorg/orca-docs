#!/usr/bin/env python3
"""Check the docs' navigation, links, Python syntax, version pins, route coverage, token price
wording, and plan facts.

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


# A price, rate, minimum, credit, fee, machine size, idle time, included
# hours or session count typed as a number.
PLAN_NUMBER = (
    r"\d+ vCPU|\d+ GiB of (?:memory|disk)"
    r"|\$\d[\d,.]* (?:a|an|per) (?:month|hour)|\| \$\d"
    r"|\$\d[\d,.]* (?:of (?:Orca )?credit|minimum|pack)|(?:below|under|at least) \**\$\d"
    r"|\d+(?:\.\d+)?% of the price|(?:paused after|used for) \d+ minutes"
    r"|\d[\d,]* hours of machine time|runs \d+ sessions? at once"
)


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
        for index, code in enumerate(re.findall(r"^```python[^\n]*\n(.*?)^```", text, re.S | re.M), 1):
            try:
                ast.parse(code)
            except SyntaxError as error:
                errors.append(f"{name}: Python block {index}: {error}")
        # The token price reads "OpenRouter's price plus their fee", linked to
        # the pricing page, which states the percentage (orca-design plan-facts,
        # P2-d and P2-e).
        for wrong in re.findall(r"\bplus its\b(?:[^.|\n]|\.\d)*?\bfee|\blist price\b|\b5\.5%", text, re.I):
            errors.append(f"{name}: token price worded \"{wrong}\"; say OpenRouter's price plus their fee")
        # Plan numbers are the pricing page's, built from the server
        # (orca-design plan-facts, D3e): the docs state rules and link there.
        if not name.startswith(("orcacode/", "reference/")):
            for number in re.findall(PLAN_NUMBER, text, re.I):
                errors.append(f"{name}: plan number \"{number}\"; link the pricing page instead")
    all_text = "\n".join(texts.values())
    for pin in (f"openai=={versions['python']}", f"openai@{versions['typescript']}"):
        if pin not in texts.get("build-with-the-api", ""):
            errors.append(f"Build with the API is missing client pin: {pin}")
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
          "navigation, local links, Python syntax, client pins, token price wording, and plan facts.")


if __name__ == "__main__":
    main()
