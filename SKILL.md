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
1. **Detects** the `[Image]` marker (Safe Trigger)
2. **Saves** image to temporary file automatically
3. **Analyzes** image using MiniMax_understand_image
4. **Cleans up** temporary files after analysis

No manual file saving required—just paste and ask!

## Installation

Run the installation script:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ComBba/minimax-clipboard-skill/master/scripts/install.sh)
```

## Usage

### Basic Workflow

1. **Copy** any image to clipboard (screenshot, drag from browser, etc.)
2. **Paste** in Claude Code chat (Cmd+V)
   - You will see `[Image 1]` automatically inserted.
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

### Strict Mode (Security)
This skill operates in **Strict Mode**. It only accesses your clipboard when it detects the `[Image]` marker that Claude Code inserts when you paste. This prevents accidental clipboard access during normal text conversation.

### Hook Events

This skill registers 4 hook events in Claude Code:

| Event | Purpose |
|-------|---------|
| `Notification` | Detects clipboard error → saves image |
| `UserPromptSubmit` | Injects MiniMax analysis context (Strict Mode) |
| `PostToolUse` | Cleans up after MiniMax_understand_image |
| `SessionEnd` | Final cleanup on session close |

### Auto Cleanup

- The skill automatically cleans up temporary files and directories that are older than **24 hours**.
- Disk space is managed automatically.

## Requirements

- **macOS** (uses `pngpaste` and `pbcopy`)
- **Python 3** (standard library only)
- **Claude Code** with MiniMax MCP enabled

## Troubleshooting

### Image not detected
**Symptom**: No automatic analysis after pasting

**Solutions**:
- Ensure you actually pasted the image (`[Image 1]` should appear in chat)
- Check `pngpaste` installed: `which pngpaste`
- Verify hook registered: `grep minimax ~/.claude/settings.json`

### "pngpaste not found"

```bash
brew install pngpaste
```

## Configuration

Hook configuration in `~/.claude/settings.json`. The installer sets this up automatically.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
