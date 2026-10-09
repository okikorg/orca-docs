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

## Editorial boundary

Publish what an application needs: client setup, the public resource lifecycle, verified API examples, tool security, compatibility limits and troubleshooting. Do not copy architecture reports, deployment diagrams, acceptance logs, storage layout, internal recovery mechanics, fixture credentials or private endpoints. Workspace and output paths and public failure semantics may be documented where a customer needs them to use the API correctly.

The OpenAI Agents API quickstart is the main upstream link: <https://developers.openai.com/api/docs/guides/agents-api/quickstart/>. These guides are the source for Orca-specific setup and behaviour; do not imply OpenAI affiliation or full feature parity.

`style.css` gives the site the voidline look. `docs.json` owns navigation, theme, palette, typography and upstream links. Logos are local SVG assets. No remote tracking scripts and no secrets.

## Rules

- A change to the server's public API or its behaviour comes with a PR here, merged with it.
- Code samples run against a real Orca server before they are published.
- Short sentences, no hype, no em dashes.
