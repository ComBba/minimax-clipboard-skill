# Contributing to MiniMax Clipboard Skill

Thank you for considering contributing! This document outlines how to contribute effectively.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/minimax-clipboard-skill.git
   cd minimax-clipboard-skill
   ```
3. **Create** a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make** your changes
5. **Test** thoroughly
6. **Commit** with clear messages
7. **Push** and create a Pull Request

## 🛠️ Development Setup

### Prerequisites

- macOS (for testing)
- Python 3.7+
- Claude Code with Oh-My-OpenCode framework
- MiniMax MCP configured

### Installation for Development

```bash
# Install from local directory
ln -s "$(pwd)/hooks/minimax_clipboard_image" ~/.claude/hooks/minimax_clipboard_image

# Make scripts executable
chmod +x hooks/minimax_clipboard_image/hook.py
chmod +x hooks/minimax_clipboard_image/test-workflow.sh
chmod +x scripts/install.sh
```

## 🧪 Testing

### Unit Testing

```bash
# Test individual hook events
echo '{"message": "Cannot read clipboard", "type": "error"}' | \
  python3 hooks/minimax_clipboard_image/hook.py Notification

echo '{"prompt": "test", "session": {"id": "test123"}}' | \
  python3 hooks/minimax_clipboard_image/hook.py UserPromptSubmit
```

### Integration Testing

```bash
# Run test workflow
./hooks/minimax_clipboard_image/test-workflow.sh
```

### Manual Testing

1. Copy an image to clipboard
2. Paste in Claude Code
3. Verify automatic analysis happens
4. Check temp files are cleaned up

## 📝 Code Style

### Python

- Follow PEP 8
- Use meaningful variable names
- Add docstrings for public functions
- Keep functions focused and small

### Shell Scripts

- Use `#!/bin/bash` shebang
- Quote variables: `"$VAR"`
- Check command success: `command || exit 1`
- Use `set -e` for error handling

## 🐛 Reporting Bugs

### Before Reporting

1. Check [existing issues](https://github.com/YOUR_USERNAME/minimax-clipboard-skill/issues)
2. Try with latest version
3. Verify pngpaste is installed
4. Test with test-workflow.sh

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Copy image
2. Paste in Claude
3. Error occurs

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- macOS version: 
- Python version: 
- Claude Code version: 
- pngpaste version: 

**Logs**
Include relevant logs from hook execution
```

## 💡 Suggesting Features

Open an issue with:
- Clear use case
- Expected behavior
- Potential implementation approach
- Why this benefits users

## 🔀 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] No new warnings
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)

### PR Title Format

Use conventional commits:
- `feat: Add feature X`
- `fix: Resolve bug Y`
- `docs: Update README`
- `refactor: Improve code structure`
- `test: Add test for Z`
- `chore: Update dependencies`

### PR Description Template

```markdown
## Description
Clear description of changes

## Motivation
Why is this change needed?

## Changes Made
- Change 1
- Change 2

## Testing
How was this tested?

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🏗️ Architecture Guidelines

### Hook Design Principles

1. **Session isolation** - Each session has separate temp storage
2. **Race condition safety** - Use lock files
3. **Automatic cleanup** - Remove temp files promptly
4. **User feedback** - Provide clear system messages
5. **Graceful degradation** - Fall back gracefully on errors

### Adding New Hook Events

1. Add handler function in `hook.py`
2. Register in `main()` dispatcher
3. Update settings.json example
4. Document in SKILL.md
5. Add tests

### Code Organization

```
hook.py structure:
├── Configuration (paths, constants)
├── Utility functions (logging, file ops)
├── Core functions (save, cleanup)
├── Event handlers (notification, submit, etc.)
└── Main dispatcher
```

## 📚 Documentation

### What to Document

- New features or changes
- Configuration options
- Troubleshooting steps
- API changes (if any)

### Where to Document

- **README.md** - User-facing features
- **SKILL.md** - Skill usage and integration
- **Code comments** - Complex logic only
- **Docstrings** - Public functions

## 🔐 Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Email: security@your-email.com

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Never log sensitive data
- Validate all file paths
- Use secure temp file creation
- Clean up sensitive data promptly

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- Git commit history

## 💬 Questions?

- Open a [Discussion](https://github.com/YOUR_USERNAME/minimax-clipboard-skill/discussions)
- Join our community chat (if applicable)
- Check existing documentation first

## 🎯 Good First Issues

Look for issues labeled:
- `good first issue`
- `help wanted`
- `documentation`

These are great entry points for new contributors!

---

Thank you for contributing to MiniMax Clipboard Skill! 🎉
