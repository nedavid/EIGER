# prepare_data_general.py

import os
import pandas as pd

class Preparation:
    def __init__(self, doc_path, model_name, ncategories, nparameters):
        """Initialize with the path to the Excel file."""
        self.doc = doc_path
        self.model_name = model_name
        self.ncategories = ncategories
        self.nparameters = nparameters
        self.dataframes = {}

    def read_data(self):
        # Read tables
        self.dataframes = {
            'alpha_'+self.model_name+'.json': pd.read_excel(self.doc,sheet_name='alpha',nrows=self.ncategories+1,
                                                            index_col=0),
            'beta_'+self.model_name+'.json': pd.read_excel(self.doc,sheet_name='beta',nrows=self.ncategories+1,
                                                           index_col=0),
            'gamma_'+self.model_name+'.json': pd.read_excel(self.doc,sheet_name='gamma',nrows=self.ncategories+1,
                                                            index_col=0),
            'x_'+self.model_name+'.json': pd.read_excel(self.doc, sheet_name='x', nrows=self.ncategories+1,
                                                        index_col=0),
            'y_'+self.model_name+'.json': pd.read_excel(self.doc, sheet_name='y', nrows=self.ncategories+1,
                                                        index_col=0),
            'z_'+self.model_name+'.json': pd.read_excel(self.doc, sheet_name='z', nrows=self.ncategories+1,
                                                        index_col=0),
            'u_'+self.model_name+'.json': pd.read_excel(self.doc, sheet_name='u', nrows=self.ncategories+1,
                                                        index_col=0),
            'v_'+self.model_name+'.json': pd.read_excel(self.doc, sheet_name='v', nrows=self.ncategories+1,
                                                        index_col=0),
            'w_'+self.model_name+'.json': pd.read_excel(self.doc, sheet_name='w', nrows=self.ncategories+1,
                                                        index_col=0),
            'valid_ranges_' + self.model_name + '.json': pd.read_excel(self.doc, sheet_name='valid_ranges',
                                                                       nrows=self.nparameters,header=None),
        }

    def write_output(self, output_dir="data/"):
        # Save all DataFrames to JSON files
        for filename, df in self.dataframes.items():
            # Convert floating-point numbers to scientific notation strings
            df = df.map(lambda x: f"{x:.6e}" if isinstance(x, float) else x)
            df.to_json(os.path.join(output_dir, filename))

def main():
    # Supplementary information from Paulillo et al. (2022), https://doi.org/10.1016/j.cesys.2022.100086
    data = Preparation('data/egs_power_5.xlsx','egs_power_5', 16, 10)

    # Read the tables
    data.read_data()

    # Save all DataFrames to JSON files
    data.write_output("data/")

if __name__ == "__main__":
    main()
