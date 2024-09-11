# main.py

import os
import sys
import pandas as pd
import prepare_data

class GeothermalPowerPlant:

    def __init__(self, plant_type, massflux=0.0, power=0.0, condenser_temperature=0.0, condenser_pressure=0.0,
                 vapor_fraction=0.0, f_co2=0.0, f_ch4=0.0):
        """Initialize plant_type."""
        self.plant_type = plant_type # conventional or enhanced
        self.massflux = massflux # kg s-1
        self.power = power # kW
        self.condenser_temperature = condenser_temperature # K
        self.condenser_pressure = condenser_pressure # bar
        self.vapor_fraction = vapor_fraction # fraction of water vapor in conventional power plant
        self.f_co2 = f_co2 # fraction of CO2 in geofluid
        self.f_ch4 = f_ch4 # fraction of CH4 in geofluid
        (self.alpha, self.beta_20, self.beta_10, self.beta_5, self.chi_20, self.chi_15, self.chi_10,
         self.chi_5, self.delta_15, self.delta_10, self.delta_5) = self.read_coefficients()

    @staticmethod
    def read_coefficients():
        # Check first if coefficient and literature data exist and if not, prepare them.
        while True:
            filelist = ['data/alpha.json','data/beta_20.json','data/beta_10.json','data/beta_5.json','data/chi_20.json',
                        'data/chi_15.json','data/chi_10.json','data/chi_5.json','data/delta_15.json',
                        'data/delta_10.json','data/delta_5.json','data/lit_conv.json','data/lit_egs.json']
            if all([os.path.isfile(f) for f in filelist]):
                break
            else:
                data = prepare_data.Preparation("data/simplified_SI.docx")

                # Read the tables
                data.read_data()

                # Save all DataFrames to JSON files
                data.write_output("data/")
                print(f"Coefficient and literature data prepared and saved to data/.")

        alpha_df = pd.read_json('data/alpha.json')
        beta_20_df = pd.read_json('data/beta_20.json')
        beta_10_df = pd.read_json('data/beta_10.json')
        beta_5_df = pd.read_json('data/beta_5.json')
        chi_20_df = pd.read_json('data/chi_20.json')
        chi_15_df = pd.read_json('data/chi_15.json')
        chi_10_df = pd.read_json('data/chi_10.json')
        chi_5_df = pd.read_json('data/chi_5.json')
        delta_15_df = pd.read_json('data/delta_15.json')
        delta_10_df = pd.read_json('data/delta_10.json')
        delta_5_df = pd.read_json('data/delta_5.json')
        return (alpha_df, beta_20_df, beta_10_df,beta_5_df,chi_20_df,chi_15_df,chi_10_df,
                chi_5_df,delta_15_df,delta_10_df, delta_5_df)

    def simple_impact_model(self, parameters, threshold=0.2):
        # Note that coefficients like alpha_1 or beta_3 are referenced as alpha.iloc[0] or beta.iloc[2] i.e. the index
        # is one number smaller than the coefficient in Paulillo et al. (2022) due to Python indexing.
        # Separate models are used for reliability thresholds 20%/15%/10%/5%.
        category_k = []
        impact_k = []

        if self.plant_type == 'conventional':
            # Check if input parameters are in valid range of Paulillo et al. (2021),
            # https://doi.org/10.1016/j.cesys.2021.100054
            if 'operational_CO2_emissions' in parameters.keys():
                if parameters['operational_CO2_emissions'] < 0 or parameters['operational_CO2_emissions'] > 740:
                    print ("Error: Operational CO2 emissions outside valid range [0-740]")
                    sys.exit(1)
            if 'operational_CH4_emissions' in parameters.keys():
                if parameters['operational_CH4_emissions'] < 0 or parameters['operational_CH4_emissions'] > 740:
                    print ("Error: Operational CH4 emissions outside valid range [0-740]")
                    sys.exit(1)
            if 'average_depth_of_wells'in parameters.keys():
                if parameters['average_depth_of_wells'] < 660 or parameters['average_depth_of_wells'] > 4000:
                    print ("Error: Average depth of wells outside valid range [660-4000]")
                    sys.exit(1)
            if 'producers_capacity' in parameters.keys():
                if parameters['producers_capacity'] < 0 or parameters['producers_capacity'] > 20:
                    print ("Error: Producers' capacity outside valid range [0-20]")
                    sys.exit(1)
            if 'initial_harmonic_decline_rate' in parameters.keys():
                if (parameters['initial_harmonic_decline_rate'] < 0.01
                        or parameters['initial_harmonic_decline_rate'] > 0.1):
                    print ("Error: Initial harmonic decline rate outside valid range  [0.01-0.1]")
                    sys.exit(1)
            if 'success_rate_primary_wells' in parameters.keys():
                if (parameters['success_rate_primary_wells'] < 0
                        or parameters['success_rate_primary_wells'] > 100):
                    print ("Error: Success rate, primary wells outside valid range  [0-100]")
                    sys.exit(1)

            # Treat climage change category separately for conventional geothermal power plants.
            # 20%/15%/10%/5%
            if 'operational_CO2_emissions' and 'operational_CH4_emissions' in parameters.keys():
                impact_cat = (parameters['operational_CO2_emissions'] * self.alpha.loc['climate change'].iloc[0]
                             + parameters['operational_CH4_emissions'] * self.alpha.loc['climate change'].iloc[1]
                             + self.alpha.loc['climate change'].iloc[2])
                impact_k.append(impact_cat)
                category_k.append('climate change')

            # Treat all other environmental impact categories.
            # 20%
            if threshold == 0.2 and 'average_depth_of_wells' and 'producers_capacity' in parameters.keys():
                for index, beta in self.beta_20.iterrows():
                    impact_cat = ((parameters['average_depth_of_wells'] * beta.iloc[0] + beta.iloc[1])
                                  / parameters['producers_capacity']
                                  + parameters['average_depth_of_wells'] * beta.iloc[2] + beta.iloc[3])
                    impact_k.append(impact_cat)
                    category_k.append(index)
            # 15%
            elif threshold == 0.15 and 'average_depth_of_wells' and 'producers_capacity' in parameters.keys():
                for index, beta in self.beta_20.iterrows():
                    impact_cat = ((parameters['average_depth_of_wells'] * beta.iloc[0]+ beta.iloc[1])
                                  / parameters['producers_capacity']
                                  + parameters['average_depth_of_wells'] * beta.iloc[2] + beta.iloc[3])
                    impact_k.append(impact_cat)
                    category_k.append(index)

            # 10%
            elif (threshold == 0.1
                  and 'average_depth_of_wells' and 'producers_capacity'
                  and 'initial_harmonic_decline_rate' in parameters.keys()) :
                for index, beta in self.beta_10.iterrows():
                    impact_cat = ((parameters['initial_harmonic_decline_rate'] * parameters['average_depth_of_wells'] *
                                   beta.iloc[0]
                                   + parameters['initial_harmonic_decline_rate'] * beta.iloc[1]
                                   + parameters['average_depth_of_wells'] * beta.iloc[2]
                                   + beta.iloc[3]
                                  ) / parameters['producers_capacity']
                                  + parameters['average_depth_of_wells'] * beta.iloc[4]
                                  + beta.iloc[5])
                    impact_k.append(impact_cat)
                    category_k.append(index)

            # 5%
            elif (threshold == 0.05
                  and 'average_depth_of_wells' and 'producers_capacity' and 'success_rate_primary_wells'
                  and 'initial_harmonic_decline_rate' in parameters.keys()):
                for index, beta in self.beta_5.iterrows():
                    impact_cat = ((parameters['success_rate_primary_wells'] *
                                   parameters['initial_harmonic_decline_rate'] * parameters['average_depth_of_wells'] *
                                   beta.iloc[0]
                                   + parameters['initial_harmonic_decline_rate']
                                   * parameters['success_rate_primary_wells'] * beta.iloc[1]
                                   + parameters['success_rate_primary_wells'] * beta.iloc[2]
                                   + parameters['average_depth_of_wells'] * beta.iloc[3]
                                  ) / (parameters['success_rate_primary_wells'] * parameters['producers_capacity'])
                                  + parameters['average_depth_of_wells'] * beta.iloc[4]
                                  + beta.iloc[5])
                    impact_k.append(impact_cat)
                    category_k.append(index)

        elif self.plant_type == 'enhanced':
            # Check if input parameters are in valid range of Paulillo et al. (2021),
            # https://doi.org/10.1016/j.cesys.2021.100054
            if 'installed_capacity' in parameters.keys():
                if parameters['installed_capacity'] < 0.4 or parameters['installed_capacity'] > 11:
                    print ("Error: Installed capacity outside valid range [0.4-11]")
                    sys.exit(1)
            if 'average_depth_of_wells'in parameters.keys():
                if parameters['average_depth_of_wells'] < 2500 or parameters['average_depth_of_wells'] > 6000:
                    print ("Error: Average depth of wells outside valid range [2500-6000]")
                    sys.exit(1)
            if 'diesel_wells' in parameters.keys():
                if parameters['diesel_wells'] < 3000 or parameters['diesel_wells'] > 14000:
                    print ("Error: Diesel consumption outside valid range [3000-14000]")
                    sys.exit(1)
            if 'success_rate_primary_wells' in parameters.keys():
                if (parameters['success_rate_primary_wells'] < 0
                        or parameters['success_rate_primary_wells'] > 100):
                    print ("Error: Success rate, primary wells outside valid range  [0-100]")
                    sys.exit(1)

            # 20%
            if threshold == 0.2 and 'installed_capacity' in parameters.keys():
                for index, chi in self.chi_20.iterrows():
                    impact_cat = chi.iloc[0] / parameters['installed_capacity'] + chi.iloc[1]
                    impact_k.append(impact_cat)
                    category_k.append(index)

            # 15%
            elif threshold == 0.15 and 'installed_capacity' in parameters.keys():
                # Group 1
                for index, chi in self.chi_15.iterrows():
                    impact_cat = chi.iloc[0] / parameters['installed_capacity'] + chi.iloc[1]
                    impact_k.append(impact_cat)
                    category_k.append(index)
                # Group 2
                if 'diesel_wells' in parameters.keys():
                    for index, delta in self.delta_15.iterrows():
                        impact_cat = (parameters['diesel_wells'] * delta.iloc[0] + delta.iloc[1]
                                      / parameters['installed_capacity'] + delta.iloc[2])
                        impact_k.append(impact_cat)
                        category_k.append(index)

            # 10%
            elif threshold == 0.1 and 'installed_capacity' in parameters.keys():
                # Group 1
                for index, chi in self.chi_10.iterrows():
                    impact_cat = chi.iloc[0] / parameters['installed_capacity'] + chi.iloc[1]
                    impact_k.append(impact_cat)
                    category_k.append(index)
                # Group 2
                if 'diesel_wells' in parameters.keys():
                    for index, delta in self.delta_10.iterrows():
                        impact_cat = (parameters['diesel_wells'] * delta.iloc[0] + delta.iloc[1]
                                      / parameters['installed_capacity'] + delta.iloc[2])
                        impact_k.append(impact_cat)
                        category_k.append(index)

            # 5%
            elif (threshold == 0.05 and 'success_rate_primary_wells' and 'average_depth_of_wells'
                  and 'installed_capacity' in parameters.keys()):
                # Group 1
                for index, chi in self.chi_5.iterrows():
                    impact_cat = ((parameters['success_rate_primary_wells'] * parameters['average_depth_of_wells']
                                   * chi.iloc[0] + parameters['success_rate_primary_wells'] * chi.iloc[1]
                                   + parameters['average_depth_of_wells'] * chi.iloc[2])
                                  / (parameters['success_rate_primary_wells'] * parameters['installed_capacity'])
                                  + chi.iloc[3])
                    impact_k.append(impact_cat)
                    category_k.append(index)
                # Group 2
                if 'diesel_wells' in parameters.keys():
                    for index, delta in self.delta_5.iterrows():
                        impact_cat = ((parameters['diesel_wells'] * parameters['average_depth_of_wells']
                                       * parameters['success_rate_primary_wells'] * delta.iloc[0]
                                       + parameters['diesel_wells'] * parameters['average_depth_of_wells']
                                       * delta.iloc[1]
                                       + parameters['success_rate_primary_wells'] * parameters['average_depth_of_wells']
                                       * delta.iloc[2] + parameters['success_rate_primary_wells'] * delta.iloc[3]
                                       + parameters['average_depth_of_wells'] * delta.iloc[4])
                                      / (parameters['success_rate_primary_wells'] * parameters['installed_capacity'])
                                      + delta.iloc[5])
                        impact_k.append(impact_cat)
                        category_k.append(index)

        return category_k, impact_k

    def operational_ghg_emissions(self):
        # Check input parameters
        if self.condenser_temperature < 273.15:
            print("Error: Temperature in the condenser must be above 0°C")
            sys.exit(1)
        if self.vapor_fraction < 0 or self.vapor_fraction > 1:
            print("Error: Fraction of steam of geofluid has to be between 0 and 1")
            sys.exit(1)
        if self.f_co2 < 0 or self.f_co2 > 1:
            print("Error: Fraction of CO2 in geofluid has to be between 0 and 1")
            sys.exit(1)
        if self.f_ch4 < 0 or self.f_ch4 > 1:
            print("Error: Fraction of CH4 in geofluid has to be between 0 and 1")
            sys.exit(1)

        # Using Henry's law to compute how much greenhouse gases are released (i.e. in vapor phase in condenser)
        massflux = self.massflux * self.vapor_fraction
        h_cp_s_co2 = 0.034 # mol l-1 bar-1
        mw_co2 = 44.009 # g mol-1
        density_water = 996  # kg m-3 at 30°C
        #Parameters for Antoine equation for T in °C and P in mmHg; 1°C<T<100°C
        param_a = 8.07131
        param_b = 1730.63
        param_c = 233.426
        vapor_pressure = 10**(param_a-param_b/(param_c+self.condenser_temperature-273.15))
        vapor_pressure = vapor_pressure / 750.062 # mmHg to bar
        # It is assumed that the volume of liquid water consists of all water while water vapor should be subtracted
        # from the volume of liquid water.

        pressure_co2 = max(self.condenser_pressure - vapor_pressure,0)

        f_direct_co2 = 1-h_cp_s_co2*pressure_co2*(1-self.f_co2)/density_water /(self.f_co2/mw_co2)

        print("fraction of CO2 in gas phase in condenser",f_direct_co2)

        operational_co2_emissions = massflux*3600/self.power * self.f_co2 * f_direct_co2

        return operational_co2_emissions

