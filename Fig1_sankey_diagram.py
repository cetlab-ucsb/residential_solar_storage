import plotly.graph_objects as go
import pandas as pd


# Please uncomment some lines to switch between ExportOnly and ImportOnly modes (line #42, 51, 57)

def draw_sankey(mode, tmy_code, utility, year, c_cost):
    df = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                     'optimal/minCost_%(mode)s_%(year)s_cc_%(c_cost)s/'
                     'optimal_minCost_%(tmy_code)s_%(utility)s_%(year)s_cc_%(c_cost)s.csv'
                     % {'mode': mode, 'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost},
                     index_col=0)

    e_PV_total = sum(df['e_PV_batt']) + sum(df['e_PV_load']) + sum(df['e_PV_grid'])

    if mode == 'ImportOnly':
        values = [sum(df['e_PV_batt']), sum(df['e_PV_load']), sum(df['e_PV_grid']),
                  sum(df['e_grid_batt']), sum(df['e_grid_load']), sum(df['p_disc']), sum(df['e_loss'])]
        e_grid_total = sum(df['e_grid_batt']) + sum(df['e_grid_load'])
        e_batt_total = sum(df['e_PV_batt']) + sum(df['e_grid_batt'])
        e_load_total = sum(df['e_PV_load']) + sum(df['e_grid_load']) + sum(df['p_disc'])
    else:
        values = [sum(df['e_PV_batt']), sum(df['e_PV_load']), sum(df['e_PV_grid']),
                  sum(df['e_grid_load']), sum(df['e_batt_load']), sum(df['e_batt_grid']), sum(df['e_loss'])]
        e_grid_total = sum(df['e_grid_load'])
        e_batt_total = sum(df['e_PV_batt'])
        e_load_total = sum(df['e_PV_load']) + sum(df['e_grid_load']) + sum(df['e_batt_load'])

    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        valueformat=".0f",
        valuesuffix="kWh",
        textfont=dict(size=32),
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["PV, %(value)s" % {'value': round(e_PV_total)},
                   "Grid, %(value)s kWh" % {'value': round(e_grid_total)},
                   "Battery, %(value)s" % {'value': round(e_batt_total)},
                   "Load, %(value)s" % {'value': round(e_load_total)},
                   # "Feed-in, %(value)s" % {'value': round(sum(df['e_PV_grid']))},  # ImportOnly mode
                   "Feed-in, %(value)s" % {'value': round(sum(df['e_PV_grid']) + sum(df['e_batt_grid']))},  # ExportOnly
                   "Loss, %(value)s" % {'value': round(sum(df['e_loss']))}],
            # x=[0.1, 0.1, 0.5, 0.9, 0.9, 0.9],
            # y=[0.7, 0.2, 0.5, 0.41, 0.92, 0.84],  # customize the node positions
            color=["orange", "gray", "deepskyblue", "purple", "gray", "red"]

        ),
        link=dict(
            # source=[0, 0, 0, 1, 1, 2, 2],
            # target=[2, 3, 4, 2, 3, 3, 5],  # ImportOnly mode
            source=[0, 0, 0, 1, 2, 2, 2],
            target=[2, 3, 4, 3, 3, 4, 5],  # ExportOnly mode
            value=values,
            color=["rgba(255, 165, 0, 0.4)", "rgba(255, 165, 0, 0.4)", "rgba(255, 165, 0, 0.4)",  # PV-yellow
                   # "rgba(128, 128, 128, 0.5)", "rgba(128, 128, 128, 0.5)",  # Grid-grey  # ImportOnly mode
                   "rgba(128, 128, 128, 0.5)", "rgba(0, 191, 255, 0.4)",  # Grid-grey  # ExportOnly mode
                   "rgba(0, 191, 255, 0.4)", "rgba(0, 191, 255, 0.4)"]  # Battery-blue
        )
    )])

    fig.update_layout(title_text='Annual energy flow of the household (kWh) <br>'
                                 '%(mode)s mode, %(utility)s %(tmy_code)s in %(year)s'
                                 # '%(utility)s %(tmy_code)s in %(year)s, minGHG'
                                 % {'mode': mode, 'year': year, 'tmy_code': tmy_code, 'utility': utility,
                                    'c_cost': c_cost},
                      font_family="Helvetica",
                      font_size=12, autosize=False, width=1000, height=800)
    fig.show()
    fig.write_image('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Visualization/'
                    'Sankey_%(mode)s_%(year)s_cc%(c_cost)s_%(utility)s_%(tmy_code)s.jpg'
                    % {'mode': mode, 'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost}, scale=2)


# Run function and export energy flow diagrams

# draw_sankey('ExportOnly', 724927, 'PGE', 2020, 1e-12)
# draw_sankey('ExportOnly', 723927, 'SCE', 2020, 1e-12)
draw_sankey('ExportOnly', 722900, 'SDGE', 2020, 1e-12)


############# Solar-only mode #############

def draw_sankey_solarOnly(mode, tmy_code, utility, year, c_cost):
    df = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
                     'optimal/minCost_%(mode)s_%(year)s_cc_%(c_cost)s/'
                     'optimal_minCost_%(tmy_code)s_%(utility)s_%(year)s_cc_%(c_cost)s.csv'
                     % {'mode': mode, 'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost},
                     index_col=0)

    e_PV_total = sum(df['e_PV_load_PVonly']) + sum(df['e_PV_grid_PVonly'])

    values = [sum(df['e_PV_load_PVonly']), sum(df['e_PV_grid_PVonly']), sum(df['e_grid_load_PVonly'])]
    e_grid_total = sum(df['e_grid_load_PVonly'])
    e_load_total = sum(df['e_PV_load_PVonly']) + sum(df['e_grid_load_PVonly'])

    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        valueformat=".0f",
        valuesuffix="kWh",
        textfont=dict(size=32),
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["PV, %(value)s" % {'value': round(e_PV_total)},
                   "Grid, %(value)s kWh" % {'value': round(e_grid_total)},
                   "Load, %(value)s" % {'value': round(e_load_total)},
                   "Feed-in, %(value)s" % {'value': round(sum(df['e_PV_grid']))}],  # SolarOnly
            # x=[0.1, 0.1, 0.5, 0.9, 0.9, 0.9],
            # y=[0.7, 0.2, 0.5, 0.41, 0.92, 0.84],  # customize the node positions
            color=["orange", "gray", "purple", "gray"]

        ),
        link=dict(
            source=[0, 0, 1],
            target=[2, 3, 2],  # ExportOnly mode
            value=values,
            color=["rgba(255, 165, 0, 0.4)", "rgba(255, 165, 0, 0.4)",  # PV-yellow
                   "rgba(128, 128, 128, 0.5)"]  # Grid-grey  # ExportOnly mode
        )
    )])

    fig.update_layout(title_text='Annual energy flow of the household (kWh) <br>'
                                 'SolarOnly mode, %(utility)s %(tmy_code)s in %(year)s'
                                 # '%(utility)s %(tmy_code)s in %(year)s, minGHG'
                                 % {'mode': mode, 'year': year, 'tmy_code': tmy_code, 'utility': utility,
                                    'c_cost': c_cost},
                      font_family="Helvetica",
                      font_size=12, autosize=False, width=1000, height=800)
    fig.show()
    fig.write_image('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Visualization/'
                    'Sankey_SolarOnly_%(year)s_cc%(c_cost)s_%(utility)s_%(tmy_code)s.jpg'
                    % {'year': year, 'tmy_code': tmy_code, 'utility': utility, 'c_cost': c_cost}, scale=2)


draw_sankey_solarOnly('ExportOnly', 722900, 'SDGE', 2020, 1e-12)
