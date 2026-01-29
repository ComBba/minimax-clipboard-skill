---
name: minimax-clipboard
description: Automatically save and analyze clipboard images using MiniMax understand_image. Use when user pastes images in Claude Code and needs automatic image analysis without manual file saving.
license: MIT
version: 1.0.0
author: Your Name
---

# MiniMax Clipboard Image Analysis

Seamlessly analyze clipboard images in Claude Code using MiniMax's `understand_image` tool.

## What This Skill Does

When you paste an image in Claude Code:
1. **Detects** "Cannot read clipboard" error
2. **Saves** image to temporary file automatically
3. **Analyzes** image using MiniMax_understand_image
4. **Cleans up** temporary files after analysis

No manual file saving required—just paste and ask!

## Installation

Run the installation script:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ComBba/minimax-clipboard-skill/master/scripts/install.sh)
```

Or manually:

```bash
# 1. Install pngpaste (macOS only)
brew install pngpaste

# 2. Copy hook to Claude directory
cp -r hooks/minimax_clipboard_image ~/.claude/hooks/

# 3. Add hook configuration to ~/.claude/settings.json
```

See [Installation Guide](README.md#installation) for details.

## Usage

### Basic Workflow

1. **Copy** any image to clipboard (screenshot, drag from browser, etc.)
2. **Paste** in Claude Code chat (Cmd+V)
3. **Ask** your question or just press Enter
4. Claude automatically analyzes the image with MiniMax

### Examples

**Analyze screenshot:**
```
[Paste screenshot]
What's in this image?
```

**Extract text (OCR):**
```
[Paste document scan]
Extract all text from this image
```

**Debug UI:**
```
[Paste UI screenshot]
What's wrong with this layout?
```

## How It Works

### Hook Events

This skill registers 4 hook events in Claude Code:

| Event | Purpose |
|-------|---------|
| `Notification` | Detects clipboard error → saves image |
| `UserPromptSubmit` | Injects MiniMax analysis context |
| `PostToolUse` | Cleans up after MiniMax_understand_image |
| `SessionEnd` | Final cleanup on session close |

### File Locations

- **Hook script**: `~/.claude/hooks/minimax_clipboard_image/hook.py`
- **Temp images**: `~/.claude/tmp/images/clipboard/[session_id]/`
- **Configuration**: `~/.claude/settings.json`

### Session Isolation

Each Claude session gets its own temp directory, preventing cross-session conflicts.

## Requirements

- **macOS** (uses `pngpaste` and `pbcopy`)
- **Python 3** (standard library only)
- **Claude Code** with MiniMax MCP enabled

## Troubleshooting

### Image not detected

**Symptom**: No automatic analysis after pasting

**Solutions**:
- Ensure image is in clipboard (try Cmd+C again)
- Check `pngpaste` installed: `which pngpaste`
- Verify hook registered: `grep minimax ~/.claude/settings.json`

### "pngpaste not found"

```bash
brew install pngpaste
```

### Hook not triggering

Restart Claude Code after installation or settings changes.

### Temp files not cleaned up

Session cleanup happens automatically. Manual cleanup:

```bash
rm -rf ~/.claude/tmp/images/clipboard/*
```

## Configuration

Hook configuration in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Notification": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py Notification"
      }]
    }],
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py UserPromptSubmit"
      }]
    }],
    "PostToolUse": [{
      "matcher": "MiniMax_understand_image",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py PostToolUse"
      }]
    }],
    "SessionEnd": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py SessionEnd"
      }]
    }]
  }
}
```

## Advanced Usage

### Custom analysis prompts

The hook preserves your prompt when analyzing images:

```
[Paste image]
Analyze this diagram and explain the data flow
```

### Multiple images

Paste one at a time. Each gets analyzed separately with session isolation.

### Direct file paths

Hook also works if you paste file paths instead of images.

## Architecture

### Design Principles

1. **Session isolation** - Each session has separate temp storage
2. **Race condition protection** - Lock file prevents concurrent saves
3. **Automatic cleanup** - Files removed after analysis and on session end
4. **User feedback** - System messages show progress
5. **Graceful degradation** - Falls back to normal behavior if image unavailable

### Code Structure

```
hook.py
├── Event Handlers
│   ├── handle_notification()      # Save clipboard → file
│   ├── handle_user_prompt_submit() # Inject MiniMax context
│   ├── handle_post_tool_use()     # Cleanup after analysis
│   └── handle_session_end()       # Final cleanup
├── Utilities
│   ├── save_clipboard_image()     # pngpaste wrapper
│   ├── cleanup_session_files()    # Session-specific cleanup
│   └── get_session_id()           # Extract/generate session ID
└── Main dispatcher
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Skills

- [Frontend UI/UX](https://github.com/oh-my-opencode/frontend-ui-ux) - UI analysis companion
- [Playwright](https://github.com/oh-my-opencode/playwright) - Browser screenshot automation

## Support

- **Issues**: [GitHub Issues](https://github.com/ComBba/minimax-clipboard-skill/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ComBba/minimax-clipboard-skill/discussions)
