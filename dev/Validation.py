# validation.py
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import os

# Change the current working directory to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(parent_dir)

from main import GeothermalPowerPlant

if __name__ == "__main__":
    # Conventional geothermal power plant - validation literature values
    lit_conv_df = pd.read_json('data/lit_conv.json')
    lit_CO2_emi = lit_conv_df['Operational CO2 emissions [g/kWh]'].to_dict()
    lit_CH4_emi = lit_conv_df['Operational CH4 emissions [g/kWh]'].to_dict()

    plant_conv = GeothermalPowerPlant('conventional_power_20',16,10)

    impact_cc_conv = []
    for study, Eco2 in lit_CO2_emi.items():
        parameters_conv = {'operational_CO2_emissions': Eco2,
                           'operational_CH4_emissions': lit_CH4_emi[study],
                           'producers_capacity': 5.9,  # MW/well
                           'average_depth_of_wells': 2250,  # m/well
                           'initial_harmonic_decline_rate': 0.05,
                           'success_rate_primary_wells': 72.1} # %

        category_k, impact_k = plant_conv.simple_impact_model(parameters_conv)
        index = category_k.index("climate change")
        impact_cc_conv.append(impact_k[index])

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
    lit_diesel = lit_egs_df['Diesel consumption (MJ/m)'].to_dict()
    lit_capacity = lit_egs_df['Installed capacity (MW)'].to_dict()
    lit_depth = lit_egs_df['Depth of wells [m]'].to_dict()
    lit_success_rate = lit_egs_df['Success rate [%]'].to_dict()

    impact_cc_egs_20 = []
    impact_cc_egs_5 = []
    for study, cap in lit_capacity.items():
        parameters_egs = {'installed_capacity': cap, 'average_depth_of_wells': lit_depth[study],
                          'diesel_wells': lit_diesel[study], 'success_rate_primary_wells': lit_success_rate[study]}
        plant_egs = GeothermalPowerPlant('egs_power_20', 16, 10)
        category_k_20, impact_k_20 = plant_egs.simple_impact_model(parameters_egs)
        plant_egs = GeothermalPowerPlant('egs_power_5', 16, 10)
        category_k_5, impact_k_5 = plant_egs.simple_impact_model(parameters_egs)
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

    category_k, impact_k_20 = plant_conv.simple_impact_model(parameters_hellisheidi)
    plant_conv = GeothermalPowerPlant('conventional_power_15',16,10)
    category_k, impact_k_15 = plant_conv.simple_impact_model(parameters_hellisheidi)
    plant_conv = GeothermalPowerPlant('conventional_power_10',16,10)
    category_k, impact_k_10 = plant_conv.simple_impact_model(parameters_hellisheidi)
    plant_conv = GeothermalPowerPlant('conventional_power_5',16,10)
    category_k, impact_k_5 = plant_conv.simple_impact_model(parameters_hellisheidi)

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

    plant_egs = GeothermalPowerPlant('egs_power_20', 16, 10)
    category_k_20, impact_k_20 = plant_egs.simple_impact_model(parameters_uddgp)
    plant_egs = GeothermalPowerPlant('egs_power_15',16,10)
    category_k_15, impact_k_15 = plant_egs.simple_impact_model(parameters_uddgp)
    plant_egs = GeothermalPowerPlant('egs_power_10',16,10)
    category_k_10, impact_k_10 = plant_egs.simple_impact_model(parameters_uddgp)
    plant_egs = GeothermalPowerPlant('egs_power_5',16,10)
    category_k_5, impact_k_5 = plant_egs.simple_impact_model(parameters_uddgp)

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

    plant_egs = GeothermalPowerPlant('egs_power_20_no_expl_wells', 16, 10)
    category_k_20, impact_k_20 = plant_egs.simple_impact_model(parameters_uddgp)
    plant_egs = GeothermalPowerPlant('egs_power_15_no_expl_wells',16,10)
    category_k_15, impact_k_15 = plant_egs.simple_impact_model(parameters_uddgp)
    plant_egs = GeothermalPowerPlant('egs_power_10_no_expl_wells',16,10)
    category_k_10, impact_k_10 = plant_egs.simple_impact_model(parameters_uddgp)
    plant_egs = GeothermalPowerPlant('egs_power_5_no_expl_wells',16,10)
    category_k_5, impact_k_5 = plant_egs.simple_impact_model(parameters_uddgp)

    # Create a figure with 16 subplots (4x4 grid)
    fig, axes = plt.subplots(4, 4, figsize=(16, 16))

    # Flatten the axes array for easy iteration
    axes = axes.flatten()

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

    fig.suptitle('UNITED DOWNS GEOTHERMAL POWER PLANT, NO EXPLORATION')

    # Save the plot
    #plt.show()
    plt.savefig('dev/FigS6.png')

    # Default parameter values for Douziech et al. (2012), https://doi.org/10.1021/acs.est.0c06751
    parameters_egs_heat =  {'power_prod_pump': 500,  # kW
                            'power_inj_pump': 0,  # kW
                            'thermal_power_output': 22.5,  # MW
                            'number_prod_wells': 1,
                            'number_inj_wells': 1,
                            'length_well': 2888, # m
                            'share_coal': 0.04,
                            'share_oil': 0.01,
                            'share_nuclear': 0.76,
                            'share_NG': 0.05,
                            'share_wind': 0.02,
                            'share_solar': 0.,
                            'share_biomass': 0.01,
                            'share_hydro': 0.11}

    plant_egs_heat = GeothermalPowerPlant('egs_heat',7,14)
    category_k, impact_k = plant_egs_heat.simple_impact_model(parameters_egs_heat)

    category_plot = ['acidification', 'climate change', 'energy resources: non-renewable', 'ecotoxicity: freshwater',
                     'human toxicity: carcinogenic', 'human toxicity: non-carcinogenic',
                     'material resources: metals/minerals']

