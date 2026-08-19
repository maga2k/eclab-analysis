def get_supercap_discharge_only(df):
    current_col = 'control/V/mA' if 'control/V/mA' in df.columns else 'control_value'
    
    if 'half cycle' in df.columns:
        half_cycles = sorted(df['half cycle'].unique())
        
        if len(half_cycles) >= 4:
            target_halves = half_cycles[2:4]
            df_cycle = df[df['half cycle'].isin(target_halves)]
            return df_cycle[df_cycle[current_col] < 0].copy()
        elif len(half_cycles) >= 2:
            target_halves = half_cycles[:2]
            df_cycle = df[df['half cycle'].isin(target_halves)]
            return df_cycle[df_cycle[current_col] < 0].copy()

    return df[df[current_col] < 0].copy()

def get_supercap_single_stable_cycle(df):

    if 'half cycle' in df.columns:
        half_cycles = sorted(df['half cycle'].unique())
        
        if len(half_cycles) >= 4:
            selected_halves = half_cycles[2:4]
            return df[df['half cycle'].isin(selected_halves)].copy()
        elif len(half_cycles) >= 2:
            selected_halves = half_cycles[:2]
            return df[df['half cycle'].isin(selected_halves)].copy()
            
    return df.copy()