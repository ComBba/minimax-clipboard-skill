#!/usr/bin/env python3
"""
MiniMax Clipboard Image Handler Hook for Claude Code

Handles clipboard image analysis workflow:
- Notification: Detects "Cannot read clipboard" error, saves image, updates clipboard
- UserPromptSubmit: Injects context for MiniMax image analysis
- PostToolUse: Cleans up temporary files after analysis
- SessionEnd: Cleans up remaining files

Usage: python3 hook.py <event_name>
"""

import json
import os
import sys
import time
import subprocess
import shutil
from pathlib import Path
from datetime import datetime


# Get session ID from stdin or generate a new one
def get_session_id(context):
    """Extract session ID from context or environment"""
    session = context.get("session", {})
    session_id = session.get("id", "") or os.environ.get("CLAUDE_SESSION_ID", "")

    # If no session ID, generate a temporary one
    if not session_id:
        session_id = f"temp_{os.getpid()}_{int(time.time())}"

    return session_id


# Configuration
TMP_DIR = Path.home() / ".claude" / "tmp" / "images"
CLIPBOARD_DIR = TMP_DIR / "clipboard"
SESSION_FILE = CLIPBOARD_DIR / ".session_id"
LAST_IMAGE_FILE = CLIPBOARD_DIR / ".last_image"
LOCK_FILE = CLIPBOARD_DIR / ".lock"

# Ensure directories exist
CLIPBOARD_DIR.mkdir(parents=True, exist_ok=True)


