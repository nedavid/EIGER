# prepare_data.py

import os
import pandas as pd
from docx import Document

class Preparation:
    def __init__(self, doc_path):
        """Initialize with the path to the DOCX file."""
        self.doc = Document(doc_path)
        self.dataframes = {}

    def read_docx_table(self, table_num=1, nheader=1):
        """Read a table from a DOCX file and return it as a DataFrame."""
        table = self.doc.tables[table_num]
        data = [[cell.text for cell in row.cells] for row in table.rows]
        df = pd.DataFrame(data)

        if nheader == 1:
            df = df.rename(columns=df.iloc[0]).drop(df.index[0]).reset_index(drop=True)
            df = df.set_index(df.columns[0])
            df = df.apply(pd.to_numeric)
        elif nheader == 2:
            df = df.drop(df.index[0]).reset_index(drop=True)
            df = df.rename(columns=df.iloc[0]).drop(df.index[0]).reset_index(drop=True)
            df = df.set_index(df.columns[0])

        return df

    def read_data(self):
        # Read tables
        self.dataframes = {
            'alpha.json': self.read_docx_table(0),
            'beta_20.json': self.read_docx_table(1),
            'beta_10.json': self.read_docx_table(2),
            'beta_5.json': self.read_docx_table(3),
            'chi_20.json': self.read_docx_table(4),
            'chi_15.json': self.read_docx_table(5),
            'chi_10.json': self.read_docx_table(6),
            'chi_5.json': self.read_docx_table(7),
            'delta_15.json': self.read_docx_table(8),
            'delta_10.json': self.read_docx_table(9),
            'delta_5.json': self.read_docx_table(10),
        }

        # Process lit_conv_df and lit_egs_df separately
        lit_conv_df = self.read_docx_table(19,2).iloc[:-1]
        lit_egs_df = self.read_docx_table(20,2)
        lit_conv_df['Operational CO2 emissions [g/kWh]'] = pd.to_numeric(
            lit_conv_df['Operational CO2 emissions [g/kWh]'], errors='coerce'
        )
        lit_conv_df['Operational CH4 emissions [g/kWh]'] = pd.to_numeric(
            lit_conv_df['Operational CH4 emissions [g/kWh]'], errors='coerce'
        ).fillna(0)
        lit_egs_df['Diesel consumption (GJ/m)'] = pd.to_numeric(
            lit_egs_df['Diesel consumption (GJ/m)'], errors='coerce'
        )
        lit_egs_df['Installed capacity (MW)'] = pd.to_numeric(
            lit_egs_df['Installed capacity (MW)'], errors='coerce'
        )
        lit_egs_df['Depth of wells [m]'] = pd.to_numeric(
            lit_egs_df['Depth of wells \n[m]'], errors='coerce'
        )
        lit_egs_df['Success rate [%]'] = pd.to_numeric(
            lit_egs_df['Success rate \n[%]'], errors='coerce'
        )
        lit_conv_df['com_key'] = lit_conv_df.index.astype(str) + '_' + lit_conv_df['Scenario'] + '_' + lit_conv_df['Technology']
        lit_conv_df = lit_conv_df.set_index('com_key')
        lit_egs_df['com_key'] = lit_egs_df.index.astype(str) + '_' + lit_egs_df['Scenario']
        lit_egs_df = lit_egs_df.set_index('com_key')

        # Add lit_conv_df and lit_egs_df to dataframes
        self.dataframes['lit_conv.json'] = lit_conv_df
        self.dataframes['lit_egs.json'] = lit_egs_df

    def write_output(self, output_dir="data/"):
        # Save all DataFrames to JSON files
        for filename, df in self.dataframes.items():
            # Convert floating-point numbers to scientific notation strings
            df = df.applymap(lambda x: f"{x:.6e}" if isinstance(x, float) else x)
            df.to_json(os.path.join(output_dir, filename))

def main():
    # Supplementary information from Paulillo et al. (2022), https://doi.org/10.1016/j.cesys.2022.100086
    data = Preparation("data/simplified_SI.docx")

    # Read the tables
    data.read_data()

    # Save all DataFrames to JSON files
    data.write_output("data/")

if __name__ == "__main__":
    main()
