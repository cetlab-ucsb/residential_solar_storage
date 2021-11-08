import glob
import pandas as pd
import re


############### 1. Calculate and export annual sums of electricity flows in optimized solutions ###############

def sum_flows(obj, mode, year, c_cost):
    if obj == 'minCost':
        flows_folder = '/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/' \
                       'Optimized/%(obj)s_%(mode)s_%(year)s_cc_%(c_cost)s/*.csv' \
                       % {'obj': obj, 'mode': mode, 'year': year, 'c_cost': c_cost}
    else:
        flows_folder = '/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/' \
                       'Optimized/%(obj)s_%(mode)s_%(year)s/*.csv' % {'obj': obj, 'mode': mode, 'year': year}

    flows_file_list = []
    for flows_path in glob.glob(flows_folder):
        flows_file_list.append(flows_path)

    df_flows = pd.DataFrame()

    for i in range(len(flows_file_list)):
        df_results = pd.read_csv(flows_file_list[i], index_col=0)

        df_i = pd.DataFrame()  # empty data frame to contain the sums of columns for file i
        df_i = df_i.append(pd.DataFrame(df_results.sum())).T  # calculate the sums of each column
        df_i.drop(df_i.columns[[0, 3, 4, 5, 12, 13]], inplace=True, axis=1)  # drop: AEF, MEF, ToU, soc_batt, e_batt

        file_name = str(flows_file_list[i]).split('.csv')[0].split('/')[-1:][0]  # get file name by slicing the path
        tmy_i = re.findall(r'_(\d{6})', file_name)
        utility_i = re.findall(r'PGE|SCE|SDGE', file_name)

        df_i.insert(0, 'tmy_code', tmy_i)  # insert the tmy code to the far left of the df
        df_i.insert(1, 'utility', utility_i)
        df_flows = df_flows.append(df_i)  # append the summed line to the data frame
        del df_i

        if obj == 'minCost':
            writer1 = pd.ExcelWriter('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                                     'Results/Optimized/Flow_%(obj)s_%(mode)s_%(year)s_cc_%(c_cost)s.xlsx'
                                     % {'obj': obj, 'mode': mode, 'year': year, 'c_cost': c_cost}, engine='xlsxwriter')
            df_flows.to_excel(writer1, sheet_name='all_households', index=False)  # Write each dataframe to a sheet
            writer1.save()  # Close the Pandas Excel writer and output the Excel file
        else:
            writer1 = pd.ExcelWriter('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                                     'Results/Optimized/Flow_%(obj)s_%(mode)s_%(year)s.xlsx'
                                     % {'obj': obj, 'mode': mode, 'year': year}, engine='xlsxwriter')
            df_flows.to_excel(writer1, sheet_name='all_households', index=False)  # Write each dataframe to a sheet
            writer1.save()  # Close the Pandas Excel writer and output the Excel file


# sum_flows('minCost', 'ExportOnly', 2020, 1e-12)
# sum_flows('minCost', 'ExportOnly', 2020, -1e-12)
# sum_flows('minCost', 'ExportOnly', 2040, 1e-12)
# sum_flows('minCost', 'ExportOnly', 2020, 51)
# sum_flows('minCost', 'ExportOnly', 2040, 73)
# sum_flows('minGHG', 'ExportOnly', 2020, 0)
# sum_flows('minGHG', 'ExportOnly', 2040, 0)

# sum_flows('minCost', 'ImportOnly', 2020, 1e-12)
# sum_flows('minCost', 'ImportOnly', 2020, -1e-12)
# sum_flows('minCost', 'ImportOnly', 2040, -1e-12)
# sum_flows('minCost', 'ImportOnly', 2020, 51)
# sum_flows('minCost', 'ImportOnly', 2040, 73)
# sum_flows('minGHG', 'ImportOnly', 2020, 0)
# sum_flows('minGHG', 'ImportOnly', 2040, 0)

# sum_flows('minCost', 'Unconstrained', 2040, 1e-12)
# sum_flows('minCost', 'Unconstrained', 2040, -1e-12)

################ 2. Calculate and export annual sums of life-cycle emissions and cost #################

