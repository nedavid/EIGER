# EIGER
**E**nvironmental **I**mpact of **G**eothermal **E**ne**R**gy systems

## Description

Based on a small number of parameters of a geothermal energy system this code computes the impact of the geothermal energy system to various environmental impact categories. Currently implemented are the models of [Paulillo et al. (2022)](https://doi.org/10.1016/j.cesys.2022.100086) for conventional (dry steam and flash) and enhanced geothermal systems for power production and [Douzciech et al. (2021)](https://doi.org/10.1021/acs.est.0c06751) for enhanced geothermal systems for heat production. The code is programmed in a way to facilitate the addition of further environmental impact models.

The impact per environmental category is computed with this general equation:
```
Impact per category = Sum_over_i[(alpha_i * x_i * y_i * z_i**beta_i * 10**(gamma_i * w_i)) / (u_i * v_i) ]
```
`alpha_i, beta_i, gamma_i` are coefficients of the models. `u_i, v_i, w_i, x_i, y_i, z_i` are parameters of the geothermal energy system, e.g. well depth.

## Usage

Import `GeothermalPlant` from `main`. A new instance of a `GeothermalPlant` can be initialized by choosing the environmental impact model for the plant type e.g. `conventional_power_20` for the 20% threshold model for conventional power plants of [Paulillo et al. (2022)](https://doi.org/10.1016/j.cesys.2022.100086), together with the number of environmental impact categories and parameters of the model:
```
plant_conv = GeothermalPlant('conventional_power_20',16,10)
```
A dictionary with parameter values of the geothermal energy system can then be passed to the `simple_impact_model` function of the geothermal energy system:
```
parameters = {'operational_CO2_emissions': 0.0209,  # kgCO2/kWh
              'operational_CH4_emissions': 0.0,  # kgCH4/kWh
              'producers_capacity': 9,  # MW/well
              'average_depth_of_wells': 2220,  # m/well
              'initial_harmonic_decline_rate': 0.03,
              'success_rate_primary_wells': 100} # %
category, impact = plant_conv.simple_impact_model(parameters)
```
The output are two lists, one containing the environmental impact of the geothermal energy system called `impact` and the second on containing the name of the environmental impact category called 'category'.

## Define new environmental impact model
The environamental impact models are defined by several tables which are contained in one Excel-file per model. There are tables for `alpha_i, beta_i, gamma_i, u_i, v_i, w_i, x_i, y_i, z_i` for each environmental impact category and valid ranges for the parameters (`u_i, v_i, w_i, x_i, y_i, z_i`). The name of the environamental impact model is defined by the name of the Excel-file.