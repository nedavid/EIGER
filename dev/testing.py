# testing.py

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd

alpha_df = pd.read_json('../data/alpha.json')
beta_20_df = pd.read_json('../data/beta_20.json')
beta_10_df = pd.read_json('../data/beta_10.json')
beta_5_df = pd.read_json('../data/beta_5.json')
chi_20_df = pd.read_json('../data/chi_20.json')
chi_15_df = pd.read_json('../data/chi_15.json')
chi_10_df = pd.read_json('../data/chi_10.json')
chi_5_df = pd.read_json('../data/chi_5.json')
delta_15_df = pd.read_json('../data/delta_15.json')
delta_10_df = pd.read_json('../data/delta_10.json')
delta_5_df = pd.read_json('../data/delta_5.json')
lit_conv_df = pd.read_json('../data/lit_conv.json')
lit_egs_df = pd.read_json('../data/lit_egs.json')

lit_CO2_emi = lit_conv_df['Operational CO2 emissions [g/kWh]'].to_dict()
lit_CH4_emi = lit_conv_df['Operational CH4 emissions [g/kWh]'].to_dict()
lit_diesel = lit_egs_df['Diesel consumption (GJ/m)'].to_dict()
lit_capacity = lit_egs_df['Installed capacity (MW)'].to_dict()
lit_depth = lit_egs_df['Depth of wells [m]'].to_dict()
lit_success_rate = lit_egs_df['Success rate [%]'].to_dict()

parameters_conv = {'operational_CO2_emissions': 77, # gCO2/kWh
                   'operational_CH4_emissions': 0.0, # gCO2/kWh
                   'producers_capacity': 5.9, # MW/well
                   'average_depth_of_wells': 2250, # m/well
                   'initial_harmonic_decline_rate': 0.05,
                   'success_rate_primary_wells': 0.721}

parameters_egs = {'installed_capacity': 5.7, # MW
                  'average_depth_of_wells': 4250, # m/well
                  'diesel_wells': 8500, # MJ/m
                  'success_rate_primary_wells': 0.721}

impact_cc_conv=[]
for study,Eco2 in lit_CO2_emi.items():
    impact_CC = (alpha_df.loc['climate change'].iloc[0]*Eco2
                 + alpha_df.loc['climate change'].iloc[1]*lit_CH4_emi[study]
                 + alpha_df.loc['climate change'].iloc[2])
    impact_cc_conv.append(impact_CC)

impact_cc_egs=[]
for study,cap in lit_capacity.items():
    impact_CC = (chi_20_df.loc['climate change'].iloc[0]/cap
                 + chi_20_df.loc['climate change'].iloc[1])
    impact_cc_egs.append(impact_CC)

impact_k_conv = []
for index, beta in beta_20_df.iterrows():
    impact_cat = (beta.iloc[0] * parameters_conv['average_depth_of_wells'] + beta.iloc[1]
                  / parameters_conv['producers_capacity']
                  + beta.iloc[2] * parameters_conv['average_depth_of_wells'] + beta.iloc[3] )
    impact_k_conv.append(impact_cat)

# Create a figure with a GridSpec layout to control the height ratios
fig = plt.figure(figsize=(16, 6))

# Create the first subplot (Conventional)
ax1 = plt.subplot2grid((2, 2), (0, 0), rowspan=2)
ax1.scatter(lit_CO2_emi.keys(), impact_cc_conv)
ax1.scatter(lit_CO2_emi.keys(), lit_conv_df['Carbon footprint  \n[gCO2 eq./kWh]'], c='black', marker='s')
ax1.set_xticks(range(len(lit_CO2_emi.keys())))
ax1.set_xticklabels(lit_CO2_emi.keys(), rotation=90)
ax1.set_ylabel('g$\mathregular{CO_2}$eq./kWh')
ax1.set_title('Conventional')
ax1.set_ylim(0, 1000)

impact_cc_egs = [x * 1E3 for x in impact_cc_egs]
# Create a GridSpec with different height ratios
gs = gridspec.GridSpec(2, 2, height_ratios=[1, 4])

# Create the upper part of the second subplot (Enhanced)
ax2_upper = fig.add_subplot(gs[0, 1])
ax2_upper.scatter(lit_capacity.keys(), impact_cc_egs)
ax2_upper.scatter(lit_capacity.keys(), lit_egs_df['Carbon footprint \n[gCO2 eq./kWh]'], c='black', marker='s')
ax2_upper.set_ylim(700, 800)  # Upper y-axis limit
ax2_upper.set_xticks([])  # Hide x-ticks for the upper plot
ax2_upper.set_title('Enhanced')

# Create the lower part of the second subplot (Enhanced)
ax2_lower = fig.add_subplot(gs[1, 1])
ax2_lower.scatter(lit_capacity.keys(), impact_cc_egs)
ax2_lower.scatter(lit_capacity.keys(), lit_egs_df['Carbon footprint \n[gCO2 eq./kWh]'], c='black', marker='s')
ax2_lower.set_ylim(0, 400)  # Lower y-axis limit
ax2_lower.set_xticks(range(len(lit_capacity.keys())))
ax2_lower.set_xticklabels(lit_capacity.keys(), rotation=90)
ax2_lower.set_ylabel('g$\mathregular{CO_2}$eq./kWh')

# Adjust layout
plt.tight_layout()
plt.show()

print(impact_k_conv)