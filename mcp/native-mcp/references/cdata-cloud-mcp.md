# CData Cloud MCP Server

CData provides a cloud-hosted MCP server at `https://mcp.cloud.cdata.com/mcp`
that exposes enterprise data sources (databases, SaaS APIs, warehouses) as MCP
tools. Useful for connecting Hermes to business data without writing custom
integrations.

## Configuration

```yaml
mcp_servers:
  cdata:
    url: https://mcp.cloud.cdata.com/mcp
    timeout: 120
    connect_timeout: 60
```

## Authentication

CData's cloud MCP endpoint typically requires an API token or OAuth. If tool
discovery returns empty or the connection fails after restart, add a Bearer
token:

```yaml
mcp_servers:
  cdata:
    url: https://mcp.cloud.cdata.com/mcp
    headers:
      Authorization: "Bearer <your-cdata-token>"
    timeout: 120
    connect_timeout: 60
```

The token is obtained from the CData Connect Cloud dashboard
(https://cloud.cdata.com) under **Settings → API Tokens** or via the
connected-app OAuth flow, depending on the data source.

## Tool Naming

Tools are registered as `mcp_cdata_<tool_name>` (hyphens/dots in tool names
replaced with underscores). Discover available tools after restart by checking
`hermes mcp list` or looking for `mcp_cdata_*` in `hermes tools list`.

## Common Data Sources

CData Connect Cloud supports 250+ connectors including: Salesforce, HubSpot,
Shopify, Snowflake, BigQuery, PostgreSQL, MySQL, SQL Server, Sage Intacct,
QuickBooks, NetSuite, and more. Each connected data source exposes its own
set of MCP tools (query, insert, update, list tables, etc.).

## Adding via execute_code (when CLI shebang is broken)

See "Pitfall: config.yaml is patch-protected" in the main SKILL.md. The
`execute_code` + PyYAML method works reliably for adding the CData server
when the `hermes` CLI binary can't be executed directly.

## Pitfalls

- **Empty tool list after restart**: Usually means auth is missing or the
  CData account has no data sources connected. Check the CData dashboard
  to verify at least one connector is active.
- **Connection timeout**: CData cloud can take 10-15s to initialize on a
  cold start. The default `connect_timeout: 60` is sufficient; don't lower
  it below 30.
- **Tool call errors mentioning credentials**: Hermes auto-redacts
  credential-like patterns in MCP error messages, so you may see `[REDACTED]`
  instead of the actual token in error output. This is expected behavior.