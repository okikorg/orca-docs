# Orca docs

The source of [docs.orcapods.ai](https://docs.orcapods.ai): one Mintlify site for Orca's customers (orca-design decision 0025). Today it holds the Orca Platform docs, moved from `orca-agent-server/docs/public` with their history. The Orcacode docs join as their own tab after launch; until then they are served at orcapods.ai/orcacode/docs from `orca-harness/docs/external`.

## Preview

```sh
npm ci
npm run dev        # mint dev, at http://localhost:3000
```

## Check

The docs describe the Orca server's API, so they are checked against its contract: the client versions they pin and every route they document.

```sh
ORCA_SERVER_DIR=../orca-agent-server npm run check
npx mint broken-links
```

CI runs both on every pull request. It reads the server's `contract/` through the `ORCA_SERVER_READ_TOKEN` secret, a fine-grained token with read access to `okikorg/orca-agent-server`.

## Rules

- A change to the server's public API or its behaviour comes with a PR here, merged with it.
- Code samples run against a real Orca server before they are published.
- Short sentences, no hype, no em dashes.
