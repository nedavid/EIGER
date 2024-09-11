def operational_ghg_emissions_v1(self): # needs liquid and gas volumes as an input
    # Using Henry's law to compute how much greenhouse gases are released (i.e. in vapor phase in condenser)
    massflux = self.massflux * self.vapor_fraction
    Rco2 = 188.92  # J kg-1 K-1; assuming non-condensable gas is predominantly CO2
    Rch4 = 518.28  # J kg-1 K-1
    Hcp_s_co2 = 0.034  # mol l-1 bar-1
    Hcp_s_ch4 = 0.0014  # mol l-1 bar-1
    condenser_temp = 303.25  # K
    mw_co2 = 44.009  # g mol-1
    mw_ch4 = 16.0425  # g mol-1
    density_water = 996  # kg m-3 at 30°C
    m_h2o = self.condenser_liquid_volume * density_water  # kg
    p_to_mass_gas_co2 = self.condenser_gas_volume / (Rco2 * condenser_temp / 1E5)  # bar to kg, Ideal gas law
    p_to_mass_gas_ch4 = self.condenser_gas_volume / (Rch4 * condenser_temp / 1E5)  # bar to kg, Ideal gas law
    p_to_mass_liquid_co2 = m_h2o * Hcp_s_co2 * mw_co2 / 1E3  # bar to kg, Henry's law
    p_to_mass_liquid_ch4 = m_h2o * Hcp_s_ch4 * mw_ch4 / 1E3  # bar to kg, Henry's law

    f_direct_co2 = p_to_mass_gas_co2 / (p_to_mass_liquid_co2 + p_to_mass_gas_co2)
    f_direct_ch4 = p_to_mass_gas_ch4 / (p_to_mass_liquid_ch4 + p_to_mass_gas_ch4)
    print(f_direct_co2, f_direct_ch4)

    operational_co2_emissions = massflux * 3600 / self.power * self.f_co2 * f_direct_co2
    operational_ch4_emissions = massflux * 3600 / self.power * self.f_ch4 * f_direct_ch4

    return operational_co2_emissions, operational_ch4_emissions

    def operational_ghg_emissions_v2(self): # neglects fraction of CO2 in solution
        # Using Henry's law to compute how much greenhouse gases are released (i.e. in vapor phase in condenser)
        massflux = self.massflux * self.vapor_fraction
        Hcp_s_co2 = 0.034 # mol l-1 bar-1
        mw_co2 = 44.009 # g mol-1

        n_co2 = self.f_co2*1000/mw_co2
        n_l_co2 = min(Hcp_s_co2*self.condenser_pressure,n_co2)

        print("n_co2",n_co2)
        print("n_l_co2",n_l_co2)

        f_direct_co2 = 1-n_l_co2/n_co2

        print("fraction of CO2 in gas phase in condenser",f_direct_co2)

        operational_co2_emissions = massflux*3600/self.power * self.f_co2 * f_direct_co2

        return operational_co2_emissions


    def operational_ghg_emissions_v3(self):
        # Using Henry's law to compute how much greenhouse gases are released (i.e. in vapor phase in condenser)
        massflux = self.massflux * self.vapor_fraction
        Hcp_s_co2 = 0.034 # mol l-1 bar-1
        mw_co2 = 44.009 # g mol-1
        density_water = 996  # kg m-3 at 30°C
        # Note that this assumes that the partial pressure of CO2 is the same as the pressure in the condenser (i.e.
        # the non-condensable gas is predominantly CO2). Actually the vapor saturation pressure at the condenser
        # temperature should be subtracted first from the pressure in the condenser to compute the partial pressure
        # of CO2. It is also assumed that the volume of liquid water consists of all water while water vapor should
        # be subtracted from the volume of liquid water.

        f_direct_co2 = 1-Hcp_s_co2*self.condenser_pressure*(1-self.f_co2)/density_water /(self.f_co2/mw_co2)

        print("fraction of CO2 in gas phase in condenser",f_direct_co2)

        operational_co2_emissions = massflux*3600/self.power * self.f_co2 * f_direct_co2

        return operational_co2_emissions

