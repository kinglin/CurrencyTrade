import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from crcytrade import mytrade


class sfsupport:

    def __init__(self):
        self.fuzzify()
        self.inference()

    def fuzzify(self):
        self.accuracy_sg_d = ctrl.Antecedent(np.arange(0, 1.01, 0.001), 'accuracy_sg_d')

        self.accuracy_sg_d['high'] = fuzz.trapmf(self.accuracy_sg_d.universe, [0, 0, 0.075, 0.15])
        self.accuracy_sg_d['medium'] = fuzz.trapmf(self.accuracy_sg_d.universe, [0.05, 0.2, 0.2, 0.35])
        self.accuracy_sg_d['low'] = fuzz.trapmf(self.accuracy_sg_d.universe, [0.25, 0.325, 100, 100])

        self.accuracy_p_d = ctrl.Antecedent(np.arange(0, 1.01, 0.001), 'accuracy_p_d')

        self.accuracy_p_d['high'] = fuzz.trapmf(self.accuracy_p_d.universe, [0, 0, 0.15, 0.3])
        self.accuracy_p_d['medium'] = fuzz.trapmf(self.accuracy_p_d.universe, [0.1, 0.4, 0.4, 0.7])
        self.accuracy_p_d['low'] = fuzz.trapmf(self.accuracy_p_d.universe, [0.5, 0.65, 100, 100])

        self.accuracy_p_sg = ctrl.Antecedent(np.arange(0, 1.01, 0.001), 'accuracy_p_sg')

        self.accuracy_p_sg['high'] = fuzz.trapmf(self.accuracy_p_sg.universe, [0, 0, 0.075, 0.15])
        self.accuracy_p_sg['medium'] = fuzz.trapmf(self.accuracy_p_sg.universe, [0.05, 0.2, 0.2, 0.35])
        self.accuracy_p_sg['low'] = fuzz.trapmf(self.accuracy_p_sg.universe, [0.25, 0.325, 100, 100])

        self.s_factor_sg_d = ctrl.Consequent(np.arange(0, 1.01, 0.001), 's_factor_sg_d')

        self.s_factor_sg_d['low'] = fuzz.trapmf(self.s_factor_sg_d.universe, [0, 0, 0.05, 0.55])
        self.s_factor_sg_d['medium'] = fuzz.trapmf(self.s_factor_sg_d.universe, [0.35, 0.5, 0.65, 0.80])
        self.s_factor_sg_d['high'] = fuzz.trapmf(self.s_factor_sg_d.universe, [0.70, 0.85, 100, 100])

        self.s_factor_p_d = ctrl.Consequent(np.arange(0, 1.01, 0.001), 's_factor_p_d')

        self.s_factor_p_d['low'] = fuzz.trapmf(self.s_factor_p_d.universe, [0, 0, 0.05, 0.55])
        self.s_factor_p_d['medium'] = fuzz.trapmf(self.s_factor_p_d.universe, [0.35, 0.5, 0.65, 0.80])
        self.s_factor_p_d['high'] = fuzz.trapmf(self.s_factor_p_d.universe, [0.70, 0.85, 100, 100])

        self.s_factor_p_sg = ctrl.Consequent(np.arange(0, 1.01, 0.001), 's_factor_p_sg')

        self.s_factor_p_sg['low'] = fuzz.trapmf(self.s_factor_p_sg.universe, [0, 0, 0.05, 0.55])
        self.s_factor_p_sg['medium'] = fuzz.trapmf(self.s_factor_p_sg.universe, [0.35, 0.5, 0.65, 0.80])
        self.s_factor_p_sg['high'] = fuzz.trapmf(self.s_factor_p_sg.universe, [0.70, 0.85, 100, 100])

        if mytrade.DEBUGLEVEL == 1:
            self.accuracy_sg_d.view()
            self.accuracy_p_d.view()
            self.accuracy_p_sg.view()
            self.s_factor_sg_d.view()
            self.s_factor_p_d.view()
            self.s_factor_p_sg.view()

        return

    def inference(self):
        self.rule11 = ctrl.Rule(self.accuracy_sg_d['low'], self.s_factor_sg_d['low'])
        self.rule12 = ctrl.Rule(self.accuracy_sg_d['medium'], self.s_factor_sg_d['medium'])
        self.rule13 = ctrl.Rule(self.accuracy_sg_d['high'], self.s_factor_sg_d['high'])

        self.rule21 = ctrl.Rule(self.accuracy_p_d['low'], self.s_factor_p_d['low'])
        self.rule22 = ctrl.Rule(self.accuracy_p_d['medium'], self.s_factor_p_d['medium'])
        self.rule23 = ctrl.Rule(self.accuracy_p_d['high'], self.s_factor_p_d['high'])

        self.rule31 = ctrl.Rule(self.accuracy_p_sg['low'], self.s_factor_p_sg['low'])
        self.rule32 = ctrl.Rule(self.accuracy_p_sg['medium'], self.s_factor_p_sg['medium'])
        self.rule33 = ctrl.Rule(self.accuracy_p_sg['high'], self.s_factor_p_sg['high'])

        ctrl_sd = ctrl.ControlSystem([self.rule11, self.rule12, self.rule13])
        self.simu_sd = ctrl.ControlSystemSimulation(ctrl_sd)

        ctrl_pd = ctrl.ControlSystem([self.rule21, self.rule22, self.rule23])
        self.simu_pd = ctrl.ControlSystemSimulation(ctrl_pd)

        ctrl_ps = ctrl.ControlSystem([self.rule31, self.rule32, self.rule33])
        self.simu_ps = ctrl.ControlSystemSimulation(ctrl_ps)

        return

    def defuzzify(self, data):
        self.simu_sd.input['accuracy_sg_d'] = data['MAPE_SG/D']
        self.simu_sd.compute()
        sf_sd = self.simu_sd.output['s_factor_sg_d']

        self.simu_pd.input['accuracy_p_d'] = data['MAPE_P/D']
        self.simu_pd.compute()
        sf_pd = self.simu_pd.output['s_factor_p_d']

        self.simu_ps.input['accuracy_p_sg'] = data['MAPE_P/SG']
        self.simu_ps.compute()
        sf_ps = self.simu_ps.output['s_factor_p_sg']

        sf_result = dict()
        sf_result['sf_sd'] = sf_sd
        sf_result['sf_pd'] = sf_pd
        sf_result['sf_ps'] = sf_ps

        if mytrade.DEBUGLEVEL == 1:
            self.s_factor_p_sg.view(sim=self.simu_ps)
            self.s_factor_p_d.view(sim=self.simu_pd)
            self.s_factor_sg_d.view(sim=self.simu_sd)

        return sf_result
