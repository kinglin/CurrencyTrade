import pandas as pd
from crcytrade import arbitrator
from pyeasyga import pyeasyga
import numpy as np
import random
from tqdm import tqdm

BASE_ACCOUNT_VALUE = 10000  # each account use its own currency
DEBUGLEVEL = 0
ALL_HOLD = 0
TEST = 0
trade_plan_result_df = pd.DataFrame(columns=(
    'week_num', 'is_trade', 'a_start', 'a_end', 'profit', 'hold_profit', 'trade_profit', 'as_start', 'as_end',
    'ad_start', 'ad_end', 'ap_start',
    'ap_end', 'trade_s_d', 'trade_s_p', 'trade_d_s', 'trade_d_p', 'trade_p_s', 'trade_p_d'))

delta_df = pd.read_csv("result_df_0927.csv")
forecast_df = pd.read_csv("forecast_df.csv")
delta_train_df = delta_df[6:501]
forecast_train_df = forecast_df[6:501]
delta_test_df = delta_df[502:606]
forecast_test_df = forecast_df[502:606]


def main():
    if TEST == 1:
        tmmf_params_df, tmmf_range_params_df = init_tmmf_dfs()
        arbi = arbitrator.arbitrator(tmmf_params_df, tmmf_range_params_df)
        trade_final_result_df = pd.DataFrame(columns=(
            'week_num', 'is_trade', 'a_start', 'a_end', 'profit', 'hold_profit', 'trade_profit', 'as_start', 'as_end',
            'ad_start', 'ad_end', 'ap_start',
            'ap_end', 'trade_s_d', 'trade_s_p', 'trade_d_s', 'trade_d_p', 'trade_p_s', 'trade_p_d'))
        for t, _ in zip(range(len(delta_test_df)), delta_test_df.iterrows()):
            if t < len(delta_test_df) - 1:
                trade_final_result_df.loc[t] = arbi.arbitrate(delta_test_df, forecast_test_df, t,
                                                              trade_final_result_df.iloc[t - 1] if t > 0 else None,
                                                              ALL_HOLD)

        trade_final_result_df.to_csv("trade_final_result.csv", index=False, sep=',')
    else:
        tmmf_params_df, tmmf_range_params_df = init_tmmf_dfs()
        data = np.append(tmmf_params_df.T.values.flatten(), tmmf_range_params_df.T.values.flatten()).tolist()
        ga = pyeasyga.GeneticAlgorithm(data,
                                       population_size=50,
                                       generations=50,
                                       crossover_probability=0.1,
                                       mutation_probability=0.9,
                                       elitism=True,
                                       maximise_fitness=True)
        ga.fitness_function = fitness
        ga.create_individual = create_individual
        ga.run()
        print(ga.best_individual())

        # ===get the best individual and fit in test
        individual_chrom = ga.best_individual()
        idmf_params_df, idmf_range_df = get_mfdf_from_data(individual_chrom[1])

        arbi = arbitrator.arbitrator(conv_paramdf_key(idmf_params_df), conv_rangedf_key(idmf_range_df))
        trade_final_result_df = pd.DataFrame(columns=(
            'week_num', 'is_trade', 'a_start', 'a_end', 'profit', 'hold_profit', 'trade_profit', 'as_start', 'as_end',
            'ad_start', 'ad_end', 'ap_start',
            'ap_end', 'trade_s_d', 'trade_s_p', 'trade_d_s', 'trade_d_p', 'trade_p_s', 'trade_p_d'))
        for t, _ in tqdm(zip(range(len(delta_test_df)), delta_test_df.iterrows())):
            if t < len(delta_test_df) - 1:
                trade_final_result_df.loc[t] = arbi.arbitrate(delta_test_df, forecast_test_df, t,
                                                              trade_final_result_df.iloc[t - 1] if t > 0 else None,
                                                              ALL_HOLD)

        trade_final_result_df.to_csv("trade_ga_result.csv", index=False, sep=',')

    return


def create_individual(data):
    result = []

    mf_range = [random.uniform(3, 40) for _ in range(6)]
    mf_params = []
    for i in range(6):
        base5 = [random.uniform(0, mf_range[i]) for _ in range(5)]
        base5.sort()
        base5[0] = 0
        low2 = [random.uniform(base5[0], base5[2]) for _ in range(2)]
        low2.sort()
        med2 = [random.uniform(base5[1], base5[4]) for _ in range(2)]
        med2.sort()
        hi1 = random.uniform(base5[3], mf_range[i])
        hi2 = mf_range[i]
        hi3 = random.uniform(mf_range[i], 60)
        mf_params.append(base5[0])
        mf_params.extend(low2)
        mf_params.append(base5[2])
        mf_params.append(base5[1])
        mf_params.extend(med2)
        mf_params.append(base5[4])
        mf_params.append(base5[3])
        mf_params.append(hi1)
        mf_params.append(hi2)
        mf_params.append(hi3)

    result.extend(mf_params)
    result.extend(mf_range)

    return result


