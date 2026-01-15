"""
League of Legends Role Quest Completion Time Calculator

This tool calculates the expected quest completion time based on player performance metrics.
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
# CONVERSION FORMULAS - Update these values as your research progresses
# ============================================================================

# Passive generation rate (points per minute when not in lane)
PASSIVE_POINTS_PER_MINUTE = 100

# Base quest completion time with passive generation only (minutes)
BASE_COMPLETION_TIME = 14

# Total points needed to complete quest (derived from passive rate * base time)
TOTAL_QUEST_POINTS = PASSIVE_POINTS_PER_MINUTE * BASE_COMPLETION_TIME

# Time reduction per game event (in seconds)
TIME_REDUCTION_PER_WAVE = 8  # Full minion wave (6 minions)
TIME_REDUCTION_PER_40_CS = 48  # 40 CS worth of minions
TIME_REDUCTION_PER_KILL = 15  # Champion takedown
TIME_REDUCTION_PER_EPIC = 18  # Epic monster (dragon, baron, etc.)
TIME_REDUCTION_PER_PLATE = 24  # Turret plate
TIME_REDUCTION_PER_TURRET = 30  # Full turret destruction

# Mid lane damage conversion (per 1000 damage dealt to champions)
TIME_REDUCTION_PER_1K_DAMAGE_MELEE = 19  # Melee mid laner
TIME_REDUCTION_PER_1K_DAMAGE_RANGED = 9  # Ranged mid laner

# Derived conversions
CS_TO_TIME_REDUCTION = TIME_REDUCTION_PER_40_CS / 40  # Seconds per CS (~1.2 seconds)


# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def calculate_time_reduction(cs_per_min, damage_per_min, plates, turret_destroyed, 
                            kills, epic_monsters, is_melee, game_duration=14):
    """
    Calculate total time reduction from all sources.
    
    Args:
        cs_per_min: Creep score per minute (float)
        damage_per_min: Champion damage per minute (float)
        plates: Number of turret plates secured (0-5)
        turret_destroyed: Boolean indicating if turret was destroyed
        kills: Number of champion takedowns (int)
        epic_monsters: Number of epic monster takedowns (int)
        is_melee: Boolean indicating if champion is melee
        game_duration: Expected game duration in minutes for CS calculation
        
    Returns:
        Dictionary containing breakdown of time reductions and total
    """
    
    # Calculate time reduction from CS
    total_cs = cs_per_min * game_duration
    cs_reduction = total_cs * CS_TO_TIME_REDUCTION
    
    # Calculate time reduction from champion damage (mid lane mechanic)
    # Damage is per minute, so total damage = damage_per_min * game_duration
    total_damage = damage_per_min * game_duration
    damage_thousands = total_damage / 1000
    
    if is_melee:
        damage_reduction = damage_thousands * TIME_REDUCTION_PER_1K_DAMAGE_MELEE
    else:
        damage_reduction = damage_thousands * TIME_REDUCTION_PER_1K_DAMAGE_RANGED
    
    # Calculate time reduction from objectives
    plates_reduction = plates * TIME_REDUCTION_PER_PLATE
    turret_reduction = TIME_REDUCTION_PER_TURRET if turret_destroyed else 0
    
    # Calculate time reduction from kills
    kills_reduction = kills * TIME_REDUCTION_PER_KILL
    epic_reduction = epic_monsters * TIME_REDUCTION_PER_EPIC
    
    # Total time reduction
    total_reduction = (cs_reduction + damage_reduction + plates_reduction + 
                      turret_reduction + kills_reduction + epic_reduction)
    
    return {
        'cs': cs_reduction,
        'damage': damage_reduction,
        'plates': plates_reduction,
        'turret': turret_reduction,
        'kills': kills_reduction,
        'epic_monsters': epic_reduction,
        'total': total_reduction
    }


def calculate_completion_time(time_reduction_seconds):
    """
    Calculate quest completion time given total time reduction.
    
    Args:
        time_reduction_seconds: Total time reduction in seconds
        
    Returns:
        Completion time in minutes (float)
    """
    base_time_seconds = BASE_COMPLETION_TIME * 60
    completion_time_seconds = base_time_seconds - time_reduction_seconds
    
    # Ensure we don't go below 0
    completion_time_seconds = max(0, completion_time_seconds)
    
    return completion_time_seconds / 60


def generate_accumulation_curve(cs_per_min, damage_per_min, plates, turret_destroyed,
                                kills, epic_monsters, is_melee, completion_time):
    """
    Generate point accumulation curve over time.
    
    This models how quest points accumulate during a game, accounting for:
    - Passive generation (constant rate)
    - CS generation (increases linearly with CS/min rate)
    - Damage dealt (increases linearly with damage/min rate)
    - Objective events (discrete jumps at assumed times)
    
    Args:
        Same as calculate_time_reduction, plus completion_time
        
    Returns:
        Tuple of (time_array, points_array) for plotting
    """
    
    # Create time array from 0 to completion time (or 14 min baseline)
    max_time = max(completion_time, BASE_COMPLETION_TIME)
    time_points = np.linspace(0, max_time, 1000)
    quest_points = np.zeros_like(time_points)
    
    for i, t in enumerate(time_points):
        # Passive generation
        points = PASSIVE_POINTS_PER_MINUTE * t
        
        # CS contribution (scales with time)
        cs_at_time = cs_per_min * t
        cs_points = cs_at_time * CS_TO_TIME_REDUCTION * PASSIVE_POINTS_PER_MINUTE / 60
        points += cs_points
        
        # Damage contribution (scales with time)
        damage_at_time = damage_per_min * t
        damage_thousands = damage_at_time / 1000
        if is_melee:
            damage_points = damage_thousands * TIME_REDUCTION_PER_1K_DAMAGE_MELEE * PASSIVE_POINTS_PER_MINUTE / 60
        else:
            damage_points = damage_thousands * TIME_REDUCTION_PER_1K_DAMAGE_RANGED * PASSIVE_POINTS_PER_MINUTE / 60
        points += damage_points
        
        # Objective contributions (simplified: assume evenly distributed)
        # In reality, these would be discrete jumps at specific times
        # For visualization purposes, we distribute them linearly
        if t > 0:
            objectives_progress = min(t / completion_time, 1.0) if completion_time > 0 else 0
            
            plates_points = plates * TIME_REDUCTION_PER_PLATE * PASSIVE_POINTS_PER_MINUTE / 60 * objectives_progress
            turret_points = (TIME_REDUCTION_PER_TURRET if turret_destroyed else 0) * PASSIVE_POINTS_PER_MINUTE / 60 * objectives_progress
            kills_points = kills * TIME_REDUCTION_PER_KILL * PASSIVE_POINTS_PER_MINUTE / 60 * objectives_progress
            epic_points = epic_monsters * TIME_REDUCTION_PER_EPIC * PASSIVE_POINTS_PER_MINUTE / 60 * objectives_progress
            
            points += plates_points + turret_points + kills_points + epic_points
        
        quest_points[i] = points
    
    return time_points, quest_points


# ============================================================================
# GUI APPLICATION
# ============================================================================

class QuestCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LoL Role Quest Completion Calculator")
        self.root.geometry("1200x700")
        
        # Stored scenarios for comparison
        self.comparison_scenarios = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface."""
        
        # Main container with two columns: inputs on left, graph on right
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel: Input controls
        input_frame = ttk.LabelFrame(main_frame, text="Performance Metrics", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Right panel: Graph and results
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        
        # ---- Input Fields ----
        row = 0
        
        # CS per minute
        ttk.Label(input_frame, text="CS per Minute:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cs_per_min = tk.StringVar(value="7.0")
        ttk.Entry(input_frame, textvariable=self.cs_per_min, width=15).grid(row=row, column=1, pady=5)
        row += 1
        
        # Champion damage per minute
        ttk.Label(input_frame, text="Champion Damage per Minute:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.damage_per_min = tk.StringVar(value="0")
        ttk.Entry(input_frame, textvariable=self.damage_per_min, width=15).grid(row=row, column=1, pady=5)
        row += 1
        
        # Melee/Ranged selector
        ttk.Label(input_frame, text="Champion Type:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.champion_type = tk.StringVar(value="Melee")
        type_frame = ttk.Frame(input_frame)
        type_frame.grid(row=row, column=1, pady=5, sticky=tk.W)
        ttk.Radiobutton(type_frame, text="Melee", variable=self.champion_type, value="Melee").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Ranged", variable=self.champion_type, value="Ranged").pack(side=tk.LEFT)
        row += 1
        
        # Turret plates
        ttk.Label(input_frame, text="Turret Plates Secured (0-5):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.plates = tk.StringVar(value="0")
        plates_spinbox = ttk.Spinbox(input_frame, from_=0, to=5, textvariable=self.plates, width=13)
        plates_spinbox.grid(row=row, column=1, pady=5)
        row += 1
        
        # Turret destroyed
        self.turret_destroyed = tk.BooleanVar(value=False)
        ttk.Checkbutton(input_frame, text="Turret Destroyed", variable=self.turret_destroyed).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=5
        )
        row += 1
        
        # Champion takedowns
        ttk.Label(input_frame, text="Champion Takedowns:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.kills = tk.StringVar(value="0")
        ttk.Entry(input_frame, textvariable=self.kills, width=15).grid(row=row, column=1, pady=5)
        row += 1
        
        # Epic monster takedowns
        ttk.Label(input_frame, text="Epic Monster Takedowns:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.epic_monsters = tk.StringVar(value="0")
        ttk.Entry(input_frame, textvariable=self.epic_monsters, width=15).grid(row=row, column=1, pady=5)
        row += 1
        
        # Separator
        ttk.Separator(input_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Calculate button
        ttk.Button(input_frame, text="Calculate Quest Time", command=self.calculate).grid(
            row=row, column=0, columnspan=2, pady=10
        )
        row += 1
        
        # Add to comparison button
        ttk.Button(input_frame, text="Add to Comparison", command=self.add_comparison).grid(
            row=row, column=0, columnspan=2, pady=5
        )
        row += 1
        
        # Clear comparison button
        ttk.Button(input_frame, text="Clear Comparisons", command=self.clear_comparisons).grid(
            row=row, column=0, columnspan=2, pady=5
        )
        row += 1
        
        # Results text area
        result_label_frame = ttk.LabelFrame(input_frame, text="Results", padding="10")
        result_label_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        input_frame.rowconfigure(row, weight=1)
        
        self.results_text = tk.Text(result_label_frame, height=15, width=40, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Initial graph setup
        self.plot_baseline()
        
    def plot_baseline(self):
        """Plot the baseline passive-only accumulation curve."""
        self.ax.clear()
        
        time_points = np.linspace(0, BASE_COMPLETION_TIME, 100)
        quest_points = PASSIVE_POINTS_PER_MINUTE * time_points
        # Calculate percentage completion
        percentage_complete = (quest_points / TOTAL_QUEST_POINTS) * 100
        percentage_complete = np.minimum(100, percentage_complete)
        
        self.ax.plot(time_points, percentage_complete, '--', color='gray', label='Passive Only (Baseline)', linewidth=2)
        self.ax.axhline(y=100, color='red', linestyle=':', label='Quest Completion', linewidth=2)
        
        self.ax.set_xlabel('Game Time (minutes)', fontsize=12)
        self.ax.set_ylabel('Quest Completion (%)', fontsize=12)
        self.ax.set_title('Role Quest - Completion Progress', fontsize=14, fontweight='bold')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
        
    def get_inputs(self):
        """Retrieve and validate all input values."""
        try:
            cs = float(self.cs_per_min.get())
            damage = float(self.damage_per_min.get())
            plates = int(self.plates.get())
            turret = self.turret_destroyed.get()
            kills = int(self.kills.get())
            epic = int(self.epic_monsters.get())
            is_melee = self.champion_type.get() == "Melee"
            
            # Validate ranges
            if cs < 0:
                raise ValueError("CS per minute cannot be negative")
            if damage < 0:
                raise ValueError("Damage per minute cannot be negative")
            if not 0 <= plates <= 5:
                raise ValueError("Turret plates must be between 0 and 5")
            if kills < 0:
                raise ValueError("Champion takedowns cannot be negative")
            if epic < 0:
                raise ValueError("Epic monster takedowns cannot be negative")
            
            return cs, damage, plates, turret, kills, epic, is_melee
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return None
    
    def calculate(self):
        """Calculate and display quest completion time."""
        inputs = self.get_inputs()
        if inputs is None:
            return
        
        cs, damage, plates, turret, kills, epic, is_melee = inputs
        
        # Calculate time reductions
        reductions = calculate_time_reduction(cs, damage, plates, turret, kills, epic, is_melee)
        
        # Calculate completion time
        completion_time = calculate_completion_time(reductions['total'])
        
        # Update results text
        self.display_results(completion_time, reductions)
        
        # Update graph
        self.plot_graph(cs, damage, plates, turret, kills, epic, is_melee, completion_time)
        
    def display_results(self, completion_time, reductions):
        """Display calculation results in the text area."""
        self.results_text.delete(1.0, tk.END)
        
        minutes = int(completion_time)
        seconds = int((completion_time - minutes) * 60)
        
        results = f"Quest Completion Time: {minutes}m {seconds}s\n"
        results += f"({completion_time:.2f} minutes)\n\n"
        results += "Time Reduction Breakdown:\n"
        results += "=" * 35 + "\n"
        results += f"CS:               {reductions['cs']:.1f} seconds\n"
        results += f"Champion Damage:  {reductions['damage']:.1f} seconds\n"
        results += f"Turret Plates:    {reductions['plates']:.1f} seconds\n"
        results += f"Turret Destroy:   {reductions['turret']:.1f} seconds\n"
        results += f"Champion Kills:   {reductions['kills']:.1f} seconds\n"
        results += f"Epic Monsters:    {reductions['epic_monsters']:.1f} seconds\n"
        results += "=" * 35 + "\n"
        results += f"Total Reduction:  {reductions['total']:.1f} seconds\n"
        results += f"                  ({reductions['total']/60:.2f} minutes)\n"
        
        self.results_text.insert(1.0, results)
        
    def plot_graph(self, cs, damage, plates, turret, kills, epic, is_melee, completion_time):
        """Plot the quest accumulation curve."""
        self.ax.clear()
        
        # Plot baseline
        time_baseline = np.linspace(0, BASE_COMPLETION_TIME, 100)
        points_baseline = PASSIVE_POINTS_PER_MINUTE * time_baseline
        percentage_baseline = (points_baseline / TOTAL_QUEST_POINTS) * 100
        percentage_baseline = np.minimum(100, percentage_baseline)
        
        self.ax.plot(time_baseline, percentage_baseline, '--', color='gray', 
                    label='Passive Only (Baseline)', linewidth=2, alpha=0.7, zorder=1)
        
        # Plot comparison scenarios first (so they appear behind current scenario)
        colors = ['green', 'orange', 'purple', 'brown', 'pink', 'cyan', 'olive', 'navy']
        for i, scenario in enumerate(self.comparison_scenarios):
            color = colors[i % len(colors)]
            scenario_percentage = (scenario['points'] / TOTAL_QUEST_POINTS) * 100
            scenario_percentage = np.minimum(100, scenario_percentage)
            self.ax.plot(scenario['time'], scenario_percentage, '-', 
                        color=color, label=scenario['label'], linewidth=2, alpha=0.7, zorder=2)
        
        # Plot current scenario on top with bright blue
        time_points, quest_points = generate_accumulation_curve(
            cs, damage, plates, turret, kills, epic, is_melee, completion_time
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
        self.ax.set_title('Role Quest - Completion Progress', fontsize=14, fontweight='bold')
        self.ax.legend(loc='best', framealpha=0.9)
        self.ax.grid(True, alpha=0.3)
        
        # Set reasonable axis limits
        self.ax.set_xlim(0, max(BASE_COMPLETION_TIME, completion_time) + 1)
        self.ax.set_ylim(-5, 110)
        
        self.canvas.draw()
        
    def add_comparison(self):
        """Add current scenario to comparison list."""
        inputs = self.get_inputs()
        if inputs is None:
            return
        
        cs, damage, plates, turret, kills, epic, is_melee = inputs
        
        reductions = calculate_time_reduction(cs, damage, plates, turret, kills, epic, is_melee)
        completion_time = calculate_completion_time(reductions['total'])
        
        time_points, quest_points = generate_accumulation_curve(
            cs, damage, plates, turret, kills, epic, is_melee, completion_time
        )
        
        # Build default label with smart formatting
        minutes = int(completion_time)
        seconds = int((completion_time - minutes) * 60)
        
        label_parts = [f"{minutes}m{seconds}s"]
        
        if cs > 0:
            label_parts.append(f"{cs:.1f} CS/Min")
        
        if damage > 0:
            label_parts.append(f"{damage:.0f} Dmg/Min")
        
        # Add champion type only if damage is being dealt
        if damage > 0:
            label_parts.append("Melee" if is_melee else "Ranged")
        
        if kills > 0:
            label_parts.append(f"{kills} KP")
        
        # Calculate total plates (in-lane + other lanes)
        total_plates = plates
        if total_plates > 0:
            label_parts.append(f"{total_plates} Plates")
        
        if epic > 0:
            label_parts.append(f"{epic} Epics")
        
        default_label = " ".join(label_parts)
        
        # Create custom dialog for label input
        dialog = tk.Toplevel(self.root)
        dialog.title("Label Comparison Scenario")
        dialog.geometry("450x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter a label for this scenario:", font=('TkDefaultFont', 10)).pack(pady=10)
        
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
            messagebox.showinfo("Added", f"Scenario added to comparison (Total: {len(self.comparison_scenarios)})")
        
        def on_cancel():
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
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
    app = QuestCalculatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
