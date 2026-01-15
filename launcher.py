#!/usr/bin/env python3
"""
League of Legends Role Quest Calculator Launcher

This script provides a simple menu to launch the appropriate calculator
for your lane.
"""

import sys
import subprocess
import os

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("  League of Legends - Role Quest Completion Calculator")
    print("  Season 2025")
    print("=" * 60)
    print()

def main():
    """Main launcher menu."""
    clear_screen()
    print_banner()
    
    print("Select your lane:")
    print()
    print("  1. Top Lane    (1200 points)")
    print("  2. Mid Lane    (1350 points)")
    print("  3. Bot Lane    (1350 points)")
    print()
    print("  4. Exit")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    calculators = {
        '1': 'quest_timer_calculator_top.py',
        '2': 'quest_timer_calculator.py',
        '3': 'quest_timer_calculator_bot.py'
    }
    
    if choice in calculators:
        script = calculators[choice]
        print(f"\nLaunching {script}...")
        print("Close the calculator window to return to this menu.\n")
        
        try:
            subprocess.run([sys.executable, script])
            print("\nCalculator closed.")
            input("Press Enter to return to menu...")
            main()  # Return to menu
        except FileNotFoundError:
            print(f"\nError: Could not find {script}")
            print("Make sure all calculator files are in the same directory.")
            input("\nPress Enter to exit...")
        except Exception as e:
            print(f"\nError launching calculator: {e}")
            input("\nPress Enter to exit...")
    
    elif choice == '4':
        print("\nThank you for using LoL Role Quest Calculator!")
        sys.exit(0)
    
    else:
        print("\nInvalid choice. Please enter 1, 2, 3, or 4.")
        input("Press Enter to try again...")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
