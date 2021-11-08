import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

# four representative days in each season (PV_gen curves on 15th-19th don't look smooth.)
winter_day = '01-15'
spring_day = '04-15'
summer_day = '07-15'
fall_day = '10-15'

year = 2020

df = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Input_Data_%(year)s/'
                 '724927_PGE_%(year)s.csv' % {'year': year})
df2 = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Input_Data_%(year)s/'
                  '723927_SCE_%(year)s.csv' % {'year': year})
df3 = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Input_Data_%(year)s/'
                  '722900_SDGE_%(year)s.csv' % {'year': year})

df.rename(columns={'Time': 'Hour'}, inplace=True)
# df = df.drop['Load', 'PV_gen']
s = df['Hour'].str.split()
df['Hour'] = pd.to_datetime(s.str[0], format="%m/%d") + pd.to_timedelta(s.str[1].str.split(':').str[0] + ' hours')
df['Hour'] = df['Hour'].dt.strftime('%m-%d %H:%M:%S')
df['Hour'] = str(year) + '-' + df['Hour']
df['Hour'] = pd.to_datetime(df['Hour'])

df['AEF_SCE'] = df2['AEF']
df['MEF_SCE'] = df2['MEF']
df['AEF_SDGE'] = df3['AEF']
df['MEF_SDGE'] = df3['MEF']

# subset the data frame to each of the four representative days
df_spring = df[(df['Hour'] >= pd.to_datetime(str(year) + '-' + spring_day + ' ' + '00:00:00')) &
               (df['Hour'] <= pd.to_datetime(str(year) + '-' + spring_day + ' ' + '23:00:00'))]
df_summer = df[(df['Hour'] >= pd.to_datetime(str(year) + '-' + summer_day + ' ' + '00:00:00')) &
               (df['Hour'] <= pd.to_datetime(str(year) + '-' + summer_day + ' ' + '23:00:00'))]
df_fall = df[(df['Hour'] >= pd.to_datetime(str(year) + '-' + fall_day + ' ' + '00:00:00')) &
             (df['Hour'] <= pd.to_datetime(str(year) + '-' + fall_day + ' ' + '23:00:00'))]
df_winter = df[(df['Hour'] >= pd.to_datetime(str(year) + '-' + winter_day + ' ' + '00:00:00')) &
               (df['Hour'] <= pd.to_datetime(str(year) + '-' + winter_day + ' ' + '23:00:00'))]

# Emissions curve (gCO2e/kWh)
fig2, axs = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(8, 8))
plt.setp(axs, xticks=np.arange(0, 24, step=2), yticks=np.arange(0, 650, step=100),
         xlim=(0, 23), ylim=(0, 650))

alist = [[0, 0, df_winter, winter_day],
         [0, 1, df_spring, spring_day],
         [1, 0, df_summer, summer_day],
         [1, 1, df_fall, fall_day]]

for i in range(4):
    axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour, alist[i][2]['AEF'],
                                       color='royalblue', label='AER-p9')
    axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour, alist[i][2]['AEF_SCE'],
                                       color='darkorange', label='AER-p10')
    axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour, alist[i][2]['AEF_SDGE'],
                                       color='forestgreen', label='AER-p11')
    axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour, alist[i][2]['MEF'],
                                       color='royalblue', label='LRMER-p9', linestyle="--")
    axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour, alist[i][2]['MEF_SCE'],
                                       color='darkorange', label='LRMER-p10', linestyle="--")
    axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour, alist[i][2]['MEF_SDGE'],
                                       color='forestgreen', label='LRMER-p11', linestyle="--")
    axs[0, 0].legend(loc='best', frameon=False, fontsize=8.5)  # bbox_to_anchor=(0.6, 0.78)
    axs[alist[i][0], alist[i][1]].set_title(str(year) + '-' + alist[i][3])

for ax in axs.flat:
    ax.set(xlabel='Hour', ylabel='gCO$_2$/kWh')

for ax in axs.flat:
    ax.label_outer()

for ax in axs.flatten():
    ax.xaxis.set_tick_params(labelbottom=True)
    ax.yaxis.set_tick_params(labelleft=True)

# fig2.suptitle('Emission Rates by Balancing Area')
plt.savefig('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Visualization/'
            'AllEFs_by_BA_%(year)s.jpg' % {'year': year},
            dpi=150, bbox_inches='tight')
