import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import seaborn as sns

results_ExportOnly = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                                   'Results/Sum_minCost_ExportOnly_2020_cc_1e-12.xlsx')
results_ImportOnly = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                                   'Results/Sum_minCost_ImportOnly_2020_cc_-1e-12.xlsx')

# to_drop = ['723925', '723840'] # two sample sites where balancing area and utility area do not align
# results_ExportOnly = results_ExportOnly[~ results_ExportOnly['tmy_code'].isin(to_drop)]
# results_ImportOnly = results_ImportOnly[~ results_ImportOnly['tmy_code'].isin(to_drop)]

clean_baseline = results_ExportOnly[['utility', 'GHG_total_noPV', 'cost_total_noPV_withCC']]
clean_SolarOnly = results_ExportOnly[['utility', 'GHG_total_PVonly', 'cost_total_PVonly_withCC']]
clean_ExportOnly = results_ExportOnly[['utility', 'GHG_total_PV+Batt', 'cost_total_PV+Batt_withCC']]
clean_ImportOnly = results_ImportOnly[['utility', 'GHG_total_PV+Batt', 'cost_total_PV+Batt_withCC']]

clean_baseline = clean_baseline.assign(mode='Baseline')
clean_SolarOnly = clean_SolarOnly.assign(mode='Solar-Only')
clean_ExportOnly = clean_ExportOnly.assign(mode='Export-Only')
clean_ImportOnly = clean_ImportOnly.assign(mode='Import-Only')

clean_baseline = clean_baseline.rename(columns={"GHG_total_noPV": "GHG_total"})
clean_baseline = clean_baseline.rename(columns={"cost_total_noPV_withCC": "cost_total"})
clean_SolarOnly = clean_SolarOnly.rename(columns={"GHG_total_PVonly": "GHG_total"})
clean_SolarOnly = clean_SolarOnly.rename(columns={"cost_total_PVonly_withCC": "cost_total"})
clean_ExportOnly = clean_ExportOnly.rename(columns={"GHG_total_PV+Batt": "GHG_total"})
clean_ExportOnly = clean_ExportOnly.rename(columns={"cost_total_PV+Batt_withCC": "cost_total"})
clean_ImportOnly = clean_ImportOnly.rename(columns={"GHG_total_PV+Batt": "GHG_total"})
clean_ImportOnly = clean_ImportOnly.rename(columns={"cost_total_PV+Batt_withCC": "cost_total"})

clean_all = pd.concat([clean_baseline, clean_ExportOnly, clean_SolarOnly, clean_ImportOnly], axis=0)
clean_all = clean_all.replace({'PGE': 'PG&E', 'SDGE': 'SDG&E'})

fig, axs = plt.subplots(1, 2, sharex=True, sharey=False, figsize=(12, 8), squeeze=False)
plt.setp(axs, ylim=(0, 4260))

# comment and uncomment to change the grouping
sns.boxplot(ax=axs[0, 0], y='GHG_total', x='mode', data=clean_all, palette="colorblind", hue='utility',
            order=['Baseline', 'Solar-Only', 'Export-Only', 'Import-Only'], hue_order=['PG&E', 'SCE', 'SDG&E'])
# sns.boxplot(ax=axs[0, 0], y='GHG_total', x='utility', data=clean_all, palette="colorblind", hue='mode',
#             hue_order=['Baseline', 'Solar-Only', 'ExportOnly', 'ImportOnly'], order=['PG&E', 'SCE', 'SDG&E'])
axs[0, 0].set_xlabel('Operation mode', fontsize=13)
axs[0, 0].set_ylabel('Annual life-cycle GHG emissions per household (kgCO$_2$)', fontsize=13)
axs[0, 0].tick_params(axis='both', which='major', labelsize=11)
axs[0, 0].legend(title=None)
for i in range(1, 4, 1):
    axs[0, 0].axvline(x=i - 0.5, color='grey', linestyle=':')

sns.boxplot(ax=axs[0, 1], y='cost_total', x='mode', data=clean_all, palette="colorblind", hue='utility',
            order=['Baseline', 'Solar-Only', 'Export-Only', 'Import-Only'], hue_order=['PG&E', 'SCE', 'SDG&E'])
# sns.boxplot(ax=axs[0, 1], y='cost_total', x='utility', data=clean_all, palette="colorblind", hue='mode',
#             hue_order=['Baseline', 'Solar-Only', 'ExportOnly', 'ImportOnly'], order=['PG&E', 'SCE', 'SDG&E'])
axs[0, 1].set_xlabel('Operation mode', fontsize=13)
axs[0, 1].set_ylabel('Annual life-cycle cost per household ($)', fontsize=13)
axs[0, 1].tick_params(axis='both', which='major', labelsize=11)
for i in range(1, 4, 1):
    axs[0, 1].axvline(x=i - 0.5, color='grey', linestyle=':')
axs[0, 1].legend(title=None)

for i in range(2):
    axs[0, i].get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

for i, label in enumerate(('a', 'b')):
    axs[0, i].text(-0.1, 1.1, label, fontsize=20, fontweight='bold', transform=axs[0, i].transAxes,
                   va='top', ha='right')

plt.rc('font', **{'sans-serif': 'Helvetica'})
fig.tight_layout()

plt.savefig('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Visualization/'
            'Fig4_box_plot_comparison_by_mode_cc0_upper_2020.jpg', dpi=300)
