# main.py

import os
import sys
import pandas as pd
import prepare_data_general

class GeothermalPlant:

    def __init__(self, plant_type, ncategories, nparameters, massflux=0.0, power=0.0, condenser_temperature=0.0,
                 condenser_pressure=0.0, vapor_fraction=0.0, f_co2=0.0, f_ch4=0.0):
        """Initialize plant_type."""
        self.plant_type = plant_type # conventional, enhanced or egs_heat_general
        self.ncategories = ncategories
        self.nparameters = nparameters
        self.massflux = massflux # kg s-1
        self.power = power # kW
        self.condenser_temperature = condenser_temperature # K
        self.condenser_pressure = condenser_pressure # bar
        self.vapor_fraction = vapor_fraction # fraction of water vapor in conventional power plant
        self.f_co2 = f_co2 # fraction of CO2 in geofluid
        self.f_ch4 = f_ch4 # fraction of CH4 in geofluid
        (self.alpha, self.beta, self.gamma, self.parameter_x, self.parameter_y, self.parameter_z,
         self.parameter_u, self.parameter_v, self.parameter_w, self.valid_ranges) = self.read_model()

    def read_model(self):
        # Check first if coefficient data exist and if not, prepare them.
        while True:
            filelist = ['data/alpha_'+self.plant_type+'.json', 'data/beta_'+self.plant_type+'.json',
                        'data/gamma_'+self.plant_type+'.json', 'data/x_'+self.plant_type+'.json',
                        'data/y_'+self.plant_type+'.json', 'data/z_'+self.plant_type+'.json',
                        'data/u_'+self.plant_type+'.json', 'data/v_'+self.plant_type+'.json',
                        'data/w_'+self.plant_type+'.json','data/valid_ranges_' + self.plant_type + '.json']
            if all([os.path.isfile(f) for f in filelist]):
                break
            else:
                data = prepare_data_general.Preparation('data/'+self.plant_type+'.xlsx',self.plant_type,
                                                        self.ncategories,self.nparameters)

                # Read the tables
                data.read_data()

                # Save all DataFrames to JSON files
                data.write_output("data/")
                print(f"Coefficient data, model parameter and valid ranges prepared and saved to data/.")

        alpha_df = pd.read_json('data/alpha_'+self.plant_type+'.json')
        beta_df = pd.read_json('data/beta_'+self.plant_type+'.json')
        gamma_df = pd.read_json('data/gamma_'+self.plant_type+'.json')
        x_df = pd.read_json('data/x_'+self.plant_type+'.json')
        y_df = pd.read_json('data/y_'+self.plant_type+'.json')
        z_df = pd.read_json('data/z_'+self.plant_type+'.json')
        u_df = pd.read_json('data/u_'+self.plant_type+'.json')
        v_df = pd.read_json('data/v_'+self.plant_type+'.json')
        w_df = pd.read_json('data/w_'+self.plant_type+'.json')
        valid_ranges_df = pd.read_json('data/valid_ranges_'+self.plant_type+'.json')
        # Convert DataFrame to dictionary
        valid_ranges = valid_ranges_df.set_index(0).T.to_dict(orient='list')
        return (alpha_df, beta_df, gamma_df, x_df, y_df, z_df, u_df, v_df, w_df, valid_ranges)

    @staticmethod
    def map_parameters(param_model, parameters):
        # Define a helper function to map parameters
        return param_model.map(lambda x: parameters[x] if isinstance(x, str) and x in parameters else x)

    def check_parameter(self,key,value):
        if key in self.valid_ranges.keys() and (value < self.valid_ranges[key][0] or value > self.valid_ranges[key][1]):
            print("Error: "+self.valid_ranges[key][2]+" of "+str(value)+" outside valid range ["
                  +str(self.valid_ranges[key][0])+"-"+str(self.valid_ranges[key][1])+"]")
            sys.exit(1)

    def simple_impact_model(self, parameters):
        """Computation of environmental impact using a general equation that can be applied to several models
        and allows for easier extension to new models which become available. The general equation is of the form:
        Sum_over_i[(alpha_i * x_i * y_i * z_i**beta_i * 10**(gamma_i * w_i)) / (u_i * v_i) ]
        All environmental impact models need to be converted to this form to be used with this function."""
        for key, value in parameters.items():
            self.check_parameter(key, value)

        # Map parameter values to model parameters
        parameter_x = self.map_parameters(self.parameter_x, parameters)
        parameter_y = self.map_parameters(self.parameter_y, parameters)
        parameter_z = self.map_parameters(self.parameter_z, parameters)
        parameter_u = self.map_parameters(self.parameter_u, parameters)
        parameter_v = self.map_parameters(self.parameter_v, parameters)
        parameter_w = self.map_parameters(self.parameter_w, parameters)

        impact_k = []
        category_k = []
        # Compute environmental impact per category
        for (index, alpha_g), (index_b, beta), (index_c, gamma) in zip(self.alpha.iterrows(),
                                                                       self.beta.iterrows(),
                                                                       self.gamma.iterrows()):
            impact_cat = 0
            for i, alpha in enumerate(alpha_g):
                impact_cat = (impact_cat
                              + (alpha * parameter_x.loc[index].iloc[i]
                                 * parameter_y.loc[index].iloc[i]
                                 * parameter_z.loc[index].iloc[i] ** beta.iloc[i]
                                 * 10 ** (gamma.iloc[i] * parameter_w.loc[index].iloc[i]))
                              / (parameter_u.loc[index].iloc[i] * parameter_v.loc[index].iloc[i]))
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

    plant_egs_heat = GeothermalPlant('egs_heat',7,14)
    category_k, impact_k = plant_egs_heat.simple_impact_model(parameters_egs_heat)

    #print("Environmental impact categories", category_k)
    #print("Environmental impact of enhanced plant", impact_k)

if __name__ == "__main__":
    main()