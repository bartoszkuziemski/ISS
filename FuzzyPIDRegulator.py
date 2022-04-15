import math

from pyparsing import version_info
from simpful import *


class FuzzyPIDRegulator:
    def __init__(self, u_amp=10.0):
        self.error_list = [0.0]
        self.integral = 0.0
        self.u_list = [0.0]
        self.time_list = [0.0]

        self.FS = FuzzySystem()
        # Define fuzzy sets and linguistic variables
        # error:
        w = 2.0 / 3.0 * math.pi
        self.e_bm = FuzzySet(function=Triangular_MF(a=-3.0 / 2.0 * w, b=-3.0 / 2.0 * w, c=-w), term="BM")
        self.e_mm = FuzzySet(function=Triangular_MF(a=-3.0 / 2.0 * w, b=-w, c=-1.0 / 2.0 * w), term="MM")
        self.e_sm = FuzzySet(function=Triangular_MF(a=-w, b=-1.0 / 2.0 * w, c=0), term="SM")
        self.e_z = FuzzySet(function=Triangular_MF(a=-1.0 / 2.0 * w, b=0, c=1.0 / 2.0 * w), term="Z")
        self.e_sp = FuzzySet(function=Triangular_MF(a=0, b=1.0 / 2.0 * w, c=w), term="SP")
        self.e_mp = FuzzySet(function=Triangular_MF(a=1.0 / 2.0 * w, b=w, c=3.0 / 2.0 * w), term="MP")
        self.e_bp = FuzzySet(function=Triangular_MF(a=w, b=3.0 / 2.0 * w, c=3.0 / 2.0 * w), term="BP")
        self.FS.add_linguistic_variable("error", LinguisticVariable([self.e_bm, self.e_mm, self.e_sm,
                                                                     self.e_z, self.e_sp, self.e_mp,
                                                                     self.e_bp], concept="error",
                                                                    universe_of_discourse=[-math.pi, math.pi]))
        # derivative of error:
        w = 2.0 / 3.0 * 3.0
        self.de_bm = FuzzySet(function=Triangular_MF(a=-3.0 / 2.0 * w, b=-3.0 / 2.0 * w, c=-w), term="BM")
        self.de_mm = FuzzySet(function=Triangular_MF(a=-3.0 / 2.0 * w, b=-w, c=-1.0 / 2.0 * w), term="MM")
        self.de_sm = FuzzySet(function=Triangular_MF(a=-w, b=-1.0 / 2.0 * w, c=0), term="SM")
        self.de_z = FuzzySet(function=Triangular_MF(a=-1.0 / 2.0 * w, b=0, c=1.0 / 2.0 * w), term="Z")
        self.de_sp = FuzzySet(function=Triangular_MF(a=0, b=1.0 / 2.0 * w, c=w), term="SP")
        self.de_mp = FuzzySet(function=Triangular_MF(a=1.0 / 2.0 * w, b=w, c=3.0 / 2.0 * w), term="MP")
        self.de_bp = FuzzySet(function=Triangular_MF(a=w, b=3.0 / 2.0 * w, c=3.0 / 2.0 * w), term="BP")
        self.FS.add_linguistic_variable("d_error", LinguisticVariable([self.de_bm, self.de_mm, self.de_sm,
                                                                       self.de_z, self.de_sp, self.de_mp,
                                                                       self.de_bp], concept="d_error",
                                                                      universe_of_discourse=[-3.0, 3.0]))

        w = 2.0 / 3.0 * 3.0
        self.i_bm = FuzzySet(function=Triangular_MF(a=-3.0 / 2.0 * w, b=-3.0 / 2.0 * w, c=-w), term="BM")
        self.i_mm = FuzzySet(function=Triangular_MF(a=-3.0 / 2.0 * w, b=-w, c=-1.0 / 2.0 * w), term="MM")
        self.i_sm = FuzzySet(function=Triangular_MF(a=-w, b=-1.0 / 2.0 * w, c=0), term="SM")
        self.i_z = FuzzySet(function=Triangular_MF(a=-1.0 / 2.0 * w, b=0, c=1.0 / 2.0 * w), term="Z")
        self.i_sp = FuzzySet(function=Triangular_MF(a=0, b=1.0 / 2.0 * w, c=w), term="SP")
        self.i_mp = FuzzySet(function=Triangular_MF(a=1.0 / 2.0 * w, b=w, c=3.0 / 2.0 * w), term="MP")
        self.i_bp = FuzzySet(function=Triangular_MF(a=w, b=3.0 / 2.0 * w, c=3.0 / 2.0 * w), term="BP")
        self.FS.add_linguistic_variable("i_error", LinguisticVariable([self.i_bm, self.i_mm, self.i_sm,
                                                                       self.i_z, self.i_sp, self.i_mp,
                                                                       self.i_bp], concept="i_error",
                                                                      universe_of_discourse=[-3.0, 3.0]))

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

    def control(self, reference_value=0.0, measured_value=0.0, time=0.0):
        error = reference_value - measured_value
        self.error_list.append(error)
        self.time_list.append(time)

        # Set antecedents values
        self.FS.set_variable("error", error)
        self.FS.set_variable("d_error", 0.0)
        self.FS.set_variable("i_error", 0.0)

        # Perform Mamdani inference and print output
        return_dict = self.FS.Mamdani_inference(terms=["u_out"], subdivisions=20)
        return return_dict['u_out']




