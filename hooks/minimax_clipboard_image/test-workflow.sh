#!/bin/bash
# Test script for MiniMax clipboard image workflow
# Usage: ./test-workflow.sh [test_image_path]

set -e

echo "🧪 Testing MiniMax Clipboard Image Workflow"
echo "============================================="

# Check if pngpaste is available
if ! command -v pngpaste &> /dev/null; then
    echo "❌ pngpaste not found. Install with: brew install pngpaste"
    exit 1
fi

# Check if hook script exists
if [ ! -f "$HOME/.claude/hooks/minimax_clipboard_image/hook.py" ]; then
    echo "❌ Hook script not found at ~/.claude/hooks/minimax_clipboard_image/hook.py"
    exit 1
fi

# Create a test image if none provided
if [ -z "$1" ]; then
    echo "📝 Creating test image..."
    TEST_IMAGE="/tmp/test_image_$(date +%s).png"
    
    # Create a simple test image using sips (built-in macOS)
    # Create a 200x200 red image
    if command -v convert &> /dev/null; then
        convert -size 200x200 xc:red "$TEST_IMAGE"
    else
        # Alternative: create a 1x1 pixel PNG and scale it
        echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==" | base64 -d > "$TEST_IMAGE"
    fi
    
    echo "✅ Created test image: $TEST_IMAGE"
else
    TEST_IMAGE="$1"
fi

# Copy test image to clipboard
echo "📋 Copying test image to clipboard..."
if command -v pbcopy &> /dev/null; then
    if command -v imgcat &> /dev/null; then
        # If imgcat is available, use it to copy
        imgcat "$TEST_IMAGE" | pbcopy
    else
        # Alternative: use osascript
        osascript -e "set the clipboard to (read (POSIX file \"$TEST_IMAGE\") as JPEG picture)"
    fi
fi

echo "✅ Test image copied to clipboard"
echo ""
echo "📋 Test Steps:"
echo "1. Open Claude Code"
echo "2. Paste the image (Cmd+V)"
echo "3. You should see 'Cannot read clipboard' error"
echo "4. Wait for Notification hook to save image"
echo "5. The image path will be copied to clipboard"
echo "6. Paste again (Cmd+V) - should now show the file path"
echo "7. Press Enter to analyze with MiniMax"
echo ""
echo "🧹 Cleanup..."
# Cleanup is handled by the hook, but we can clean test files
# rm -f "$TEST_IMAGE" 2>/dev/null || true

echo ""
echo "✅ Test setup complete!"
echo "Now test in Claude Code with the image in your clipboard."
