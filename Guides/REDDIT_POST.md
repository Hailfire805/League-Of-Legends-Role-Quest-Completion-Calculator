# [Tool] I made a calculator that tells you exactly when your Role Quest completes

**What it does:** Input your typical stats (CS/min, kills, plates, etc.) and it calculates your exact quest completion time with a visual graph.

**Why I made this:** Got tired of wondering "when will my quest actually finish?" Wanted to see how different playstyles affect completion time.

## Key Features

- Separate calculators for Top/Mid/Bot with accurate point values
- Visual graph showing completion % over time
- Compare multiple scenarios side-by-side (e.g., "farm heavy" vs "roam heavy")
- Custom labels for your comparisons
- Interactive zoom to see specific time ranges

## Example Results



The graph makes it really easy to visualize - you can see exactly when each playstyle hits 100%.

## How Quest Mechanics Work

**Top:** 1200 points needed, 96 pts/min passive (starting 1:05), 2 pts per CS in lane
**Bot:** 1350 points, 96 pts/min passive, 3 pts per CS in lane
**Mid:** 1350 points, 25 pts per kill (higher!), champion damage bonus

*Important:* Passive generation only works IN your lane - roaming slows your quest

## Installation

**Easy way:**
1. Download zip from [link]
2. Extract and double-click `launch.bat` (Windows) or `launch.sh` (Mac/Linux)
3. Done - it auto-installs everything

**Manual:**
```bash
pip install -r requirements.txt
python launcher.py
```

Needs Python 3.8+, which most people already have.

## Download

[Your hosting link here - GitHub, Google Drive, etc.]

## Screenshots

[Image 1: Main calculator interface]
[Image 2: Graph with multiple comparison scenarios]

---

Built this for my own use but figured others might find it helpful. Open source, all the quest formulas are in the code if you want to verify accuracy.

Let me know if you find any bugs or have suggestions!
