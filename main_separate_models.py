# main.py

import os
import sys
import pandas as pd
import prepare_data
import prepare_data_egs_heat

class GeothermalPowerPlant:

    def __init__(self, plant_type, massflux=0.0, power=0.0, condenser_temperature=0.0, condenser_pressure=0.0,
                 vapor_fraction=0.0, f_co2=0.0, f_ch4=0.0):
        """Initialize plant_type."""
        self.plant_type = plant_type # conventional, enhanced or egs_heat
        self.massflux = massflux # kg s-1
        self.power = power # kW
        self.condenser_temperature = condenser_temperature # K
        self.condenser_pressure = condenser_pressure # bar
        self.vapor_fraction = vapor_fraction # fraction of water vapor in conventional power plant
        self.f_co2 = f_co2 # fraction of CO2 in geofluid
        self.f_ch4 = f_ch4 # fraction of CH4 in geofluid
        (self.alpha, self.beta_20, self.beta_10, self.beta_5, self.chi_20, self.chi_15, self.chi_10,
         self.chi_5, self.delta_15, self.delta_10, self.delta_5, self.alpha_egs_heat, self.beta_egs_heat,
         self.gamma_egs_heat) = self.read_coefficients()

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
        while True:
            filelist = ['data/alpha_egs_heat.json','data/beta_egs_heat.json','data/gamma_egs_heat.json']
            if all([os.path.isfile(f) for f in filelist]):
                break
            else:
                data = prepare_data_egs_heat.Preparation("data/Coefficients_Douziech_et_al_2021.xlsx")

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
        alpha_egs_heat_df = pd.read_json('data/alpha_egs_heat.json')
        beta_egs_heat_df = pd.read_json('data/beta_egs_heat.json')
        gamma_egs_heat_df = pd.read_json('data/gamma_egs_heat.json')
        return (alpha_df, beta_20_df, beta_10_df,beta_5_df,chi_20_df,chi_15_df,chi_10_df,
                chi_5_df,delta_15_df,delta_10_df, delta_5_df, alpha_egs_heat_df, beta_egs_heat_df, gamma_egs_heat_df)

    def check_parameter(self,key,value):
        if self.plant_type == 'conventional':
            valid_ranges = {'operational_CO2_emissions': [0,740,"Operational CO2 emissions"],
                            'operational_CH4_emissions': [0,740,"Operational CH4 emissions"],
                            'average_depth_of_wells': [660, 4000, "Average depth of wells"],
                            'producers_capacity': [0, 20, "Producers' capacity"],
                            'initial_harmonic_decline_rate': [0.01, 0.1, "Initial harmonic decline rate"],
                            'success_rate_primary_wells': [0, 100, "Success rate, primary wells"],
                            'condenser_temperature': [273.15, 373.15, "Condenser temperature"],
                            'vapor_fraction': [0, 1, "Vapor fraction of geofluid"],
                            'f_co2': [0, 1, "Fraction of CO2 in geofluid"],
                            'f_ch4': [0, 1, "Fraction of CH4 in geofluid"]
                            }
        if self.plant_type == 'enhanced':
            valid_ranges = {'average_depth_of_wells': [2500, 6000, "Average depth of wells"],
                            'installed_capacity': [0.4, 11.1, "Installed capacity"],
                            'diesel_wells': [2600, 14200, "Diesel consumption"],
                            'success_rate_primary_wells': [0, 100, "Success rate, primary wells"]
                            }
        if self.plant_type == 'egs_heat':
            valid_ranges = {'power_prod_pump': [200, 1200, "Power production pump"],
                            'power_inj_pump': [0, 500, "Power injection pump"],
                            'thermal_power_output': [10, 40, "Thermal power output"],
                            'number_prod_wells': [1, 2, "Number production wells"],
                            'number_inj_wells': [1, 2, "Number injection wells"],
                            'length_well': [1300, 5500, "Length_well"],
                            'share_coal': [0, 1, "Share of coal"],
                            'share_oil': [0, 1, "Share of oil"],
                            'share_nuclear': [0, 1, "Share of nuclear"],
                            'share_NG': [0, 1, "Share of natural gas"],
                            'share_wind': [0, 1, "Share of wind"],
                            'share_solar': [0, 1, "Share of solar"],
                            'share_biomass': [0, 1, "Share of biomass"],
                            'share_hydro': [0, 1, "Share of hydro"]
                            }
        if key in valid_ranges.keys() and (value < valid_ranges[key][0] or value > valid_ranges[key][1]):
            print("Error: "+valid_ranges[key][2]+" of "+str(value)+" outside valid range ["
                  +str(valid_ranges[key][0])+"-"+str(valid_ranges[key][1])+"]")
            sys.exit(1)

    def simple_impact_model(self, parameters, threshold=0.2):
        # Note that coefficients like alpha_1 or beta_3 are referenced as alpha.iloc[0] or beta.iloc[2] i.e. the index
        # is one number smaller than the coefficient in Paulillo et al. (2022) due to Python indexing.
        # Separate models are used for reliability thresholds 20%/15%/10%/5%.
        category_k = []
        impact_k = []

        if self.plant_type == 'conventional':
            # Check if input parameters are in valid range of Paulillo et al. (2021),
            # https://doi.org/10.1016/j.cesys.2021.100054
            for key, value in parameters.items():
                self.check_parameter(key,value)

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
                                   + parameters['average_depth_of_wells'] * beta.iloc[2]
                                   + parameters['success_rate_primary_wells'] * beta.iloc[3]
                                  ) / (parameters['success_rate_primary_wells'] * parameters['producers_capacity'])
                                  + parameters['average_depth_of_wells'] * beta.iloc[4]
                                  + beta.iloc[5])
                    impact_k.append(impact_cat)
                    category_k.append(index)

        elif self.plant_type == 'enhanced':
            # Check if input parameters are in valid range of Paulillo et al. (2021),
            # https://doi.org/10.1016/j.cesys.2021.100054
            for key, value in parameters.items():
                self.check_parameter(key,value)

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

        elif self.plant_type == 'egs_heat':
            # Check if input parameters are in valid range of Douziech et al. (2021),
            # https://doi.org/10.1021/acs.est.0c06751
            for key, value in parameters.items():
                self.check_parameter(key,value)

            if ('share_coal' and 'share_NG' and 'share_nuclear' and 'share_oil' and 'share_hydro' and 'share_wind'
                and 'share_biomass' and 'share_solar' and 'number_inj_wells' and 'number_prod_wells'
                and 'length_well' and 'power_prod_pump' and 'power_inj_pump'
                and 'thermal_power_output') in parameters.keys():
                for (index, alpha), (index_b, beta), (index_c, gamma) in zip(self.alpha_egs_heat.iterrows(),
                               self.beta_egs_heat.iterrows(),
                               self.gamma_egs_heat.iterrows()):
                    impact_cat = (((parameters['number_inj_wells'] * parameters['power_inj_pump']
                                   + parameters['number_prod_wells'] * parameters['power_prod_pump'])
                                  * (alpha.iloc[0] * parameters['share_biomass']
                                     + alpha.iloc[1] * parameters['share_coal']
                                     + alpha.iloc[2] * parameters['share_hydro']
                                     + alpha.iloc[3] * parameters['share_NG']
                                     + alpha.iloc[4] * parameters['share_nuclear']
                                     + alpha.iloc[5] * parameters['share_oil']
                                     + alpha.iloc[6] * parameters['share_solar']
                                     + alpha.iloc[7] * parameters['share_wind'])
                                  + (alpha.iloc[8] * parameters['number_inj_wells']
                                     + alpha.iloc[9] * parameters['number_prod_wells'] * parameters['power_prod_pump']
                                     + (parameters['number_inj_wells'] + parameters['number_prod_wells'])
                                     * (alpha.iloc[10] * 10**(gamma.iloc[0] * parameters['length_well'])
                                        + alpha.iloc[11] * parameters['length_well']
                                        + alpha.iloc[12] * parameters['length_well']**beta.iloc[0]
                                        + alpha.iloc[13] * parameters['length_well']**beta.iloc[1]
                                        + alpha.iloc[14] * parameters['length_well']**beta.iloc[2])
                                     +alpha.iloc[15]))
                                  / parameters['thermal_power_output'])
                    impact_k.append(impact_cat)
                    category_k.append(index)

        return category_k, impact_k

    def operational_ghg_emissions(self):
        # Check input parameters
        self.check_parameter('condenser_temperature', self.condenser_temperature)
        self.check_parameter('vapor_fraction', self.vapor_fraction)
        self.check_parameter('f_co2', self.f_co2)
        self.check_parameter('f_ch4', self.f_ch4)

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
        # from the volume of liquid water. It is further assumed that the non-condensable gas consists only of CO2.

        pressure_co2 = max(self.condenser_pressure - vapor_pressure,0)

        f_direct_co2 = 1-h_cp_s_co2*pressure_co2*(1-self.f_co2)/density_water /(self.f_co2/mw_co2)

        print("Fraction of CO2 in gas phase in condenser",f_direct_co2)

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