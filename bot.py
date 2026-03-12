"""Claude Wake-Up: Telegram bot to remotely launch Claude Code sessions in Zellij."""

import asyncio
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

URL_PATTERN = re.compile(r"https://claude\.ai/code/session_[\w]+")

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USERS: set[int] = {
    int(uid.strip())
    for uid in os.environ.get("TELEGRAM_ALLOWED_USERS", "").split(",")
    if uid.strip()
}
ZELLIJ_SESSION = os.environ.get("ZELLIJ_TARGET_SESSION", "").strip()
if not ZELLIJ_SESSION:
    raise RuntimeError("ZELLIJ_TARGET_SESSION must be set in .env")
SKIP_PERMISSIONS = os.environ.get("DANGEROUSLY_SKIP_PERMISSIONS", "false").strip().lower() == "true"
IS_MACOS = sys.platform == "darwin"


# --- Tool resolution (cached at startup) ---

def _require_tool(name: str, label: str | None = None) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"{label or name} not found in PATH")
    return path


ZELLIJ_PATH = _require_tool("zellij")
CLAUDE_PATH = _require_tool("claude")
SCRIPT_PATH = _require_tool("script", "BSD script" if IS_MACOS else "script (util-linux)")


# --- Auth ---

def is_authorized(user_id: int) -> bool:
    if not ALLOWED_USERS:
        return False
    return user_id in ALLOWED_USERS


# --- Background task tracking ---

_background_tasks: set[asyncio.Task] = set()


def _track_task(coro) -> asyncio.Task:
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


# --- Zellij helpers ---

