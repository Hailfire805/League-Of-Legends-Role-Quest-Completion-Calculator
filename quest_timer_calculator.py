"""
League of Legends MID LANE Role Quest Completion Time Calculator

This tool calculates the expected quest completion time based on player performance metrics
for MID LANE role quests.

All conversion formulas are defined as constants at the top for easy adjustment.

Author: Created for LoL Role Quest Research
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


# ============================================================================
# CONVERSION FORMULAS - MID LANE SPECIFIC
# ============================================================================

# Passive generation rate in mid lane (after 1:05)
# 8 points every 5 seconds = 96 points per minute
PASSIVE_POINTS_PER_MINUTE = 96

# Base quest completion requirement
TOTAL_QUEST_POINTS = 1350

# Quest generation start time
PASSIVE_START_TIME = 1 + 5/60  # 1:05 in minutes

# Base completion time with passive generation only
# = 1:05 startup + (1350 points / 96 points per min) = 1:05 + 14.06 min ≈ 15.1 min
BASE_COMPLETION_TIME = PASSIVE_START_TIME + \
    (TOTAL_QUEST_POINTS / PASSIVE_POINTS_PER_MINUTE)

# Point values for MID LANE from official data
POINTS_PER_KILL = 25  # Champion takedowns (HIGHER than other lanes)
POINTS_PER_MINION_MID = 2  # Minion kills in mid lane
POINTS_PER_MINION_OTHER = 1  # Minion kills in other lanes
POINTS_PER_TURRET_MID = 50  # Turret takedowns in mid lane
POINTS_PER_TURRET_OTHER = 25  # Turret takedowns in other lanes
POINTS_PER_PLATE_MID = 40  # Turret plates in mid lane
POINTS_PER_PLATE_OTHER = 20  # Turret plates in other lanes
POINTS_PER_EPIC = 30  # Epic monster takedowns

# Champion damage conversion (Mid lane specific)
DAMAGE_TO_POINTS_MELEE = 0.03  # 3% of damage dealt (melee)
DAMAGE_TO_POINTS_RANGED = 0.015  # 1.5% of damage dealt (ranged)


# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def calculate_points_from_cs(cs_in_mid, cs_in_other):
    """
    Calculate points from CS.

    Args:
        cs_in_mid: CS earned in mid lane
        cs_in_other: CS earned in other lanes

    Returns:
        Total points from CS
    """
    return (cs_in_mid * POINTS_PER_MINION_MID +
            cs_in_other * POINTS_PER_MINION_OTHER)


def calculate_points_from_objectives(plates_mid, plates_other, turrets_mid,
                                     turrets_other, kills, epic_monsters):
    """
    Calculate points from objectives and kills.

    Args:
        plates_mid: Turret plates in mid lane (0-5)
        plates_other: Turret plates in other lanes
        turrets_mid: Turrets destroyed in mid lane
        turrets_other: Turrets destroyed in other lanes
        kills: Champion takedowns
        epic_monsters: Epic monster takedowns

    Returns:
        Dictionary with breakdown of points
    """
    plates_points = (plates_mid * POINTS_PER_PLATE_MID +
                     plates_other * POINTS_PER_PLATE_OTHER)
    turret_points = (turrets_mid * POINTS_PER_TURRET_MID +
                     turrets_other * POINTS_PER_TURRET_OTHER)
    kill_points = kills * POINTS_PER_KILL
    epic_points = epic_monsters * POINTS_PER_EPIC

    return {
        'plates': plates_points,
        'turrets': turret_points,
        'kills': kill_points,
        'epic': epic_points,
        'total': plates_points + turret_points + kill_points + epic_points
    }


def calculate_points_from_damage(damage_dealt, is_melee):
    """
    Calculate points from champion damage (Mid lane specific).
    
    Args:
        damage_dealt: Total damage dealt to champions
        is_melee: Boolean indicating if champion is melee
        
    Returns:
        Points from damage
    """
    rate = DAMAGE_TO_POINTS_MELEE if is_melee else DAMAGE_TO_POINTS_RANGED
    return damage_dealt * rate


def calculate_passive_points(time_minutes):
    """
    Calculate passive points accumulated over time in mid lane.

    Args:
        time_minutes: Game time in minutes

    Returns:
        Total passive points at this time
    """
    if time_minutes <= PASSIVE_START_TIME:
        # No points before 1:05
        return 0

    # After 1:05: 96 points per minute
    time_after_start = time_minutes - PASSIVE_START_TIME
    points = PASSIVE_POINTS_PER_MINUTE * time_after_start

    return points


def calculate_completion_time(cs_per_min_mid, cs_per_min_other, damage_per_min,
                              is_melee, plates_mid, plates_other,
                              turrets_mid, turrets_other, kills, epic_monsters):
    """
    Calculate quest completion time given performance metrics.

    This function uses a binary search algorithm to find the exact time when the quest
    completes (reaches 1350 points). We use binary search because quest completion is
    an inverse problem: we know the target points (1350) and need to find the time.

    The quest point formula is:
        total_points(t) = passive_points(t) + cs_points(t) + damage_points(t) + objective_points

    Where:
        - passive_points(t): 96 points/min after 1:05 (time-dependent, non-linear)
        - cs_points(t): CS rate * time * points per CS (linear with time)
        - damage_points(t): Damage rate * time * conversion rate (linear with time)
        - objective_points: Fixed value (independent of time)

    Binary Search Strategy:
        - Search space: [1.083, 30.0] minutes (from passive start to max game time)
        - Convergence tolerance: 0.001 minutes (~0.06 seconds precision)
        - Invariant: At each iteration, the completion time lies in [low, high]
        - Terminates when high - low <= 0.001 minutes

    Args:
        cs_per_min_mid (float): Minion kills per minute in mid lane (typically 5-10)
        cs_per_min_other (float): Minion kills per minute in other lanes (typically 0-3)
        damage_per_min (float): Champion damage per minute (typically 300-1500)
        is_melee (bool): True if champion is melee (3% conversion), False if ranged (1.5%)
        plates_mid (int): Turret plates destroyed in mid lane (0-5)
        plates_other (int): Turret plates destroyed in other lanes (0-10)
        turrets_mid (int): Full turrets destroyed in mid lane (0-3)
        turrets_other (int): Full turrets destroyed in other lanes (0-8)
        kills (int): Champion takedowns (kills + assists)
        epic_monsters (int): Epic monster takedowns (dragons, heralds, barons)

    Returns:
        tuple: (completion_time, breakdown) where:
            - completion_time (float): Time in minutes when quest completes
            - breakdown (dict): Detailed point breakdown with keys:
                - 'cs_mid': Points from mid lane CS
                - 'cs_other': Points from other lane CS
                - 'cs_total': Total CS points
                - 'damage': Points from champion damage
                - 'plates': Points from turret plates
                - 'turrets': Points from full turrets
                - 'kills': Points from champion kills
                - 'epic': Points from epic monsters
                - 'active_total': Sum of all active point sources
                - 'passive_total': Passive generation points

    Example:
        >>> # Calculate for a typical mid lane game
        >>> time, breakdown = calculate_completion_time(
        ...     cs_per_min_mid=7.0,
        ...     cs_per_min_other=0.5,
        ...     damage_per_min=600,
        ...     is_melee=False,
        ...     plates_mid=2, plates_other=0,
        ...     turrets_mid=0, turrets_other=0,
        ...     kills=5, epic_monsters=1
        ... )
        >>> print(f"Quest completes at {time:.2f} minutes")
        Quest completes at 11.47 minutes
    """
    # Calculate points from objectives
    obj_breakdown = calculate_points_from_objectives(
        plates_mid, plates_other, turrets_mid, turrets_other, kills, epic_monsters
    )
    objective_points = obj_breakdown['total']

    # Binary search to find completion time where total points = TOTAL_QUEST_POINTS (1350)
    #
    # Why binary search?
    # - The point accumulation function is monotonically increasing (more time = more points)
    # - We need to solve for t in: f(t) = 1350, where f(t) is complex and non-linear
    # - Binary search converges in O(log n) iterations, typically 15-20 iterations
    #
    # Search bounds:
    # - low: PASSIVE_START_TIME (1.083 min) - earliest possible completion
    # - high: 30.0 min - conservative upper bound (games rarely go this long)
    # - tolerance: 0.001 min ≈ 0.06 seconds - more precision is unnecessary for game times
    low, high = PASSIVE_START_TIME, 30.0
    tolerance = 0.001

    while high - low > tolerance:
        mid = (low + high) / 2

        passive = calculate_passive_points(mid)
        cs_points = (cs_per_min_mid * mid * POINTS_PER_MINION_MID +
                     cs_per_min_other * mid * POINTS_PER_MINION_OTHER)
        damage_points = calculate_points_from_damage(
            damage_per_min * mid, is_melee)
        total_points = passive + cs_points + damage_points + objective_points

        if total_points < TOTAL_QUEST_POINTS:
            low = mid
        else:
            high = mid

    completion_time = (low + high) / 2

    # Calculate actual values at completion time
    final_cs_mid = cs_per_min_mid * completion_time
    final_cs_other = cs_per_min_other * completion_time
    final_damage = damage_per_min * completion_time
    
    cs_points = calculate_points_from_cs(final_cs_mid, final_cs_other)
    damage_points = calculate_points_from_damage(final_damage, is_melee)
    active_points = cs_points + damage_points + obj_breakdown['total']

    # Build detailed breakdown
    breakdown = {
        'cs_mid': final_cs_mid * POINTS_PER_MINION_MID,
        'cs_other': final_cs_other * POINTS_PER_MINION_OTHER,
        'cs_total': cs_points,
        'damage': damage_points,
        'plates': obj_breakdown['plates'],
        'turrets': obj_breakdown['turrets'],
        'kills': obj_breakdown['kills'],
        'epic': obj_breakdown['epic'],
        'active_total': active_points,
        'passive_total': calculate_passive_points(completion_time)
    }

    return completion_time, breakdown


def generate_accumulation_curve(cs_per_min_mid, cs_per_min_other, damage_per_min,
                                is_melee, plates_mid, plates_other, turrets_mid,
                                turrets_other, kills, epic_monsters, completion_time):
    """
    Generate point accumulation curve over time for visualization.

    This function creates 1000 data points representing how quest points accumulate from
    game start to beyond completion time. This data is used to plot the quest progress
    graph in the GUI.

    Visualization Strategy:
        The curve uses a LINEAR DISTRIBUTION model for simplicity and clarity in the graph:
        - CS and damage accumulate linearly with time (constant rates)
        - Objectives (plates, turrets, kills) are distributed linearly across the completion time
        - This is a SIMPLIFICATION for visualization - in reality, objectives happen discretely

    Why Linear Distribution?
        - Creates smooth, readable graphs that show overall point accumulation trends
        - Avoids step functions that would make comparison graphs cluttered
        - The completion time is accurate; the curve shape is illustrative
        - For planning purposes, knowing "when quest completes" matters more than exact event timing

    Args:
        cs_per_min_mid (float): Minion kills per minute in mid lane
        cs_per_min_other (float): Minion kills per minute in other lanes
        damage_per_min (float): Champion damage per minute
        is_melee (bool): True if champion is melee (affects damage conversion rate)
        plates_mid (int): Turret plates destroyed in mid lane
        plates_other (int): Turret plates destroyed in other lanes
        turrets_mid (int): Full turrets destroyed in mid lane
        turrets_other (int): Full turrets destroyed in other lanes
        kills (int): Champion takedowns (kills + assists)
        epic_monsters (int): Epic monster takedowns
        completion_time (float): Calculated quest completion time in minutes

    Returns:
        tuple: (time_points, quest_points) where:
            - time_points (np.ndarray): Array of 1000 time values from 0 to max_time
            - quest_points (np.ndarray): Array of 1000 quest point values at each time
            - max_time = max(completion_time, BASE_COMPLETION_TIME) + 1 minute

    Implementation Details:
        - Uses numpy.linspace to create 1000 evenly spaced time points
        - Calculates passive points at each time (kicks in after 1:05)
        - Scales active points (CS, damage, objectives) linearly by progress ratio
        - Progress ratio = min(current_time / completion_time, 1.0) ensures capping at 100%

    Example:
        >>> time_arr, points_arr = generate_accumulation_curve(
        ...     cs_per_min_mid=7.0, cs_per_min_other=0, damage_per_min=500,
        ...     is_melee=False, plates_mid=2, plates_other=0,
        ...     turrets_mid=0, turrets_other=0, kills=3, epic_monsters=1,
        ...     completion_time=12.5
        ... )
        >>> # time_arr and points_arr can now be plotted with matplotlib
        >>> plt.plot(time_arr, points_arr)
    """
    max_time = max(completion_time, BASE_COMPLETION_TIME) + 1
    time_points = np.linspace(0, max_time, 1000)
    quest_points = np.zeros_like(time_points)

    # Calculate totals at completion
    total_cs_mid = cs_per_min_mid * completion_time
    total_cs_other = cs_per_min_other * completion_time
    total_damage = damage_per_min * completion_time

    for i, t in enumerate(time_points):
        # Passive generation
        points = calculate_passive_points(t)

        # CS and damage contribution (scales linearly with time)
        if completion_time > 0:
            progress = min(t / completion_time, 1.0)
            cs_mid_at_time = total_cs_mid * progress
            cs_other_at_time = total_cs_other * progress
            damage_at_time = total_damage * progress
            
            points += calculate_points_from_cs(cs_mid_at_time, cs_other_at_time)
            points += calculate_points_from_damage(damage_at_time, is_melee)

            # Objectives (distributed linearly for visualization)
            obj_points = calculate_points_from_objectives(
                plates_mid * progress, plates_other * progress,
                turrets_mid * progress, turrets_other * progress,
                kills * progress, epic_monsters * progress
            )
            points += obj_points['total']

        quest_points[i] = points

    return time_points, quest_points


# ============================================================================
# GUI APPLICATION
# ============================================================================

class MidLaneQuestCalculatorGUI:
    def __init__(self, root):
        """
        Initialize the Mid Lane Quest Calculator GUI application.

        This constructor sets up the main application window and initializes the state
        management for scenario comparisons. The UI is constructed through the setup_ui()
        method, which creates all input fields, buttons, and the matplotlib graph canvas.

        Args:
            root (tk.Tk): The root Tkinter window object that will contain this application.
                         This should be an initialized Tk() instance.

        Attributes Created:
            root (tk.Tk): Reference to the main application window
            comparison_scenarios (list): Empty list to store comparison scenario data.
                                       Each scenario is a dict with keys:
                                       - 'time': numpy array of time points
                                       - 'points': numpy array of quest points at each time
                                       - 'label': string label for the scenario
                                       - 'completion_time': float completion time in minutes

        Side Effects:
            - Sets window title to "LoL MID LANE Quest Completion Calculator"
            - Sets window geometry to 1200x750 pixels
            - Calls setup_ui() to construct all UI elements

        Example:
            >>> root = tk.Tk()
            >>> app = MidLaneQuestCalculatorGUI(root)
            >>> root.mainloop()
        """
        self.root = root
        self.root.title("LoL MID LANE Quest Completion Calculator")
        self.root.geometry("1200x750")

        self.comparison_scenarios = []
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface."""

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(
            tk.W, tk.E, tk.N, tk.S))  # type: ignore

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Left panel: Input controls
        input_frame = ttk.LabelFrame(
            main_frame, text="MID LANE Performance Metrics", padding="10")
        input_frame.grid(row=0, column=0, sticky=(
            tk.W, tk.E, tk.N, tk.S), padx=(0, 10))  # pyright: ignore[reportArgumentType]

        # Right panel: Graph and results
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)

        # ---- Input Fields ----
        row = 0

        # Champion type section
        ttk.Label(input_frame, text="=== Champion Type ===", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, pady=(0, 5))
        row += 1

        self.is_melee = tk.BooleanVar(value=False)
        ttk.Radiobutton(input_frame, text="Melee (3% damage)", variable=self.is_melee,
                        value=True).grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(input_frame, text="Ranged (1.5% damage)", variable=self.is_melee,
                        value=False).grid(row=row, column=1, sticky=tk.W, pady=2)
        row += 1

        # CS section
        ttk.Label(input_frame, text="=== Creep Score ===", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1

        ttk.Label(input_frame, text="CS/min in Mid Lane:").grid(row=row,
                                                                column=0, sticky=tk.W, pady=5)
        self.cs_per_min_mid = tk.StringVar(value="7.0")
        ttk.Spinbox(input_frame, from_=0.0, to=12.0, textvariable=self.cs_per_min_mid,
                    width=15, increment=0.1).grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(input_frame, text="CS/min in Other Lanes:").grid(row=row,
                                                                   column=0, sticky=tk.W, pady=5)
        self.cs_per_min_other = tk.StringVar(value="0")
        ttk.Spinbox(input_frame, from_=0, to=12, textvariable=self.cs_per_min_other,
                    width=15, increment=0.1).grid(row=row, column=1, pady=5)
        row += 1

        # Champion damage section
        ttk.Label(input_frame, text="=== Champion Damage ===", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1

        ttk.Label(input_frame, text="Damage/min to Champions:").grid(row=row,
                                                                      column=0, sticky=tk.W, pady=5)
        self.damage_per_min = tk.StringVar(value="500")
        ttk.Spinbox(input_frame, from_=0, to=3000, textvariable=self.damage_per_min,
                    width=15, increment=50).grid(row=row, column=1, pady=5)
        row += 1

        # Turret plates section
        ttk.Label(input_frame, text="=== Turret Plates ===", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1

        ttk.Label(input_frame, text="Plates in Mid Lane:").grid(row=row,
                                                                column=0, sticky=tk.W, pady=5)
        self.plates_mid = tk.StringVar(value="0")
        ttk.Spinbox(input_frame, from_=0, to=10, textvariable=self.plates_mid,
                    width=13).grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(input_frame, text="Plates in Other Lanes:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.plates_other = tk.StringVar(value="0")
        ttk.Spinbox(input_frame, from_=0, to=10, textvariable=self.plates_other,
                    width=13).grid(row=row, column=1, pady=5)
        row += 1

        # Turrets section
        ttk.Label(input_frame, text="=== Turret Takedowns ===", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1

        ttk.Label(input_frame, text="Turrets in Mid Lane:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.turrets_mid = tk.StringVar(value="0")
        ttk.Spinbox(input_frame, from_=0, to=3, textvariable=self.turrets_mid,
                    width=15).grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(input_frame, text="Turrets in Other Lanes:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.turrets_other = tk.StringVar(value="0")
        ttk.Spinbox(input_frame, from_=0, to=3, textvariable=self.turrets_other,
                    width=15).grid(row=row, column=1, pady=5)
        row += 1

        # Objectives section
        ttk.Label(input_frame, text="=== Objectives & Kills ===", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1

        ttk.Label(input_frame, text="Champion Takedowns:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.kills = tk.StringVar(value="0")
        ttk.Spinbox(input_frame, from_=0, to=15, textvariable=self.kills,
                    width=15).grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(input_frame, text="Epic Monster Takedowns:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.epic_monsters = tk.StringVar(value="0")
        ttk.Spinbox(input_frame, from_=0, to=5, textvariable=self.epic_monsters,
                    width=15).grid(row=row, column=1, pady=5)
        row += 1

        # Separator
        ttk.Separator(input_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Calculate button
        ttk.Button(input_frame, text="Calculate Quest Time", command=self.calculate).grid(
            row=row, column=0, columnspan=2, pady=10
        )
        row += 1

        # Comparison buttons
        ttk.Button(input_frame, text="Add to Comparison", command=self.add_comparison).grid(
            row=row, column=0, columnspan=2, pady=5
        )
        row += 1

        ttk.Button(input_frame, text="Clear Comparisons", command=self.clear_comparisons).grid(
            row=row, column=0, columnspan=2, pady=5
        )
        row += 1

        # Results text area
        result_label_frame = ttk.LabelFrame(
            input_frame, text="Results", padding="10")
        result_label_frame.grid(row=row, column=0, columnspan=2, sticky=(
            tk.W, tk.E, tk.N, tk.S), pady=10)
        input_frame.rowconfigure(row, weight=1)

        self.results_text = tk.Text(
            result_label_frame, height=12, width=40, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(
            result_label_frame, orient='vertical', command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ---- Graph Area ----
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=output_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add matplotlib toolbar for zoom/pan
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar_frame = ttk.Frame(output_frame)
        toolbar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()

        self.plot_baseline()

    def plot_baseline(self):
        """Plot the baseline passive-only accumulation curve."""
        self.ax.clear()

        time_points = np.linspace(0, BASE_COMPLETION_TIME, 200)
        quest_points = np.array([calculate_passive_points(t)
                                for t in time_points])
        percentage_complete = (quest_points / TOTAL_QUEST_POINTS) * 100
        percentage_complete = np.minimum(100, percentage_complete)

        self.ax.plot(time_points, percentage_complete, '--', color='gray',
                     label=f'{int(BASE_COMPLETION_TIME * 60 // 60)}m{int(BASE_COMPLETION_TIME * 60 % 60)}s Passive Only (Mid Lane)', linewidth=2)
        self.ax.axhline(y=100, color='red', linestyle=':',
                        label='Quest Completion (1350 pts)', linewidth=2)

        self.ax.set_xlabel('Game Time (minutes)', fontsize=12)
        self.ax.set_ylabel('Quest Completion (%)', fontsize=12)
        self.ax.set_title('MID LANE Quest - Completion Progress',
                          fontsize=14, fontweight='bold')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

        self.canvas.draw()

    def get_inputs(self):
        """Retrieve and validate all input values."""
        cs_mid = 0
        cs_other = 0
        damage = 0
        plates_mid = 0
        plates_other = 0
        turrets_mid = 0
        turrets_other = 0
        kills = 0
        epic = 0

        try:
            cs_mid = float(self.cs_per_min_mid.get())
            cs_other = float(self.cs_per_min_other.get())
            damage = float(self.damage_per_min.get())
            plates_mid = int(self.plates_mid.get())
            plates_other = int(self.plates_other.get())
            turrets_mid = int(self.turrets_mid.get())
            turrets_other = int(self.turrets_other.get())
            kills = int(self.kills.get())
            epic = int(self.epic_monsters.get())

        except ValueError as e:
            print(f"Invalid input detected : {e}")

        # Validate all inputs
        if not 0 <= cs_mid:
            cs_mid = max(0, cs_mid)
        if not 0 <= cs_other:
            cs_other = max(0, cs_other)
        if not 0 <= damage:
            damage = max(0, damage)
        if not 0 <= plates_mid <= 10:
            plates_mid = max(0, plates_mid)
        if not 0 <= plates_other:
            plates_other = max(0, plates_other)
        if not 0 <= turrets_mid <= 10 or not 0 <= turrets_other <= 10:
            turrets_mid = max(0, turrets_mid)
            turrets_other = max(0, turrets_other)
        if not 0 <= kills:
            kills = max(0, kills)
        if not 0 <= epic <= 10:
            epic = max(0, epic)

        is_melee = self.is_melee.get()

        return cs_mid, cs_other, damage, is_melee, plates_mid, plates_other, turrets_mid, turrets_other, kills, epic

    def calculate(self):
        """Calculate and display quest completion time."""
        inputs = self.get_inputs()
        if inputs is None:
            return

        cs_mid, cs_other, damage, is_melee, plates_mid, plates_other, turrets_mid, turrets_other, kills, epic = inputs

        completion_time, breakdown = calculate_completion_time(
            cs_mid,  # CS per minute
            cs_other,  # CS per minute
            damage,  # Damage per minute
            is_melee,
            plates_mid, plates_other,
            turrets_mid, turrets_other,
            kills, epic
        )

        self.display_results(completion_time, breakdown, cs_mid, cs_other, damage, is_melee)
        self.plot_graph(cs_mid, cs_other, damage, is_melee, plates_mid, plates_other,
                        turrets_mid, turrets_other, kills, epic, completion_time)

    def display_results(self, completion_time, breakdown, cs_mid, cs_other, damage, is_melee):
        """Display calculation results in the text area."""
        self.results_text.delete(1.0, tk.END)

        minutes = int(completion_time * 60) // 60
        seconds = int(completion_time * 60) % 60

        champ_type = "Melee (3%)" if is_melee else "Ranged (1.5%)"

        results = f"Quest Completion Time: {minutes}m {seconds}s\n"
        results += "Points Breakdown:\n"
        results += "=" * 40 + "\n"
        results += f"CS in Mid Lane:      {breakdown['cs_mid']:.0f} pts\n"
        results += f"CS in Other Lanes:   {breakdown['cs_other']:.0f} pts\n"
        results += f"  Total CS:          {breakdown['cs_total']:.0f} pts\n\n"
        results += f"Champion Damage ({champ_type}): {breakdown['damage']:.0f} pts\n\n"
        results += f"Turret Plates:       {breakdown['plates']:.0f} pts\n"
        results += f"Turret Takedowns:    {breakdown['turrets']:.0f} pts\n"
        results += f"Champion Kills:      {breakdown['kills']:.0f} pts\n"
        results += f"Epic Monsters:       {breakdown['epic']:.0f} pts\n"
        results += "=" * 40 + "\n"
        results += f"Active Points:       {breakdown['active_total']:.0f} pts\n"
        results += f"Passive Points:      {breakdown['passive_total']:.0f} pts\n"
        results += f"TOTAL:               {breakdown['active_total'] + breakdown['passive_total']:.0f} pts\n\n"

        # Time saved calculation
        time_saved = int((BASE_COMPLETION_TIME - completion_time) * 60) // 60
        time_saved_seconds = int(
            (BASE_COMPLETION_TIME - completion_time) * 60 % 60)
        results += f"Time Saved: {time_saved}m {time_saved_seconds}s\n"

        self.results_text.insert(1.0, results)

    def plot_graph(self, cs_mid, cs_other, damage, is_melee, plates_mid, plates_other,
                   turrets_mid, turrets_other, kills, epic, completion_time):
        """Plot the quest accumulation curve."""
        self.ax.clear()

        # Plot baseline
        time_baseline = np.linspace(0, BASE_COMPLETION_TIME, 200)
        points_baseline = np.array(
            [calculate_passive_points(t) for t in time_baseline])
        percentage_baseline = (points_baseline / TOTAL_QUEST_POINTS) * 100
        percentage_baseline = np.minimum(100, percentage_baseline)

        self.ax.plot(time_baseline, percentage_baseline, '--', color='gray',
                     label=f'{int(BASE_COMPLETION_TIME * 60 // 60)}m{int(BASE_COMPLETION_TIME * 60 % 60)}s Passive Only', linewidth=2, alpha=0.7, zorder=1)

        # Plot comparison scenarios first
        colors = ['green', 'orange', 'purple',
                  'brown', 'pink', 'cyan', 'olive', 'navy']
        for i, scenario in enumerate(self.comparison_scenarios):
            color = colors[i % len(colors)]
            scenario_percentage = (
                scenario['points'] / TOTAL_QUEST_POINTS) * 100
            scenario_percentage = np.minimum(100, scenario_percentage)
            self.ax.plot(scenario['time'], scenario_percentage, '-',
                         color=color, label=scenario['label'], linewidth=2, alpha=0.7, zorder=2)

        # Plot current scenario on top
        time_points, quest_points = generate_accumulation_curve(
            cs_mid, cs_other, damage, is_melee, plates_mid, plates_other,
            turrets_mid, turrets_other, kills, epic, completion_time
        )
        percentage_complete = (quest_points / TOTAL_QUEST_POINTS) * 100
        percentage_complete = np.minimum(100, percentage_complete)
        minutes = int(completion_time * 60) // 60
        seconds = int(completion_time * 60) % 60
        self.ax.plot(time_points, percentage_complete, '-', color='#0066FF',
                     label=f"{minutes}m{seconds}s Current", linewidth=3, zorder=3)

        # Quest completion threshold
        self.ax.axhline(y=100, color='red', linestyle=':',
                        label='Quest Completion', linewidth=2, zorder=0)

        self.ax.set_xlabel('Game Time (minutes)', fontsize=12)
        self.ax.set_ylabel('Quest Completion (%)', fontsize=12)
        self.ax.set_title('MID LANE Quest - Completion Progress',
                          fontsize=14, fontweight='bold')
        self.ax.legend(loc='best', framealpha=0.9)
        self.ax.grid(True, alpha=0.3)

        self.ax.set_xlim(0, max(BASE_COMPLETION_TIME, completion_time) + 1)
        self.ax.set_ylim(-5, 110)

        self.canvas.draw()

    def add_comparison(self):
        """Add current scenario to comparison list."""
        inputs = self.get_inputs()
        if inputs is None:
            return

        cs_mid, cs_other, damage, is_melee, plates_mid, plates_other, turrets_mid, turrets_other, kills, epic = inputs

        completion_time, _ = calculate_completion_time(
            cs_mid, cs_other, damage, is_melee,
            plates_mid, plates_other,
            turrets_mid, turrets_other,
            kills, epic
        )

        time_points, quest_points = generate_accumulation_curve(
            cs_mid, cs_other, damage, is_melee, plates_mid, plates_other,
            turrets_mid, turrets_other, kills, epic, completion_time
        )

        # Build default label
        minutes = int(completion_time)
        seconds = int((completion_time - minutes) * 60)

        label_parts = [f"{minutes}m{seconds}s"]

        total_cs = cs_mid + cs_other
        if total_cs > 0:
            label_parts.append(f"{total_cs:.1f} CS/Min")

        if damage > 0:
            label_parts.append(f"{int(damage)} DPM")

        if kills > 0:
            label_parts.append(f"{kills} KP")

        total_plates = plates_mid + plates_other
        if total_plates > 0:
            label_parts.append(f"{int(total_plates)} Plates")

        if epic > 0:
            label_parts.append(f"{epic} Epics")

        champ_type = "M" if is_melee else "R"
        label_parts.append(champ_type)

        default_label = " ".join(label_parts)

        # Create custom dialog for label input
        dialog = tk.Toplevel(self.root)
        dialog.title("Label Comparison Scenario")
        dialog.geometry("450x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Enter a label for this scenario:",
                  font=('TkDefaultFont', 10)).pack(pady=10)

        label_var = tk.StringVar(value=default_label)
        entry = ttk.Entry(dialog, textvariable=label_var, width=60)
        entry.pack(pady=10)
        entry.select_range(0, tk.END)
        entry.focus()

        def on_ok():
            """
            Dialog callback for OK button - saves comparison scenario and closes dialog.

            This nested function is a closure that captures variables from add_comparison():
            - time_points: numpy array of time values for the curve
            - quest_points: numpy array of point values for the curve
            - completion_time: calculated quest completion time
            - label_var: tkinter StringVar containing user's custom label
            - default_label: auto-generated label as fallback

            Behavior:
                1. Retrieves and sanitizes the user's label (falls back to default if empty)
                2. Appends scenario dict to self.comparison_scenarios list
                3. Destroys the dialog window
                4. Recalculates and redraws the graph with the new comparison line
                5. Shows confirmation messagebox with total scenario count

            Side Effects:
                - Modifies self.comparison_scenarios (appends new dict)
                - Closes dialog window
                - Triggers graph redraw via self.calculate()
                - Displays info messagebox
            """
            label = label_var.get().strip()
            if not label:
                label = default_label

            self.comparison_scenarios.append({
                'time': time_points,
                'points': quest_points,
                'label': label,
                'completion_time': completion_time
            })

            dialog.destroy()
            self.calculate()
            messagebox.showinfo(
                "Added", f"Scenario added (Total: {len(self.comparison_scenarios)})")

        def on_cancel():
            """
            Dialog callback for Cancel button - closes dialog without saving.

            This nested function is a closure that captures the dialog window reference.
            It provides a clean way to dismiss the label input dialog when the user
            clicks Cancel or presses Escape.

            Behavior:
                - Simply destroys the dialog window
                - Does NOT modify self.comparison_scenarios
                - Does NOT trigger graph redraw
                - Does NOT show any messagebox

            Side Effects:
                - Closes dialog window (no other side effects)
            """
            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="OK", command=on_ok).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel",
                   command=on_cancel).pack(side=tk.LEFT, padx=5)

        entry.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())

    def clear_comparisons(self):
        """Clear all comparison scenarios."""
        self.comparison_scenarios = []
        self.calculate()
        messagebox.showinfo("Cleared", "All comparison scenarios removed")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """
    Main entry point for the Mid Lane Quest Calculator application.

    This function initializes and launches the Tkinter GUI application. It creates
    the root window, instantiates the calculator GUI, and starts the main event loop.

    Execution Flow:
        1. Creates the root Tkinter window (tk.Tk())
        2. Instantiates MidLaneQuestCalculatorGUI with the root window
           - This triggers __init__ which sets up all UI elements
        3. Starts the Tkinter event loop (root.mainloop())
           - Blocks until the user closes the window
           - Handles all user interactions, button clicks, graph updates

    Usage:
        This function is called when the script is executed directly:
        $ python quest_timer_calculator.py

        Or programmatically:
        >>> from quest_timer_calculator import main
        >>> main()  # Opens the GUI application

    Application Lifecycle:
        - Program starts → main() is called
        - Root window created → GUI initialized
        - Event loop runs → user interacts with calculator
        - Window closed → event loop exits → program terminates

    Side Effects:
        - Creates and displays a 1200x750 GUI window
        - Blocks execution until window is closed
        - May show messageboxes for validation errors or confirmations

    Returns:
        None (implicitly when window is closed)

    Notes:
        - This is a blocking call - the function won't return until the GUI is closed
        - The application handles all exceptions internally with messageboxes
        - No command-line arguments are processed
    """
    root = tk.Tk()
    app = MidLaneQuestCalculatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
