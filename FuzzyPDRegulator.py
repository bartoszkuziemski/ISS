import math
from PIDRegulator import limit_saturation, limit_value

from pyparsing import version_info
from simpful import *


# This class describes fuzzy PD regulator with ,,classic'' integral block added for controlling the aeropendulum.

class FuzzyPDRegulator:
    def __init__(self, u_amp=10.0, u_min=-10.0, u_max=10, u_delta_max=0.01):
        self.error_list = [0.0]
        self.u_list = [0.0]
        self.time_list = [0.0]
        self.integral = 0.0
        self.u_min = u_min
        self.u_max = u_max
        self.u_list = [0.0]
        self.u_delta_max = u_delta_max

        self.FS = FuzzySystem()
        # Define fuzzy sets and linguistic variables
        # error:
        pi = math.pi
        self.e_bm = FuzzySet(function=Trapezoidal_MF(a=-pi, b=-pi, c=-pi / 2.0, d=-pi / 12.0), term="BM")
        self.e_sm = FuzzySet(function=Triangular_MF(a=-pi / 2.0, b=-pi / 4.0, c=0.0), term="SM")
        self.e_z = FuzzySet(function=Triangular_MF(a=-pi / 12.0, b=0.0, c=pi / 12.0), term="Z")
        self.e_sp = FuzzySet(function=Triangular_MF(a=0.0, b=pi / 4.0, c=pi / 2.0), term="SP")
        self.e_bp = FuzzySet(function=Trapezoidal_MF(a=pi / 12.0, b=pi / 2.0, c=pi, d=pi), term="BP")
        self.FS.add_linguistic_variable("error", LinguisticVariable([self.e_bm, self.e_sm,
                                                                     self.e_z, self.e_sp,
                                                                     self.e_bp], concept="error",
                                                                    universe_of_discourse=[-math.pi, math.pi]))
        # derivative of error:
        big_de = 3.0
        self.de_bm = FuzzySet(
            function=Trapezoidal_MF(a=-big_de, b=-big_de, c=-2.0 / 3.0 * big_de, d=-1.0 / 3.0 * big_de), term="BM")
        self.de_sm = FuzzySet(function=Triangular_MF(a=-2.0 / 3.0 * big_de, b=-1.0 / 3.0 * big_de, c=0.0), term="SM")
        self.de_z = FuzzySet(function=Triangular_MF(a=-1.0 / 3.0 * big_de, b=0.0, c=1.0 / 3.0 * big_de), term="Z")
        self.de_sp = FuzzySet(function=Triangular_MF(a=0.0, b=1.0 / 3.0 * big_de, c=2.0 / 3.0 * big_de), term="SP")
        self.de_bp = FuzzySet(function=Trapezoidal_MF(a=1.0 / 3.0 * big_de, b=2.0 / 3.0 * big_de, c=big_de, d=big_de),
                              term="BP")
        self.FS.add_linguistic_variable("d_error", LinguisticVariable([self.de_bm, self.de_sm,
                                                                       self.de_z, self.de_sp,
                                                                       self.de_bp], concept="d_error",
                                                                      universe_of_discourse=[-math.pi, math.pi]))

        # Define output fuzzy sets and linguistic variable
        # u_out:
        w = 2.0 / 3.0 * 10.0
        self.o_bm = FuzzySet(function=Triangular_MF(a=-3.0 / 2.0 * w, b=-3.0 / 2.0 * w, c=-w), term="BM")
        self.o_mm = FuzzySet(function=Triangular_MF(a=-3.0 / 2.0 * w, b=-w, c=-1.0 / 2.0 * w), term="MM")
        self.o_sm = FuzzySet(function=Triangular_MF(a=-w, b=-1.0 / 2.0 * w, c=0), term="SM")
        self.o_z = FuzzySet(function=Triangular_MF(a=-1.0 / 2.0 * w, b=0, c=1.0 / 2.0 * w), term="Z")
        self.o_sp = FuzzySet(function=Triangular_MF(a=0, b=1.0 / 2.0 * w, c=w), term="SP")
        self.o_mp = FuzzySet(function=Triangular_MF(a=1.0 / 2.0 * w, b=w, c=3.0 / 2.0 * w), term="MP")
        self.o_bp = FuzzySet(function=Triangular_MF(a=w, b=3.0 / 2.0 * w, c=3.0 / 2.0 * w), term="BP")

        self.FS.add_linguistic_variable("u_out", LinguisticVariable([self.o_bm, self.o_mm, self.o_sm,
                                                                     self.o_z, self.o_sp, self.o_mp,
                                                                     self.o_bp],
                                                                    universe_of_discourse=[-10.0, 10.0]))

        # Define fuzzy rules
        self.FS.add_rules_from_file("rules.txt", verbose=True)

    def control(self, reference_value=0.0, measured_value=0.0, time=0.0, ti=0.5):
        error = reference_value - measured_value
        self.error_list.append(error)
        if len(self.error_list) <= 1:
            self.error_list.append(error)

        time_delta = (time - self.time_list[-1])
        self.integral += error * time_delta
        self.time_list.append(time)
        de = (self.error_list[-1] - self.error_list[-2]) / time_delta

        # Set antecedents values
        self.FS.set_variable("error", error)
        self.FS.set_variable("d_error", de)

        # Perform Mamdani inference
        return_dict = self.FS.Mamdani_inference(terms=["u_out"], subdivisions=10)
        u = return_dict['u_out']

        # classic integral:
        u += self.integral * ti

        u_sat = limit_saturation(u, self.u_min, self.u_max)
        u_lim = limit_value(u_sat, self.u_list[-1], self.u_delta_max)
        self.u_list.append(u_lim)

        return u