def log(message):
    """Log hook activity"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[MiniMax Clipboard Hook {timestamp}] {message}", flush=True)


def acquire_lock():
    """Acquire lock to prevent concurrent execution"""
    try:
        LOCK_FILE.touch(exist_ok=True)
        return True
    except:
        return False


def release_lock():
    """Release lock"""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
        return True
    except:
        return False


def save_clipboard_image(session_id):
    """
    Save clipboard image to session-specific temporary file using pngpaste.
    Returns the file path or None if failed.
    """
    # Create session-specific directory
    session_dir = CLIPBOARD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = session_dir / f"clipboard_{timestamp}.png"

    # Retry logic for race conditions
    for attempt in range(5):
        try:
            result = subprocess.run(
                ["pngpaste", str(filepath)], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0 and filepath.exists():
                file_size = filepath.stat().st_size
                if file_size > 0:
                    log(f"Saved clipboard image: {filepath} ({file_size} bytes)")
                    last_image_path = CLIPBOARD_DIR / f".last_image_{session_id}"
                    last_image_path.write_text(str(filepath))
                    return str(filepath)

        except subprocess.TimeoutExpired:
            log(f"Timeout on attempt {attempt + 1}")
        except FileNotFoundError:
            log("Error: pngpaste not found. Install with: brew install pngpaste")
            return None
        except Exception as e:
            log(f"Error saving clipboard: {e}")

        time.sleep(0.1)  # Wait before retry

    log("Failed to save clipboard image after 5 attempts")
    return None


def copy_to_clipboard(text):
    """Copy text to clipboard"""
    try:
        subprocess.run(["pbcopy"], input=text.encode(), check=True)
        log(f"Copied to clipboard: {text}")
        return True
    except Exception as e:
        log(f"Error copying to clipboard: {e}")
        return False


def cleanup_temp_file(filepath):
    """Safely cleanup a temporary file"""
    try:
        if filepath and Path(filepath).exists():
            # Only delete files in our clipboard directory
            if CLIPBOARD_DIR in Path(filepath).parents or Path(filepath) == Path(
                filepath
            ):
                Path(filepath).unlink()
                log(f"Cleaned up: {filepath}")
                return True
        return False
    except Exception as e:
        log(f"Error cleaning up {filepath}: {e}")
        return False


def cleanup_session_files(session_id):
    """Clean up all files for this session only"""
    try:
        session_dir = CLIPBOARD_DIR / session_id
        if session_dir.exists():
            files = list(session_dir.glob("*.png"))
            count = 0
            for f in files:
                try:
                    f.unlink()
                    count += 1
                except:
                    pass
            if count > 0:
                log(
                    f"Cleaned up {count} temporary image files for session {session_id}"
                )

            # Remove session directory
            try:
                session_dir.rmdir()
            except:
                pass

        # Clean up session-specific last image reference
        session_last_image = CLIPBOARD_DIR / f".last_image_{session_id}"
        if session_last_image.exists():
            session_last_image.unlink()

        return True
    except Exception as e:
        log(f"Error during session cleanup: {e}")
        return False


def handle_notification():
    """
    Handle Notification events.
    Detects "Cannot read clipboard" error and saves image to file.
    """
    log("Processing Notification event")

    # Read context from stdin
    try:
        context = json.load(sys.stdin)
    except json.JSONDecodeError:
        log("Error: Invalid JSON input")
        return

    # Get session ID for isolation
    session_id = get_session_id(context)
    log(f"Session ID: {session_id}")

    message = context.get("message", "")

    # Check if this is a clipboard error
    if "Cannot read clipboard" in message:
        log("Detected 'Cannot read clipboard' error")

        # Acquire lock to prevent concurrent access
        if not acquire_lock():
            log("Could not acquire lock, skipping")
            return

        try:
            # Save clipboard image to file (session-specific)
            image_path = save_clipboard_image(session_id)

            if image_path:
                copy_to_clipboard(image_path)

                context["message"] = (
                    "🖼️ 이미지 저장됨! 파일 경로가 클립보드에 복사되었습니다. 다시 붙여넣기 하면 분석됩니다."
                )
                context["clipboard_updated"] = True
                context["image_path"] = image_path
                context["session_id"] = session_id

                log(f"Image saved and clipboard updated: {image_path}")
            else:
                context["message"] = (
                    "❌ 클립보드 이미지 저장 실패. 이미지가 클립보드에 있는지 확인해주세요."
                )
                context["clipboard_updated"] = False
        finally:
            release_lock()

    # Output modified context
    print(json.dumps(context), flush=True)


def cleanup_old_files():
    """Clean up files/directories older than 24 hours"""
    try:
        # 24 hours in seconds
        max_age = 24 * 60 * 60
        now = time.time()

        # Check if directory exists
        if not CLIPBOARD_DIR.exists():
            return

        count = 0
        # Iterate over all items in clipboard directory
        for item in CLIPBOARD_DIR.iterdir():
            try:
                # Check age
                stat = item.stat()
                age = now - stat.st_mtime

                if age > max_age:
                    if item.is_dir():
                        shutil.rmtree(item)
                        log(
                            f"Cleaned up old session directory: {item.name} ({age / 3600:.1f}h old)"
                        )
                        count += 1
                    elif item.is_file():
                        # Don't delete lock file unless it's REALLY old (stale lock)
                        if item.name == ".lock" and age < 300:  # 5 mins for lock
                            continue
                        item.unlink()
                        log(f"Cleaned up old file: {item.name} ({age / 3600:.1f}h old)")
                        count += 1
            except Exception as e:
                # Ignore errors for individual files
                pass

        if count > 0:
            log(f"Cleanup finished. Removed {count} old items.")

    except Exception as e:
        log(f"Error during global cleanup: {e}")


def handle_user_prompt_submit():
    """
    Handle UserPromptSubmit events.
    Check if there's a clipboard image to analyze and inject context.
    """
    log("Processing UserPromptSubmit event")

    # Run global cleanup (opportunistic, doesn't block much)
    cleanup_old_files()

    # Read context from stdin
    try:
        context = json.load(sys.stdin)
    except json.JSONDecodeError:
        log("Error: Invalid JSON input")
        return

    # Get session ID for isolation
    session_id = get_session_id(context)
    log(f"Session ID: {session_id}")

    # Determine prompt - use user's prompt if provided
    prompt = context.get("prompt", "") or context.get("message", "")
    user_prompt = prompt.strip()

    # Define keywords that trigger clipboard analysis
    # STRICT MODE: Only trigger when Claude's image marker is present
    # This prevents accidental triggers from words like "image" in text conversation
    trigger_keywords = [
        "[image",
        "[Image",  # Claude's automatic marker when pasting images
    ]

    prompt_lower = user_prompt.lower()
    is_triggered = any(k.lower() in prompt_lower for k in trigger_keywords)

    if not is_triggered:
        # If no trigger keyword is found, do not access clipboard or inject context
        log("No [Image] marker found in prompt. Skipping analysis.")
        print(json.dumps(context), flush=True)
        return

    # Create session-specific last image reference
    session_last_image = CLIPBOARD_DIR / f".last_image_{session_id}"

    # Try to save clipboard image if not already saved
    image_path = None

    # Force refresh from clipboard if [Image] marker is present
    # This ensures we get the NEW image user just pasted, not the old cached one
    log("Image marker detected, refreshing from clipboard...")
    image_path = save_clipboard_image(session_id)

    if not image_path or not Path(image_path).exists():
        # No image to analyze - just pass through
        # Only warn if it looked like they REALLY tried to paste an image (Claude marker)
        if "[Image" in prompt or "[image" in prompt:
            log("Image reference found in prompt but no clipboard image available")
            # User tried to paste an image but it's not available
            # Add a clear system message instead of auto-injecting
            system_messages = context.get("systemMessages", [])
            system_messages.append(
                "⚠️ 이미지가 클립보드에서 감지되지 않았습니다. 이미지가 클립보드에 있는지 확인해주세요."
            )
            context["systemMessages"] = system_messages
        print(json.dumps(context), flush=True)
        return

    log(f"Found image to analyze: {image_path}")

    if not user_prompt:
        user_prompt = "이 이미지를 분석해 주세요. 무엇이 보이는지 설명하고, 텍스트가 있다면 추출하고, 중요한 세부사항을 포함해 주세요."

    # Inject context for MiniMax analysis
    analysis_instruction = f"""
