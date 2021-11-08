import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.io as pio
import json
import urllib.request

with urllib.request.urlopen('https://services3.arcgis.com/bWPjFyq029ChCGur/arcgis/rest/services/'
                            'California_Electric_Utility_Service_Areas/FeatureServer/0/'
                            'query?where=OBJECTID%20%3E%3D%2056%20AND%20OBJECTID%20%3C%3D%2058&out'
                            'Fields=Acronym&outSR=4326&f=json') as url:
    utilities = json.loads(url.read().decode())

# Read TMY 3 location data with geo-information
map_tmy = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                        'Annual_Load_PV_BA_by_Location.xlsx', index_col=0)  # a table listing TMY 3 location codes

map_loc = map_tmy.loc[:, 'ToU Assigned': 'Longitude']
map_loc = map_loc.rename(columns={"ToU Assigned": "Utility"})


# Define function to draw bubble map 

def draw_bubble_map(obj, mode, year, c_cost):
    """ 
    Draw bubble map showing the cost and emissions differences

    """

    # Draw utility borders
    fig = go.Figure()

    for i in range(39):
        df_SCE = pd.json_normalize(utilities['features'][0])['geometry.rings'].apply(
            lambda r: [(j[0], j[1]) for j in r[i]])
        fig.add_trace(go.Scattergeo(
            showlegend=False,
            lat=np.array(df_SCE[0])[:, 1],
            lon=np.array(df_SCE[0])[:, 0],
            mode="lines",
            line=dict(width=0.5, color="darkgrey")
        )
        )

    for i in range(99):
        df_PGE = pd.json_normalize(utilities['features'][1])['geometry.rings'].apply(
            lambda r: [(j[0], j[1]) for j in r[i]])
        fig.add_trace(go.Scattergeo(
            showlegend=False,
            lat=np.array(df_PGE[0])[:, 1],
            lon=np.array(df_PGE[0])[:, 0],
            mode="lines",
            line=dict(width=0.5, color="darkgrey")
        )
        )

    for i in range(6):
        df_SDGE = pd.json_normalize(utilities['features'][2])['geometry.rings'].apply(
            lambda r: [(j[0], j[1]) for j in r[i]])
        fig.add_trace(go.Scattergeo(
            showlegend=False,
            lat=np.array(df_SDGE[0])[:, 1],
            lon=np.array(df_SDGE[0])[:, 0],
            mode="lines",
            line=dict(width=0.5, color="darkgrey")
        )
        )

    # import results from csv files and sum up the GHG emissions and costs
    df = pd.DataFrame()
    for i in range(len(map_tmy)):
        tmy_i = map_tmy.index[i]
        utility = map_tmy.loc[tmy_i, 'ToU Assigned']

        if obj == 'minCost':
            df_results = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                                     'Results/results_%(obj)s_%(mode)s_%(year)s_cc_%(c_cost)s_RTP/'
                                     'results_%(obj)s_%(tmy_code)s_%(utility)s_%(year)s_cc_%(c_cost)s.csv'
                                     % {'obj': obj, 'mode': mode, 'year': year, 'tmy_code': tmy_i,
                                        'utility': utility, 'c_cost': c_cost}, index_col=0)

        else:
            df_results = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                                     'Results/results_%(obj)s_%(mode)s_%(year)s/'
                                     'results_%(obj)s_%(tmy_code)s_%(utility)s_%(year)s.csv'
                                     % {'obj': obj, 'mode': mode, 'year': year, 'tmy_code': tmy_i,
                                        'utility': utility}, index_col=0)

        sum_i = pd.DataFrame(pd.to_numeric(df_results.sum()[-8:])).T
        sum_i.insert(0, 'Location', tmy_i)  # insert the file name to the far left of the df
        df = df.append(sum_i)  # calculate the sums of each column and keep the totals

    df = df.merge(map_loc, how='left', on='Location')

    df['GHG_diff'] = pd.to_numeric((df['GHG_total_PV+Batt'] - df['GHG_total_PVonly']) / df['GHG_total_PVonly'])
    df['cost_diff'] = pd.to_numeric((df['cost_total_PV+Batt_withCC'] -
                                     df['cost_total_PVonly_withCC']) / df['cost_total_PVonly_withCC'])
    df['GHG_diff_pos'] = np.where(df['GHG_diff'] > 0, df['GHG_diff'], 0)
    df['GHG_diff_neg'] = np.where(df['GHG_diff'] < 0, df['GHG_diff'], 0)
    df['cost_diff_pos'] = np.where(df['cost_diff'] > 0, df['cost_diff'], 0)
    df['cost_diff_neg'] = np.where(df['cost_diff'] < 0, df['cost_diff'], 0)

    df.drop(df.columns[1:9], inplace=True, axis=1)

    GHG_diff_mean = '{:.1%}'.format(df['GHG_diff'].mean())
    cost_diff_mean = '{:.1%}'.format(df['cost_diff'].mean())

    GHG_diff_mean_PGE = '{:.0%}'.format(df[df['Utility'] == "PGE"]['GHG_diff'].mean())
    cost_diff_mean_PGE = '{:.0%}'.format(df[df['Utility'] == "PGE"]['cost_diff'].mean())
    GHG_diff_mean_SCE = '{:.0%}'.format(df[df['Utility'] == "SCE"]['GHG_diff'].mean())
    cost_diff_mean_SCE = '{:.0%}'.format(df[df['Utility'] == "SCE"]['cost_diff'].mean())
    GHG_diff_mean_SDGE = '{:.0%}'.format(df[df['Utility'] == "SDGE"]['GHG_diff'].mean())
    cost_diff_mean_SDGE = '{:.0%}'.format(df[df['Utility'] == "SDGE"]['cost_diff'].mean())

    # add a dummy row for negative legend to show
    df.loc[len(df.index)] = ['700000', "Dummy", 40, -120, 0, 0, 0.0000001, -0.0000001, 0.0000001, -0.0000001]

    # create a list of parameters for four traces
    trace_list = [[df['GHG_diff_pos'], 'GHG - higher', 'rgba(219, 67, 37, 0.8)', 'rgba(219, 67, 37, 0)'],  # (236,91,18)
                  [df['GHG_diff_neg'], 'GHG - lower', 'rgba(70, 180, 155, 0.8)', 'rgba(70, 180, 155, 0)'],
                  [df['cost_diff_pos'], 'Cost - higher', 'rgba(0,0,0,0)', 'rgba(219, 67, 37, 1)'],
                  [df['cost_diff_neg'], 'Cost - lower', 'rgba(0,0,0,0)', 'rgba(57, 166, 143, 1)']]

    # iterate and create each trace
    for index in range(len(trace_list)):
        fig.add_trace(go.Scattergeo(
            locationmode='USA-states',
            lon=df['Longitude'],
            lat=df['Latitude'],
            hoverinfo='text',
            text=trace_list[index][0] * 100,
            mode='markers',
            name=trace_list[index][1],
            # opacity=0.6,
            marker=dict(
                size=trace_list[index][0] * (-1) ** index,  # use -1 to show bubbles of negative values
                sizemode='area',  # 'area' or 'diameter'
                sizeref=2. * 0.5 / (40. ** 2),
                symbol='circle',
                color=trace_list[index][2],  # circle fill color
                line=dict(
                    width=1,
                    color=trace_list[index][3]  # circle border color
                )
            )))

    bb_lon = -118.2  # bubble legend location - longitude
    bb_lat = 39.32

    bb_size_data = [['5%', 0.05, bb_lon, bb_lat],
                    ['15%', 0.15, bb_lon + 0.122, bb_lat - 0.36],
                    ['25%', 0.25, bb_lon + 0.271, bb_lat - 0.79]]
    bb_size = pd.DataFrame(bb_size_data, columns=['percentage', 'size', 'longitude', 'latitude'])

    # add bubble size legend
    fig.add_trace(go.Scattergeo(
        showlegend=False,
        locationmode='USA-states',
        lon=bb_size['longitude'],
        lat=bb_size['latitude'],
        hoverinfo='text',
        # text=round(bb_size['size'] * 100, 1),
        mode='markers',
        marker=dict(
            size=bb_size['size'].tolist(),
            sizemode='area',
            sizeref=2. * 0.5 / (40. ** 2),
            symbol='circle',
            color='rgba(0, 0, 0, 0)',
            line=dict(
                width=1,
                color='black'
            )
        )))

    bb_x_txt = 0.699  # bubble legend text position - x
    bb_y_txt = 0.648

    # legend - bubble sizes
    fig.add_annotation(x=bb_x_txt, y=bb_y_txt + 0.002, text="5%", showarrow=False,
                       font=dict(family="Helvetica", size=20))
    fig.add_annotation(x=bb_x_txt, y=bb_y_txt - 0.032, text="15%", showarrow=False,
                       font=dict(family="Helvetica", size=20))
    fig.add_annotation(x=bb_x_txt, y=bb_y_txt - 0.068, text="25%", showarrow=False,
                       font=dict(family="Helvetica", size=20))

    # mark of utility territory
    fig.add_annotation(x=0.38, y=0.75, text='PG&E', showarrow=False, font=dict(family="Helvetica", size=20))
    fig.add_annotation(x=0.66, y=0.31, text='SCE', showarrow=False, font=dict(family="Helvetica", size=20))
    fig.add_annotation(x=0.61, y=0.074, text='SDG&E', showarrow=False, font=dict(family="Helvetica", size=20))

    # legend - mean values of all samples
    # fig.add_annotation(x=bb_x_txt + 0.1, y=bb_y_txt - 0.15,
    #                    text=f"Mean value <br> GHG difference: {GHG_diff_mean} <br> Cost difference: {cost_diff_mean}",
    #                    showarrow=False, font=dict(family="Helvetica", size=14))

    # summary table of mean values by utility
    sum_x_txt = 0.24
    sum_y_txt = 0.02
    fig.add_annotation(x=sum_x_txt, y=sum_y_txt + 0.066, text='PG&E', showarrow=False,
                       font=dict(family="Helvetica", size=20))
    fig.add_annotation(x=sum_x_txt, y=sum_y_txt + 0.033, text='SCE', showarrow=False,
                       font=dict(family="Helvetica", size=20))
    fig.add_annotation(x=sum_x_txt, y=sum_y_txt, text='SDG&E', showarrow=False,
                       font=dict(family="Helvetica", size=20))
    fig.add_annotation(x=sum_x_txt + 0.16, y=sum_y_txt + 0.099, text='GHG diff  Cost diff',
                       showarrow=False, font=dict(family="Helvetica", size=20))

    fig.add_annotation(x=sum_x_txt + 0.16, y=sum_y_txt + 0.066, text=f"{GHG_diff_mean_PGE}    {cost_diff_mean_PGE}",
                       showarrow=False, font=dict(family="Helvetica", size=20))
    fig.add_annotation(x=sum_x_txt + 0.16, y=sum_y_txt + 0.033, text=f"{GHG_diff_mean_SCE}    {cost_diff_mean_SCE}",
                       showarrow=False, font=dict(family="Helvetica", size=20))
    fig.add_annotation(x=sum_x_txt + 0.16, y=sum_y_txt, text=f"{GHG_diff_mean_SDGE}    {cost_diff_mean_SDGE}",
                       showarrow=False, font=dict(family="Helvetica", size=20))

    fig.update_annotations(align="left")

    fig.update_layout(
        # title=go.layout.Title(
        #     text=f'{mode} {year}, carbon cost = $0/tonneCO2, upper',
        #     # text=f'{mode}, {year}, minGHG',
        #     x=0.5, y=0.95,
        #     font=dict(family='Helvetica', size=18)),

        geo=go.layout.Geo(
            resolution=50,
            scope='usa',
            showframe=False,
            showland=True,
            showsubunits=True,
            showcoastlines=True,
            coastlinecolor="grey",
            landcolor="rgb(235, 235, 235)",
            subunitcolor="grey",
            countrycolor="grey",
            countrywidth=0.5,
            subunitwidth=0.5,
            center=dict(lon=-119.5, lat=37.3),
            projection=dict(scale=0.4),
            lonaxis=dict(range=[-127.0, -124.9]),
            lataxis=dict(range=[35.2, 39.5]),
        ),
        # showlegend=True,
        # legend_traceorder='reversed',
        legend=dict(
            itemsizing='constant', x=0.6, y=0.83,
            title='',
            title_font_family='Helvetica',
            title_font_size=18,
            font=dict(family='Helvetica', size=20), bgcolor='rgba(0,0,0,0)')
    )

    # fig.show()

    pio.write_image(fig,
                    '/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Visualization/'
                    'Bubble_map_%(obj)s_%(mode)s_%(year)s_cc_%(c_cost)s_RTP.jpg'
                    % {'obj': obj, 'mode': mode, 'year': year, 'c_cost': c_cost},
                    format='jpg', scale=3, width=1000, height=1000, validate=True, engine='auto')


draw_bubble_map('minCost', 'ExportOnly', 2040, 0)
draw_bubble_map('minCost', 'ImportOnly', 2040, 0)
draw_bubble_map('minCost', 'Unconstrained', 2040, 0)


