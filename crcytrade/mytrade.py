import pandas as pd
from crcytrade import arbitrator

BASE_ACCOUNT_VALUE = 10000  # each account use its own currency
DEBUGLEVEL = 0
ALL_HOLD = 0
trade_plan_result_df = pd.DataFrame(columns=(
    'week_num', 'is_trade', 'a_start', 'a_end', 'profit', 'as_start', 'as_end', 'ad_start', 'ad_end', 'ap_start',
    'ap_end', 'trade_s_d', 'trade_s_p', 'trade_d_s', 'trade_d_p', 'trade_p_s', 'trade_p_d'))


def main():
    delta_df = pd.read_csv("result_df_0927.csv")
    forecast_df = pd.read_csv("forecast_df.csv")
    start, end = 502, 606
    delta_test_df = delta_df[start:end]  # just use num 503 to 605, due to forecast number
    forecast_test_df = forecast_df[start:end]

    arbi = arbitrator.arbitrator()

    for t, data in zip(range(len(delta_test_df)), delta_test_df.iterrows()):
        if t < end - start - 1:
            trade_plan_result_df.loc[t] = arbi.arbitrate(delta_test_df, forecast_test_df, data[1], t,
                                                         trade_plan_result_df.iloc[t - 1] if t > 0 else None, ALL_HOLD)

    trade_plan_result_df.to_csv("trade_plan_result.csv", index=False, sep=',')

    return


if __name__ == "__main__":
    main()
