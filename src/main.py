import parser
import pandas as pd
import plot
import cells_analysis as cell

if __name__ == "__main__":
    file_path = "data/li-ion/180917_INR18650-29E_mod1_cell1_00.mpr"
    NOMINAL_CAPACITY = 2250  # mAh (es. INR18650-29E)

    df = parser.parse_mpr_file(file_path)

    print("Dataset dimensions:", df.shape)
    print("\nAvailable columns:")
    print(df.columns.tolist())
    
    print("\nFirst 5 rows:")
    print(df.head(30))

    #print(min(df["control/V/mA"]))

    df_first_charge = cell.get_charge_data(df, cycle_number=0)
    print(df_first_charge.head())

    plot.save_charge_plot(df_first_charge, folder_name="output_plots", filename="carica_ciclo_1.png")

    summary_df = cell.get_capacity_and_ce(df)
    
    print("Summary table:")
    print(summary_df.head(max(df["half cycle"])))
    
    plot.save_coulombic_efficiency_plot(summary_df, folder_name="output_plots", filename="cycles_capacity_CE.png")

    crate_dict = cell.extract_crates(df, NOMINAL_CAPACITY)
    print(f"C-rate identificati: {list(crate_dict.keys())}")
    plot.save_crate_voltage_plots(crate_dict, folder_name="output_plots")
