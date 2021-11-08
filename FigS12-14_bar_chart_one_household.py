import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


def bar_plot(tmy_code, utility, year, c_cost):
    # draw bar plot comparing the emissions and cost breakdown of four scenarios
    scenario = ['Baseline', 'Solar-Only', 'ExportOnly', 'ImportOnly', 'Unconstrained']
    df = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                     'results_minCost_ExportOnly_%(year)s_cc_1e-12/'
                     'results_minCost_%(tmy_code)s_%(utility)s_%(year)s_cc_1e-12.csv'
                     % {'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost}, index_col=0)

    df2 = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                      'results_minCost_ImportOnly_%(year)s_cc_-1e-12/'
                      'results_minCost_%(tmy_code)s_%(utility)s_%(year)s_cc_-1e-12.csv'
                      % {'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost}, index_col=0)

    df3 = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                      'results_minCost_Unconstrained_%(year)s_cc_1e-12/'
                      'results_minCost_%(tmy_code)s_%(utility)s_%(year)s_cc_1e-12.csv'
                      % {'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost}, index_col=0)

    # Annual GHG emissions breakdown under each scenario

    df_ghg = pd.DataFrame(index=scenario)

    df_ghg['GHG_emb_PV'] = [0, sum(df['GHG_emb_PV']), sum(df['GHG_emb_PV']), sum(df2['GHG_emb_PV']),
                            sum(df3['GHG_emb_PV'])]
    df_ghg['GHG_grid'] = [sum(df['GHG_total_noPV']), sum(df['GHG_grid_PVonly']),
                          sum(df['GHG_grid']), sum(df2['GHG_grid']), sum(df3['GHG_grid'])]
    df_ghg['GHG_feedin'] = [0, sum(df['GHG_feedin_PVonly']),
                            sum(df['GHG_PV_grid'] + df['GHG_batt_grid']), sum(df2['GHG_PV_grid']),
                            sum(df3['GHG_PV_grid'] + df3['GHG_batt_grid'])]
    df_ghg['GHG_emb_batt'] = [0, 0, sum(df['GHG_emb_batt']), sum(df2['GHG_emb_batt']), sum(df3['GHG_emb_batt'])]
    df_ghg['Net GHG emissions'] = df_ghg['GHG_emb_PV'] + df_ghg['GHG_grid'] + \
                                  df_ghg['GHG_feedin'] + df_ghg['GHG_emb_batt']

    fig1, axs = plt.subplots(2, 1, sharex=False, sharey=True, figsize=(8, 8), squeeze=False)  # figsize=(10, 6)

    axs[0, 0].barh(df_ghg.index, df_ghg['GHG_feedin'], color='seagreen', label='Emissions of feed-in',
                   height=0.4, edgecolor='black')
    axs[0, 0].barh(df_ghg.index, df_ghg['GHG_emb_PV'], color='orange', label='Embodied emissions of PV',
                   height=0.4, edgecolor='black')
    axs[0, 0].barh(df_ghg.index, df_ghg['GHG_grid'], left=df_ghg['GHG_emb_PV'], color='skyblue',
                   label='Emissions from grid use', height=0.4, edgecolor='black')
    axs[0, 0].barh(df_ghg.index, df_ghg['GHG_emb_batt'], left=df_ghg['GHG_grid'] + df_ghg['GHG_emb_PV'],
                   color='mediumpurple', label='Embodied emissions of battery', height=0.4, edgecolor='black')

    axs[0, 0].axvline(x=0, color='grey', linestyle=':')
    axs[0, 0].plot(df_ghg['Net GHG emissions'], df_ghg.index, marker='D', color='black',
                   linestyle="", linewidth=0)

    axs[0, 0].legend(bbox_to_anchor=(0.01, 0.04), loc='lower left', borderaxespad=0., frameon=False, fontsize=9)
    axs[0, 0].set_xlim(-2000, 3400)
    axs[0, 0].set_xlabel('GHG emissions (kgCO$_2$)')

    # axs[0, 0].set_title('Comparison of annual GHG emissions')

    net_emissions_value = df_ghg['Net GHG emissions']
    for i in range(5):
        axs[0, 0].annotate('{:.0f}'.format(net_emissions_value[i]),
                           xy=(net_emissions_value[i], i - 0.09),
                           xytext=(20, 0), textcoords='offset points', ha='center', va='bottom')

    # legend for net emission values
    axs[0, 0].plot(-1800, 1.1, 'D', color='black', markersize=5, linewidth=0)
    axs[0, 0].annotate('Net emissions', xy=(-1790, 1.1), xytext=(15, 0),  # xy=(-1808, 0.83), xytext=(15, 0), # 4 modes
                       textcoords='offset points', ha='left', va='center', color='black', fontsize=9)

    ########### Annual cost breakdown under each scenario ##############

    df_cost = pd.DataFrame(index=scenario)

    df_cost['cost_cap_PV'] = [0, sum(df['cost_cap_PV']), sum(df['cost_cap_PV']), sum(df2['cost_cap_PV']),
                              sum(df3['cost_cap_PV'])]
    df_cost['cost_grid'] = [sum(df['cost_total_noPV_noCC']), sum(df['cost_grid_PVonly']),
                            sum(df['cost_grid']), sum(df2['cost_grid']), sum(df3['cost_grid'])]
    df_cost['cost_feedin'] = [0, sum(df['cost_feedin_PVonly']), sum(df['cost_feedin']), sum(df2['cost_feedin']),
                              sum(df3['cost_feedin'])]
    df_cost['cost_cap_batt'] = [0, 0, sum(df['cost_cap_batt']), sum(df2['cost_cap_batt']), sum(df3['cost_cap_batt'])]
    df_cost['cost_carbon'] = [sum(df['cost_carbon_noPV']), sum(df['cost_carbon_PVonly']),
                              sum(df['cost_carbon_PV+Batt']), sum(df2['cost_carbon_PV+Batt']),
                              sum(df3['cost_carbon_PV+Batt'])]

    df_cost['Total cost'] = df_cost['cost_cap_PV'] + df_cost['cost_grid'] + df_cost['cost_feedin'] + \
                            df_cost['cost_cap_batt'] + df_cost['cost_carbon']

    axs[1, 0].barh(df_cost.index, df_cost['cost_feedin'], color='seagreen', label='Cost of feed-in',
                   height=0.4, edgecolor='black')
    axs[1, 0].barh(df_cost.index, df_cost['cost_cap_PV'], color='orange', label='Annualized cost of PV',
                   height=0.4, edgecolor='black')
    axs[1, 0].barh(df_cost.index, df_cost['cost_grid'], left=df_cost['cost_cap_PV'], color='skyblue',
                   label='Cost of grid use', height=0.4, edgecolor='black')
    axs[1, 0].barh(df_cost.index, df_cost['cost_cap_batt'], left=df_cost['cost_grid'] + df_cost['cost_cap_PV'],
                   color='mediumpurple', label='Annualized cost of battery', height=0.4, edgecolor='black')
    axs[1, 0].barh(df_cost.index, df_cost['cost_carbon'],
                   left=df_cost['cost_grid'] + df_cost['cost_cap_PV'] + df_cost['cost_cap_batt'],
                   color='grey', label='Cost of GHG emissions', height=0.4, edgecolor='black')

    axs[1, 0].axvline(x=0, color='grey', linestyle=':')
    axs[1, 0].plot(df_cost['Total cost'], df_cost.index, marker='D', color='black', linestyle="", linewidth=0)

    axs[1, 0].legend(bbox_to_anchor=(0.01, 0.04), loc='lower left', borderaxespad=0., frameon=False, fontsize=9)
    axs[1, 0].set_xlim(-3500, 4800)
    axs[1, 0].set_xlabel('Cost ($)')

    net_cost_value = df_cost['Total cost']
    for i in range(5):
        axs[1, 0].annotate('{:.0f}'.format(net_cost_value[i]),
                           xy=(net_cost_value[i], i - 0.09),
                           xytext=(20, 0), textcoords='offset points', ha='center', va='bottom')

    # legend for net cost values
    axs[1, 0].plot(-3185, 1.41, 'D', color='black', markersize=5, linewidth=0)  # -2705, 1.05,  # 4 modes
    axs[1, 0].annotate('Net cost', xy=(-3180, 1.41), xytext=(15, 0),  #  xy=(-2690, 1.05), xytext=(15, 0),  # 4 modes
                       textcoords='offset points', ha='left', va='center', fontsize=9)

    for i in range(2):
        axs[i, 0].get_xaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    fig1.suptitle('%(utility)s %(tmy_code)s, no carbon price (%(year)s)'
                  % {'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost})
    fig1.tight_layout()
    plt.savefig('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Visualization/'
                'Annual_emissions_cost_%(utility)s_%(tmy_code)s_%(year)s_cc_0.jpg'
                % {'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost},
                dpi=150, bbox_inches='tight')


# 2020-2040, three representative households

bar_plot(724936, 'PGE', 2020, 1e-12)
bar_plot(722977, 'SCE', 2020, 1e-12)
bar_plot(722900, 'SDGE', 2020, 1e-12)

bar_plot(724936, 'PGE', 2040, 1e-12)
bar_plot(722977, 'SCE', 2040, 1e-12)
bar_plot(722900, 'SDGE', 2040, 1e-12)
