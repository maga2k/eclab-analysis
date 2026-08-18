import pandas as pd
import numpy as np

def split_cycles(df):
    """
    Ritorna un dizionario dove ogni chiave è il numero di ciclo
    e il valore è un altro dict con 'charge' e 'discharge' come DataFrame.
    """
    cycles = {}
    
    unique_cycles = df['half cycle'].unique()
    
    for cycle in unique_cycles:
        cycle_data = df[df['half cycle'] == cycle]
        cycles[cycle] = {
            'charge': cycle_data[cycle_data['control/V/mA'] > 0],
            'discharge': cycle_data[cycle_data['control/V/mA'] < 0]
        }
    return cycles

def get_charge_data(df, cycle_number):
    
    cycle_data = df[df['half cycle'] == cycle_number]
    charge_only = cycle_data[cycle_data['control/V/mA'] > 0]
    
    return charge_only[['time_s', 'control/V/mA', 'voltage_V', '(Q-Qo)/mA.h']]


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