def main():
    # Conventional geothermal power plant - median literature values
    parameters_conv = {'operational_CO2_emissions': 77,  # gCO2/kWh
                       'operational_CH4_emissions': 0.0,  # gCH4/kWh
                       'producers_capacity': 5.9,  # MW/well
                       'average_depth_of_wells': 2250,  # m/well
                       'initial_harmonic_decline_rate': 0.05,
                       'success_rate_primary_wells': 72.1} # %

    plant_conv = GeothermalPowerPlant('conventional')


    category_k, impact_k = plant_conv.simple_impact_model(parameters_conv,0.05)
    #print("Environmental impact categories", category_k)
    #print("Environmental impact of conventional plant", impact_k)

    # Enhanced geothermal power plant - median literature values
    parameters_egs = {'installed_capacity': 5.7,  # MW
                      'average_depth_of_wells': 4250,  # m/well
                      'diesel_wells': 8500,  # MJ/m
                      'success_rate_primary_wells': 72.1} # %

    plant_egs = GeothermalPowerPlant('enhanced')

    category_k, impact_k = plant_egs.simple_impact_model(parameters_egs,0.05)
    #print("Environmental impact categories", category_k)
    #print("Environmental impact of enhanced plant", impact_k)

    plant_conv = GeothermalPowerPlant('conventional',massflux=100.0, power=70000.0,
                                      condenser_temperature=303.25, condenser_pressure=0.1,
                                      vapor_fraction=0.3, f_co2=0.02)
    operational_co2_emissions = plant_conv.operational_ghg_emissions()
    print("Operational CO2 emissions [kgCO2eq/kWh]:",operational_co2_emissions)

if __name__ == "__main__":
    main()