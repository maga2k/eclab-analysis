import pandas as pd
import numpy as np

def split_cycles(df):

    cycles = {}
    
    unique_cycles = df['half cycle'].unique()
    
    for cycle in unique_cycles:
        cycle_data = df[df['half cycle'] == cycle]
        cycles[cycle] = {
            'charge': cycle_data[cycle_data['control/V/mA'] > 0],
            'discharge': cycle_data[cycle_data['control/V/mA'] < 0]
        }
    return cycles

def get_charge_data(df, cycle_number=0):
    
    cycle_data = df[df['half cycle'] == cycle_number]
    charge_only = cycle_data[cycle_data['control/V/mA'] > 0]
    
    return charge_only[['time_s', 'control/V/mA', 'voltage_V', '(Q-Qo)/mA.h']]

import pandas as pd

def get_full_charge(df):

    q_col = '(Q-Qo)/mA.h' if '(Q-Qo)/mA.h' in df.columns else df.columns[4]
    unique_hc = sorted(df['half cycle'].unique())
    
    best_charge_df = None
    lowest_v_start = float('inf')
    
    for i in range(0, len(unique_hc) - 1, 2):
        hc1 = unique_hc[i]
        hc2 = unique_hc[i+1] if i+1 < len(unique_hc) else None
        
        sub1 = df[df['half cycle'] == hc1]
        sub2 = df[df['half cycle'] == hc2] if hc2 is not None else pd.DataFrame()
        
        full_cycle = pd.concat([sub1, sub2])
        
        charge_phase = full_cycle[full_cycle['control/V/mA'] > 0].copy()
        
        if charge_phase.empty:
            continue

        v_start = charge_phase['voltage_V'].iloc[0]
        
        if v_start < lowest_v_start:
            lowest_v_start = v_start
            best_charge_df = charge_phase[['time_s', 'control/V/mA', 'voltage_V', q_col]]
            
    if best_charge_df is not None:
        return best_charge_df
    
    return pd.DataFrame()


def get_capacity_and_ce(df):
   
    q_col = '(Q-Qo)/mA.h' if '(Q-Qo)/mA.h' in df.columns else df.columns[4]
    
    summary_data = []
    
    unique_hc = sorted(df['half cycle'].unique())
    
    for i in range(0, len(unique_hc) - 1, 2):
        hc_charge = unique_hc[i]
        hc_discharge = unique_hc[i+1] if i+1 < len(unique_hc) else None
        
        sub_charge = df[df['half cycle'] == hc_charge]
        q_charge = sub_charge[q_col].max() - sub_charge[q_col].min()
        
        q_discharge = 0
        if hc_discharge is not None:
            sub_discharge = df[df['half cycle'] == hc_discharge]
            q_discharge = sub_discharge[q_col].max() - sub_discharge[q_col].min()
            
        ce = (q_discharge / q_charge * 100) if q_charge > 0 else 0
        
        summary_data.append({
            'cycle': (i // 2) + 1,
            'charge_capacity': q_charge,
            'discharge_capacity': q_discharge,
            'coulombic_efficiency': ce
        })
        
    return pd.DataFrame(summary_data)

def extract_crates(df, nominal_capacity=2900):
    
    unique_hc = sorted(df['half cycle'].unique())
    cycle_list = []
    
    for i in range(0, len(unique_hc) - 1, 2):
        hc1 = unique_hc[i]
        hc2 = unique_hc[i+1] if i+1 < len(unique_hc) else None
        
        sub1 = df[df['half cycle'] == hc1]
        sub2 = df[df['half cycle'] == hc2] if hc2 is not None else pd.DataFrame()
        
        full_cycle_df = pd.concat([sub1, sub2])
        
        discharge_phase = full_cycle_df[full_cycle_df['control/V/mA'] < 0].copy()
        
        if discharge_phase.empty:
            continue
            
        mean_discharge_current = abs(discharge_phase['control/V/mA'].mean())
        
        c_rate = mean_discharge_current / nominal_capacity
        
        cycle_list.append({
            'c_rate_val': c_rate,
            'data': discharge_phase
        })
        
    if not cycle_list:
        return {}

    df_cycles = pd.DataFrame(cycle_list)
    
    df_cycles['crate_rounded'] = df_cycles['c_rate_val'].round(1)
    
    crate_dict = {}
    for crate_val, group in df_cycles.groupby('crate_rounded'):
        first_cycle = group.iloc[0]
        label = f"Discharge @ {crate_val:.1f}C"
        crate_dict[label] = first_cycle['data']
        
    return crate_dict


def get_single_supercap_full_cycle(df):
    """
    Extracts the first complete cycle (charge and discharge) from a supercapacitor dataset 
    based on the first unique cycle number or half-cycle sequence.
    """
    if 'half cycle' in df.columns:
        # Take the first two half-cycles (e.g., half cycle 1 and 2, which form a full charge-discharge pair)
        first_two_halves = df['half cycle'].unique()[:2]
        if len(first_two_halves) > 0:
            df_filtered = df[df['half cycle'].isin(first_two_halves)].copy()
            return df_filtered
            
    # Fallback if 'half cycle' is missing: return the whole dataframe if it's already a single session
    return df.copy()

def get_single_supercap_discharge(df):
    """
    Extracts only the first discharge cycle/half-cycle from a supercapacitor dataset 
    by filtering where the current (control/V/mA) is negative.
    """
    current_col = 'control/V/mA' if 'control/V/mA' in df.columns else 'control_value'
    
    if 'half cycle' in df.columns:
        # Find the first half-cycle where the current is negative (discharge mode)
        discharge_cycles = df[df[current_col] < 0]['half cycle'].unique()
        if len(discharge_cycles) > 0:
            first_discharge_half_cycle = discharge_cycles[0]
            df_filtered = df[df['half cycle'] == first_discharge_half_cycle].copy()
            return df_filtered
            
    # Fallback if 'half cycle' is not available: just return rows with negative current
    return df[df[current_col] < 0].copy()