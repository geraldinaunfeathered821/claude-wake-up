# Claude Wake-Up

Telegram bot that remotely launches Claude Code sessions in Zellij.

## First Time?

Run `/setup` to start the interactive setup wizard. It will check dependencies, configure `.env`, and optionally register the systemd service.

## Project Structure

```
bot.py                  — Single-file bot (all logic)
claude-wake-up.service  — systemd user unit
.env.example            — Environment variable template
pyproject.toml          — uv/Python dependencies
.claude/commands/setup.md — /setup slash command
```

## Bot Commands (Telegram)

- `/start` — Usage help
- `/wake <path>` — Launch Claude in a new Zellij tab (session auto-created if needed)
- `/sessions` — List active Zellij sessions
- `/status` — Bot health check

## Running

```bash
uv run python bot.py
```
