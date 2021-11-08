import glob
import pandas as pd
import os
import re


########## Below are codes to change ToU rates to RTP rates ############
## Prepare real-time pricing based on total_marginal_cost & enduse_load from Cambium

map_tmy = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                        'Annual_Load_PV_BA_by_Location.xlsx', index_col=0)  # a table listing TMY 3 location codes

data_input = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                         'Input_Data_2040_RTP/690150_SCE_2040.csv', index_col=0)

for i in range(len(map_tmy)):
    tmy_code = map_tmy.index[i]
    BA_i = map_tmy.iloc[i, 4]  # covered by which balancing area
    utility_i = map_tmy.iloc[i, 6]  # assigned utility company whose ToU plan is used

    data_input = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                             'Input_Data_2040_RTP/%(tmy)s_%(utility)s_2040.csv'
                             % {'tmy': tmy_code, 'utility': utility_i}, index_col=0)

    ef_df = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/MEFs/'
                        'StdScen20_MidCase_hourly_%s_2040.csv' % BA_i, skiprows=2)

    data_input = data_input.rename(columns={'ToU': 'ToU_old'})
    data_input['Load'] = round(data_input['Load'], 4)
    data_input['PV_gen'] = round(data_input['PV_gen'], 4)

    data_input['target_revenue'] = data_input['ToU_old'] * ef_df['enduse_load'] * 0.001  # in million $
    data_input['supply_cost'] = ef_df['total_cost_enduse'] * (ef_df['generation'] + ef_df['imports'] -
                                                              ef_df['exports']) * 0.000001  # in million $
    data_input['other_cost'] = (data_input['target_revenue'].sum() - data_input['supply_cost'].sum()) * \
                               ef_df['enduse_load'] / ef_df['enduse_load'].sum()
    data_input['ToU'] = (data_input['supply_cost'] + data_input['other_cost']) * 1000 / ef_df['enduse_load']

    data_input['ToU'] = round(data_input['ToU'], 4)  # column still named 'ToU' but it is actually RTP
    del data_input['target_revenue']
    del data_input['supply_cost']
    del data_input['other_cost']

    data_input.to_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                      'Input_Data_2040_RTP/%(tmy_code)s_%(utility_i)s_2040.csv'
                      % {'tmy_code': tmy_code, 'utility_i': utility_i})