# Create a figure with 7 subplots (2x4 grid)
    fig, axes = plt.subplots(2, 4, figsize=(16, 16))

    # Flatten the axes array for easy iteration
    axes = axes.flatten()
    # Remove not needed subplot
    fig.delaxes(axes[7])

    # Set y-lables and y-limits
    ylabels = ['mol H+-Eq/kWh', 'kg CO2-Eq/kWh', 'MJ/kWh','CTU/kWh',
               'CTUh/kWh', 'CTUh/kWh', 'kg Sb-Eq/kWh']
    y_limits = [(0, 0.0025), (0, 0.3), (0, 5), (0, 1.2),
                (0, 2E-9), (0, 4E-8),  (0, 2E-6)]

    # Loop over each category and create a subplot
    for i, category in enumerate(category_plot):
        # Find the indices in each category list
        idx = category_k.index(category)
        # Plotting the points for each impact list
        axes[i].bar(1, impact_k[idx], color='red')

        # Set the x-ticks to correspond to the labels
        axes[i].set_xticks([1])
        axes[i].set_xticklabels(['simple model'])

        # Set the title of the subplot to the category name
        axes[i].set_title(category, pad=12)

        # Set the y-labels
        axes[i].set_ylabel(ylabels[i])

        # Set the y-limits for each subplot individually
        axes[i].set_ylim(y_limits[i])

        # Adjust the layout slightly for better appearance
        plt.subplots_adjust(hspace=0.4, wspace=0.4)

    fig.suptitle('Representative energy generating installation')

    # Save the plot
    # plt.show()
    plt.savefig('dev/Fig2_Douziech.png')

    # Enhanced geothermal heat plant
    parameters_egs_heat_Alsace = {'power_prod_pump': 400,  # kW
                                  'power_inj_pump': 0,  # kW
                                  'thermal_power_output': 25,  # MW
                                  'number_prod_wells': 1,
                                  'number_inj_wells': 1,
                                  'length_well': 2888,  # m
                                  'share_coal': 0.036,
                                  'share_oil': 0,
                                  'share_nuclear': 0.503,
                                  'share_NG': 0,
                                  'share_wind': 0,
                                  'share_solar': 0.006,
                                  'share_biomass': 0,
                                  'share_hydro': 0.45}
    parameters_egs_heat_France = {'power_prod_pump': 400,  # kW
                                  'power_inj_pump': 0,  # kW
                                  'thermal_power_output': 25,  # MW
                                  'number_prod_wells': 1,
                                  'number_inj_wells': 1,
                                  'length_well': 2888,  # m
                                  'share_coal': 0.04,
                                  'share_oil': 0.01,
                                  'share_nuclear': 0.76,
                                  'share_NG': 0.05,
                                  'share_wind': 0.02,
                                  'share_solar': 0,
                                  'share_biomass': 0.01,
                                  'share_hydro': 0.11}

    category_k_A, impact_k_A = plant_egs_heat.simple_impact_model(parameters_egs_heat_Alsace)
    category_k_F, impact_k_F = plant_egs_heat.simple_impact_model(parameters_egs_heat_France)

    fig, ax = plt.subplots(figsize=(16, 6))

    idx = category_k_A.index('climate change')
    ax.scatter(impact_k_A[idx]*1000,1, color='yellow', label='Alsace', s=200)
    idx = category_k_F.index('climate change')
    ax.scatter(impact_k_F[idx]*1000,1, color='blue', label='France', s=200)

    # Set the y-labels
    ax.set_yticks([1])
    ax.set_yticklabels(['Pratiwi et al 2018'], fontsize=30)

    # Set the x-limits
    ax.set_xlim(3.8, 7.3)

    # Add legend
    ax.legend(fontsize=30)

    # Increase the font size of the x-axis labels and ticks
    ax.tick_params(axis='x', labelsize=30)
    ax.set_xlabel('g CO2-eq/kWh heat', fontsize=30)

    # Hide the y-axis ticks
    ax.yaxis.set_ticks_position('none')

    # Adjust layout
    plt.tight_layout()

    # Save the plot
    plt.savefig('dev/FigS8_Douziech.png')