async def _list_all_sessions() -> tuple[list[str], list[str]]:
    """Return (active, dead) session name lists."""
    proc = await asyncio.create_subprocess_exec(
        ZELLIJ_PATH, "list-sessions", "--no-formatting",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    if proc.returncode != 0:
        return [], []
    active, dead = [], []
    for line in stdout.decode().splitlines():
        line = line.strip()
        if not line:
            continue
        name = line.split()[0]
        if "EXITED" in line:
            dead.append(name)
        else:
            active.append(name)
    return active, dead


async def get_zellij_sessions() -> list[str]:
    """Return names of active (non-EXITED) Zellij sessions."""
    active, _ = await _list_all_sessions()
    return active


async def kill_dead_session(session_name: str) -> None:
    """Kill an EXITED Zellij session so the name can be reused."""
    proc = await asyncio.create_subprocess_exec(
        ZELLIJ_PATH, "delete-session", session_name,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.communicate()


async def create_zellij_session(session_name: str) -> bool:
    """Create a new Zellij session headlessly using script for PTY."""
    # Clean up dead session with the same name first
    _, dead = await _list_all_sessions()
    if session_name in dead:
        await kill_dead_session(session_name)

    if IS_MACOS:
        cmd = [SCRIPT_PATH, "-q", "/dev/null", ZELLIJ_PATH, "-s", session_name]
    else:
        cmd = [SCRIPT_PATH, "-qfc", f"{ZELLIJ_PATH} -s {session_name}", "/dev/null"]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
        start_new_session=True,
    )
    _track_task(proc.wait())

    for _ in range(10):
        await asyncio.sleep(0.5)
        if session_name in await get_zellij_sessions():
            return True
    return False


def generate_layout_kdl(capture_file: str) -> str:
    if IS_MACOS:
        # BSD script: script -q -F file command [args...]
        args_parts = ["-q", "-F", capture_file, CLAUDE_PATH]
        if SKIP_PERMISSIONS:
            args_parts.append("--dangerously-skip-permissions")
    else:
        # util-linux script: script -qf -c "command" file
        cmd = f"{CLAUDE_PATH} --dangerously-skip-permissions" if SKIP_PERMISSIONS else CLAUDE_PATH
        args_parts = ["-qf", "-c", cmd, capture_file]

    args_str = " ".join(f'"{a}"' for a in args_parts)
    return (
        "layout {\n"
        f'    pane command="{SCRIPT_PATH}" {{\n'
        f'        args {args_str}\n'
        "    }\n"
        "}\n"
    )


async def poll_for_url(
    capture_file: str, timeout: float = 60.0, interval: float = 0.5
) -> str | None:
    """Poll the capture file for a Claude remote control URL."""
    elapsed = 0.0
    while elapsed < timeout:
        try:
            content = Path(capture_file).read_text(errors="replace")
            match = URL_PATTERN.search(content)
            if match:
                return match.group(0)
        except FileNotFoundError:
            pass
        await asyncio.sleep(interval)
        elapsed += interval
    return None


async def wake_claude(path: str, capture_file: str, session: str) -> tuple[bool, str]:
    layout_content = generate_layout_kdl(capture_file)
    layout_path = Path(f"/tmp/claude-wake-{uuid4().hex[:8]}.kdl")
    layout_path.write_text(layout_content)

    tab_name = f"claude:{Path(path).name}-{uuid4().hex[:4]}"
    cmd = [
        ZELLIJ_PATH, "-s", session, "action", "new-tab",
        "--cwd", path,
        "--name", tab_name,
        "--layout", str(layout_path),
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            return False, f"zellij failed (rc={proc.returncode}): {stderr.decode().strip()}"
        return True, f"Claude started in tab '{tab_name}' on session '{session}'"
    finally:
        layout_path.unlink(missing_ok=True)


# --- Command handlers ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update.effective_user.id):
        return
    await update.message.reply_text(
        "Claude Wake-Up Bot\n\n"
        "Commands:\n"
        "/wake <path> — Launch Claude in Zellij\n"
        "/sessions — List active Zellij sessions\n"
        "/status — Bot status"
    )


async def cmd_wake(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        logger.warning("Unauthorized /wake from user %d", user_id)
        return

    if not context.args:
        await update.message.reply_text("Usage: /wake <path>")
        return

    raw_path = context.args[0]

    # Resolve and validate path
    resolved = Path(raw_path).expanduser().resolve()
    if not resolved.is_dir():
        reason = "Not a directory" if resolved.exists() else "Path not found"
        await update.message.reply_text(f"{reason}: {resolved}")
        return

    # Resolve Zellij session — create if it doesn't exist
    sessions = await get_zellij_sessions()
    if ZELLIJ_SESSION not in sessions:
        await update.message.reply_text(
            f"Session '{ZELLIJ_SESSION}' not found. Creating..."
        )
        if not await create_zellij_session(ZELLIJ_SESSION):
            await update.message.reply_text(
                f"Failed to create Zellij session '{ZELLIJ_SESSION}'"
            )
            return

    # Launch
    capture_file = f"/tmp/claude-wake-{uuid4().hex[:8]}.capture"
    await update.message.reply_text(f"Launching Claude in {resolved}...")
    ok, result = await wake_claude(str(resolved), capture_file, ZELLIJ_SESSION)
    msg = await update.message.reply_text(result)

    if ok:
        _track_task(_poll_and_reply(msg, capture_file))


async def _poll_and_reply(message, capture_file: str) -> None:
    try:
        url = await poll_for_url(capture_file)
        if url:
            await message.reply_text(f"Remote: {url}")
        else:
            await message.reply_text("Remote control URL not detected.")
    except Exception:
        logger.exception("Failed to poll for remote URL")
    finally:
        Path(capture_file).unlink(missing_ok=True)


async def cmd_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update.effective_user.id):
        return

    sessions = await get_zellij_sessions()
    if not sessions:
        await update.message.reply_text("No active Zellij sessions.")
        return

    lines = "\n".join(f"  • {s}" for s in sessions)
    await update.message.reply_text(f"Active Zellij sessions:\n{lines}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update.effective_user.id):
        return

    sessions = await get_zellij_sessions()
    await update.message.reply_text(
        f"Bot: running\n"
        f"Zellij: {ZELLIJ_PATH}\n"
        f"Claude: {CLAUDE_PATH}\n"
        f"Target session: {ZELLIJ_SESSION}\n"
        f"Active sessions: {len(sessions)}"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling update:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(f"Error: {context.error}")


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("wake", cmd_wake))
    app.add_handler(CommandHandler("sessions", cmd_sessions))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_error_handler(error_handler)

    logger.info("Bot starting... (allowed users: %s)", ALLOWED_USERS)
    app.run_polling()


if __name__ == "__main__":
    main()
