"""
Build Script for Creating Standalone EXE Files

This script uses PyInstaller to create standalone executables that don't require
Python to be installed on the user's machine.

Usage:
    pip install pyinstaller
    python build_exe.py
"""

import os
import subprocess
import shutil
import sys

def build_executable(script_name, exe_name, icon_path=None):
    """Build a standalone executable from a Python script."""
    
    print(f"\nBuilding {exe_name}...")
    
    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window (GUI only)
        "--name", exe_name,
        "--clean",  # Clean build cache
    ]
    
    # Add icon if provided
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # Add hidden imports that PyInstaller might miss
    cmd.extend([
        "--hidden-import", "matplotlib",
        "--hidden-import", "numpy",
        "--hidden-import", "PIL",
        "--hidden-import", "tkinter",
    ])
    
    # Add the script to build
    cmd.append(script_name)
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✓ Successfully built {exe_name}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build {exe_name}.exe: {e}")
        return False

def build_launcher_exe():
    """Build the launcher executable."""
    
    print("\nBuilding launcher executable...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",  # Keep console for launcher menu
        "--name", "LoL_Quest_Calculator",
        "--clean",
    ]
    
    cmd.extend([
        "--hidden-import", "matplotlib",
        "--hidden-import", "numpy",
        "--hidden-import", "tkinter",
    ])
    
    cmd.append("launcher.py")
    
    try:
        subprocess.run(cmd, check=True)
        print("✓ Successfully built LoL_Quest_Calculator.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build launcher: {e}")
        return False

def clean_build_files():
    """Clean up build artifacts."""
    
    print("\nCleaning up build files...")
    
    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = [
        "LoL_Quest_Calculator.spec",
        "LoL_Quest_Calculator_Top.spec",
        "LoL_Quest_Calculator_Mid.spec",
        "LoL_Quest_Calculator_Bot.spec",
    ]
    
    for directory in dirs_to_remove:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"  Removed {directory}/")
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Removed {file}")

def main():
    """Main build process."""
    
    print("=" * 60)
    print("LoL Quest Calculator - EXE Builder")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("\n✗ PyInstaller is not installed!")
        print("\nInstall it with: pip install pyinstaller")
        sys.exit(1)
    
    print("\nThis will build standalone .exe files for Windows.")
    print("The process may take several minutes...")
    
    # Build the main launcher (recommended approach)
    success = build_launcher_exe()
    
    if success:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        print("\nThe executable can be found in the 'dist' folder:")
        print("  dist/LoL_Quest_Calculator.exe")
        print("\nThis single .exe contains everything needed to run all calculators.")
        print("Users can run it without installing Python!")
        
        # Optional: Build individual calculator exes
        print("\n" + "-" * 60)
        response = input("\nBuild individual calculator .exe files? (y/n): ")
        if response.lower() == 'y':
            print("\nBuilding individual executables...")
            build_executable("quest_timer_calculator_top.py", "LoL_Quest_Calculator_Top")
            build_executable("quest_timer_calculator.py", "LoL_Quest_Calculator_Mid")
            build_executable("quest_timer_calculator_bot.py", "LoL_Quest_Calculator_Bot")
            print("\nIndividual executables built in dist/ folder")
    
    # Clean up
    print("\n" + "-" * 60)
    clean_response = input("\nClean up build files? (y/n): ")
    if clean_response.lower() == 'y':
        clean_build_files()
        print("\n✓ Cleanup complete")
    
    print("\n" + "=" * 60)
    print("Done! Your executables are ready for distribution.")
    print("=" * 60)

if __name__ == "__main__":
    main()
