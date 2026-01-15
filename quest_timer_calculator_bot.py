"""
League of Legends BOT LANE Role Quest Completion Time Calculator

This tool calculates the expected quest completion time based on player performance metrics
for BOT LANE role quests.

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
# CONVERSION FORMULAS - BOT LANE SPECIFIC
# ============================================================================

# Passive generation rate in bot lane (after 1:05)
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

# Point values for BOT LANE from official data
POINTS_PER_KILL = 15  # Champion takedowns
POINTS_PER_MINION_BOT = 3  # Minion kills in bot lane
POINTS_PER_MINION_OTHER = 1.5  # Minion kills in other lanes
POINTS_PER_TURRET_BOT = 50  # Turret takedowns in bot lane
POINTS_PER_TURRET_OTHER = 25  # Turret takedowns in other lanes
POINTS_PER_PLATE_BOT = 40  # Turret plates in bot lane
POINTS_PER_PLATE_OTHER = 20  # Turret plates in other lanes
POINTS_PER_EPIC = 30  # Epic monster takedowns


# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def calculate_points_from_cs(cs_in_bot, cs_in_other):
    """
    Calculate points from CS.

    Args:
        cs_in_bot: CS earned in bot lane
        cs_in_other: CS earned in other lanes

    Returns:
        Total points from CS
    """
    return (cs_in_bot * POINTS_PER_MINION_BOT +
            cs_in_other * POINTS_PER_MINION_OTHER)


def calculate_points_from_objectives(plates_bot, plates_other, turrets_bot,
                                     turrets_other, kills, epic_monsters):
    """
    Calculate points from objectives and kills.

    Args:
        plates_bot: Turret plates in bot lane (0-5)
        plates_other: Turret plates in other lanes
        turrets_bot: Turrets destroyed in bot lane
        turrets_other: Turrets destroyed in other lanes
        kills: Champion takedowns
        epic_monsters: Epic monster takedowns

    Returns:
        Dictionary with breakdown of points
    """
    plates_points = (plates_bot * POINTS_PER_PLATE_BOT +
                     plates_other * POINTS_PER_PLATE_OTHER)
    turret_points = (turrets_bot * POINTS_PER_TURRET_BOT +
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


def calculate_passive_points(time_minutes):
    """
    Calculate passive points accumulated over time in bot lane.

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


def calculate_completion_time(cs_per_min_bot, cs_per_min_other, plates_bot, plates_other,
                              turrets_bot, turrets_other, kills, epic_monsters):
    """
    Calculate quest completion time given performance metrics.

    Args:
        cs_per_min_bot: CS per minute in bot lane
        cs_per_min_other: CS per minute in other lanes
        plates_bot: Turret plates in bot lane (0-5)
        plates_other: Turret plates in other lanes
        turrets_bot: Turrets destroyed in bot lane
        turrets_other: Turrets destroyed in other lanes
        kills: Champion takedowns
        epic_monsters: Epic monster takedowns

    Returns:
        Tuple of (completion_time, points_breakdown)
    """
    # Calculate points from objectives (these don't depend on time)
    obj_breakdown = calculate_points_from_objectives(
        plates_bot, plates_other, turrets_bot, turrets_other, kills, epic_monsters
    )
    objective_points = obj_breakdown['total']

    # We need to find time t where:
    # passive_points(t) + cs_points(t) + objective_points = TOTAL_QUEST_POINTS
    # Where cs_points(t) = (cs_per_min_bot * t * POINTS_PER_MINION_BOT) + (cs_per_min_other * t * POINTS_PER_MINION_OTHER)

    # Use binary search to find completion time
    low, high = PASSIVE_START_TIME, 30.0  # Search between 1:05 and 30 minutes
    tolerance = 0.001  # 0.001 minute precision (~0.06 seconds)

    while high - low > tolerance:
        mid = (low + high) / 2

        # Calculate points at this time
        passive = calculate_passive_points(mid)

        # CS accumulated up to this time
        time_farming = mid  # Time spent in game
        cs_points = (cs_per_min_bot * time_farming * POINTS_PER_MINION_BOT +
                     cs_per_min_other * time_farming * POINTS_PER_MINION_OTHER)

        total_points = passive + cs_points + objective_points

        if total_points < TOTAL_QUEST_POINTS:
            low = mid
        else:
            high = mid

    completion_time = (low + high) / 2

    # Build detailed breakdown at completion time
    final_cs_bot_total = cs_per_min_bot * completion_time
    final_cs_other_total = cs_per_min_other * completion_time

    breakdown = {
        'cs_bot': final_cs_bot_total * POINTS_PER_MINION_BOT,
        'cs_other': final_cs_other_total * POINTS_PER_MINION_OTHER,
        'cs_total': (final_cs_bot_total * POINTS_PER_MINION_BOT +
                     final_cs_other_total * POINTS_PER_MINION_OTHER),
        'plates': obj_breakdown['plates'],
        'turrets': obj_breakdown['turrets'],
        'kills': obj_breakdown['kills'],
        'epic': obj_breakdown['epic'],
        'active_total': (final_cs_bot_total * POINTS_PER_MINION_BOT +
                         final_cs_other_total * POINTS_PER_MINION_OTHER +
                         obj_breakdown['total']),
        'passive_total': calculate_passive_points(completion_time)
    }

    return completion_time, breakdown


