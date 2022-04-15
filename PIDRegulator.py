def limit_saturation(value=0.0, min_value=-10.0, max_value=10.0):
    if value > max_value:
        value = max_value
    elif value < min_value:
        value = min_value

    return value


def limit_value(new_value=0.0, last_value=0.0, delta_max=1.0):
    delta_max = abs(delta_max)
    if new_value > last_value:
        if new_value < last_value + delta_max:
            return new_value
        else:
            return last_value + delta_max
    else:
        if new_value > last_value - delta_max:
            return new_value
        else:
            return last_value - delta_max


class PIDRegulator:

    def __init__(self, kp=1.0, ti=99999999999.0, td=0.0,
                 u_min=-10.0, u_max=10, u_delta_max=0.01):
        self.kp = kp
        self.ti = ti
        self.td = td
        self.u_min = u_min
        self.u_max = u_max
        self.u_delta_max = u_delta_max
        self.integral = 0.0
        self.error_list = []
        self.u_list = [0.0]
        self.time_list = [0.0]
        # debug:
        self.de_list = []
        self.i_list = [0.0]

    def control(self, reference_value=0.0, measured_value=0.0, time=0.0):
        time_delta = (time - self.time_list[-1])
        self.time_list.append(time)
        error = reference_value - measured_value
        self.error_list.append(error)
        self.integral = self.integral + time_delta * error
        self.i_list.append(self.integral)
        if len(self.error_list) <= 1:
            self.error_list.append(error)

        de = (self.error_list[-1] - self.error_list[-2]) / time_delta
        #debug
        self.de_list.append(de)

        u = self.kp * (self.error_list[-1] + 1 / self.ti * self.integral + self.td * de)
        u_sat = limit_saturation(u, self.u_min, self.u_max)
        u_lim = limit_value(u_sat, self.u_list[-1], self.u_delta_max)
        self.u_list.append(u_lim)
        return self.u_list[-1]

    def set_coefs(self, kp=1.0, ti=999999.9, td=0.0):
        self.kp = kp
        self.ti = ti
        self.td = td

