# prepare_data_egs_heat.py

import os
import pandas as pd

class Preparation:
    def __init__(self, doc_path):
        """Initialize with the path to the Excel file."""
        self.doc = doc_path
        self.dataframes = {}

    def read_data(self):
        # Read tables
        self.dataframes = {
            'alpha_egs_heat.json': pd.read_excel(self.doc,sheet_name='alpha',nrows=8,index_col=0),
            'beta_egs_heat.json': pd.read_excel(self.doc,sheet_name='beta',nrows=8,index_col=0),
            'gamma_egs_heat.json': pd.read_excel(self.doc,sheet_name='gamma',nrows=8,index_col=0),
        }

    def write_output(self, output_dir="data/"):
        # Save all DataFrames to JSON files
        for filename, df in self.dataframes.items():
            # Convert floating-point numbers to scientific notation strings
            df = df.map(lambda x: f"{x:.6e}" if isinstance(x, float) else x)
            df.to_json(os.path.join(output_dir, filename))

def main():
    # Supplementary information from Paulillo et al. (2022), https://doi.org/10.1016/j.cesys.2022.100086
    data = Preparation("data/Coefficients_Douziech_et_al_2021.xlsx")

    # Read the tables
    data.read_data()

    # Save all DataFrames to JSON files
    data.write_output("data/")

if __name__ == "__main__":
    main()
