#!/bin/bash
# League of Legends Role Quest Calculator - macOS/Linux Launcher

echo "Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo ""
echo "Checking for required packages..."
python3 -c "import matplotlib, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to install packages"
        echo "Try running: pip3 install matplotlib numpy"
        exit 1
    fi
fi

echo ""
echo "Launching LoL Role Quest Calculator..."
echo ""
python3 launcher.py

read -p "Press Enter to exit..."
