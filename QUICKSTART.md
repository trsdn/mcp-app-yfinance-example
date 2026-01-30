````markdown
# Quick Start Guide

## Using This Repository

This MCP Apps Stock Server provides stock market data with interactive UI.

### Start the Server

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Start the server
uv run python server.py
```

### VS Code Configuration

The server is configured in `.vscode/mcp.json`:

```json
{
  "servers": {
    "yfinance-http": {
      "type": "sse",
      "url": "http://localhost:3002/sse"
    }
  }
}
```

### Enable MCP Apps in VS Code

```json
{
  "chat.mcp.apps.enabled": true
}
```

## Available AI Customizations

### Skills (`.claude/skills/`)

| Skill | Purpose |
|-------|---------|
| `skill-builder` | Create new skills for Claude/Copilot |
| `git-create-pr` | Create PRs with proper formatting |
| `git-workflow` | Git commit/branch conventions |
| `code-review` | Structured code review process |
| `doc-readme` | README best practices |
| `doc-adr` | Architecture Decision Records |
| `structure-conventions` | Project structure guidance |
| `blueprint-sync` | Sync from blueprint repos |

### Copilot Skills (`.github/skills/`)

| Skill | Purpose |
|-------|---------|
| `mcp-apps` | Build MCP Apps with interactive UI |
| `copilot-skill-builder` | Create Copilot skills |
| `copilot-setup-audit` | Audit Copilot configuration |

### Agents

| Agent | Location | Purpose |
|-------|----------|---------|
| `claude-customization-builder` | `.claude/agents/` | Create Claude customizations |
| `copilot-customization-builder` | `.github/agents/` | Create Copilot customizations |

### Prompts (`.github/prompts/`)

- `/copilot-audit-setup` - Audit Copilot configuration
- `/copilot-new-agent` - Create a new agent
- `/copilot-new-skill` - Create a new skill
- `/copilot-new-prompt` - Create a new prompt

## Common Tasks

### Create a New Skill

Ask: "Create a skill for [purpose]"

Or use the skill-builder skill directly.

### Sync Blueprint Updates

Ask: "sync blueprints" to get latest skills from upstream templates.

### Code Review

Ask: "review this code" to get a structured review.

### Create a PR

Ask: "create a PR" to generate a properly formatted pull request.

## MCP Configuration

Edit `.mcp.json` for MCP server integrations:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Resources

- [MCP Apps SKILL](.github/skills/mcp-apps/SKILL.md) - MCP Apps development
- [Agent Skills Specification](https://agentskills.io/specification)
- [AGENTS.md](AGENTS.md) - Project architecture

````
