#!/bin/bash
#
# MiniMax Clipboard Skill - Installation Script
# 
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/minimax-clipboard-skill/main/scripts/install.sh)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SKILL_HOOK_DIR="$HOOKS_DIR/minimax_clipboard_image"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

# Print functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}  MiniMax Clipboard Skill - Installation${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo ""
}

# Check if running on macOS
check_os() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This skill only works on macOS (uses pngpaste and pbcopy)"
        exit 1
    fi
    print_success "Running on macOS"
}

# Check Python installation
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.7+"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python 3 found: $python_version"
}

# Check and install pngpaste
check_pngpaste() {
    if command -v pngpaste &> /dev/null; then
        print_success "pngpaste already installed"
        return 0
    fi
    
    print_warning "pngpaste not found. Installing..."
    
    if command -v brew &> /dev/null; then
        brew install pngpaste
        print_success "pngpaste installed via Homebrew"
    else
        print_error "Homebrew not found. Please install Homebrew first:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
}

# Create directories
create_directories() {
    print_info "Creating directories..."
    
    mkdir -p "$HOOKS_DIR"
    mkdir -p "$CLAUDE_DIR/tmp/images/clipboard"
    
    print_success "Directories created"
}

# Download and install hook files
install_hook() {
    print_info "Installing hook files..."
    
    # Create hook directory
    mkdir -p "$SKILL_HOOK_DIR"
    
    # Download hook.py
    if command -v curl &> /dev/null; then
        curl -fsSL "https://raw.githubusercontent.com/YOUR_USERNAME/minimax-clipboard-skill/main/hooks/minimax_clipboard_image/hook.py" \
            -o "$SKILL_HOOK_DIR/hook.py"
        curl -fsSL "https://raw.githubusercontent.com/YOUR_USERNAME/minimax-clipboard-skill/main/hooks/minimax_clipboard_image/test-workflow.sh" \
            -o "$SKILL_HOOK_DIR/test-workflow.sh"
    elif command -v wget &> /dev/null; then
        wget -q "https://raw.githubusercontent.com/YOUR_USERNAME/minimax-clipboard-skill/main/hooks/minimax_clipboard_image/hook.py" \
            -O "$SKILL_HOOK_DIR/hook.py"
        wget -q "https://raw.githubusercontent.com/YOUR_USERNAME/minimax-clipboard-skill/main/hooks/minimax_clipboard_image/test-workflow.sh" \
            -O "$SKILL_HOOK_DIR/test-workflow.sh"
    else
        print_error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    
    # Make executable
    chmod +x "$SKILL_HOOK_DIR/hook.py"
    chmod +x "$SKILL_HOOK_DIR/test-workflow.sh"
    
    print_success "Hook files installed"
}

# Update settings.json
update_settings() {
    print_info "Updating Claude settings..."
    
    # Backup existing settings
    if [ -f "$SETTINGS_FILE" ]; then
        cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        print_info "Backup created: $SETTINGS_FILE.backup.*"
    else
        # Create new settings file
        echo "{}" > "$SETTINGS_FILE"
    fi
    
    # Check if jq is available for JSON manipulation
    if command -v jq &> /dev/null; then
        # Use jq for safe JSON manipulation
        update_settings_with_jq
    else
        # Manual update (basic, may not handle all edge cases)
        print_warning "jq not found. Using basic JSON update."
        print_warning "For better results, install jq: brew install jq"
        update_settings_manual
    fi
    
    print_success "Settings updated"
}

update_settings_with_jq() {
    local hook_config
    hook_config=$(cat <<'EOF'
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py Notification"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py UserPromptSubmit"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "MiniMax_understand_image",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py PostToolUse"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py SessionEnd"
          }
        ]
      }
    ]
  }
}
EOF
)
    
    # Merge hook config into existing settings
    jq -s '.[0] * .[1]' "$SETTINGS_FILE" <(echo "$hook_config") > "$SETTINGS_FILE.tmp"
    mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
}

update_settings_manual() {
    print_warning "Please manually add the following to $SETTINGS_FILE:"
    echo ""
    cat <<'EOF'
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py Notification"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py UserPromptSubmit"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "MiniMax_understand_image",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py PostToolUse"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/minimax_clipboard_image/hook.py SessionEnd"
          }
        ]
      }
    ]
  }
}
EOF
    echo ""
    read -p "Press Enter after updating settings.json..."
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    # Test hook script
    if [ -x "$SKILL_HOOK_DIR/hook.py" ]; then
        print_success "Hook script is executable"
    else
        print_error "Hook script is not executable"
        return 1
    fi
    
    # Test pngpaste
    if command -v pngpaste &> /dev/null; then
        print_success "pngpaste is available"
    else
        print_error "pngpaste not found"
        return 1
    fi
    
    print_success "Installation test passed"
}

# Print completion message
print_completion() {
    echo ""
    echo -e "${GREEN}=================================================${NC}"
    echo -e "${GREEN}  ✅ Installation Complete!${NC}"
    echo -e "${GREEN}=================================================${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Restart Claude Code"
    echo "  2. Copy an image to clipboard"
    echo "  3. Paste in Claude Code (Cmd+V)"
    echo "  4. Ask Claude to analyze it"
    echo ""
    echo -e "${BLUE}Test the installation:${NC}"
    echo "  $SKILL_HOOK_DIR/test-workflow.sh"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  https://github.com/YOUR_USERNAME/minimax-clipboard-skill"
    echo ""
}

# Main installation flow
main() {
    print_header
    
    check_os
    check_python
    check_pngpaste
    create_directories
    install_hook
    update_settings
    test_installation
    
    print_completion
}

# Run installation
main
