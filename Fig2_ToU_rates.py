import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

hour = list(range(0, 25, 1))
tou_PGE_weekday_winter = [0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27,
                          0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27,
                          0.27, 0.27, 0.29, 0.29, 0.29, 0.27, 0.27, 0.27, 0.27]
tou_SCE_weekday_winter = [0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27,
                          0.27, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
                          0.25, 0.36, 0.36, 0.36, 0.36, 0.36, 0.27, 0.27, 0.27]
tou_SDGE_weekday_winter = [0.2494, 0.2494, 0.2494, 0.2494, 0.2494, 0.2494, 0.2494, 0.2579,
                           0.2579, 0.2579, 0.2579, 0.2579, 0.2579, 0.2579, 0.2579, 0.2579,
                           0.2579, 0.2656, 0.2656, 0.2656, 0.2656, 0.2656, 0.2579, 0.2579, 0.2579]

tou_PGE_weekend_winter = [0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27,
                          0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27,
                          0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27]
tou_SCE_weekend_winter = [0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27,
                          0.27, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
                          0.25, 0.36, 0.36, 0.36, 0.36, 0.36, 0.27, 0.27, 0.27]
tou_SDGE_weekend_winter = [0.2494, 0.2494, 0.2494, 0.2494, 0.2494, 0.2494, 0.2494, 0.2579,
                           0.2579, 0.2579, 0.2579, 0.2579, 0.2579, 0.2579, 0.2579, 0.2579,
                           0.2579, 0.2656, 0.2656, 0.2656, 0.2656, 0.2656, 0.2579, 0.2579, 0.2579]

tou_PGE_weekday_summer = [0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27,
                          0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27,
                          0.27, 0.27, 0.37, 0.37, 0.37, 0.27, 0.27, 0.27, 0.27]
tou_SCE_weekday_summer = [0.26, 0.26, 0.26, 0.26, 0.26, 0.26, 0.26, 0.26,
                          0.26, 0.26, 0.26, 0.26, 0.26, 0.26, 0.26, 0.26,
                          0.26, 0.41, 0.41, 0.41, 0.41, 0.41, 0.26, 0.26, 0.26]
tou_SDGE_weekday_summer = [0.2487, 0.2487, 0.2487, 0.2487, 0.2487, 0.2487, 0.2487, 0.2980,
                           0.2980, 0.2980, 0.2980, 0.2980, 0.2980, 0.2980, 0.2980, 0.2980,
                           0.2980, 0.5120, 0.5120, 0.5120, 0.5120, 0.5120, 0.2980, 0.2980, 0.2980]

tou_PGE_weekend_summer = [0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27,
                          0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27,
                          0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27]
tou_SCE_weekend_summer = [0.26, 0.26, 0.26, 0.26, 0.26, 0.26, 0.26, 0.26,
                          0.26, 0.26, 0.26, 0.26, 0.26, 0.26, 0.26, 0.26,
                          0.26, 0.34, 0.34, 0.34, 0.34, 0.34, 0.26, 0.26, 0.26]
tou_SDGE_weekend_summer = [0.2487, 0.2487, 0.2487, 0.2487, 0.2487, 0.2487, 0.2487, 0.2487,
                           0.2487, 0.2487, 0.2487, 0.2487, 0.2487, 0.2487, 0.2487, 0.2980,
                           0.2980, 0.5120, 0.5120, 0.5120, 0.5120, 0.5120, 0.2980, 0.2980, 0.2980]

fig, axs = plt.subplots(2, 2, sharey=True, sharex=True, figsize=(8, 8))
plt.setp(axs, xticks=np.arange(0, 25, step=2), yticks=np.arange(0.15, 0.53, step=0.05),
         xlim=(0, 24), ylim=(0.15, 0.53))

axs[0, 0].step(hour, tou_PGE_weekday_winter, color='royalblue', label='PG&E')
axs[0, 0].step(hour, tou_SCE_weekday_winter, color='darkorange', label='SCE')
axs[0, 0].step(hour, tou_SDGE_weekday_winter, color='forestgreen', label='SDG&E')
axs[0, 0].legend(loc='upper left', frameon=False)
axs[0, 0].set_title('Winter Weekday')

axs[0, 1].step(hour, tou_PGE_weekend_winter, color='royalblue', label='PG&E')
axs[0, 1].step(hour, tou_SCE_weekend_winter, color='darkorange', label='SCE')
axs[0, 1].step(hour, tou_SDGE_weekend_winter, color='forestgreen', label='SDG&E')
axs[0, 1].set_title('Winter Weekend')

axs[1, 0].step(hour, tou_PGE_weekday_summer, color='royalblue', label='PG&E')
axs[1, 0].step(hour, tou_SCE_weekday_summer, color='darkorange', label='SCE')
axs[1, 0].step(hour, tou_SDGE_weekday_summer, color='forestgreen', label='SDG&E')
axs[1, 0].set_title('Summer Weekday')

axs[1, 1].step(hour, tou_PGE_weekend_summer, color='royalblue', label='PG&E')
axs[1, 1].step(hour, tou_SCE_weekend_summer, color='darkorange', label='SCE')
axs[1, 1].step(hour, tou_SDGE_weekend_summer, color='forestgreen', label='SDG&E')
axs[1, 1].set_title('Summer Weekend')

for ax in axs.flat:
    ax.set(xlabel='Hour', ylabel='$/kWh')

for ax in axs.flat:
    ax.label_outer()

for ax in axs.flatten():
    ax.xaxis.set_tick_params(labelbottom=True)
    ax.yaxis.set_tick_params(labelleft=True)

plt.rc('font', **{'sans-serif': 'Helvetica'})

fig.suptitle('Time-of-Use Rates in California')
plt.savefig('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Visualization/'
            'Fig2_ToU_rates_CA.jpg', dpi=300, bbox_inches='tight')
