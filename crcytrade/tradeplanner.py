import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from crcytrade import mytrade


class tradeplanner:

    def __init__(self, tmmf_params_df, tmmf_range_params_df):
        self.fuzzify(tmmf_params_df, tmmf_range_params_df)
        self.inference()

    def fuzzify(self, tmmf_params_df, tmmf_range_params_df):

        self.pos_pct_delta_s_d = ctrl.Antecedent(np.arange(0, 2.01, 0.01), 'pos_pct_delta_s_d')
        self.neg_pct_delta_s_d = ctrl.Antecedent(np.arange(0, 2.01, 0.01), 'neg_pct_delta_s_d')
        self.pos_pct_delta_p_d = ctrl.Antecedent(np.arange(0, 4.01, 0.01), 'pos_pct_delta_p_d')
        self.neg_pct_delta_p_d = ctrl.Antecedent(np.arange(0, 4.01, 0.01), 'neg_pct_delta_p_d')
        self.pos_pct_delta_p_s = ctrl.Antecedent(np.arange(0, 4.01, 0.01), 'pos_pct_delta_p_s')
        self.neg_pct_delta_p_s = ctrl.Antecedent(np.arange(0, 4.01, 0.01), 'neg_pct_delta_p_s')

        self.tm_s_d = ctrl.Consequent(np.arange(0, tmmf_range_params_df['tm_sd'][0], 0.01), 'tm_s_d')
        self.tm_s_p = ctrl.Consequent(np.arange(0, tmmf_range_params_df['tm_sp'][0], 0.01), 'tm_s_p')
        self.tm_d_s = ctrl.Consequent(np.arange(0, tmmf_range_params_df['tm_ds'][0], 0.01), 'tm_d_s')
        self.tm_d_p = ctrl.Consequent(np.arange(0, tmmf_range_params_df['tm_dp'][0], 0.01), 'tm_d_p')
        self.tm_p_s = ctrl.Consequent(np.arange(0, tmmf_range_params_df['tm_ps'][0], 0.01), 'tm_p_s')
        self.tm_p_d = ctrl.Consequent(np.arange(0, tmmf_range_params_df['tm_pd'][0], 0.01), 'tm_p_d')

        # MF for self.pos_pct_delta_s_d
        self.pos_pct_delta_s_d['low'] = fuzz.trapmf(self.pos_pct_delta_s_d.universe, [0, 0, 0.25, 0.75])
        self.pos_pct_delta_s_d['medium'] = fuzz.trapmf(self.pos_pct_delta_s_d.universe, [0.25, 0.75, 0.75, 1.25])
        self.pos_pct_delta_s_d['high'] = fuzz.trapmf(self.pos_pct_delta_s_d.universe, [0.75, 1.5, 100, 100])

        # MF for self.neg_pct_delta_s_d
        self.neg_pct_delta_s_d['low'] = fuzz.trapmf(self.neg_pct_delta_s_d.universe, [0, 0, 0.25, 0.75])
        self.neg_pct_delta_s_d['medium'] = fuzz.trapmf(self.neg_pct_delta_s_d.universe, [0.25, 0.75, 0.75, 1.25])
        self.neg_pct_delta_s_d['high'] = fuzz.trapmf(self.neg_pct_delta_s_d.universe, [0.75, 1.5, 100, 100])

        # MF for self.pos_pct_delta_p_d
        self.pos_pct_delta_p_d['low'] = fuzz.trapmf(self.pos_pct_delta_p_d.universe, [0, 0, 0.5, 1.5])
        self.pos_pct_delta_p_d['medium'] = fuzz.trapmf(self.pos_pct_delta_p_d.universe, [0.5, 1.5, 1.5, 2.5])
        self.pos_pct_delta_p_d['high'] = fuzz.trapmf(self.pos_pct_delta_p_d.universe, [1.5, 3, 100, 100])

        # MF for self.neg_pct_delta_p_d
        self.neg_pct_delta_p_d['low'] = fuzz.trapmf(self.neg_pct_delta_p_d.universe, [0, 0, 0.5, 1.5])
        self.neg_pct_delta_p_d['medium'] = fuzz.trapmf(self.neg_pct_delta_p_d.universe, [0.5, 1.5, 1.5, 2.5])
        self.neg_pct_delta_p_d['high'] = fuzz.trapmf(self.neg_pct_delta_p_d.universe, [1.5, 3, 100, 100])

        # MF for self.pos_pct_delta_p_s
        self.pos_pct_delta_p_s['low'] = fuzz.trapmf(self.pos_pct_delta_p_s.universe, [0, 0, 0.5, 1.5])
        self.pos_pct_delta_p_s['medium'] = fuzz.trapmf(self.pos_pct_delta_p_s.universe, [0.5, 1.5, 1.5, 2.5])
        self.pos_pct_delta_p_s['high'] = fuzz.trapmf(self.pos_pct_delta_p_s.universe, [1.5, 3, 100, 100])

        # MF for self.neg_pct_delta_p_s
        self.neg_pct_delta_p_s['low'] = fuzz.trapmf(self.neg_pct_delta_p_s.universe, [0, 0, 0.5, 1.5])
        self.neg_pct_delta_p_s['medium'] = fuzz.trapmf(self.neg_pct_delta_p_s.universe, [0.5, 1.5, 1.5, 2.5])
        self.neg_pct_delta_p_s['high'] = fuzz.trapmf(self.neg_pct_delta_p_s.universe, [1.5, 3, 100, 100])

        # MF for self.tm_s_d
        self.tm_s_d['low'] = fuzz.trapmf(self.tm_s_d.universe, tmmf_params_df['tm_sd_low'])
        self.tm_s_d['medium'] = fuzz.trapmf(self.tm_s_d.universe, tmmf_params_df['tm_sd_medium'])
        self.tm_s_d['high'] = fuzz.trapmf(self.tm_s_d.universe, tmmf_params_df['tm_sd_high'])

        # MF for self.tm_d_s
        self.tm_d_s['low'] = fuzz.trapmf(self.tm_d_s.universe, tmmf_params_df['tm_ds_low'])
        self.tm_d_s['medium'] = fuzz.trapmf(self.tm_d_s.universe, tmmf_params_df['tm_ds_medium'])
        self.tm_d_s['high'] = fuzz.trapmf(self.tm_d_s.universe, tmmf_params_df['tm_ds_high'])

        # MF for self.tm_p_d
        self.tm_p_d['low'] = fuzz.trapmf(self.tm_p_d.universe, tmmf_params_df['tm_pd_low'])
        self.tm_p_d['medium'] = fuzz.trapmf(self.tm_p_d.universe, tmmf_params_df['tm_pd_medium'])
        self.tm_p_d['high'] = fuzz.trapmf(self.tm_p_d.universe, tmmf_params_df['tm_pd_high'])

        # MF for self.tm_d_p
        self.tm_d_p['low'] = fuzz.trapmf(self.tm_d_p.universe, tmmf_params_df['tm_dp_low'])
        self.tm_d_p['medium'] = fuzz.trapmf(self.tm_d_p.universe, tmmf_params_df['tm_dp_medium'])
        self.tm_d_p['high'] = fuzz.trapmf(self.tm_d_p.universe, tmmf_params_df['tm_dp_high'])

        # MF for self.tm_p_s
        self.tm_p_s['low'] = fuzz.trapmf(self.tm_p_s.universe, tmmf_params_df['tm_ps_low'])
        self.tm_p_s['medium'] = fuzz.trapmf(self.tm_p_s.universe, tmmf_params_df['tm_ps_medium'])
        self.tm_p_s['high'] = fuzz.trapmf(self.tm_p_s.universe, tmmf_params_df['tm_ps_high'])

        # MF for self.tm_s_p
        self.tm_s_p['low'] = fuzz.trapmf(self.tm_s_p.universe, tmmf_params_df['tm_sp_low'])
        self.tm_s_p['medium'] = fuzz.trapmf(self.tm_s_p.universe, tmmf_params_df['tm_sp_medium'])
        self.tm_s_p['high'] = fuzz.trapmf(self.tm_s_p.universe, tmmf_params_df['tm_sp_high'])
        # ===define MF for consequence end===

        if mytrade.DEBUGLEVEL == 1:
            self.pos_pct_delta_s_d.view()
            self.neg_pct_delta_s_d.view()
            self.pos_pct_delta_p_d.view()
            self.neg_pct_delta_p_d.view()
            self.pos_pct_delta_p_s.view()
            self.neg_pct_delta_p_s.view()
            self.tm_s_d.view()
            self.tm_s_p.view()
            self.tm_d_s.view()
            self.tm_d_p.view()
            self.tm_p_s.view()
            self.tm_p_d.view()

        return

    def inference(self):

        self.rule11 = ctrl.Rule(self.pos_pct_delta_s_d['low'], self.tm_d_s['low'])
        self.rule12 = ctrl.Rule(self.pos_pct_delta_s_d['medium'], self.tm_d_s['medium'])
        self.rule13 = ctrl.Rule(self.pos_pct_delta_s_d['high'], self.tm_d_s['high'])

        self.rule21 = ctrl.Rule(self.neg_pct_delta_s_d['low'], self.tm_s_d['low'])
        self.rule22 = ctrl.Rule(self.neg_pct_delta_s_d['medium'], self.tm_s_d['medium'])
        self.rule23 = ctrl.Rule(self.neg_pct_delta_s_d['high'], self.tm_s_d['high'])

        self.rule31 = ctrl.Rule(self.pos_pct_delta_p_d['low'], self.tm_d_p['low'])
        self.rule32 = ctrl.Rule(self.pos_pct_delta_p_d['medium'], self.tm_d_p['medium'])
        self.rule33 = ctrl.Rule(self.pos_pct_delta_p_d['high'], self.tm_d_p['high'])

        self.rule41 = ctrl.Rule(self.neg_pct_delta_p_d['low'], self.tm_p_d['low'])
        self.rule42 = ctrl.Rule(self.neg_pct_delta_p_d['medium'], self.tm_p_d['medium'])
        self.rule43 = ctrl.Rule(self.neg_pct_delta_p_d['high'], self.tm_p_d['high'])

        self.rule51 = ctrl.Rule(self.pos_pct_delta_p_s['low'], self.tm_s_p['low'])
        self.rule52 = ctrl.Rule(self.pos_pct_delta_p_s['medium'], self.tm_s_p['medium'])
        self.rule53 = ctrl.Rule(self.pos_pct_delta_p_s['high'], self.tm_s_p['high'])

        self.rule61 = ctrl.Rule(self.neg_pct_delta_p_s['low'], self.tm_p_s['low'])
        self.rule62 = ctrl.Rule(self.neg_pct_delta_p_s['medium'], self.tm_p_s['medium'])
        self.rule63 = ctrl.Rule(self.neg_pct_delta_p_s['high'], self.tm_p_s['high'])

        ctrl_sd = ctrl.ControlSystem([self.rule11, self.rule12, self.rule13])
        self.simu_sd = ctrl.ControlSystemSimulation(ctrl_sd)

        ctrl_ds = ctrl.ControlSystem([self.rule21, self.rule22, self.rule23])
        self.simu_ds = ctrl.ControlSystemSimulation(ctrl_ds)

        ctrl_pd = ctrl.ControlSystem([self.rule31, self.rule32, self.rule33])
        self.simu_pd = ctrl.ControlSystemSimulation(ctrl_pd)

        ctrl_dp = ctrl.ControlSystem([self.rule41, self.rule42, self.rule43])
        self.simu_dp = ctrl.ControlSystemSimulation(ctrl_dp)

        ctrl_ps = ctrl.ControlSystem([self.rule51, self.rule52, self.rule53])
        self.simu_ps = ctrl.ControlSystemSimulation(ctrl_ps)

        ctrl_sp = ctrl.ControlSystem([self.rule61, self.rule62, self.rule63])
        self.simu_sp = ctrl.ControlSystemSimulation(ctrl_sp)

        return

    # data here is one row data
    def defuzzify(self, data):

        trade_s_d = 0
        trade_s_p = 0
        trade_d_s = 0
        trade_d_p = 0
        trade_p_s = 0
        trade_p_d = 0

        pct_delta_s_d = data["%delta_SG/D_Forecast"]
        pct_delta_p_d = data["%delta_P/D_Forecast"]
        pct_delta_p_s = data["%delta_P/SG_Forecast"]

        if pct_delta_s_d >= 0:
            self.simu_sd.input['pos_pct_delta_s_d'] = pct_delta_s_d
            self.simu_sd.compute()
            trade_d_s = self.simu_sd.output['tm_d_s']
        else:
            self.simu_ds.input['neg_pct_delta_s_d'] = -pct_delta_s_d
            self.simu_ds.compute()
            trade_s_d = self.simu_ds.output['tm_s_d']

        if pct_delta_p_d >= 0:
            self.simu_pd.input['pos_pct_delta_p_d'] = pct_delta_p_d
            self.simu_pd.compute()
            trade_d_p = self.simu_pd.output['tm_d_p']
        else:
            self.simu_dp.input['neg_pct_delta_p_d'] = -pct_delta_p_d
            self.simu_dp.compute()
            trade_p_d = self.simu_dp.output['tm_p_d']

        if pct_delta_p_s >= 0:
            self.simu_ps.input['pos_pct_delta_p_s'] = pct_delta_p_s
            self.simu_ps.compute()
            trade_s_p = self.simu_ps.output['tm_s_p']

        else:
            self.simu_sp.input['neg_pct_delta_p_s'] = -pct_delta_p_s
            self.simu_sp.compute()
            trade_p_s = self.simu_sp.output['tm_p_s']

        trade_result = dict()
        trade_result['trade_s_d'] = trade_s_d / 100
        trade_result['trade_d_s'] = trade_d_s / 100
        trade_result['trade_d_p'] = trade_d_p / 100
        trade_result['trade_p_d'] = trade_p_d / 100
        trade_result['trade_s_p'] = trade_s_p / 100
        trade_result['trade_p_s'] = trade_p_s / 100

        if mytrade.DEBUGLEVEL == 1:
            self.tm_s_d.view(sim=self.simu_ds)
            self.tm_d_s.view(sim=self.simu_sd)
            self.tm_s_p.view(sim=self.simu_ps)
            self.tm_p_s.view(sim=self.simu_sp)
            self.tm_p_d.view(sim=self.simu_dp)
            self.tm_d_p.view(sim=self.simu_pd)

        return trade_result
