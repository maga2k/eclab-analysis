import os
import matplotlib.pyplot as plt

def save_charge_plot(df, folder_name="plots", filename="viq_plot.png"):
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


def save_coulombic_efficiency_plot(summary_df, folder_name="plots", filename="eff_plot.png"):
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
    ax2.set_ylim(min(summary_df['coulombic_efficiency']), max(summary_df['coulombic_efficiency'])) 
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