import pandas as pd
from galvani import BioLogic

def parse_mpr_file(file_path):
    mpr_file = BioLogic.MPRfile(file_path)
    df = pd.DataFrame(mpr_file.data)
    df.columns = df.columns.str.strip()

    rename_mapping = {
        'time/s' : 'time_s',
        'Ewe/V' : 'voltage_V',
        'P/W' : 'power_W'
    }

    df = df.rename(columns = rename_mapping)

    return df