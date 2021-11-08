import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory
from datetime import datetime
from scipy.optimize import *
import gurobipy

df_params = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                          'df_params_2040.xlsx')  # read the technical, cost and embodied emissions parameters

map_tmy = pd.read_excel('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                        'Annual_Load_PV_BA_by_Location.xlsx', index_col=0)  # a table listing TMY 3 location codes

# Techno-economic-emissions data
dt = df_params['value'][0]  # hour, time step
eff_round = df_params['value'][1]  # battery round-trip efficiency
p_max = df_params['value'][2]  # kW, rated peak power of the battery
e_max = df_params['value'][3]  # kWh, usable storage capacity of the battery
e_thruput = df_params['value'][4]  # kWh, lifetime aggregate discharge limit of the battery
# life_PV = int(df_params['value'][6])  # years, lifetime of a solar PV system
life_batt = int(df_params['value'][7])  # years, lifetime of a solar PV system
# deg_rate_PV = df_params['value'][8]  # reduction of solar output per year
deg_rate_batt = df_params['value'][9]  # reduction of solar output per year

eff_single = eff_round ** 0.5  # single-trip efficiency, charging or discharging
e_disc_yr_limit = e_thruput / sum(
    [(1 - deg_rate_batt) ** x for x in range(life_batt)])  # discharge limit, 1st year


def min_cost(year, c_cost):  # carbon cost - in $/tonneCO2

    for j in range(len(map_tmy)):
        tmy_code = map_tmy.index[j]
        utility = map_tmy.at[tmy_code, 'ToU Assigned']

        df = pd.read_csv('/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/'
                         'Input_Data_%(year)s_RTP/%(tmy_code)s_%(utility)s_%(year)s.csv'
                         % {'year': year, 'tmy_code': tmy_code, 'utility': utility},
                         index_col=0)  # read the df containing load, PV generation, and emission factors

        # calculate the energy flow under PV_only scenario
        df['e_PV_load_PVonly'] = df[['Load', 'PV_gen']].min(axis=1)
        df['e_grid_load_PVonly'] = df['Load'] - df['e_PV_load_PVonly']
        df['e_PV_grid_PVonly'] = df['PV_gen'] - df['e_PV_load_PVonly']

        # Build the optimization model using Pyomo
        model = ConcreteModel()

        # Sets
        model.N = Set(initialize=df.index, ordered=True)  # the set is 1-8760 hours in a year

        # Parameters
        model.dmd = Param(model.N, initialize=df['Load'].to_dict())  # kWh, electricity demand of the household
        model.PV_gen = Param(model.N, initialize=df['PV_gen'].to_dict())  # kWh, PV generation of the household
        model.tou = Param(model.N, initialize=df['ToU'].to_dict())  # $/kWh, ToU electricity retail prices
        model.mef = Param(model.N, initialize=df['MEF'].to_dict())  # gCO2/kWh, marginal emission factors of the grid
        model.aef = Param(model.N, initialize=df['AEF'].to_dict())  # gCO2/kWh, average emission factors of the grid

        # Variables
        model.p_char = Var(model.N, initialize=-1, bounds=(-p_max, 0))  # kW, power when charging, before loss
        model.p_disc = Var(model.N, initialize=1, bounds=(0, p_max))  # kW, power when discharging, after loss
        model.soc_batt = Var(model.N, initialize=0.5, bounds=(0, 1))  # state of charge of battery
        model.e_batt = Var(model.N, initialize=e_max*0.5, bounds=(0, e_max))  # kWh, energy stored in battery
        model.e_loss_char = Var(model.N, initialize=0, bounds=(0, None))  # kWh, energy loss per hour (charging)
        model.e_loss_disc = Var(model.N, initialize=0, bounds=(0, None))  # kWh, energy loss per hour (discharging)
        model.e_PV_load = Var(model.N, initialize=0, bounds=(0, None))  # kWh, energy from PV to load
        model.e_PV_batt = Var(model.N, initialize=0, bounds=(0, p_max * dt))  # kWh, energy from PV to battery
        model.e_PV_grid = Var(model.N, initialize=0, bounds=(0, None))  # kWh, excess energy exported from PV to grid
        model.e_grid_load = Var(model.N, initialize=0, bounds=(0, None))  # kWh, energy from grid to load
        model.e_batt_grid = Var(model.N, initialize=0, bounds=(0, p_max * dt))  # kWh, energy from battery to grid
        model.e_batt_load = Var(model.N, initialize=0, bounds=(0, p_max * dt))  # kWh, energy from battery to load

        # Constraints
        model.p_cons = ConstraintList()
        for i in model.N:
            model.p_cons.add(model.p_char[i] * model.p_disc[i] == 0)
            # battery cannot charge and discharge at the same time

        model.p_first_hr = Constraint(expr=model.p_char[0] + model.p_disc[0] == 0)
            # in the first hour, battery doesn't charge nor discharge

        model.soc_e_cons = ConstraintList()
        for i in model.N:
            model.soc_e_cons.add(model.e_batt[i] - model.soc_batt[i] * e_max == 0)
            # define state of charge as percentage of maximum usable capacity

        model.e_loss_char_cons = ConstraintList()
        for i in model.N:
            model.e_loss_char_cons.add(
                model.e_loss_char[i] == (- model.p_char[i]) * dt * (1 - eff_single))
            # energy loss during charging = charged energy times the single trip loss ratio, non-negative

        model.e_loss_disc_cons = ConstraintList()
        for i in model.N:
            model.e_loss_disc_cons.add(
                model.e_loss_disc[i] == (model.p_disc[i] * dt + model.e_loss_disc[i]) * (1 - eff_single))
            # energy loss during discharging = discharging energy (before loss) times single trip loss ratio, >=0

        model.char_con = ConstraintList()
        for i in model.N:
            model.char_con.add(
                model.p_char[i] * dt + model.e_PV_batt[i] == 0)
            # battery can charge only from solar PV (ExportOnly mode; different from ImportOnly mode)

        model.disc_cons = ConstraintList()
        for i in model.N:
            model.disc_cons.add(
                model.dmd[i] - (model.p_char[i] + model.e_batt_load[i]) * dt >= 0)
            # battery to load can't exceed load at any hour

        model.batt_balance = ConstraintList()
        for i in model.N:
            if i == 0:
                model.batt_balance.add(
                    model.soc_batt[i] == 0.5)  # stored energy of the battery set as half of rated capacity at 1st hour
            else:
                model.batt_balance.add(
                    model.e_batt[i] == model.e_batt[i - 1] - (model.p_char[i] + model.p_disc[i]) * dt -
                    model.e_loss_char[i] - model.e_loss_disc[i])
                # model.e_cons.add(
                #   model.e_batt[i] == model.e_batt[i-1] - (model.p_char[i] + model.p_disc[i]) * model.k[i] * dt)
                # energy balance of battery:
                # stored energy = the energy level of last hour + charged or discharged energy during dt - energy loss

        model.batt_disc_balance = ConstraintList()
        for i in model.N:
            model.batt_disc_balance.add(
                model.p_disc[i] * dt == model.e_batt_load[i] + model.e_batt_grid[i])
            # battery discharge can serve load or feed back to grid

        model.PV_cons = ConstraintList()
        for i in model.N:
            model.PV_cons.add(
                model.e_PV_grid[i] * model.e_grid_load[i] == 0)
            # the household cannot send excess PV to grid while using grid power or vice versa

        model.PV_balance = ConstraintList()
        for i in model.N:
            model.PV_balance.add(
                model.PV_gen[i] == model.e_PV_load[i] + model.e_PV_batt[i] + model.e_PV_grid[i])
            # energy balance of PV generation

        model.load_balance = ConstraintList()
        for i in model.N:
            model.load_balance.add(
                model.dmd[i] == model.e_PV_load[i] + model.e_batt_load[i] + model.e_grid_load[i])
            # energy balance of load

        def disc_limit(m):
            return sum(m.p_disc[i] for i in m.N) <= e_disc_yr_limit

        model.disc_limit = Constraint(rule=disc_limit)  # total annual discharge <= lifetime throughput/lifetime

        # Objective 1 - minimize total utility cost
        def obj_rule(m):
            return sum(
                m.tou[n] * (m.e_grid_load[n] - m.e_PV_grid[n] - m.e_batt_grid[n]) +
                c_cost * 0.001 * (m.aef[n] * m.e_grid_load[n] * 0.001)
                for n in m.N)

        model.lc_cost = Objective(rule=obj_rule, sense=1)  # Minimize total utility cost

        # solve the optimization problem and export the outputs
        opt = SolverFactory("gurobi", solver_io="python")  # opt = SolverFactory("ipopt")
        opt.options["NonConvex"] = 2  # model.setParam("NonConvex", 2) or model.params.NonConvex = 2 doesn't work

        opt.solve(model, tee=True)

        # export results and save as .csv files
        print('Exporting results:')
        # extract the values of the variables under optimal solution and add them to the data frame
        df_p_char = pd.DataFrame.from_dict(model.p_char.extract_values(), orient='index', columns=[str(model.p_char)])
        df_p_disc = pd.DataFrame.from_dict(model.p_disc.extract_values(), orient='index', columns=[str(model.p_disc)])
        df_e_loss_char = pd.DataFrame.from_dict(model.e_loss_char.extract_values(), orient='index',
                                                columns=[str(model.e_loss_char)])
        df_e_loss_disc = pd.DataFrame.from_dict(model.e_loss_disc.extract_values(), orient='index',
                                                columns=[str(model.e_loss_disc)])
        df_soc_batt = pd.DataFrame.from_dict(model.soc_batt.extract_values(), orient='index',
                                             columns=[str(model.soc_batt)])
        df_e_batt = pd.DataFrame.from_dict(model.e_batt.extract_values(), orient='index',
                                           columns=[str(model.e_batt)])
        df_e_PV_load = pd.DataFrame.from_dict(model.e_PV_load.extract_values(), orient='index',
                                              columns=[str(model.e_PV_load)])
        df_e_grid_load = pd.DataFrame.from_dict(model.e_grid_load.extract_values(), orient='index',
                                                columns=[str(model.e_grid_load)])
        df_e_PV_batt = pd.DataFrame.from_dict(model.e_PV_batt.extract_values(), orient='index',
                                              columns=[str(model.e_PV_batt)])
        df_e_batt_grid = pd.DataFrame.from_dict(model.e_batt_grid.extract_values(), orient='index',
                                                columns=[str(model.e_batt_grid)])
        df_e_batt_load = pd.DataFrame.from_dict(model.e_batt_load.extract_values(), orient='index',
                                                columns=[str(model.e_batt_load)])
        df_e_PV_grid = pd.DataFrame.from_dict(model.e_PV_grid.extract_values(), orient='index',
                                              columns=[str(model.e_PV_grid)])

        df['p_char'] = df_p_char
        df['p_disc'] = df_p_disc
        df['e_loss'] = df_e_loss_char['e_loss_char'] + df_e_loss_disc['e_loss_disc']
        df['soc_batt'] = df_soc_batt
        df['e_batt'] = df_e_batt

        df['e_PV_load'] = df_e_PV_load
        df['e_grid_load'] = df_e_grid_load
        df['e_PV_batt'] = df_e_PV_batt
        df['e_batt_grid'] = df_e_batt_grid
        df['e_batt_load'] = df_e_batt_load
        df['e_PV_grid'] = df_e_PV_grid

        # export the data frame to the Results folder
        df.round(3).to_csv(
            '/Users/jiajiazheng/Box/Suh\'s lab/GSRs/Jiajia/3-Residential Solar-plus-storage/Results/'
            'Optimized/minCost_ExportOnly_%(year)s_cc_%(c_cost)s_RTP/'
            'optimal_minCost_%(tmy_code)s_%(utility)s_%(year)s_cc_%(c_cost)s.csv'
            % {'tmy_code': tmy_code, 'utility': utility, 'year': year, 'c_cost': c_cost})


# run the concrete model and record the time it takes
model_start_time = datetime.now()
print("Optimization model started at:", model_start_time)

# min_cost(2020, -1e-12)
# min_cost(2020, 1e-12)
# min_cost(2020, 51)

min_cost(2040, 0)
# min_cost(2020, 1e-12)  # change the year to 2040 in input data frame

model_end_time = datetime.now()
model_duration = model_end_time - model_start_time
print("Results saved. Total model running time:", str(model_duration)[:-5])
