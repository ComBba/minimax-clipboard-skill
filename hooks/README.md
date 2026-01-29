# Hooks

This skill provides two complementary hooks for different workflows:

## 1. Clipboard Image Hook (Python)

**Location**: `minimax_clipboard_image/hook.py`

**Workflow**: Clipboard paste → Auto-save → Auto-analyze

### Events Handled
- `Notification`: Detects "Cannot read clipboard" → saves image to file
- `UserPromptSubmit`: Injects MiniMax analysis context
- `PostToolUse`: Cleanup after MiniMax_understand_image
- `SessionEnd`: Final cleanup

### Use Case
Perfect for quick screenshot analysis:
1. Take screenshot (Cmd+Shift+4)
2. Paste in Claude Code
3. Ask question
4. Automatic analysis

### Installation
Copy to `~/.claude/hooks/minimax_clipboard_image/`

### Configuration
Add to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "Notification": [{ "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py Notification" }] }],
    "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py UserPromptSubmit" }] }],
    "PostToolUse": [{ "matcher": "MiniMax_understand_image", "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py PostToolUse" }] }],
    "SessionEnd": [{ "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py SessionEnd" }] }]
  }
}
```

---

## 2. OpenCode Image Handler Hook (JavaScript)

**Location**: `opencode/minimax-image-handler.js`

**Workflow**: File attachment → Direct MiniMax call

### Events Handled
- `PreToolUse` (look_at matcher): Intercepts look_at tool usage
- `Notification`: Shows MiniMax is analyzing

### Use Case
For users who prefer attaching image files directly or using look_at tool.

### Installation
Copy to `~/.config/opencode/hooks/`

### Configuration
Add to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "look_at",
      "hooks": [{
        "type": "command",
        "command": "node ~/.config/opencode/hooks/minimax-image-handler.js"
      }]
    }]
  }
}
```

---

## Which One To Use?

### Use Python Hook If:
- ✅ You frequently paste screenshots
- ✅ You want automatic clipboard → file conversion
- ✅ You prefer Python-based hooks
- ✅ You need session-isolated temp file management

### Use JavaScript Hook If:
- ✅ You prefer attaching files via drag-and-drop
- ✅ You use look_at tool frequently
- ✅ You want Node.js-based hooks
- ✅ You need PreToolUse interception

### Use Both If:
- ✅ You want maximum flexibility
- ✅ Different workflows for different scenarios
- ✅ Team members have different preferences

**Note**: Both hooks can coexist without conflicts. They handle different event types.

---

## Testing

### Test Python Hook
```bash
./minimax_clipboard_image/test-workflow.sh
```

### Test JavaScript Hook
```bash
node opencode/minimax-image-handler.js
```

---

## Dependencies

### Python Hook
- Python 3.7+
- pngpaste (macOS): `brew install pngpaste`

### JavaScript Hook
- Node.js 14+
- Oh-My-OpenCode framework

---

## Architecture Comparison

| Feature | Python Hook | JavaScript Hook |
|---------|-------------|-----------------|
| **Trigger** | Clipboard paste | look_at tool |
| **File Saving** | Automatic | User provides |
| **Temp Cleanup** | Automatic | N/A |
| **Session Isolation** | Yes | N/A |
| **MiniMax Call** | Via context injection | Direct MCP call |
| **Platform** | macOS only | Cross-platform |
