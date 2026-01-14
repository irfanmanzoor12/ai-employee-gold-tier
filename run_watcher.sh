#!/bin/bash
# Start the File Watcher

echo "🚀 Starting AI Employee File Watcher..."
echo "========================================="
echo ""
echo "Monitoring: AI_Employee_Vault/Drop_Folder/"
echo "Tasks created in: AI_Employee_Vault/Needs_Action/"
echo ""
echo "Drop any file into Drop_Folder to test!"
echo "Press Ctrl+C to stop"
echo ""
echo "========================================="
echo ""

cd "$(dirname "$0")"
uv run python file_watcher.py
