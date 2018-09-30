from crcytrade.tradeplanner import tradeplanner
from crcytrade.sfsupport import sfsupport
from crcytrade import mytrade


class arbitrator:

    def __init__(self, tmmf_params_df, tmmf_range_params_df):

        self.planner = tradeplanner(tmmf_params_df, tmmf_range_params_df)
        self.sfspt = sfsupport()
        self.blank_trade = {'trade_s_d':0, 'trade_s_p' : 0, 'trade_d_s' : 0, 'trade_d_p' : 0,'trade_p_s' : 0,'trade_p_d' : 0}
        pass

    def arbitrate(self, delta_test_df, forecast_test_df, t, last_trade, ALL_HOLD):

        a_origin = self.get_a(last_trade)
        if ALL_HOLD == 1:
            a_hold_next, hold_profit = self.get_all_hold_profit(a_origin, forecast_test_df, delta_test_df, t)
            return self.get_trade_plan_df_row(t, 0, a_hold_next, self.blank_trade, hold_profit, hold_profit, 0)

        trade_plan = self.planner.defuzzify(delta_test_df.iloc[t+1])
        trade_plan = self.eliminate_useless_trade(trade_plan)
        trade_plan = self.sf_mape(trade_plan, self.sfspt.defuzzify(delta_test_df.iloc[t]))
        a_hold_next, hold_profit = self.get_all_hold_profit(a_origin, forecast_test_df, delta_test_df, t)
        a_trade_next, trade_plan, trade_profit = self.get_trade_profit(a_origin, forecast_test_df, delta_test_df, trade_plan, t)

        if trade_profit > hold_profit:
            return self.get_trade_plan_df_row(t, 1, a_trade_next, trade_plan, trade_profit, hold_profit, trade_profit)
        else:
            return self.get_trade_plan_df_row(t, 0, a_hold_next, self.blank_trade, hold_profit, hold_profit, trade_profit)

    def eliminate_useless_trade(self, trade_dict):

        trade_result = trade_dict.copy()

        trade_result = self.sub_elim_rule_2(trade_result)

        return trade_result

    def sub_elim_rule_1(self, trade_result):

        if trade_result['trade_s_d'] > 0 and trade_result['trade_s_p'] > 0 and trade_result['trade_d_p'] > 0:
            trade_result['trade_s_d'] = 0
        elif trade_result['trade_s_d'] > 0 and trade_result['trade_s_p'] > 0 and trade_result['trade_p_d'] > 0:
            trade_result['trade_s_p'] = 0
        elif trade_result['trade_p_s'] > 0 and trade_result['trade_p_d'] > 0 and trade_result['trade_s_d'] > 0:
            trade_result['trade_p_s'] = 0
        elif trade_result['trade_p_s'] > 0 and trade_result['trade_p_d'] > 0 and trade_result['trade_d_s'] > 0:
            trade_result['trade_p_d'] = 0
        elif trade_result['trade_d_s'] > 0 and trade_result['trade_d_p'] > 0 and trade_result['trade_s_p'] > 0:
            trade_result['trade_d_s'] = 0
        elif trade_result['trade_d_s'] > 0 and trade_result['trade_d_p'] > 0 and trade_result['trade_p_s'] > 0:
            trade_result['trade_d_p'] = 0

        return trade_result

    def sub_elim_rule_2(self, trade_result):

        if trade_result['trade_s_d'] > 0 and trade_result['trade_s_p'] > 0 and trade_result['trade_d_p'] > 0:
            trade_result['trade_s_p'] += trade_result['trade_s_d']
            trade_result['trade_s_d'] = 0
        elif trade_result['trade_s_d'] > 0 and trade_result['trade_s_p'] > 0 and trade_result['trade_p_d'] > 0:
            trade_result['trade_s_d'] += trade_result['trade_s_p']
            trade_result['trade_s_p'] = 0
        elif trade_result['trade_p_s'] > 0 and trade_result['trade_p_d'] > 0 and trade_result['trade_s_d'] > 0:
            trade_result['trade_p_d'] += trade_result['trade_p_s']
            trade_result['trade_p_s'] = 0
        elif trade_result['trade_p_s'] > 0 and trade_result['trade_p_d'] > 0 and trade_result['trade_d_s'] > 0:
            trade_result['trade_p_s'] += trade_result['trade_p_d']
            trade_result['trade_p_d'] = 0
        elif trade_result['trade_d_s'] > 0 and trade_result['trade_d_p'] > 0 and trade_result['trade_s_p'] > 0:
            trade_result['trade_d_p'] += trade_result['trade_d_s']
            trade_result['trade_d_s'] = 0
        elif trade_result['trade_d_s'] > 0 and trade_result['trade_d_p'] > 0 and trade_result['trade_p_s'] > 0:
            trade_result['trade_d_s'] += trade_result['trade_d_p']
            trade_result['trade_d_p'] = 0

        return trade_result

    def sf_mape(self, trade_dict, sf_dict):

        trade_result = trade_dict.copy()
        trade_result['trade_s_d'] *= sf_dict['sf_sd']
        trade_result['trade_d_s'] *= sf_dict['sf_sd']
        trade_result['trade_p_s'] *= sf_dict['sf_ps']
        trade_result['trade_s_p'] *= sf_dict['sf_ps']
        trade_result['trade_p_d'] *= sf_dict['sf_pd']
        trade_result['trade_d_p'] *= sf_dict['sf_pd']

        return trade_result

    def get_a(self, last_trade):
        a_origin = dict()
        a_as, a_ad, a_ap = mytrade.BASE_ACCOUNT_VALUE, mytrade.BASE_ACCOUNT_VALUE, mytrade.BASE_ACCOUNT_VALUE
        if last_trade is not None:
            a_as = last_trade["as_end"]
            a_ad = last_trade["ad_end"]
            a_ap = last_trade["ap_end"]

        a_origin["a_as"] = a_as
        a_origin["a_ad"] = a_ad
        a_origin["a_ap"] = a_ap

        return a_origin

    def get_trade_plan_df_row(self, t, is_trade, a_next, trade_plan, profit, hold_profit, trade_profit):

        row_dict = {**a_next, **trade_plan}
        row_dict['is_trade'] = is_trade
        row_dict['week_num'] = t
        row_dict['profit'] = profit
        row_dict['hold_profit'] = hold_profit
        row_dict['trade_profit'] = trade_profit

        return row_dict

    def get_trade_profit(self, a_origin, forecast_df, delta_df, trade_plan, t):
        a_as = a_origin["a_as"]
        a_ad = a_origin["a_ad"]
        a_ap = a_origin["a_ap"]

        a_start = a_as * delta_df.iloc[t]["SG/D"] + a_ad + a_ap * delta_df.iloc[t]["P/D"]

        trade_plan['trade_s_d'] *= a_as
        trade_plan['trade_s_p'] *= a_as
        trade_plan['trade_d_s'] *= a_ad
        trade_plan['trade_d_p'] *= a_ad
        trade_plan['trade_p_s'] *= a_ap
        trade_plan['trade_p_d'] *= a_ap

        ad_end, ap_end, as_end = self.sub_total_value_rule_2(a_ad, a_ap, a_as, delta_df, forecast_df, t, trade_plan)

        a_end = as_end * delta_df.iloc[t + 1]["SG/D_Forecast"] + ad_end + ap_end * delta_df.iloc[t + 1]["P/D_Forecast"]

        a_next = dict()
        a_next["as_start"] = a_as
        a_next["ad_start"] = a_ad
        a_next["ap_start"] = a_ap
        a_next["as_end"] = as_end
        a_next["ad_end"] = ad_end
        a_next["ap_end"] = ap_end
        a_next["a_start"] = a_start
        a_next["a_end"] = a_end

        profit = a_end - a_start

        return a_next, trade_plan, profit

    def sub_total_value_rule_1(self, a_ad, a_ap, a_as, delta_df, forecast_df, t, trade_plan):
        as_end = (a_as - trade_plan['trade_s_d'] - trade_plan['trade_s_p']) * (
                1 + forecast_df.iloc[t]["SGPRIME"] / 5200) + trade_plan['trade_d_s'] * 0.99 / delta_df.iloc[t][
                     "SG/D"] + trade_plan['trade_p_s'] * 0.99 * delta_df.iloc[t]["P/SG"]
        ad_end = (a_ad - trade_plan['trade_d_s'] - trade_plan['trade_d_p']) * (
                1 + forecast_df.iloc[t]["USPRIME"] / 5200) + trade_plan['trade_s_d'] * 0.99 * delta_df.iloc[t][
                     "SG/D"] + trade_plan['trade_p_d'] * 0.99 * delta_df.iloc[t]["P/D"]
        ap_end = (a_ap - trade_plan['trade_p_s'] - trade_plan['trade_p_d']) * (
                1 + forecast_df.iloc[t]["UKPRIME"] / 5200) + trade_plan['trade_d_p'] * 0.99 / delta_df.iloc[t][
                     "P/D"] + trade_plan['trade_s_p'] * 0.99 / delta_df.iloc[t]["P/SG"]
        return ad_end, ap_end, as_end

    def sub_total_value_rule_2(self, a_ad, a_ap, a_as, delta_df, forecast_df, t, trade_plan):
        as_end = (a_as - trade_plan['trade_s_d'] - trade_plan['trade_s_p'] + trade_plan['trade_d_s'] * 0.99 /
                  delta_df.iloc[t][
                      "SG/D"] + trade_plan['trade_p_s'] * 0.99 * delta_df.iloc[t]["P/SG"]) * (
                             1 + forecast_df.iloc[t]["SGPRIME"] / 5200)
        ad_end = (a_ad - trade_plan['trade_d_s'] - trade_plan['trade_d_p'] + trade_plan['trade_s_d'] * 0.99 *
                  delta_df.iloc[t][
                      "SG/D"] + trade_plan['trade_p_d'] * 0.99 * delta_df.iloc[t]["P/D"]) * (
                             1 + forecast_df.iloc[t]["USPRIME"] / 5200)
        ap_end = (a_ap - trade_plan['trade_p_s'] - trade_plan['trade_p_d'] + trade_plan['trade_d_p'] * 0.99 /
                  delta_df.iloc[t][
                      "P/D"] + trade_plan['trade_s_p'] * 0.99 / delta_df.iloc[t]["P/SG"]) * (
                             1 + forecast_df.iloc[t]["UKPRIME"] / 5200)
        return ad_end, ap_end, as_end

    def get_all_hold_profit(self, a_origin, forecast_df, delta_df, t):
        a_as = a_origin["a_as"]
        a_ad = a_origin["a_ad"]
        a_ap = a_origin["a_ap"]

        as_end = a_as * (1 + forecast_df.iloc[t]["SGPRIME"] / 5200)
        ad_end = a_ad * (1 + forecast_df.iloc[t]["USPRIME"] / 5200)
        ap_end = a_ap * (1 + forecast_df.iloc[t]["UKPRIME"] / 5200)

        a_start = a_as * delta_df.iloc[t]["SG/D"] + a_ad + a_ap * delta_df.iloc[t]["P/D"]
        a_end = as_end * delta_df.iloc[t + 1]["SG/D_Forecast"] + ad_end + ap_end * delta_df.iloc[t + 1]["P/D_Forecast"]

        a_next = dict()
        a_next["as_start"] = a_as
        a_next["ad_start"] = a_ad
        a_next["ap_start"] = a_ap
        a_next["as_end"] = as_end
        a_next["ad_end"] = ad_end
        a_next["ap_end"] = ap_end
        a_next["a_start"] = a_start
        a_next["a_end"] = a_end

        profit = a_end - a_start

        return a_next, profit
