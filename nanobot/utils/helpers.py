"""Utility functions for nanobot."""

import re
from datetime import datetime
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_data_path() -> Path:
    """~/.nanobot data directory."""
    return ensure_dir(Path.home() / ".nanobot")


def get_workspace_path(workspace: str | None = None) -> Path:
    """Resolve and ensure workspace path. Defaults to ~/.nanobot/workspace."""
    path = Path(workspace).expanduser() if workspace else Path.home() / ".nanobot" / "workspace"
    return ensure_dir(path)


def timestamp() -> str:
    """Current ISO timestamp."""
    return datetime.now().isoformat()


_UNSAFE_CHARS = re.compile(r'[<>:"/\\|?*]')

def safe_filename(name: str) -> str:
    """Replace unsafe path characters with underscores."""
    return _UNSAFE_CHARS.sub("_", name).strip()


def check_workspace_migration(workspace: Path) -> tuple[bool, Path | None]:
    """Check if workspace path has changed and old workspace has data.

    Returns:
        (needs_migration, old_workspace_path) - True if migration recommended
    """
    import json

    workspace_record = get_data_path() / "workspace_record.json"
    current_path = str(workspace.resolve())

    # Check if we have a previous workspace record
    if not workspace_record.exists():
        # First time setup or fresh install
        workspace_record.write_text(json.dumps({"path": current_path}), encoding="utf-8")
        return (False, None)

    try:
        record = json.loads(workspace_record.read_text(encoding="utf-8"))
        old_path = record.get("path")

        if not old_path or old_path == current_path:
            # Same workspace, no migration needed
            return (False, None)

        # Workspace path changed!
        old_workspace = Path(old_path)

        # Check if old workspace exists and has important files
        if not old_workspace.exists():
            # Old workspace doesn't exist anymore, safe to update record
            workspace_record.write_text(json.dumps({"path": current_path}), encoding="utf-8")
            return (False, None)

        # Check if old workspace has any user-modified files
        important_files = ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "HEARTBEAT.md"]
        has_data = False

        for fname in important_files:
            old_file = old_workspace / fname
            if old_file.exists():
                # Check if it's been modified (not the default template)
                try:
                    size = old_file.stat().st_size
                    # If file size is different from tiny defaults, likely has user data
                    if size > 500:  # Templates are usually < 500 bytes when fresh
                        has_data = True
                        break
                except Exception:
                    pass

        # Check memory directory
        old_memory = old_workspace / "memory" / "MEMORY.md"
        if old_memory.exists():
            try:
                content = old_memory.read_text(encoding="utf-8")
                # Check if memory has been customized (more than template default)
                if len(content) > 300:
                    has_data = True
            except Exception:
                pass

        if has_data:
            return (True, old_workspace)
        else:
            # Old workspace exists but has no important data, safe to switch
            workspace_record.write_text(json.dumps({"path": current_path}), encoding="utf-8")
            return (False, None)

    except Exception:
        # Error reading record, play it safe
        return (False, None)


def migrate_workspace_data(old_workspace: Path, new_workspace: Path, silent: bool = False) -> bool:
    """Migrate data from old workspace to new workspace.

    Returns:
        True if migration successful, False otherwise
    """
    import shutil
    from rich.console import Console

    console = Console()

    try:
        if not old_workspace.exists():
            return False

        # Create new workspace if it doesn't exist
        new_workspace.mkdir(parents=True, exist_ok=True)

        # Files to migrate
        important_files = ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "HEARTBEAT.md"]
        migrated = []

        for fname in important_files:
            old_file = old_workspace / fname
            new_file = new_workspace / fname

            if old_file.exists():
                # Only copy if new file doesn't exist or is a template (small)
                if not new_file.exists() or new_file.stat().st_size < 500:
                    shutil.copy2(old_file, new_file)
                    migrated.append(fname)

        # Migrate memory directory
        old_memory = old_workspace / "memory"
        new_memory = new_workspace / "memory"

        if old_memory.exists():
            new_memory.mkdir(exist_ok=True)
            for mfile in old_memory.glob("*.md"):
                new_mfile = new_memory / mfile.name
                if not new_mfile.exists() or new_mfile.stat().st_size < 300:
                    shutil.copy2(mfile, new_mfile)
                    migrated.append(f"memory/{mfile.name}")

        # Migrate skills directory
        old_skills = old_workspace / "skills"
        new_skills = new_workspace / "skills"

        if old_skills.exists() and old_skills.is_dir():
            new_skills.mkdir(exist_ok=True)
            # Copy entire skills directory structure
            for item in old_skills.iterdir():
                if item.is_dir():
                    dest = new_skills / item.name
                    if dest.exists():
                        # Merge directories
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copytree(item, dest)
                    migrated.append(f"skills/{item.name}/")
                elif item.is_file():
                    shutil.copy2(item, new_skills / item.name)
                    migrated.append(f"skills/{item.name}")

        # Update workspace record
        import json
        workspace_record = get_data_path() / "workspace_record.json"
        workspace_record.write_text(json.dumps({"path": str(new_workspace.resolve())}), encoding="utf-8")

        if migrated and not silent:
            console.print(f"[green]✓[/green] Migrated {len(migrated)} items from old workspace")
            for item in migrated[:5]:  # Show first 5
                console.print(f"  [dim]• {item}[/dim]")
            if len(migrated) > 5:
                console.print(f"  [dim]• ... and {len(migrated) - 5} more[/dim]")

        return True

    except Exception as e:
        if not silent:
            console.print(f"[yellow]Warning: Migration partially failed: {e}[/yellow]")
        return False


def sync_workspace_templates(workspace: Path, silent: bool = False) -> list[str]:
    """Sync bundled templates to workspace. Only creates missing files."""
    from importlib.resources import files as pkg_files
    try:
        tpl = pkg_files("nanobot") / "templates"
    except Exception:
        return []
    if not tpl.is_dir():
        return []

    added: list[str] = []

    def _write(src, dest: Path):
        if dest.exists():
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(src.read_text(encoding="utf-8") if src else "", encoding="utf-8")
        added.append(str(dest.relative_to(workspace)))

    for item in tpl.iterdir():
        if item.name.endswith(".md"):
            _write(item, workspace / item.name)
    _write(tpl / "memory" / "MEMORY.md", workspace / "memory" / "MEMORY.md")
    _write(None, workspace / "memory" / "HISTORY.md")
    (workspace / "skills").mkdir(exist_ok=True)

    if added and not silent:
        from rich.console import Console
        for name in added:
            Console().print(f"  [dim]Created {name}[/dim]")
    return added
