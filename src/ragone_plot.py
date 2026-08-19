import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_and_save_ragone_points(crate_dict, cell_name, cell_mass_g, output_dir="output"):
    """
    Computes the full time-series of specific energy vs specific power for each C-rate 
    and appends all points to a global CSV database for the Ragone plot.
    """
    ragone_rows = []
    cell_mass_kg = cell_mass_g / 1000.0  # Convert mass from grams to kilograms
    
    for label, df_discharge in crate_dict.items():
        time_s = df_discharge['time_s'].to_numpy()
        time_s = time_s - time_s[0]
        time_h = time_s / 3600.0
        
        voltage = df_discharge['voltage_V'].to_numpy()
        current_col = 'control/V/mA' if 'control/V/mA' in df_discharge.columns else 'control_value'
        current_a = abs(df_discharge[current_col].to_numpy()) / 1000.0
        
        # Instantaneous Power (W)
        power_w = voltage * current_a
        
        # Cumulative Energy profile over time (Wh)
        dt_h = np.diff(time_h)
        p_avg = (power_w[:-1] + power_w[1:]) / 2.0
        energy_wh = np.concatenate([[0.0], np.cumsum(dt_h * p_avg)])
        
        # Compute specific metrics point-by-point for the entire discharge curve
        spec_power_array = power_w / cell_mass_kg
        spec_energy_array = energy_wh / cell_mass_kg
        
        # Append every single time step to build the continuous curve
        for sp, se in zip(spec_power_array, spec_energy_array):
            ragone_rows.append({
                "cell_name": cell_name,
                "crate_label": label,
                "specific_energy_wh_kg": se,
                "specific_power_w_kg": sp,
                "technology": "Li-ion"
            })
        
    ragone_df = pd.DataFrame(ragone_rows)
    
    base_output_dir = "output"
    os.makedirs(base_output_dir, exist_ok=True)
    global_ragone_path = os.path.join(base_output_dir, "global_ragone_database.csv")
    
    if os.path.exists(global_ragone_path):
        existing_df = pd.read_csv(global_ragone_path)
        existing_df = existing_df[existing_df['cell_name'] != cell_name]
        updated_df = pd.concat([existing_df, ragone_df], ignore_index=True)
    else:
        updated_df = ragone_df
        
    try:
        updated_df.to_csv(global_ragone_path, index=False)
        print(f"Ragone full-curve data updated in global database: {global_ragone_path}")
    except PermissionError:
        print(f"Permission denied: Could not write to {global_ragone_path}. Please close Excel and retry.")

def plot_global_ragone_chart(global_db_path="output/global_ragone_database.csv", output_folder="plots"):
    """
    Reads the global Ragone database and generates a log-log Ragone plot 
    complete with constant-time diagonal lines (10s, 100s, 1000s, 10000s).
    """
    if not os.path.exists(global_db_path):
        print(f"Global Ragone database not found at: {global_db_path}")
        return

    df = pd.read_csv(global_db_path)
    
    if df.empty:
        print("The Ragone database is empty.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    plt.figure(figsize=(10, 8))
    
    # --- 1. PLOT CONSTANT-TIME DIAGONALS ---
    # Formula: Energy (Wh/kg) = Power (W/kg) * (time_seconds / 3600)
    power_range = np.logspace(0, 6, 500)  # From 1 W/kg to 1,000,000 W/kg
    constant_times_seconds = [10, 100, 1000, 10000]
    time_styles = [('--', 'Time 10s'), ('-.', 'Time 100s'), (':', 'Time 1000s'), ('-', 'Time 10000s')]
    
    for t_sec, (linestyle, label) in zip(constant_times_seconds, time_styles):
        energy_line = power_range * (t_sec / 3600.0)
        plt.plot(power_range, energy_line, color='gray', linestyle=linestyle, alpha=0.7, label=label)

    unique_cells = df['cell_name'].unique()
    
    for cell in unique_cells:
        cell_data = df[df['cell_name'] == cell]
        unique_crates = cell_data['crate_label'].unique()
        
        for crate in unique_crates:
            crate_data = cell_data[cell_data['crate_label'] == crate]
            
            plt.plot(
                crate_data['specific_power_w_kg'], 
                crate_data['specific_energy_wh_kg'], 
                linestyle='-', 
                linewidth=2, 
                label=f"{cell} - {crate}"
            )

    plt.xscale('log')
    plt.yscale('log')
    
    plt.xlabel("Specific Power [W/kg]", fontsize=12)
    plt.ylabel("Specific Energy [Wh/kg]", fontsize=12)
    plt.title("Ragone Plot (Global Comparison)", fontsize=14, fontweight='bold')
    
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    
    plt.xlim(1, 100000)
    plt.ylim(0.01, 1000)
    
    plt.tight_layout()
    
    save_path = os.path.join(output_folder, "global_ragone_plot.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Global Ragone plot successfully saved to: {save_path}")

if __name__ == "__main__":
    plot_global_ragone_chart()