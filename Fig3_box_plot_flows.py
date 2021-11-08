import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import seaborn as sns

results_ExportOnly = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                                   'Results/Optimized/Flow_minCost_ExportOnly_2020_cc_1e-12.xlsx')
results_ImportOnly = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                                   'Results/Optimized/Flow_minCost_ImportOnly_2020_cc_-1e-12.xlsx')

# to_drop = ['723925', '723840'] # two sample sites where balancing area and utility area do not align
# results_ExportOnly = results_ExportOnly[~ results_ExportOnly['tmy_code'].isin(to_drop)]
clean_SolarOnly = results_ExportOnly[['utility', 'e_PV_load_PVonly', 'e_PV_grid_PVonly',
                                      'e_grid_load_PVonly']]

empty_cols = ['e_PV_batt', 'e_batt_load', 'e_batt_grid']
df_empty = pd.DataFrame(columns=empty_cols)
clean_SolarOnly = pd.concat([clean_SolarOnly, df_empty])

clean_ExportOnly = results_ExportOnly[['utility', 'e_PV_load', 'e_PV_batt',
                                       'e_PV_grid', 'e_grid_load', 'e_batt_load', 'e_batt_grid']]

# clean_ExportOnly = clean_ExportOnly.assign(mode='ExportOnly')
# clean_SolarOnly = clean_SolarOnly.assign(mode='SolarOnly')

# results_ImportOnly = results_ImportOnly[~ results_ImportOnly['tmy_code'].isin(to_drop)]
clean_ImportOnly = results_ImportOnly[['utility', 'e_PV_load', 'e_PV_grid',
                                       'e_grid_load', 'e_PV_batt', 'p_disc', 'e_grid_batt']]
# clean_ImportOnly = clean_ImportOnly.assign(mode='ImportOnly')

clean_SolarOnly = pd.melt(clean_SolarOnly, id_vars='utility',
                          value_vars=['e_PV_load_PVonly', 'e_PV_grid_PVonly', 'e_grid_load_PVonly',
                                      'e_PV_batt', 'e_batt_load', 'e_batt_grid'])
clean_ExportOnly = pd.melt(clean_ExportOnly, id_vars='utility',
                           value_vars=['e_PV_load', 'e_PV_grid', 'e_grid_load', 'e_PV_batt',
                                       'e_batt_load', 'e_batt_grid'])
clean_ImportOnly = pd.melt(clean_ImportOnly, id_vars='utility',
                           value_vars=['e_PV_load', 'e_PV_grid', 'e_grid_load', 'e_PV_batt',
                                       'p_disc', 'e_grid_batt'])

clean_SolarOnly = clean_SolarOnly.replace({'PGE': 'PG&E', 'SDGE': 'SDG&E',
                                           'e_PV_load_PVonly': 'PV to load', 'e_PV_grid_PVonly': 'PV to grid',
                                           'e_grid_load_PVonly': 'Grid to load', 'e_PV_batt': 'PV to battery',
                                           'e_batt_load': 'Battery to load', 'e_batt_grid': 'Battery to grid'})
clean_ExportOnly = clean_ExportOnly.replace({'PGE': 'PG&E', 'SDGE': 'SDG&E',
                                             'e_PV_load': 'PV to load', 'e_PV_batt': 'PV to battery',
                                             'e_PV_grid': 'PV to grid', 'e_grid_load': 'Grid to load',
                                             'e_batt_load': 'Battery to load', 'e_batt_grid': 'Battery to grid'})
clean_ImportOnly = clean_ImportOnly.replace({'PGE': 'PG&E', 'SDGE': 'SDG&E',
                                             'e_PV_load': 'PV to load', 'e_PV_batt': 'PV to battery',
                                             'e_PV_grid': 'PV to grid', 'e_grid_load': 'Grid to load',
                                             'p_disc': 'Battery to load', 'e_grid_batt': 'Grid to battery'})

clean_SolarOnly['mode'] = 'Solar-Only'
clean_ExportOnly['mode'] = 'Export-Only'
clean_ImportOnly['mode'] = 'Import-Only'

clean_all = pd.concat([clean_SolarOnly, clean_ExportOnly, clean_ImportOnly])

fig, axs = plt.subplots(3, 1, sharex=False, sharey=False, figsize=(10, 12), squeeze=False)
plt.setp(axs, ylim=(0, 11000))

sns.boxplot(ax=axs[0, 0], y='value', x='variable', data=clean_SolarOnly, palette="colorblind",
            hue='utility', hue_order=['PG&E', 'SCE', 'SDG&E'])  # hue_order=['Solar-Only', 'Export-Only', 'Import-Only']
axs[0, 0].set_xlabel('')
axs[0, 0].set_ylabel('Annual electricity flow (kWh)', fontsize=13)
axs[0, 0].tick_params(axis='both', which='major', labelsize=11)
axs[0, 0].legend(title=None, loc='upper right')
for i in range(1, 6, 1):  # (1, 7, 1)
    axs[0, 0].axvline(x=i - 0.5, color='grey', linestyle=':')
axs[0, 0].set_title('Solar-Only')  # 'PG&E'

sns.boxplot(ax=axs[1, 0], y='value', x='variable', data=clean_ExportOnly, palette="colorblind",
            hue='utility', hue_order=['PG&E', 'SCE', 'SDG&E'])
axs[1, 0].set_xlabel('')
axs[1, 0].set_ylabel('Annual electricity flow (kWh)', fontsize=13)
axs[1, 0].tick_params(axis='both', which='major', labelsize=11)
for i in range(1, 6, 1):
    axs[1, 0].axvline(x=i - 0.5, color='grey', linestyle=':')
axs[1, 0].get_legend().remove()
axs[1, 0].set_title('Export-Only')

sns.boxplot(ax=axs[2, 0], y='value', x='variable', data=clean_ImportOnly, palette="colorblind",
            hue='utility', hue_order=['PG&E', 'SCE', 'SDG&E'])
axs[2, 0].set_xlabel('')
axs[2, 0].set_ylabel('Annual electricity flow (kWh)', fontsize=13)
axs[2, 0].tick_params(axis='both', which='major', labelsize=11)
for i in range(1, 6, 1):
    axs[2, 0].axvline(x=i - 0.5, color='grey', linestyle=':')
axs[2, 0].get_legend().remove()
axs[2, 0].set_title('Import-Only')

for i in range(3):
    axs[i, 0].get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

plt.rc('font', **{'sans-serif': 'Helvetica'})

for i, label in enumerate(('a', 'b', 'c')):
    axs[i, 0].text(-0.1, 1.1, label, fontsize=20, fontweight='bold', transform=axs[i, 0].transAxes,
                   va='top', ha='right')

plt.savefig('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Visualization/'
            'Fig3_box_plot_parameters_by_utility.jpg', dpi=300)