def fitness(individual, data):
    fitness_value = 0
    idmf_params_df, idmf_range_df = get_mfdf_from_data(individual)

    if is_meet_constraints(idmf_params_df, idmf_range_df):
        arbi = arbitrator.arbitrator(conv_paramdf_key(idmf_params_df), conv_rangedf_key(idmf_range_df))
        trade_plan_result_df = pd.DataFrame(columns=(
            'week_num', 'is_trade', 'a_start', 'a_end', 'profit', 'hold_profit', 'trade_profit', 'as_start', 'as_end',
            'ad_start', 'ad_end', 'ap_start',
            'ap_end', 'trade_s_d', 'trade_s_p', 'trade_d_s', 'trade_d_p', 'trade_p_s', 'trade_p_d'))
        for t, _ in tqdm(zip(range(len(delta_train_df)), delta_train_df.iterrows())):
            if t < len(delta_train_df) - 1:
                trade_plan_result_df.loc[t] = arbi.arbitrate(delta_train_df, forecast_train_df, t,
                                                             trade_plan_result_df.iloc[t - 1] if t > 0 else None,
                                                             ALL_HOLD)
        fitness_value = trade_plan_result_df['a_start'][len(trade_plan_result_df['a_start']) - 1] - \
                        trade_plan_result_df['a_start'][0]
        print(fitness_value)
    return fitness_value


def get_mfdf_from_data(data):
    idmf_params_df = pd.DataFrame()
    idmf_range_df = pd.DataFrame()
    for i in range(18):
        idmf_params_df[i] = data[i * 4:(i + 1) * 4]
    for i in range(len(data) - 4 * 3 * 6):
        idmf_range_df[i] = [data[4 * 3 * 6 + i]]
    return idmf_params_df, idmf_range_df


def init_tmmf_dfs():
    tmmf_params_df = pd.DataFrame()
    tmmf_params_df['tm_sd_low'] = [0, 0, 0.25, 1.5]
    tmmf_params_df['tm_sd_medium'] = [0.5, 2, 2, 3.5]
    tmmf_params_df['tm_sd_high'] = [2.5, 4, 100, 100]
    tmmf_params_df['tm_ds_low'] = [0, 0, 0.25, 1.5]
    tmmf_params_df['tm_ds_medium'] = [0.5, 2, 2, 3.5]
    tmmf_params_df['tm_ds_high'] = [2.5, 4, 100, 100]
    tmmf_params_df['tm_dp_low'] = [0, 0, 0.25, 1.5]
    tmmf_params_df['tm_dp_medium'] = [0.5, 2, 2, 3.5]
    tmmf_params_df['tm_dp_high'] = [2.5, 4, 100, 100]
    tmmf_params_df['tm_pd_low'] = [0, 0, 0.25, 1.5]
    tmmf_params_df['tm_pd_medium'] = [0.5, 2, 2, 3.5]
    tmmf_params_df['tm_pd_high'] = [2.5, 4, 100, 100]
    tmmf_params_df['tm_sp_low'] = [0, 0, 0.25, 1.5]
    tmmf_params_df['tm_sp_medium'] = [0.5, 2, 2, 3.5]
    tmmf_params_df['tm_sp_high'] = [2.5, 4, 100, 100]
    tmmf_params_df['tm_ps_low'] = [0, 0, 0.25, 1.5]
    tmmf_params_df['tm_ps_medium'] = [0.5, 2, 2, 3.5]
    tmmf_params_df['tm_ps_high'] = [2.5, 4, 100, 100]
    tmmf_range_params_df = pd.DataFrame()
    tmmf_range_params_df['tm_sd'] = [6.01]
    tmmf_range_params_df['tm_ds'] = [6.01]
    tmmf_range_params_df['tm_dp'] = [6.01]
    tmmf_range_params_df['tm_pd'] = [6.01]
    tmmf_range_params_df['tm_sp'] = [6.01]
    tmmf_range_params_df['tm_ps'] = [6.01]
    return tmmf_params_df, tmmf_range_params_df


