import pandas as pd

map_tmy = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                        'Annual_Load_PV_BA_by_Location.xlsx', index_col=0)  # a table listing TMY 3 location codes


# define a function to calculate the life-cycle cost and emissions

def calc_lifecycle(obj, mode, year, c_cost):
    df_params = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                              'df_params_%(year)s_sensitivity_size.xlsx' % {'year': year})  # read the parameters

    e_max = df_params['value'][3]  # kWh, usable storage capacity of the battery
    # e_thruput = df_params['value'][4]  # kWh, lifetime aggregate discharge limit of the battery
    e_PV_avg_life = df_params['value'][5]  # kWh, lifetime aggregate generation of a 4-kW PV (average value)
    life_PV = int(df_params['value'][6])  # years, lifetime of a solar PV system
    life_batt = int(df_params['value'][7])  # years, lifetime of a solar PV system
    # deg_rate_PV = df_params['value'][8]  # reduction of solar output per year
    # deg_rate_batt = df_params['value'][9]  # reduction of solar output per year
    cost_batt = df_params['value'][10]  # $, initial cost to purchase battery
    cost_PV = df_params['value'][11]  # $, initial cost to purchase a 10 kW solar PV system
    unit_ebem_batt = df_params['value'][12]  # kgCO2e per kWh usable capacity, unit embodied emissions of the battery
    unit_ebem_PV = df_params['value'][13]  # gCO2e per kWh electricity output, unit embodied emissions of solar PV

    ebem_batt = unit_ebem_batt * e_max  # total embodied emissions of the battery
    ebem_PV = unit_ebem_PV * e_PV_avg_life * 0.001  # kgCO2e, total embodied emissions of PV

    indirect_EF_grid = {'ind_grid': [df_params['value'][14], df_params['value'][15], df_params['value'][16]]}
    indirect_EF_grid = pd.DataFrame(indirect_EF_grid, index=('p9', 'p10', 'p11'))

    discount = df_params['value'][17]
    annuity_PV = (1 - (1 + discount) ** (-1 * life_PV))/discount
    annuity_batt = (1 - (1 + discount) ** (-1 * life_batt)) / discount

    for i in range(len(map_tmy)):  #
        tmy_code = map_tmy.index[i]
        utility = map_tmy.at[tmy_code, 'ToU Assigned']
        BA = map_tmy.iloc[i, 4]  # balancing area
        grid_ind_ef = indirect_EF_grid.loc[BA, 'ind_grid']

        if obj == 'minCost':
            df = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                             'Optimized/%(obj)s_%(mode)s_%(year)s_cc_%(c_cost)s_batteryX0.5/'
                             'optimal_%(obj)s_%(tmy_code)s_%(utility)s_%(year)s_cc_%(c_cost)s.csv'
                             % {'obj': obj, 'mode': mode, 'tmy_code': tmy_code,
                                'utility': utility, 'year': year, 'c_cost': c_cost},
                             index_col=0)  # read the optimal solution
        else:
            df = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                             'Optimized/%(obj)s_%(mode)s_%(year)s/optimal_%(obj)s_%(tmy_code)s_%(utility)s_%(year)s.csv'
                             % {'obj': obj, 'mode': mode, 'tmy_code': tmy_code,
                                'utility': utility, 'year': year},
                             index_col=0)  # read the optimal solution

        # e_life_PV = sum(df['PV_gen']) * sum([(1 - deg_rate_PV) ** x for x in range(life_PV)])  # lifetime PV output

        # calculate the utility cost and GHG emissions under PV_only scenario

        df['cost_grid_PVonly'] = df['ToU'] * df['e_grid_load_PVonly']
        df['cost_feedin_PVonly'] = - df['ToU'] * df['e_PV_grid_PVonly']

        # MEF applied to the change in net load and feedin

        df['GHG_grid_PVonly'] = df['AEF'] * df['Load'] * 0.001 + df['e_grid_load_PVonly'] * grid_ind_ef * 0.001 + \
                                df['MEF'] * (df['e_grid_load_PVonly'] - df['Load']) * 0.001
        df['GHG_feedin_PVonly'] = - df['MEF'] * df['e_PV_grid_PVonly'] * 0.001

        # calculate hourly GHG emissions of PV+batt scenario (all in kgCO2e). dt = 1 hr is omitted in formulas

        df['GHG_emb_batt'] = ebem_batt / life_batt / 8760  # hourly embodied emissions of battery (static allocation)
        # df['GHG_emb_batt'] = ebem_batt * df['p_disc'] / e_thruput  # hourly embodied emissions of battery
        df['GHG_emb_PV'] = ebem_PV / life_PV / 8760  # hourly embodied emissions - PV
        df['GHG_grid'] = df['AEF'] * df['Load'] * 0.001 + \
                         (df['e_grid_load'] + df['e_grid_batt']) * grid_ind_ef * 0.001 + \
                         df['MEF'] * (df['e_grid_load'] + df['e_grid_batt'] - df['Load']) * 0.001  # emissions, grid
        df['GHG_PV_grid'] = - df['MEF'] * df['e_PV_grid'] * 0.001  # emissions, PV to grid

        # cost breakdown of PV+batt scenario (all in $)

        df['cost_cap_batt'] = cost_batt / annuity_batt / 8760  # hourly capital cost of battery (static allocation)
        # df['cost_cap_batt'] = cost_batt * df['p_disc'] / e_thruput  # hourly capital cost of battery
        df['cost_cap_PV'] = cost_PV / annuity_PV / 8760  # hourly capital cost of solar PV (static allocation)
        # df['cost_cap_PV'] = cost_PV * df['PV_gen'] / e_life_PV  # hourly capital cost of solar PV
        df['cost_grid'] = df['ToU'] * (df['e_grid_load'] + df['e_grid_batt'])  # hourly cost for using grid
        df['cost_feedin'] = - df['ToU'] * df['e_PV_grid']  # hourly feedin cost for exporting PV

        # calculate hourly carbon cost of embodied + operational emissions under noPV, PVonly and PV+Batt scenario

        df['cost_carbon_noPV'] = c_cost * 0.001 * (df['AEF'] * df['Load'] * 0.001
                                                   + grid_ind_ef * df['Load'] * 0.001)  # no_PV
        df['cost_carbon_PVonly'] = c_cost * 0.001 * (df['GHG_grid_PVonly'] + df['GHG_emb_PV'])  # PVonly
        df['cost_carbon_PV+Batt'] = c_cost * 0.001 * ((df['AEF'] + grid_ind_ef) *
                                                      (df['e_grid_load'] + df['e_grid_batt']) * 0.001 +
                                                      df['GHG_emb_PV'] + df['GHG_emb_batt'])  # PV+Batt

        # calculate total GHG emissions at each hour under noPV, PVonly and PV+Batt scenario

        df['GHG_total_noPV'] = df['AEF'] * df['Load'] * 0.001 + df['Load'] * grid_ind_ef * 0.001  # GHG, no_PV
        df['GHG_total_PVonly'] = df['GHG_grid_PVonly'] + df['GHG_feedin_PVonly'] + df['GHG_emb_PV']  # GHG, PV_only
        df['GHG_total_PV+Batt'] = df['GHG_grid'] + df['GHG_PV_grid'] + \
                                  df['GHG_emb_PV'] + df['GHG_emb_batt']  # GHG, PV+Batt

        # calculate total cost at each hour under noPV, PVonly and PV+Batt scenario

        df['cost_total_noPV_noCC'] = df['ToU'] * df['Load']
        df['cost_total_noPV_withCC'] = df['cost_total_noPV_noCC'] + df['cost_carbon_noPV']
        df['cost_total_PVonly_noCC'] = df['cost_grid_PVonly'] + df['cost_feedin_PVonly'] + df['cost_cap_PV']
        df['cost_total_PVonly_withCC'] = df['cost_total_PVonly_noCC'] + df['cost_carbon_PVonly']
        df['cost_total_PV+Batt_withCC'] = df['cost_cap_batt'] + df['cost_cap_PV'] + \
                                          df['cost_grid'] + df['cost_feedin'] + df['cost_carbon_PV+Batt']

        df.drop(df.iloc[:, 1:19], axis=1, inplace=True)

        if obj == 'minCost':
            df.round(3).to_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                               'results_%(obj)s_%(mode)s_%(year)s_cc_%(c_cost)s_batteryX0.5/'
                               'results_%(obj)s_%(tmy_code)s_%(utility)s_%(year)s_cc_%(c_cost)s.csv'
                               % {'obj': obj, 'mode': mode, 'tmy_code': tmy_code,
                                  'utility': utility, 'year': year, 'c_cost': c_cost})
        else:
            df.round(3).to_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                               'results_%(obj)s_%(mode)s_%(year)s/results_%(obj)s_%(tmy_code)s_%(utility)s_%(year)s.csv'
                               % {'obj': obj, 'mode': mode, 'tmy_code': tmy_code, 'utility': utility, 'year': year})


# calc_lifecycle('minCost', 'ImportOnly', 2020, 0)
# calc_lifecycle('minCost', 'ImportOnly', 2020, 1e-12)
calc_lifecycle('minCost', 'ImportOnly', 2020, -1e-12)
# calc_lifecycle('minCost', 'ImportOnly', 2020, 51)
# calc_lifecycle('minCost', 'ImportOnly', 2040, 73)
# calc_lifecycle('minGHG', 'ImportOnly', 2020, 0)
# calc_lifecycle('minGHG', 'ImportOnly', 2040, 0)
