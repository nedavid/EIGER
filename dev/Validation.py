# validation.py
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from main import GeothermalPowerPlant

if __name__ == "__main__":
     # Conventional geothermal power plant - validation literature values
    lit_conv_df = pd.read_json('data/lit_conv.json')
    lit_CO2_emi = lit_conv_df['Operational CO2 emissions [g/kWh]'].to_dict()
    lit_CH4_emi = lit_conv_df['Operational CH4 emissions [g/kWh]'].to_dict()

    plant_conv = GeothermalPowerPlant('conventional')

    impact_cc_conv = []
    for study, Eco2 in lit_CO2_emi.items():
        parameters_conv = {}
        parameters_conv['operational_CO2_emissions'] = Eco2
        parameters_conv['operational_CH4_emissions'] = lit_CH4_emi[study]

        category_k, impact_k = plant_conv.simple_impact_model(parameters_conv)
        impact_cc_conv.append(impact_k)

    #print("Environmental impact categories", category_k)
    #print("Environmental impact of conventional plant", impact_cc_conv)

    # Create a figure with a GridSpec layout to control the height ratios
    fig = plt.figure(figsize=(16, 10))

    # Create the first subplot (Conventional)
    ax1 = plt.subplot2grid((2, 2), (0, 0), rowspan=2)
    ax1.scatter(lit_CO2_emi.keys(), impact_cc_conv, label='simplified models: all thresholds')
    ax1.scatter(lit_CO2_emi.keys(), lit_conv_df['Carbon footprint  \n[gCO2 eq./kWh]'], c='black', marker='s',
                label='literature')
    ax1.set_xticks(range(len(lit_CO2_emi.keys())))
    ax1.set_xticklabels(lit_CO2_emi.keys(), rotation=90)
    ax1.set_ylabel('g$\mathregular{CO_2}$eq./kWh')
    ax1.set_title('Conventional')
    ax1.set_ylim(0, 1000)
    ax1.legend(loc='upper right')

    # Enhanced geothermal power plant - validation literature values
    lit_egs_df = pd.read_json('data/lit_egs.json')
    lit_diesel = lit_egs_df['Diesel consumption (GJ/m)'].to_dict()
    lit_capacity = lit_egs_df['Installed capacity (MW)'].to_dict()
    lit_depth = lit_egs_df['Depth of wells [m]'].to_dict()
    lit_success_rate = lit_egs_df['Success rate [%]'].to_dict()

    plant_egs = GeothermalPowerPlant('enhanced')

    impact_cc_egs_20 = []
    impact_cc_egs_5 = []
    for study, cap in lit_capacity.items():
        parameters_egs = {}
        parameters_egs['installed_capacity'] = cap
        parameters_egs['average_depth_of_wells'] = lit_depth[study]
        parameters_egs['diesel_wells'] = lit_diesel[study]
        parameters_egs['success_rate_primary_wells'] = lit_success_rate[study]

        category_k_20, impact_k_20 = plant_egs.simple_impact_model(parameters_egs, 0.2)
        category_k_5, impact_k_5 = plant_egs.simple_impact_model(parameters_egs, 0.05)
        ind_20 = category_k_20.index("climate change")
        ind_5 = category_k_5.index("climate change")
        impact_cc_egs_20.append(impact_k_20[ind_20])
        impact_cc_egs_5.append(impact_k_5[ind_5])

    #print("Environmental impact of enhanced plant", impact_cc_egs_20)
    #print("Environmental impact of enhanced plant", impact_cc_egs_5)

    # Convert from kgCO2 eq./kWh to gCO2 eq./kWh
    impact_cc_egs_20 = [x * 1E3 for x in impact_cc_egs_20]
    impact_cc_egs_5 = [x * 1E3 for x in impact_cc_egs_5]
    # Create a GridSpec with different height ratios
    gs = gridspec.GridSpec(2, 2, height_ratios=[1, 4])

    # Create the upper part of the second subplot (Enhanced)
    ax2_upper = fig.add_subplot(gs[0, 1])
    ax2_upper.scatter(lit_capacity.keys(), impact_cc_egs_20, label='simplified models: 10,15,20%')
    ax2_upper.scatter(lit_capacity.keys(), impact_cc_egs_5, c='orange', label='5%')
    ax2_upper.scatter(lit_capacity.keys(), lit_egs_df['Carbon footprint \n[gCO2 eq./kWh]'], c='black', marker='s',
                      label='literature')
    ax2_upper.set_ylim(700, 800)  # Upper y-axis limit
    ax2_upper.set_xticks([])  # Hide x-ticks for the upper plot
    ax2_upper.set_title('Enhanced')
    ax2_upper.legend(loc='upper right')

    # Create the lower part of the second subplot (Enhanced)
    ax2_lower = fig.add_subplot(gs[1, 1])
    ax2_lower.scatter(lit_capacity.keys(), impact_cc_egs_20)
    ax2_lower.scatter(lit_capacity.keys(), impact_cc_egs_5, c='orange')
    ax2_lower.scatter(lit_capacity.keys(), lit_egs_df['Carbon footprint \n[gCO2 eq./kWh]'], c='black', marker='s')
    ax2_lower.set_ylim(0, 400)  # Lower y-axis limit
    ax2_lower.set_xticks(range(len(lit_capacity.keys())))
    ax2_lower.set_xticklabels(lit_capacity.keys(), rotation=90)
    ax2_lower.set_ylabel('g$\mathregular{CO_2}$eq./kWh')

    # Adjust layout
    plt.tight_layout()
    #plt.show()
    plt.savefig('dev/Fig2.png')

    #Hellisheidi plant (conventional, double flash, Iceland)
    parameters_hellisheidi = {'operational_CO2_emissions': 0.0209,  # kgCO2/kWh
                       'operational_CH4_emissions': 0.0,  # kgCH4/kWh
                       'producers_capacity': 9,  # MW/well
                       'average_depth_of_wells': 2220,  # m/well
                       'initial_harmonic_decline_rate': 0.03,
                       'success_rate_primary_wells': 100} # %

    category_k, impact_k_20 = plant_conv.simple_impact_model(parameters_hellisheidi,0.2)
    category_k, impact_k_15 = plant_conv.simple_impact_model(parameters_hellisheidi, 0.15)
    category_k, impact_k_10 = plant_conv.simple_impact_model(parameters_hellisheidi, 0.10)
    category_k, impact_k_5 = plant_conv.simple_impact_model(parameters_hellisheidi, 0.05)

    # Create a figure with 16 subplots (4x4 grid)
    fig, axes = plt.subplots(4, 4, figsize=(16, 16))

    # Flatten the axes array for easy iteration
    axes = axes.flatten()

    # Set y-lables and y-limits
    ylabels = ['kg CO2-Eq','CTUh','kg U235-eq','CTUh','kg CFC-11-Eq','kg NMVOC-Eq','disease incidence','mol H+-Eq',
               'CTUe','kg P-Eq','kg N-Eq','mol N-Eq','kg Sb-Eq','m3 water-Eq','MJ','points']
    y_limits = [(0, 6E-1), (0, 8E-9), (0, 1.25E-3), (0, 2E-8),
                (0, 4E-9), (0, 3E-4), (0, 2E-9), (0, 2.5E-4),
                (0, 2E-1), (0, 1.5E-6), (0, 10E-5), (0, 1E-3),
                (0, 4E-7), (0, 10E-3), (0, 4E-1), (0, 1.25E-1)]

    # Loop over each category and create a subplot
    for i, category in enumerate(category_k):
        # Plotting the points for each impact list
        axes[i].scatter(1, impact_k_20[i], color='blue', label='20%')
        axes[i].scatter(2, impact_k_15[i], color='orange', label='15%')
        axes[i].scatter(3, impact_k_10[i], color='green', label='10%')
        axes[i].scatter(4, impact_k_5[i], color='red', label='5%')

        # Set the x-ticks to correspond to the labels
        axes[i].set_xticks([1, 2, 3, 4])
        axes[i].set_xticklabels(['20%', '15%', '10%', '5%'])

        # Set the title of the subplot to the category name
        axes[i].set_title(category, pad=12)

        # Set the y-labels
        axes[i].set_ylabel(ylabels[i])

        # Set the y-limits for each subplot individually
        axes[i].set_ylim(y_limits[i])

        # Adjust the layout slightly for better appearance
        plt.subplots_adjust(hspace=0.4, wspace=0.4)

    ind_20 = category_k.index("material resources: metals/minerals")
    print('material resources: metals/minerals')
    print('HELLISHEIDI', '20%', impact_k_20[ind_20])
    print('HELLISHEIDI', '15%', impact_k_15[ind_20])
    print('HELLISHEIDI', '10%', impact_k_10[ind_20])
    print('HELLISHEIDI', '5%', impact_k_5[ind_20])

    fig.suptitle('HELLISHEIDI GEOTHERMAL POWER PLANT')

    # Save the plot
    #plt.show()
    plt.savefig('dev/Fig3.png')

    #United Down Deep Geothermal Power (UDDGP, egs, UK)
    parameters_uddgp = {'installed_capacity': 1,  # MW
                      'average_depth_of_wells': 4000,  # m/well
                      'diesel_wells': 7200,  # MJ/m
                      'success_rate_primary_wells': 100} # %

    category_k_20, impact_k_20 = plant_egs.simple_impact_model(parameters_uddgp,0.2)
    category_k_15, impact_k_15 = plant_egs.simple_impact_model(parameters_uddgp, 0.15)
    category_k_10, impact_k_10 = plant_egs.simple_impact_model(parameters_uddgp, 0.10)
    category_k_5, impact_k_5 = plant_egs.simple_impact_model(parameters_uddgp, 0.05)

    # Create a figure with 16 subplots (4x4 grid)
    fig, axes = plt.subplots(4, 4, figsize=(16, 16))

    # Flatten the axes array for easy iteration
    axes = axes.flatten()

    # Set y-lables and y-limits
    ylabels = ['kg CO2-Eq','CTUh','kg U235-eq','CTUh','kg CFC-11-Eq','kg NMVOC-Eq','disease incidence','mol H+-Eq',
               'CTUe','kg P-Eq','kg N-Eq','mol N-Eq','kg Sb-Eq','m3 water-Eq','MJ','points']
    y_limits = [(0, 4E-1), (0, 4E-8), (0, 2E-2), (0, 1E-7),
                (0, 7E-8), (0, 6E-3), (0, 1.25E-8), (0, 5E-3),
                (0, 1.2), (0, 8E-6), (0, 2E-3), (0, 2E-2),
                (0, 2E-6), (0, 5E-2), (0, 5), (0, 8E-1)]

    # Remove trailing blanks from each string in the list
    category_k_5 = [category.strip() for category in category_k_5]

    # Loop over each category and create a subplot
    for i, category in enumerate(category_k_20):
        # Find the indices in each category list
        idx_20 = category_k_20.index(category)
        idx_15 = category_k_15.index(category)
        idx_10 = category_k_10.index(category)
        idx_5 = category_k_5.index(category)
        # Plotting the points for each impact list
        axes[i].scatter(1, impact_k_20[idx_20], color='blue', label='20%')
        axes[i].scatter(2, impact_k_15[idx_15], color='orange', label='15%')
        axes[i].scatter(3, impact_k_10[idx_10], color='green', label='10%')
        axes[i].scatter(4, impact_k_5[idx_5], color='red', label='5%')

        # Set the x-ticks to correspond to the labels
        axes[i].set_xticks([1, 2, 3, 4])
        axes[i].set_xticklabels(['20%', '15%', '10%', '5%'])

        # Set the title of the subplot to the category name
        axes[i].set_title(category, pad=12)

        # Set the y-labels
        axes[i].set_ylabel(ylabels[i])

        # Set the y-limits for each subplot individually
        axes[i].set_ylim(y_limits[i])

        # Adjust the layout slightly for better appearance
        plt.subplots_adjust(hspace=0.4, wspace=0.4)

    ind_20 = category_k_20.index("ozone depletion")
    ind_15 = category_k_15.index("ozone depletion")
    ind_10 = category_k_10.index("ozone depletion")
    ind_5 = category_k_5.index("ozone depletion")
    print('ozone depletion')
    print('UDDGP', '20%', impact_k_20[ind_20])
    print('UDDGP', '15%', impact_k_15[ind_15])
    print('UDDGP', '10%', impact_k_10[ind_10])
    print('UDDGP', '5%', impact_k_5[ind_5])

    fig.suptitle('UNITED DOWNS GEOTHERMAL POWER PLANT')

    # Save the plot
    #plt.show()
    plt.savefig('dev/Fig4.png')