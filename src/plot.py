import os
import matplotlib.pyplot as plt
import numpy as np

def save_voltage_plot(df, folder_name="plots", filename="voltage_plot.png"):
    plt.figure(figsize=(10, 6))
    plt.xlabel("time (s)")
    plt.ylabel("voltage (V)")
    plt.title("Voltage vs time")
    plt.plot(df["voltage_V"])
    save_path = os.path.join(folder_name, filename)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    #plt.show()
    plt.close()

def save_charge_plot(df, folder_name="plots", filename="charge_curves_plot.png"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Left axis: voltage
    color_v = 'tab:red'
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Voltage (V)', color=color_v)
    ax1.plot(df['time_s'], df['voltage_V'], color=color_v, label='Voltage (V)')
    ax1.tick_params(axis='y', labelcolor=color_v)

    # Right axis: current
    ax2 = ax1.twinx()
    color_i = 'tab:green'
    ax2.set_ylabel('Current (mA)', color=color_i)
    ax2.plot(df['time_s'], df['control/V/mA'], color=color_i, linestyle='-', label='Current (mA)')
    ax2.tick_params(axis='y', labelcolor=color_i)

    # Far right axis: capacity
    ax3 = ax1.twinx()
    color_q = 'tab:blue'
    
    # Third axis moved to avoid overlaps
    ax3.spines['right'].set_position(('axes', 1.15))
    
    q_col = '(Q-Qo)/mA.h' if '(Q-Qo)/mA.h' in df.columns else df.columns[4]
    ax3.set_ylabel('Capacity (mAh)', color=color_q)
    ax3.plot(df['time_s'], df[q_col], color=color_q, linestyle='--', label='Capacity (mAh)')
    ax3.tick_params(axis='y', labelcolor=color_q)

    fig.subplots_adjust(right=0.85)

    plt.title('Voltage, Current and Capacity Profiles')
    
    save_path = os.path.join(folder_name, filename)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Charge plot V-I-Q saved in: {save_path}")


def save_coulombic_efficiency_plot(summary_df, folder_name="plots", filename="coulombic_efficiency_plot.png"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.set_xlabel('Cycle Number')
    ax1.set_ylabel('Capacity (mAh)', color='tab:blue')
    
    ax1.plot(summary_df['cycle'], summary_df['charge_capacity'], 'r-o', label='Charge Capacity')
    ax1.plot(summary_df['cycle'], summary_df['discharge_capacity'], 'b-s', label='Discharge Capacity')
    
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='lower left')

    ax2 = ax1.twinx()
    color_ce = 'tab:orange'
    ax2.set_ylabel('Coulombic Efficiency (%)', color=color_ce)
    
    ax2.plot(summary_df['cycle'], summary_df['coulombic_efficiency'], color=color_ce, marker='^', linestyle='-', label='Coulombic Efficiency')
    ax2.tick_params(axis='y', labelcolor=color_ce)
    
    # Fix axis limits
    ax2.set_ylim(min(summary_df['coulombic_efficiency'])-20, max(max(summary_df['coulombic_efficiency']),120)) 
    ax2.legend(loc='upper right')

    plt.title('Cycle Capacity and Coulombic Efficiency')
    
    save_path = os.path.join(folder_name, filename)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Coulombic efficiency plot saved in: {save_path}")

def save_crate_voltage_plots(crate_dict, folder_name="plots"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
    plt.figure(figsize=(10, 6))
    
    for label, df_discharge in crate_dict.items():

        time_normalized = df_discharge['time_s'] - df_discharge['time_s'].iloc[0]
        
        plt.plot(time_normalized, df_discharge['voltage_V'], label=label, linewidth=2)
        
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.title('Discharge Voltage Profiles across Different C-rates')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    save_path = os.path.join(folder_name, "voltage_vs_time_by_crate.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"C-rate plot saved in: {save_path}")


def save_crate_capacity_plots(crate_dict, folder_name="plots"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
    plt.figure(figsize=(10, 6))
    
    q_col = '(Q-Qo)/mA.h'
    for label, df_discharge in crate_dict.items():
        active_q_col = q_col if q_col in df_discharge.columns else df_discharge.columns[4]
        
        capacity_normalized = -(df_discharge[active_q_col] - df_discharge[active_q_col].iloc[0])
        
        plt.plot(capacity_normalized, df_discharge['voltage_V'], label=label, linewidth=2)
        
    plt.xlabel('Capacity (mA)')
    plt.ylabel('Voltage (V)')
    plt.title('Discharge Voltage Profiles across Different C-rates')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    save_path = os.path.join(folder_name, "voltage_vs_capacity_by_crate.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"C-rate plot saved in: {save_path}")


def save_power_and_energy_subplots(crate_dict, folder_name="plots", filename="power_energy_vs_time.png"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    for label, df_discharge in crate_dict.items():
        time_s = df_discharge['time_s'].to_numpy()
        time_s = time_s - time_s[0]
        time_h = time_s / 3600.0    
        
        voltage = df_discharge['voltage_V'].to_numpy()
        
        current_a = abs(df_discharge["control/V/mA"].to_numpy()) / 1000.0 
        
        # Instantaneous Power (W) = Voltage * Current
        power_w = voltage * current_a
        
        # Cumulative Energy (Wh) using safe trapezoidal integration over time (in hours)
        dt_h = np.diff(time_h)
        p_avg = (power_w[:-1] + power_w[1:]) / 2.0
        energy_increments = dt_h * p_avg
        energy_wh = np.concatenate([[0.0], np.cumsum(energy_increments)])
        
        # Instantaneous Power vs Time
        ax1.plot(time_h, power_w, label=label, linewidth=2)
        
        # Cumulative Energy vs Time
        ax2.plot(time_h, energy_wh, label=label, linewidth=2)
        
    ax1.set_ylabel("Power [W]")
    ax1.set_title("Instantaneous Power vs Time (Discharge)")
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper right')
    ax1.set_ylim(bottom=0)
    
    ax2.set_xlabel("Time [h]")
    ax2.set_ylabel("Energy [Wh]")
    ax2.set_title("Cumulative Energy vs Time (Discharge)")
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.set_ylim(bottom=0)
    
    plt.tight_layout()
    save_path = os.path.join(folder_name, filename)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Power & Energy subplots saved to: {save_path}")

def save_supercap_voltage_plots(crate_dict_supercap, folder_name="output"):
    """
    Saves the Voltage vs Time plot showing both charge and discharge for all selected supercapacitor files.
    """
    plt.figure(figsize=(10, 6))
    
    for label, df_disc in crate_dict_supercap.items():
        time_s = df_disc['time_s'].to_numpy()
        time_s = time_s - time_s[0]  # Normalize time to start at 0
        time_h = time_s / 3600.0
        voltage = df_disc['voltage_V'].to_numpy()
        
        plt.plot(time_h, voltage, label=label, linewidth=1.5)
        
    plt.xlabel("Time (hours)", fontsize=12)
    plt.ylabel("Voltage (V)", fontsize=12)
    plt.title("Voltage vs Time (Charge & Discharge) for Supercaps", fontsize=14, fontweight='bold')
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc='upper right', fontsize=10)
    plt.tight_layout()
    
    save_path = os.path.join(folder_name, "supercap_charge_discharge_voltage.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Supercap charge/discharge voltage plot saved to: {save_path}")