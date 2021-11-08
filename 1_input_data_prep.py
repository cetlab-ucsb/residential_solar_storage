import pandas as pd
import glob
import re

# make a list of paths to load .csv files
load_path = '/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Load_Profiles_Clean/*.csv'

load_code_list = []
for load_code in glob.glob(load_path):
    load_code_list.append(load_code)

# define the parameters for right paths
suffix = "TYA.CSV_PV_gen"
PV_folder_path = "/Users/jiajiazheng/Box/Suh's lab/GSRs/Jiajia/3-Residential Solar-plus-storage/PV_Outputs_4kW/"
save_to_path = "/Users/jiajiazheng/Box/Suh's lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Input_Data_2020/"

df_shape = list()  # a list to contain the shapes of combined input data frames to check completeness
df_load_sum = {}  # a dictionary to store the location code and total load

# iterate over the solar PV generation profiles and merge with load profiles for all 73 households
for i in range(len(load_code_list)):
    df_load = pd.read_csv(load_code_list[i])
    df_load = df_load.drop(['Sum_gas'], axis=1)
    df_load.columns = ['Time', 'Load']

    tmy_code = re.findall(r'(\d{6})', load_code_list[i])[0]

    PV_gen_path = PV_folder_path + tmy_code + suffix + ".csv"
    df_PV_gen = pd.read_csv(PV_gen_path, header=None)
    df_PV_gen.columns = ["PV_gen"]
    df_load_PV = df_load.join(df_PV_gen * 0.001)

    df_load_sum[tmy_code] = [df_load['Load'].sum(), df_load_PV['PV_gen'].sum()]

    # df_shape.append((tmy_code, df_load_PV.shape))
    df_merged = df_load_PV.round(4).to_csv(save_to_path + tmy_code + "_2020.csv")

# save the list containing tmy_code & data frame shape pairs to a .txt file
# with open(save_to_path + "Completeness_check.txt", 'w') as output:
#     for row in df_shape:
#         output.write(str(row) + '\n')

# there are two TMY 3 locations with incomplete load data: #722895 LOMPOC and #722976 FULLERTON MUNICIPAL
# removed in Load_Profiles_Sum folder

# sum up the annual load and PV generation of 52 households and export to an excel file
df_load_sum = pd.DataFrame(data=df_load_sum).T  # turn dict to data frame
df_load_sum.columns = ['Annual Load', 'PV Generation']
df_load_sum.index.names = ['Location']
df_load_sum['PV to load ratio'] = round(df_load_sum['PV Generation'] / df_load_sum['Annual Load'], 2)
df_load_sum.round(2).to_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                            'Annual_Load_PV_by_Location.csv')

# Add the AEF, MEF columns to the data_input csv file for each location
# firstly map the location by its Balancing Area
map_tmy = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                        'Annual_Load_PV_BA_by_Location.xlsx', index_col=0)

tou_df = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                       'ToU_CA_hourly.xlsx')

for i in range(len(map_tmy)):
    tmy_code = map_tmy.index[i]
    BA_i = map_tmy.iloc[i, 4]  # covered by which balancing area
    utility_i = map_tmy.iloc[i, 6]  # assigned utility company whose ToU plan is used
    data_input = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                             'Input_Data_2040/%s_2040.csv' % tmy_code, index_col=0)

    ef_df = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/MEFs/'
                        'StdScen20_MidCase_hourly_%s_2040.csv' % BA_i, skiprows=2)

    data_input['Load'] = round(data_input['Load'], 4)
    data_input['PV_gen'] = round(data_input['PV_gen'], 4)

    data_input['AEF'] = ef_df['co2_rate_avg_load_enduse']
    data_input['MEF'] = ef_df['co2_lrmer_enduse']
    data_input['ToU'] = tou_df[utility_i]

    data_input.to_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                      'Input_Data_2040/%(tmy_code)s_%(utility_i)s_2040.csv'
                      % {'tmy_code': tmy_code, 'utility_i': utility_i})

