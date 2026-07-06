# Orca Docs

Public Mintlify documentation for Orca.

This repository contains customer-facing documentation only: product concepts, quickstarts, CLI usage, SDK usage, and public API references. Internal architecture, deployment plans, design notes, and implementation details stay out of this repo.

## Local preview

```bash
npx mintlify dev
```

## Source of truth

- `api-reference/orca-openapi.yaml` is the public control-plane OpenAPI spec used by SDKs.
- `api-reference/chat-openapi.yaml` is the public chat gateway OpenAPI spec.
- CLI behavior is documented from `https://github.com/okikorg/orca-cli`.
