#!/bin/bash
# Install cf to ~/.local/bin

set -e

INSTALL_DIR="$HOME/.local/bin"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$INSTALL_DIR"

# Symlink so updates are automatic
ln -sf "$SCRIPT_DIR/cf" "$INSTALL_DIR/cf"

echo "Installed cf to $INSTALL_DIR/cf"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "Add to your ~/.bashrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
