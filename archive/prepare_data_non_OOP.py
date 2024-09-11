# prepare_data_non_OOP.py

import os
import pandas as pd
from docx import Document

def read_docx_table(document,table_num=1,nheader=1):
    """Read a table from a DOCX file and return it as a DataFrame."""
    table = document.tables[table_num]
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

# Supplementary information from Paulillo et al. (2022), https://doi.org/10.1016/j.cesys.2022.100086
SI_doc = Document("data/simplified_SI.docx")

# Read tables
dataframes = {
    'alpha.json': read_docx_table(SI_doc, 0),
    'beta_20.json': read_docx_table(SI_doc, 1),
    'beta_10.json': read_docx_table(SI_doc, 2),
    'beta_5.json': read_docx_table(SI_doc, 3),
    'chi_20.json': read_docx_table(SI_doc, 4),
    'chi_15.json': read_docx_table(SI_doc, 5),
    'chi_10.json': read_docx_table(SI_doc, 6),
    'chi_5.json': read_docx_table(SI_doc, 7),
    'delta_15.json': read_docx_table(SI_doc, 8),
    'delta_10.json': read_docx_table(SI_doc, 9),
    'delta_5.json': read_docx_table(SI_doc, 10),
}

# Process lit_conv_df separately
lit_conv_df = read_docx_table(SI_doc,19,2).iloc[:-1]
lit_conv_df['Operational CO2 emissions [g/kWh]'] = pd.to_numeric(
    lit_conv_df['Operational CO2 emissions [g/kWh]'], errors='coerce'
)
lit_conv_df['Operational CH4 emissions [g/kWh]'] = pd.to_numeric(
    lit_conv_df['Operational CH4 emissions [g/kWh]'], errors='coerce'
).fillna(0)
lit_conv_df['com_key'] = lit_conv_df.index.astype(str) + '_' + lit_conv_df['Scenario'] + '_' + lit_conv_df['Technology']
lit_conv_df = lit_conv_df.set_index('com_key')

# Add lit_conv_df to dataframes
dataframes['lit_conv.json'] = lit_conv_df

# Save all DataFrames to JSON files
output_dir = "../data/"
for filename, df in dataframes.items():
    df.to_json(os.path.join(output_dir, filename))