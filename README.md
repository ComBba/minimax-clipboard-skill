# MiniMax Clipboard Image Analysis for Claude Code

> **Paste. Analyze. Done.**  
> Automatically save and analyze clipboard images using MiniMax's vision capabilities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Oh-My-OpenCode](https://img.shields.io/badge/Oh--My--OpenCode-Skill-blue)](https://github.com/oh-my-opencode)

## ✨ Features

- 🖼️ **Zero-friction image analysis** - Just paste, no file saving needed
- 🔄 **Automatic workflow** - Detects clipboard → saves → analyzes → cleans up
- 🎯 **Session isolation** - Strict mode ensures images only attach when intended (`[Image]` marker)
- 🧹 **Auto cleanup** - Temporary files older than 24h are automatically removed
- 🔒 **Race condition safe** - Lock mechanism prevents conflicts

## 🎬 Demo

```
User: [Pastes screenshot]
User: What's in this image?

Claude: 🖼️ Clipboard image detected. Starting MiniMax analysis...

[MiniMax analyzes the image]

Claude: This screenshot shows a web application dashboard with...
```

## 📦 Installation

Just run this single command to install the clipboard skill:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ComBba/minimax-clipboard-skill/master/scripts/install.sh)
```

> **Note:** Requires `pngpaste` on macOS. If not installed, run `brew install pngpaste`.

## 🚀 Usage

### How to use

1. **Copy** any image to your clipboard:
   - Screenshot (Cmd+Shift+4 on macOS)
   - Drag image from browser
   - Copy from Preview/Photos
   - Right-click → Copy Image

2. **Paste** in Claude Code (Cmd+V)
   - You will see `[Image 1]` automatically inserted.

3. **Ask** your question or press Enter

4. Claude **automatically analyzes** the image using MiniMax.

### Strict Mode & Safety

This skill operates in **Strict Mode**:
- It **ONLY** accesses your clipboard when it detects the `[Image]` marker that Claude Code inserts when you paste.
- It will **NOT** trigger if you just say "image" or "clipboard" in text.
- This ensures your clipboard privacy and prevents accidental image attachments from other sessions.

### Auto Cleanup

- The skill automatically cleans up temporary files and directories that are older than **24 hours**.
- You don't need to worry about disk space usage.

### Use Cases

#### 📸 Screenshot Analysis

```
[Paste screenshot]
Analyze this UI and suggest improvements
```

#### 📄 OCR / Text Extraction

```
[Paste document scan]
Extract all text from this image and format as markdown
```

#### 🐛 Debugging Visuals

```
[Paste browser screenshot]
Why is the layout broken on mobile?
```

## 📋 Requirements

- **Operating System**: macOS (uses `pngpaste` and `pbcopy`)
- **Python**: 3.7+ (uses standard library only)
- **Claude Code**: Latest version with hook support
- **MiniMax MCP**: Configured and enabled

## 🔧 Configuration

The hook uses these defaults (customizable in `hook.py`):

- **Temp directory**: `~/.claude/tmp/images/clipboard/`
- **Cleanup Age**: 24 hours
- **Retry attempts**: 5 (for race condition handling)

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for [Oh-My-OpenCode](https://github.com/oh-my-opencode) framework
- Uses [MiniMax MCP](https://docs.minimax.com) for image understanding