def init_test_tmmf_dfs():
    tmmf_params_df = pd.DataFrame()
    tmmf_params_df['tm_sd_low'] = [0.261242, 1.381069, 1.862636, 1.88244]
    tmmf_params_df['tm_sd_medium'] = [1.810455, 2.889105, 3.272381, 4.653242]
    tmmf_params_df['tm_sd_high'] = [3.195062, 6.922101, 7.63856, 30.047753]
    tmmf_params_df['tm_ds_low'] = [8.86079, 11.331855, 11.523117, 15.047379]
    tmmf_params_df['tm_ds_medium'] = [11.726143, 14.114206, 14.862071, 18.091705]
    tmmf_params_df['tm_ds_high'] = [16.236941, 16.972135, 31.359355, 59.173443]
    tmmf_params_df['tm_dp_low'] = [4.526909, 4.623369, 5.709045, 6.476277]
    tmmf_params_df['tm_dp_medium'] = [5.320263, 5.439658, 6.118445, 8.721897]
    tmmf_params_df['tm_dp_high'] = [7.202551, 8.996399, 10.955782, 37.776516]
    tmmf_params_df['tm_pd_low'] = [3.376361, 3.869348, 5.160224, 6.337651]
    tmmf_params_df['tm_pd_medium'] = [4.736352, 12.712693, 13.824749, 23.542887]
    tmmf_params_df['tm_pd_high'] = [12.960441, 24.714076, 37.416962, 52.424049]
    tmmf_params_df['tm_sp_low'] = [0.512873, 1.018532, 6.37799, 6.421009]
    tmmf_params_df['tm_sp_medium'] = [1.046854, 2.870308, 9.469998, 9.633121]
    tmmf_params_df['tm_sp_high'] = [8.617949, 9.436742, 12.335769, 55.607369]
    tmmf_params_df['tm_ps_low'] = [4.191831, 6.103279, 8.097556, 8.770849]
    tmmf_params_df['tm_ps_medium'] = [6.682647, 6.914652, 18.262102, 18.451308]
    tmmf_params_df['tm_ps_high'] = [15.342418, 19.319586, 19.97686, 32.781648]

    tmmf_range_params_df = pd.DataFrame()
    tmmf_range_params_df['tm_sd'] = [7.63856]
    tmmf_range_params_df['tm_ds'] = [31.359355]
    tmmf_range_params_df['tm_dp'] = [10.955782]
    tmmf_range_params_df['tm_pd'] = [37.416962]
    tmmf_range_params_df['tm_sp'] = [12.335769]
    tmmf_range_params_df['tm_ps'] = [19.97686]
    return tmmf_params_df, tmmf_range_params_df


def conv_paramdf_key(idmf_params_df):
    df = pd.DataFrame()
    df['tm_sd_low'] = idmf_params_df[0]
    df['tm_sd_medium'] = idmf_params_df[1]
    df['tm_sd_high'] = idmf_params_df[2]
    df['tm_ds_low'] = idmf_params_df[3]
    df['tm_ds_medium'] = idmf_params_df[4]
    df['tm_ds_high'] = idmf_params_df[5]
    df['tm_dp_low'] = idmf_params_df[6]
    df['tm_dp_medium'] = idmf_params_df[7]
    df['tm_dp_high'] = idmf_params_df[8]
    df['tm_pd_low'] = idmf_params_df[9]
    df['tm_pd_medium'] = idmf_params_df[10]
    df['tm_pd_high'] = idmf_params_df[11]
    df['tm_sp_low'] = idmf_params_df[12]
    df['tm_sp_medium'] = idmf_params_df[13]
    df['tm_sp_high'] = idmf_params_df[14]
    df['tm_ps_low'] = idmf_params_df[15]
    df['tm_ps_medium'] = idmf_params_df[16]
    df['tm_ps_high'] = idmf_params_df[17]
    return df


def conv_rangedf_key(idmf_range_df):
    df = pd.DataFrame()
    df['tm_sd'] = idmf_range_df[0]
    df['tm_ds'] = idmf_range_df[1]
    df['tm_dp'] = idmf_range_df[2]
    df['tm_pd'] = idmf_range_df[3]
    df['tm_sp'] = idmf_range_df[4]
    df['tm_ps'] = idmf_range_df[5]
    return df


def is_meet_constraints(idmf_params_df, idmf_range_df):
    for i in range(len(idmf_params_df.columns)):
        if idmf_params_df[i][0] > idmf_params_df[i][1] or \
                idmf_params_df[i][1] > idmf_params_df[i][2] or \
                idmf_params_df[i][2] > idmf_params_df[i][3]:
            print("====do not meet constraints 1===")
            print(idmf_params_df)
            return False
    for i in range(6):
        if idmf_range_df[i][0] < 3:
            print("====do not meet constraints 4===")
            print(idmf_params_df)
            return False
        if idmf_params_df[i * 3][0] != 0:
            print("====do not meet constraints 5===")
            print(idmf_params_df)
            return False
        if not idmf_params_df[i * 3][0] < idmf_params_df[i * 3 + 1][0] < idmf_params_df[i * 3][3] < \
               idmf_params_df[i * 3 + 2][0] < idmf_params_df[i * 3 + 1][3]:
            print("====do not meet constraints 2===")
            print(idmf_params_df)
            return False
        if idmf_params_df[i * 3 + 2][3] < idmf_range_df[i][0]:
            print("====do not meet constraints 3===")
            print(idmf_params_df)
            return False
    return True


if __name__ == "__main__":
    main()