def sum_results(obj, mode, year, c_cost):
    if obj == 'minCost':
        results_folder = '/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/' \
                         'results_%(obj)s_%(mode)s_%(year)s_cc_%(c_cost)s_batteryX2/*.csv' \
                         % {'obj': obj, 'mode': mode, 'year': year, 'c_cost': c_cost}
    else:
        results_folder = '/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/' \
                         'results_%(obj)s_%(mode)s_%(year)s/*.csv' % {'obj': obj, 'mode': mode, 'year': year}

    results_file_list = []
    for results_path in glob.glob(results_folder):
        results_file_list.append(results_path)

    df_sum = pd.DataFrame()

    for i in range(len(results_file_list)):
        df_results = pd.read_csv(results_file_list[i], index_col=0)
        # df_results = df_results.rename(columns={"p_disc": "e_batt_load"})

        df_i = pd.DataFrame()  # empty data frame to contain the sums of columns for file i
        df_i = df_i.append(pd.DataFrame(df_results.sum())).T  # calculate the sums of each column
        df_i.drop(df_i.columns[0], inplace=True, axis=1)  # drop: AEF, MEF, ToU, soc_batt, e_batt

        file_name = str(results_file_list[i]).split('.csv')[0].split('/')[-1:][0]  # get file name by slicing the path
        tmy_i = re.findall(r'_(\d{6})', file_name)
        utility_i = re.findall(r'PGE|SCE|SDGE', file_name)

        df_i.insert(0, 'tmy_code', tmy_i)  # insert the tmy code to the far left of the df
        df_i.insert(1, 'utility', utility_i)
        df_sum = df_sum.append(df_i)  # append the summed line to the data frame
        del df_i

        # df_sum.reset_index(drop=True)
        # df_sum.set_index('file')
        # df_sum = df_sum.sort_values(by='c_cost', ascending=True)

        df_sum['GHG_diff_PVonly'] = df_sum['GHG_total_PVonly'] - df_sum['GHG_total_noPV']
        df_sum['GHG_diff_PVbatt'] = df_sum['GHG_total_PV+Batt'] - df_sum['GHG_total_noPV']
        df_sum['cost_diff_PVonly'] = df_sum['cost_total_PVonly_withCC'] - df_sum['cost_total_noPV_withCC']
        df_sum['cost_diff_PVbatt'] = df_sum['cost_total_PV+Batt_withCC'] - df_sum['cost_total_noPV_withCC']

        df_sum['GHG_reduce_PVonly'] = (df_sum['GHG_total_PVonly'] - df_sum['GHG_total_noPV']) / df_sum['GHG_total_noPV']
        df_sum['GHG_reduce_PVonly'] = df_sum['GHG_reduce_PVonly'].map('{:.3f}'.format)

        df_sum['GHG_reduce_PVbatt'] = (df_sum['GHG_total_PV+Batt'] - df_sum['GHG_total_noPV']) / df_sum[
            'GHG_total_noPV']
        df_sum['GHG_reduce_PVbatt'] = df_sum['GHG_reduce_PVbatt'].map('{:.3f}'.format)

        df_sum['cost_reduce_PVonly'] = (df_sum['cost_total_PVonly_withCC'] -
                                        df_sum['cost_total_noPV_withCC']) / df_sum['cost_total_noPV_withCC']
        df_sum['cost_reduce_PVonly'] = df_sum['cost_reduce_PVonly'].map('{:.3f}'.format)

        df_sum['cost_reduce_PVbatt'] = (df_sum['cost_total_PV+Batt_withCC'] -
                                        df_sum['cost_total_noPV_withCC']) / df_sum['cost_total_noPV_withCC']
        df_sum['cost_reduce_PVbatt'] = df_sum['cost_reduce_PVbatt'].map('{:.3f}'.format)

        # df_sum['self_cons_rate'] = (df_sum['e_PV_load'] + df_sum['e_PV_batt'])/df_sum['PV_gen']  # for ImportOnly
        # df_sum['self_cons_rate'] = (df_sum['e_PV_load'] + df_sum['e_batt_load']) / df_sum['PV_gen']  # for ExportOnly
        # df_sum['self_cons_rate'] = df_sum['self_cons_rate'].map('{:.3f}'.format)

        if obj == 'minCost':
            writer = pd.ExcelWriter('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                                    'Results/Sum_%(obj)s_%(mode)s_%(year)s_cc_%(c_cost)s_batteryX2.xlsx'
                                    % {'obj': obj, 'mode': mode, 'year': year, 'c_cost': c_cost}, engine='xlsxwriter')
            df_sum.to_excel(writer, sheet_name='all_households', index=False)  # Write each dataframe to a sheet
            writer.save()  # Close the Pandas Excel writer and output the Excel file
        else:
            writer = pd.ExcelWriter('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                                    'Results/Sum_%(obj)s_%(mode)s_%(year)s.xlsx'
                                    % {'obj': obj, 'mode': mode, 'year': year}, engine='xlsxwriter')
            df_sum.to_excel(writer, sheet_name='all_households', index=False)  # Write each dataframe to a sheet
            writer.save()  # Close the Pandas Excel writer and output the Excel file


sum_results('minCost', 'ExportOnly', 2020, 1e-12)
# sum_results('minCost', 'ExportOnly', 2020, -1e-12)
# sum_results('minCost', 'ExportOnly', 2040, 1e-12)
# sum_results('minCost', 'ExportOnly', 2020, 51)
# sum_results('minCost', 'ExportOnly', 2040, 73)
#
# sum_results('minCost', 'ImportOnly', 2020, 1e-12)
sum_results('minCost', 'ImportOnly', 2020, -1e-12)
# sum_results('minCost', 'ImportOnly', 2040, -1e-12)
# sum_results('minCost', 'ImportOnly', 2020, 51)
# sum_results('minCost', 'ImportOnly', 2040, 73)
#
# sum_results('minGHG', 'ExportOnly', 2020, 0)
# sum_results('minGHG', 'ExportOnly', 2040, 0)
# sum_results('minGHG', 'ImportOnly', 2020, 0)
# sum_results('minGHG', 'ImportOnly', 2040, 0)

# sum_results('minCost', 'Unconstrained', 2040, 1e-12)
# sum_results('minCost', 'Unconstrained', 2040, -1e-12)


################### 3. Summary table of the mean and median values of all results by utility area ################

summary_folder = '/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/*.xlsx'

summary_file_list = []
for summary_path in glob.glob(summary_folder):
    summary_file_list.append(summary_path)

sum_table = pd.DataFrame()

for i in range(len(summary_file_list)):
    df_sum = pd.read_excel(summary_file_list[i], index_col=0)

    df_sum = pd.concat([df_sum.iloc[:, 0:1], df_sum.iloc[:, -16:]], axis=1)

    df_mean = df_sum.groupby('utility').mean().round(3)
    df_median = df_sum.groupby('utility').median().round(3)

    file_name = str(summary_file_list[i]).split('.xlsx')[0].split('/')[-1:][0]  # get file name by slicing the path
    file_name = file_name.strip('Sum')

    with pd.ExcelWriter('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                        'Sum_tables/%(file_name)s.xlsx' % {'file_name': file_name}) as writer:
        df_mean.to_excel(writer, sheet_name='mean')
        df_median.to_excel(writer, sheet_name='median')

    del df_sum
    del df_mean
    del df_median
