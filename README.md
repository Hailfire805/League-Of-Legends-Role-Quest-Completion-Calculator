# LoL Role Quest Completion Calculators

## Overview

A suite of Python applications for calculating and visualizing League of Legends Season 2025 role quest completion times. Each calculator is tailored to a specific lane (Top, Mid, Bot) with accurate point values and passive generation mechanics based on official game data.

## What This Does

These calculators help you understand **when your role quest will complete** based on your in-game performance. Input your CS/min, kills, objectives, and other metrics to see:
- Exact completion time
- Visual progression graph showing quest completion percentage over time
- Comparison between different playstyles and scenarios
- Breakdown of how each metric contributes to faster completion

Perfect for:
- Planning your early game strategy
- Understanding which objectives matter most for your role
- Comparing aggressive vs. farm-focused playstyles
- Educational content and game analysis

## Requirements

- **Python 3.8 or higher**
- **tkinter** (usually comes pre-installed with Python)
- **matplotlib** and **numpy** (installed via requirements.txt)

## Installation

1. **Ensure Python is installed:**
   ```bash
   python --version
   ```
   If not installed, download from [python.org](https://www.python.org/downloads/)

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```
   
   If you encounter permission errors, try:
   ```bash
   pip install -r requirements.txt --user
   ```

3. **For Linux users:** If tkinter is not installed:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # Fedora
   sudo dnf install python3-tkinter
   ```

## Quick Start

### Option 1: Standalone EXE (Easiest - No Python Required!)
**Windows users only - Download the .exe version if available**
1. Download `LoL_Quest_Calculator.exe`
2. Double-click to run
3. Select your lane from the menu
4. Done!

*No installation needed - the .exe includes everything*

### Option 2: Double-Click Launcher
**Windows users:**
- Double-click `launch.bat`

**macOS/Linux users:**
- Double-click `launch.sh` (or run `./launch.sh` in terminal)

The launcher will automatically:
- Check if Python is installed
- Install required packages if needed
- Show you a menu to select your lane

### Option 3: Using the Python Launcher
1. Download all files to a folder
2. Install dependencies: `pip install -r requirements.txt`
3. Run the launcher:
   ```bash
   python launcher.py
   ```
4. Select your lane from the menu

### Option 4: Direct Launch (For advanced users)
1. Download all files to a folder
2. Install dependencies: `pip install -r requirements.txt`
3. Run your lane's calculator directly:
   ```bash
   python quest_timer_calculator_top.py    # For Top Lane
   python quest_timer_calculator_bot.py    # For Bot Lane
   python quest_timer_calculator.py        # For Mid Lane
   ```

> **Note for Distributors:** See `BUILD_EXE_GUIDE.md` for instructions on creating the standalone .exe version

## Available Calculators

| File | Lane | Quest Points Required |
|------|------|----------------------|
| `quest_timer_calculator_top.py` | Top Lane | 1200 points |
| `quest_timer_calculator_bot.py` | Bot Lane | 1350 points |
| `quest_timer_calculator.py` | Mid Lane | 1350 points |

## How to Use

1. **Enter your performance metrics** in the left panel:
   - CS per minute (separated by lane)
   - Champion damage per minute (Mid Lane only)
   - Turret plates secured
   - Turrets destroyed
   - Champion takedowns (kills/assists)
   - Epic monster takedowns

2. **Click "Calculate Quest Time"** to see:
   - Estimated completion time
   - Points breakdown
   - Visual graph showing completion progress

3. **Add scenarios to compare:**
   - Click "Add to Comparison" to save the current scenario
   - Enter a custom label (or use the auto-generated one)
   - Compare multiple playstyles side-by-side on the graph

4. **Use zoom tools:**
   - Click the magnifying glass icon to zoom into specific time ranges
   - Use the home button to reset the view
   - Save graphs as images with the save button

## Lane-Specific Details

## Lane-Specific Quest Mechanics

### Top Lane (1200 points)
- **Quest starts at**: 1:05 game time
- **Passive generation**: 96 points/minute (8 points every 5 seconds) when in top lane
- **Baseline completion**: ~13.6 minutes
- **Minion kills**: 2 points in top lane, 1 point in other lanes
- **Turret takedowns**: 50 points in top lane, 25 points in other lanes
- **Turret plates**: 40 points in top lane, 20 points in other lanes
- **Champion takedowns**: 15 points
- **Epic monsters**: 30 points

### Bot Lane (1350 points)
- **Quest starts at**: 1:05 game time
- **Passive generation**: 96 points/minute (8 points every 5 seconds) when in bot lane
- **Baseline completion**: ~15.1 minutes
- **Minion kills**: 3 points in bot lane, 1.5 points in other lanes
- **Turret takedowns**: 50 points in bot lane, 25 points in other lanes
- **Turret plates**: 40 points in bot lane, 20 points in other lanes
- **Champion takedowns**: 15 points
- **Epic monsters**: 30 points

### Mid Lane (1350 points)
- **Minion kills**: 2 points in mid lane, 1 point in other lanes
- **Turret takedowns**: 50 points in mid lane, 25 points in other lanes
- **Turret plates**: 40 points in mid lane, 20 points in other lanes
- **Champion takedowns**: 25 points
- **Epic monsters**: 30 points
- **Champion damage**: Gain (3% / 1.5%) of damage dealt to champions as points (melee / ranged)
- **Special note**: Gold and experience from minions is reduced by 25% outside of mid lane until level 3

> **Important**: The passive generation only occurs when you're in your designated lane. Roaming or lane swapping will slow your quest completion.

## Common Features (All Calculators)

### Input Parameters
- **CS per Minute**: Your average creep score rate (separated by lane for Top/Bot calculators)
- **Champion Damage per Minute**: Damage dealt to enemy champions (Mid Lane only)
- **Champion Type**: Melee or Ranged (Mid Lane only - affects damage conversion rate)
- **Turret Plates**: Number of plates secured (0-5), separated by lane
- **Turret Takedowns**: Number of turrets destroyed, separated by lane
- **Champion Takedowns**: Number of kills/assists
- **Epic Monster Takedowns**: Dragons, barons, etc.

### Outputs
- Quest completion time in minutes and seconds
- Breakdown showing time reduction from each source
- Accumulation curve graph showing quest progress over time
- Baseline comparison (passive generation only)

### Comparison Feature
Click "Add to Comparison" to save the current scenario, then modify inputs and calculate again. The graph will overlay multiple scenarios for easy comparison.

## Updating Conversion Formulas

All conversion constants are defined at the top of each script. The formulas have been set based on official League of Legends role quest data, but if adjustments are needed:

**For Mid Lane** (quest_timer_calculator.py):
```python
# Lines 15-40 contain constants like:
PASSIVE_POINTS_PER_MINUTE = 100
TIME_REDUCTION_PER_KILL = 15
# ... etc
```

**For Top Lane** (quest_timer_calculator_top.py):
```python
# Lines 20-50 contain constants like:
TOTAL_QUEST_POINTS = 1200
POINTS_PER_MINION_TOP = 2
POINTS_PER_MINION_OTHER = 1
# ... etc
```

**For Bot Lane** (quest_timer_calculator_bot.py):
```python
# Lines 20-50 contain constants like:
TOTAL_QUEST_POINTS = 1350
POINTS_PER_MINION_BOT = 3
POINTS_PER_MINION_OTHER = 1.5
# ... etc
```

## Graph Interpretation

The graphs display **quest completion percentage** over time, making it intuitive to track progress toward 100%.

- **Gray dashed line**: Baseline passive generation
- **Blue solid line**: Your current scenario (showing faster completion)
- **Red dotted line**: Quest completion threshold (at Y = 100%)
- **Red circle**: Marks when your quest completes (at 100%)
- **Colored lines**: Comparison scenarios with custom labels
- **Y-axis**: Quest completion percentage (0% to 100%)
- **X-axis**: Game time in minutes

The graph shows how completion percentage increases over the course of the game. Steeper upward slopes indicate faster quest completion due to CS, kills, objectives, and damage (Mid Lane). When a line reaches Y = 100%, the quest is complete.

## New Features

### Custom Comparison Labels
When adding a scenario to comparison, you'll be prompted to enter a custom label. This allows you to name scenarios meaningfully (e.g., "Aggressive Early", "Farm Focus", "With First Blood") rather than using generic numbering.

### Graph Zoom and Pan
The matplotlib toolbar below the graph provides zoom and pan controls:
- **Zoom**: Click the magnifying glass icon, then drag on the graph to zoom into a region
- **Pan**: Click the crossed arrows icon, then drag to move around
- **Home**: Click the house icon to reset the view
- **Back/Forward**: Navigate through zoom history
- **Save**: Export the current graph as an image

## Notes

- The accumulation curves model the passive generation system (starts at 1:05)
- CS and damage contributions scale continuously with time based on your input rates
- Objective timing is simplified by distributing contributions linearly for visualization purposes
- All formulas are based on official League of Legends Season 2025 role quest data
- Each lane has different point requirements and CS multipliers reflecting unique quest mechanics

## Troubleshooting

**"ModuleNotFoundError: No module named 'tkinter'"**
- tkinter needs to be installed separately on some systems
- Linux: `sudo apt-get install python3-tk` (Ubuntu/Debian)
- The module should come pre-installed on Windows and macOS

**"ModuleNotFoundError: No module named 'matplotlib'"**
- Run: `pip install -r requirements.txt`
- If that fails, try: `pip install matplotlib numpy --user`

**Graph not displaying or window is blank**
- Make sure you're running Python 3.8 or higher
- Try updating matplotlib: `pip install --upgrade matplotlib`

**Performance issues or slow loading**
- This is normal on first launch as matplotlib initializes
- Subsequent calculations should be faster

## Customization

All conversion formulas are defined as constants at the top of each calculator file. If you want to adjust values for testing or as the game is patched, simply edit these constants:

```python
# Example from quest_timer_calculator_top.py
PASSIVE_POINTS_PER_MINUTE = 96
TOTAL_QUEST_POINTS = 1200
POINTS_PER_MINION_TOP = 2
# ... etc
```

## Credits

Calculators created for League of Legends Season 2025 role quest research and analysis.

Quest mechanics and point values sourced from official Riot Games documentation and in-game testing.

## License

These tools are provided for educational and analytical purposes. League of Legends and all related properties are trademarks of Riot Games, Inc.
