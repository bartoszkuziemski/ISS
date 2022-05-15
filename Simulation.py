import math


class Simulation:
    def __init__(self):
        self.time = []
        self.ref_signal = []

    def simulate(self, aero_pendulum, regulator, ref_val, simulation_time, mode, f):
        simulation_samples = int(simulation_time / aero_pendulum.time_delta_sim)
        t = 0.0
        u = 0.0
        # =============================================  Fuzzy modes   =============================================
        # mode = 0 - unit step function
        if mode == 0:
            ref_signal = ref_val
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)

        # mode = 1 - ref_val * sin(2pi*f*t)
        if mode == 1:
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                ref_signal = ref_val * math.sin(2 * math.pi * f * t)
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)

        # mode = 2 - pulse function (50/50, +ref_val, -ref_val)
        if mode == 2:
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                if ref_val * math.sin(2 * math.pi * f * t) >= 0:
                    ref_signal = ref_val
                else:
                    ref_signal = -ref_val
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)
        # =============================================  PID modes   =============================================
        # mode = 3 - unit step function
        if mode == 3:
            ref_signal = ref_val
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)

        # mode = 4 - ref_val * sin(2pi*f*t)
        if mode == 4:
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                ref_signal = ref_val * math.sin(2 * math.pi * f * t)
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)

        # mode = 5 - pulse function (50/50, +ref_val, -ref_val)
        if mode == 5:
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                if ref_val * math.sin(2 * math.pi * f * t) >= 0:
                    ref_signal = ref_val
                else:
                    ref_signal = -ref_val
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)