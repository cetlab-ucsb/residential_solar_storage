import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# four representative days in each season 
winter_day = '01-15'
spring_day = '04-15'
summer_day = '07-15'
fall_day = '10-15'


# define a function to plot household profile and battery storage level
def plot_4days(mode, tmy_code, utility, year, c_cost):
    df = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                     'optimized/minCost_%(mode)s_%(year)s_cc_%(c_cost)s/'
                     'optimal_minCost_%(tmy_code)s_%(utility)s_%(year)s_cc_%(c_cost)s.csv'
                     % {'year': year, 'mode': mode, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost},
                     index_col=0)

    df.rename(columns={'Time': 'Hour'}, inplace=True)
    s = df['Hour'].str.split()
    df['Hour'] = pd.to_datetime(s.str[0], format="%m/%d") + pd.to_timedelta(s.str[1].str.split(':').str[0] + ' hours')
    df['Hour'] = df['Hour'].dt.strftime('%m-%d %H:%M:%S')
    df['Hour'] = str(year) + '-' + df['Hour']
    df['Hour'] = pd.to_datetime(df['Hour'])

    df['batt_char_disc'] = np.where(df['p_char'] == 0, df['p_disc'],
                                    df['p_char'] + df['e_loss'])  # curve of battery charging and discharging

    year = str(year)
    # subset the data frame to each of the four representative days
    df_spring = df[(df['Hour'] >= pd.to_datetime(year + '-' + spring_day + ' ' + '00:00:00')) &
                   (df['Hour'] <= pd.to_datetime(year + '-' + spring_day + ' ' + '23:00:00'))]
    df_summer = df[(df['Hour'] >= pd.to_datetime(year + '-' + summer_day + ' ' + '00:00:00')) &
                   (df['Hour'] <= pd.to_datetime(year + '-' + summer_day + ' ' + '23:00:00'))]
    df_fall = df[(df['Hour'] >= pd.to_datetime(year + '-' + fall_day + ' ' + '00:00:00')) &
                 (df['Hour'] <= pd.to_datetime(year + '-' + fall_day + ' ' + '23:00:00'))]
    df_winter = df[(df['Hour'] >= pd.to_datetime(year + '-' + winter_day + ' ' + '00:00:00')) &
                   (df['Hour'] <= pd.to_datetime(year + '-' + winter_day + ' ' + '23:00:00'))]

    # Fig 1 - energy use plot in each of the four days (kWh)
    fig1, axs = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(8, 8))
    plt.setp(axs, xticks=np.arange(0, 24, step=2), yticks=np.arange(-5, 6, step=2),
             xlim=(0, 23), ylim=(-5, 6))

    alist = [[0, 0, df_winter, winter_day],
             [0, 1, df_spring, spring_day],
             [1, 0, df_summer, summer_day],
             [1, 1, df_fall, fall_day]]

    for i in range(4):  # draw four panel for each season
        axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour, alist[i][2]['Load'],
                                           color='purple', label='Load')
        axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour, alist[i][2]['PV_gen'],
                                           color='orange', label='PV')
        axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour,
                                           # alist[i][2]['e_grid_load'] + alist[i][2]['e_grid_batt'],  # ImportOnly
                                           alist[i][2]['e_grid_load'],  # ExportOnly
                                           color='grey', alpha=0.6, label='Grid')
        axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour, alist[i][2]['batt_char_disc'],
                                           color='blue', alpha=0.6, label='Battery')
        axs[0, 0].legend(loc='lower left', frameon=False)
        axs[alist[i][0], alist[i][1]].set_title(year + '-' + alist[i][3])

    for ax in axs.flat:
        ax.set(xlabel='Hour', ylabel='kWh')
        if utility == 'PGE':
            ax.axvspan(17, 20, alpha=0.3, color='pink', lw=0)
        else:
            ax.axvspan(16, 21, alpha=0.3, color='pink', lw=0)
        ax.label_outer()

    for ax in axs.flatten():
        ax.xaxis.set_tick_params(labelbottom=True)
        ax.yaxis.set_tick_params(labelleft=True)

    fig1.suptitle('Energy use profile, %(utility)s %(tmy_code)s (minCost, $%(c_cost)s/tCO2)'
                  % {'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost})
    plt.savefig('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Visualization/'
                'Dispatch_%(mode)s_%(year)s_%(utility)s_%(tmy_code)s_cc_%(c_cost)s.jpg' %
                {'mode': mode, 'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost},
                dpi=150, bbox_inches='tight')

    # Fig 2 - stored energy in battery in each of the four days (kWh)
    fig2, axs = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(8, 8))
    plt.setp(axs, xticks=np.arange(0, 24, step=2), yticks=np.arange(0, 15.1, step=3),
             xlim=(0, 23), ylim=(0, 15))

    for i in range(4):
        axs[alist[i][0], alist[i][1]].plot(alist[i][2]['Hour'].dt.hour, alist[i][2]['e_batt'],
                                           color='deepskyblue', label='')
        axs[alist[i][0], alist[i][1]].set_title(year + '-' + alist[i][3])

    for ax in axs.flat:
        ax.set(xlabel='Hour', ylabel='kWh')
        if utility == 'PGE':
            ax.axvspan(17, 20, alpha=0.3, color='pink', lw=0)
        else:
            ax.axvspan(16, 21, alpha=0.3, color='pink', lw=0)
        ax.label_outer()

    for ax in axs.flatten():
        ax.xaxis.set_tick_params(labelbottom=True)
        ax.yaxis.set_tick_params(labelleft=True)

    fig2.suptitle('Stored energy in battery, %(utility)s %(tmy_code)s (minCost, $%(c_cost)s/tCO2)'
                  % {'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost})
    plt.savefig('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Visualization/'
                'Storage_%(mode)s_%(year)s_%(utility)s_%(tmy_code)s_cc_%(c_cost)s.jpg' %
                {'mode': mode, 'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost},
                dpi=150, bbox_inches='tight')


plot_4days('Unconstrained', 724936, 'PGE', 2020, 1e-12)
plot_4days('Unconstrained', 722977, 'SCE', 2020, 1e-12)
plot_4days('Unconstrained', 722900, 'SDGE', 2020, 1e-12)