def generate_accumulation_curve(cs_per_min_bot, cs_per_min_other, plates_bot,
                                plates_other, turrets_bot, turrets_other,
                                kills, epic_monsters, completion_time):
    """
    Generate point accumulation curve over time.

    Returns:
        Tuple of (time_array, points_array) for plotting
    """
    max_time = max(completion_time, BASE_COMPLETION_TIME) + 1
    time_points = np.linspace(0, max_time, 1000)
    quest_points = np.zeros_like(time_points)

    # Calculate total CS and objectives at completion
    total_cs_bot = cs_per_min_bot * completion_time
    total_cs_other = cs_per_min_other * completion_time

    for i, t in enumerate(time_points):
        # Passive generation (with bot lane boost)
        points = calculate_passive_points(t)

        # CS contribution (scales linearly with time)
        if completion_time > 0:
            progress = min(t / completion_time, 1.0)
            cs_bot_at_time = total_cs_bot * progress
            cs_other_at_time = total_cs_other * progress
            points += calculate_points_from_cs(cs_bot_at_time,
                                               cs_other_at_time)

            # Objectives (distributed linearly for visualization)
            obj_points = calculate_points_from_objectives(
                plates_bot * progress, plates_other * progress,
                turrets_bot * progress, turrets_other * progress,
                kills * progress, epic_monsters * progress
            )
            points += obj_points['total']

        quest_points[i] = points

    return time_points, quest_points


# ============================================================================
# GUI APPLICATION
# ============================================================================

class BotLaneQuestCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LoL BOT LANE Quest Completion Calculator")
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
            main_frame, text="BOT LANE Performance Metrics", padding="10")
        input_frame.grid(row=0, column=0, sticky=(
            tk.W, tk.E, tk.N, tk.S), padx=(0, 10))  # pyright: ignore[reportArgumentType]

        # Right panel: Graph and results
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)

        # ---- Input Fields ----
        row = 0

        # CS section
        ttk.Label(input_frame, text="=== Creep Score ===", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, pady=(0, 5))
        row += 1

        ttk.Label(input_frame, text="CS/min in Bot Lane:").grid(row=row,
                                                                column=0, sticky=tk.W, pady=5)
        self.cs_per_min_bot = tk.StringVar(value="7.0")
        ttk.Spinbox(input_frame, from_=0.0, to=12.0, textvariable=self.cs_per_min_bot,
                    width=15, increment=0.1).grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(input_frame, text="CS/min in Other Lanes:").grid(row=row,
                                                                   column=0, sticky=tk.W, pady=5)
        self.cs_per_min_other = tk.StringVar(value="0")
        ttk.Spinbox(input_frame, from_=0, to=12, textvariable=self.cs_per_min_other,
                    width=15, increment=0.1).grid(row=row, column=1, pady=5)
        row += 1

        # Turret plates section
        ttk.Label(input_frame, text="=== Turret Plates ===", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1

        ttk.Label(input_frame, text="Plates in Bot Lane:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.plates_bot = tk.StringVar(value="0")
        ttk.Spinbox(input_frame, from_=0, to=10, textvariable=self.plates_bot,
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

        ttk.Label(input_frame, text="Turrets in Bot Lane:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.turrets_bot = tk.StringVar(value="0")
        ttk.Spinbox(input_frame, from_=0, to=3, textvariable=self.turrets_bot,
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
                     label=f'{int(BASE_COMPLETION_TIME * 60 // 60)}m{int(BASE_COMPLETION_TIME * 60 % 60)}s Passive Only (Bot Lane)', linewidth=2)
        self.ax.axhline(y=100, color='red', linestyle=':',
                        label='Quest Completion (1350 pts)', linewidth=2)

        self.ax.set_xlabel('Game Time (minutes)', fontsize=12)
        self.ax.set_ylabel('Quest Completion (%)', fontsize=12)
        self.ax.set_title('BOT LANE Quest - Completion Progress',
                          fontsize=14, fontweight='bold')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

        self.canvas.draw()

    def get_inputs(self):
        """Retrieve and validate all input values."""
        try:
            cs_bot = float(self.cs_per_min_bot.get())
            cs_other = float(self.cs_per_min_other.get())
            plates_bot = int(self.plates_bot.get())
            plates_other = int(self.plates_other.get())
            turrets_bot = int(self.turrets_bot.get())
            turrets_other = int(self.turrets_other.get())
            kills = int(self.kills.get())
            epic = int(self.epic_monsters.get())

            if cs_bot < 0 or cs_other < 0:
                raise ValueError("CS per minute cannot be negative")
            if not 0 <= plates_bot <= 5:
                raise ValueError("Bot lane plates must be between 0 and 5")
            if plates_other < 0 or turrets_bot < 0 or turrets_other < 0:
                raise ValueError("Objective values cannot be negative")
            if kills < 0 or epic < 0:
                raise ValueError("Kills and epic monsters cannot be negative")

            return cs_bot, cs_other, plates_bot, plates_other, turrets_bot, turrets_other, kills, epic

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return None

    def calculate(self):
        """Calculate and display quest completion time."""
        inputs = self.get_inputs()
        if inputs is None:
            return

        cs_bot, cs_other, plates_bot, plates_other, turrets_bot, turrets_other, kills, epic = inputs

        # Pass CS rates (per minute), not totals
        completion_time, breakdown = calculate_completion_time(
            cs_bot,  # CS per minute
            cs_other,  # CS per minute
            plates_bot, plates_other,
            turrets_bot, turrets_other,
            kills, epic
        )

        self.display_results(completion_time, breakdown, cs_bot, cs_other)
        self.plot_graph(cs_bot, cs_other, plates_bot, plates_other,
                        turrets_bot, turrets_other, kills, epic, completion_time)

    def display_results(self, completion_time, breakdown, cs_bot, cs_other):
        """Display calculation results in the text area."""
        self.results_text.delete(1.0, tk.END)

        minutes = int(completion_time)
        seconds = int((completion_time - minutes) * 60)

        results = f"Quest Completion Time: {minutes}m {seconds}s\n"
        results += f"({completion_time:.2f} minutes)\n\n"
        results += "Points Breakdown:\n"
        results += "=" * 40 + "\n"
        results += f"CS in Bot Lane:      {breakdown['cs_bot']:.0f} pts\n"
        results += f"CS in Other Lanes:   {breakdown['cs_other']:.0f} pts\n"
        results += f"  Total CS:          {breakdown['cs_total']:.0f} pts\n\n"
        results += f"Turret Plates:       {breakdown['plates']:.0f} pts\n"
        results += f"Turret Takedowns:    {breakdown['turrets']:.0f} pts\n"
        results += f"Champion Kills:      {breakdown['kills']:.0f} pts\n"
        results += f"Epic Monsters:       {breakdown['epic']:.0f} pts\n"
        results += "=" * 40 + "\n"
        results += f"Active Points:       {breakdown['active_total']:.0f} pts\n"
        results += f"Passive Points:      {breakdown['passive_total']:.0f} pts\n"
        results += f"TOTAL:               {breakdown['active_total'] + breakdown['passive_total']:.0f} pts\n\n"

        # Time saved calculation
        time_saved = BASE_COMPLETION_TIME - completion_time
        time_saved_seconds = int(time_saved * 60)
        results += f"Time Saved: {time_saved:.2f} min ({time_saved_seconds}s)\n"

        self.results_text.insert(1.0, results)

    def plot_graph(self, cs_bot, cs_other, plates_bot, plates_other,
                   turrets_bot, turrets_other, kills, epic, completion_time):
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

        # Plot comparison scenarios first (so they appear behind current scenario)
        colors = ['green', 'orange', 'purple',
                  'brown', 'pink', 'cyan', 'olive', 'navy']
        for i, scenario in enumerate(self.comparison_scenarios):
            color = colors[i % len(colors)]
            scenario_percentage = (
                scenario['points'] / TOTAL_QUEST_POINTS) * 100
            scenario_percentage = np.minimum(100, scenario_percentage)
            self.ax.plot(scenario['time'], scenario_percentage, '-',
                         color=color, label=scenario['label'], linewidth=2, alpha=0.7, zorder=2)

        # Plot current scenario on top with bright blue
        time_points, quest_points = generate_accumulation_curve(
            cs_bot, cs_other, plates_bot, plates_other,
            turrets_bot, turrets_other, kills, epic, completion_time
        )
        percentage_complete = (quest_points / TOTAL_QUEST_POINTS) * 100
        percentage_complete = np.minimum(100, percentage_complete)

        self.ax.plot(time_points, percentage_complete, '-', color='#0066FF',
                     label='Current Scenario', linewidth=3, zorder=3)

        # Quest completion threshold (now at y=100%)
        self.ax.axhline(y=100, color='red', linestyle=':',
                        label='Quest Completion', linewidth=2, zorder=0)

        # Mark completion point
        if completion_time <= max(time_points):
            self.ax.plot(completion_time, 100, 'o', color='red', markersize=10,
                         label=f'Completion: {completion_time:.2f}m', zorder=4)

        self.ax.set_xlabel('Game Time (minutes)', fontsize=12)
        self.ax.set_ylabel('Quest Completion (%)', fontsize=12)
        self.ax.set_title('BOT LANE Quest - Completion Progress',
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

        cs_bot, cs_other, plates_bot, plates_other, turrets_bot, turrets_other, kills, epic = inputs

        completion_time, _ = calculate_completion_time(
            cs_bot * BASE_COMPLETION_TIME,
            cs_other * BASE_COMPLETION_TIME,
            plates_bot, plates_other,
            turrets_bot, turrets_other,
            kills, epic
        )

        time_points, quest_points = generate_accumulation_curve(
            cs_bot, cs_other, plates_bot, plates_other,
            turrets_bot, turrets_other, kills, epic, completion_time
        )

        # Build default label with smart formatting
        minutes = int(completion_time)
        seconds = int((completion_time - minutes) * 60)

        label_parts = [f"{minutes}m{seconds}s"]

        # Total CS/Min (bot + other)
        total_cs = cs_bot + cs_other
        if total_cs > 0:
            label_parts.append(f"{total_cs:.1f} CS/Min")

        if kills > 0:
            label_parts.append(f"{kills} KP")

        # Total plates (bot + other lanes)
        total_plates = plates_bot + plates_other
        if total_plates > 0:
            label_parts.append(f"{int(total_plates)} Plates")

        if epic > 0:
            label_parts.append(f"{epic} Epics")

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
            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="OK", command=on_ok).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel",
                   command=on_cancel).pack(side=tk.LEFT, padx=5)

        # Bind Enter key to OK
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
    root = tk.Tk()
    app = BotLaneQuestCalculatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
