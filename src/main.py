import os
import tkinter as tk
from tkinter import filedialog

import parser
import plot
import cells_analysis as cell
import ragone_plot as ragone
import supercap_analysis as supercap

def select_files_dialog(mode):
    # Opens the file dialog depending on the selected technology mode.
    # mode == '1' (Li-ion): Single file selection (.mpr)
    # mode == '2' (Supercap): Multiple files selection (one per discharge current)

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)  

    if mode == "1":
        file_path = filedialog.askopenfilename(
            title="Select Li-ion .mpr file",
            filetypes=[("MPR files", "*.mpr"), ("All files", "*.*")],
        )
        return [file_path] if file_path else []
    
    elif mode == "2":
        file_paths = filedialog.askopenfilenames(
            title="Select ALL Supercap discharge files (one per current)",
            filetypes=[("Data files", "*.*"), ("MPR files", "*.mpr"), ("CSV/TXT files", "*.csv *.txt")],
        )
        return list(file_paths)
    
    return []

def get_technology_choice():
    # Prompt
    print("\n" + "=" * 40)
    print(" Select Technology Type")
    print("=" * 40)
    print("1 - Li-ion Battery")
    print("2 - Supercapacitor")
    
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice in ["1", "2"]:
            return choice
        print("Invalid choice. Please enter 1 or 2.\n")

def get_user_inputs(tech_choice):
    print("\n" + "=" * 40)
    print(" Cell Parameters")
    print("=" * 40)

    while True:
        try:
            if tech_choice == "1":
                capacity = float(input("Insert nominal capacity (mAh) [e.g. 2900]: "))
            else:
                capacity = float(input("Insert capacitance (F) [e.g. 3000]: "))
                
            cell_mass = float(input("Insert mass cell (g) [e.g. 45.2]: "))

            if capacity <= 0 or cell_mass <= 0:
                print("Values must be positive!\n")
                continue

            return capacity, cell_mass
        except ValueError:
            print("Invalid inputs. Please enter numeric values.\n")

if __name__ == "__main__":
    # Select technology type (Li-ion or supercap)
    tech_choice = get_technology_choice()
    tech_name = "Li-ion" if tech_choice == "1" else "Supercap"
    
    # Select file or files
    file_paths = select_files_dialog(tech_choice)

    if not file_paths:
        print("No files selected. Exiting.")
        exit()

    print(f"Technology selected: {tech_name}")
    print(f"Selected {len(file_paths)} file(s).")

    # Get cell parameters
    NOMINAL_CAPACITY, CELL_MASS = get_user_inputs(tech_choice)

    # Workflow based on technology
    if tech_choice == "1":
        # LI-ION WORKFLOW
        file_path = file_paths[0]
        file_name_full = os.path.basename(file_path)
        file_name_no_ext = os.path.splitext(file_name_full)[0]

        output_folder = os.path.join("output", file_name_no_ext)
        os.makedirs(output_folder, exist_ok=True)
        print(f"Files will be saved in: {output_folder}/")

        df = parser.parse_mpr_file(file_path)
        plot.save_voltage_plot(df, folder_name=output_folder)

        csv_output_path = os.path.join(output_folder, f"{file_name_no_ext}_parsed.csv")
        df.to_csv(csv_output_path, index=False)
        print(f"DataFrame saved in CSV: {csv_output_path}")

        df_first_charge = cell.get_full_charge(df)
        plot.save_charge_plot(df_first_charge, folder_name=output_folder)

        summary_df = cell.get_capacity_and_ce(df)
        plot.save_coulombic_efficiency_plot(summary_df, folder_name=output_folder)

        crate_dict = cell.extract_crates(df, NOMINAL_CAPACITY)
        print(f"Identified C-rates: {list(crate_dict.keys())}")
        
        plot.save_crate_voltage_plots(crate_dict, folder_name=output_folder)
        plot.save_crate_capacity_plots(crate_dict, folder_name=output_folder)
        plot.save_power_and_energy_subplots(crate_dict, folder_name=output_folder)

        ragone.compute_and_save_ragone_points(
            crate_dict, 
            cell_name=file_name_no_ext, 
            cell_mass_g=CELL_MASS, 
            output_dir="output"
        )

    else:
        # SUPERCAP WORKFLOW
        supercap_name = input("Insert a name/ID for this Supercapacitor cell [e.g. BCAP3000]: ").strip()
        if not supercap_name:
            supercap_name = "Supercap_Cell"

        output_folder = os.path.join("output", supercap_name)
        os.makedirs(output_folder, exist_ok=True)
        print(f"Files will be saved in: {output_folder}/")
        
        crate_dict_voltage = {}
        crate_dict_power_energy = {}

        for fp in file_paths:
            discharge_label = os.path.splitext(os.path.basename(fp))[0]
            print(f"Processing file: {discharge_label}")
            
            df_raw = parser.parse_mpr_file(fp) 
            
            df_voltage = supercap.get_supercap_single_stable_cycle(df_raw)
            crate_dict_voltage[discharge_label] = df_voltage
            
            df_discharge = supercap.get_supercap_discharge_only(df_raw)
            crate_dict_power_energy[discharge_label] = df_discharge

        plot.save_supercap_voltage_plots(crate_dict_voltage, folder_name=output_folder)
    
        plot.save_power_and_energy_subplots(crate_dict_power_energy, folder_name=output_folder)
        
        ragone.compute_and_save_ragone_points(
            crate_dict_power_energy, 
            cell_name=supercap_name, 
            cell_mass_g=CELL_MASS, 
            output_dir="output"
        )
        
    # Generate global ragone plot
    ragone.plot_global_ragone_chart(
        global_db_path="output/global_ragone_database.csv", 
        output_folder="output"
    )