# Tool Usage Notes

Tool signatures are provided automatically via function calling.
This file documents non-obvious constraints and usage patterns.

## exec — Safety Limits

- Commands have a configurable timeout (default 60s)
- Dangerous commands are blocked (rm -rf, format, dd, shutdown, etc.)
- Output is truncated at 10,000 characters
- `restrictToWorkspace` config can limit file access to the workspace
- `allowedDirs` can further constrain access to a specific allowlist of directories

## cron — Scheduled Reminders

- Please refer to cron skill for usage.

## image_generate — Image Generation

- Uses the configured image model (agents.defaults.imageModel)
- Returns local file paths; send them to the user via the `message` tool with `media`