[Auto-Injected Image Analysis Context]
이미지 파일: {image_path}
작업: MiniMax_understand_image 도구를 사용하여 이 이미지를 분석하세요.

사용자 요청: {user_prompt}

분석 후 결과를 명확하게 표시하고, 발견한 모든 텍스트(OCR), 객체, 레이아웃을 포함하세요.
"""

    # Add to additional context
    existing_context = context.get("additionalContext", "")
    context["additionalContext"] = existing_context + analysis_instruction
    context["minimax_image_path"] = image_path
    context["auto_analyze_image"] = True

    # Add system message for user feedback
    system_messages = context.get("systemMessages", [])
    system_messages.append("🖼️ 클립보드 이미지 감지됨. MiniMax로 분석을 시작합니다...")
    context["systemMessages"] = system_messages

    log(f"Injected image analysis context for: {image_path}")

    # Output modified context
    print(json.dumps(context), flush=True)


def handle_post_tool_use():
    """
    Handle PostToolUse events.
    Clean up temporary files after MiniMax_understand_image.
    """
    log("Processing PostToolUse event")

    # Read context from stdin
    try:
        context = json.load(sys.stdin)
    except json.JSONDecodeError:
        log("Error: Invalid JSON input")
        return

    tool_name = context.get("tool_name", "")

    # Check if this is MiniMax_understand_image
    if "understand_image" in tool_name.lower() or "minimax" in tool_name.lower():
        log(f"Detected MiniMax image tool: {tool_name}")

        # Get the image path from tool input
        tool_input = context.get("tool_input", {})
        image_url = tool_input.get("image_url", "") or tool_input.get(
            "image_source", ""
        )

        if image_url and CLIPBOARD_DIR in Path(image_url).parents:
            log(f"Cleaning up temporary image: {image_url}")
            cleanup_temp_file(image_url)

            # Clear last image reference if this was the current image
            if LAST_IMAGE_FILE.exists():
                last_path = LAST_IMAGE_FILE.read_text().strip()
                if last_path == image_path:
                    LAST_IMAGE_FILE.unlink()

    # Output context
    print(json.dumps(context), flush=True)


def handle_session_end():
    """
    Handle SessionEnd events.
    Clean up all remaining temporary files.
    """
    log("Processing SessionEnd event")

    # Read context from stdin (may be empty)
    try:
        context = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except json.JSONDecodeError:
        context = {}

    # Get session ID for cleanup
    session_id = get_session_id(context)
    log(f"Cleaning up session: {session_id}")

    # Clean up session-specific files only
    cleanup_session_files(session_id)

    # Also clean up lock file if it exists
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()

    log("Session cleanup completed")

    # Output context
    print(json.dumps(context), flush=True)


def main():
    """Main entry point - dispatch to appropriate handler"""
    if len(sys.argv) < 2:
        log("Usage: python3 hook.py <event_name>")
        log("Events: Notification, UserPromptSubmit, PostToolUse, SessionEnd")
        sys.exit(1)

    event_name = sys.argv[1]

    # Route to appropriate handler
    handlers = {
        "Notification": handle_notification,
        "UserPromptSubmit": handle_user_prompt_submit,
        "PostToolUse": handle_post_tool_use,
        "SessionEnd": handle_session_end,
    }

    handler = handlers.get(event_name)
    if handler:
        try:
            handler()
        except Exception as e:
            log(f"Error in {event_name} handler: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)
    else:
        log(f"Unknown event: {event_name}")
        # For unknown events, just pass through the input
        try:
            if not sys.stdin.isatty():
                content = sys.stdin.read()
                if content.strip():
                    print(content, flush=True)
        except:
            pass


if __name__ == "__main__":
    main()
