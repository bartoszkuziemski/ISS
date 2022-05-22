import math


def normalize_angle(angle: float):
    while angle >= math.pi or angle < -math.pi:
        if angle > math.pi:
            angle -= 2.0 * math.pi
        elif angle < -math.pi:
            angle += 2.0 * math.pi

    return float(angle)


class AeroPendulum:
    #################################################################################################################
    # The AeroPendulum model is described with following equation:
    #          q                         q
    # m*r^2 * ---- = -m*g*r*sin(q) - c * -- + r*Ft(u)
    #         dt^2                       dt
    # Where:
    #
    # --> q - angular displacement of the pendulum (range [-pi : pi)) (described as alpha in code)
    #
    #      q
    # --> ---- - angular velocity of the pendulum [rad/s] (described as omega code)
    #      dt
    #      q
    # --> ---- - angular acceleration of the pendulum [rad/s^2] (described as epsilon in code)
    #     dt^2
    #
    # --> m - mass of the ,,dumbbell'' (we are assuming that the radius part is weightless) [kg]
    #
    # --> r - radius between center of mass and center of rotation [m]
    #
    # --> g - acceleration of gravity [m/s^2]
    #
    # --> c - torque coefficient [kg*m^2/s]
    #
    # --> Ft(u) - force of thrust as a function of voltage passed to fan's motor
    #
    #
    #################################################################################################################
    def __init__(self, time_delta_sim=0.01,
                 m=0.5, r=1, g=9.81, c=0.1,
                 alpha=0.0, omega=0.0, epsilon=0.0):
        self.time_delta_sim = time_delta_sim  # quantum of time [s]
        self.m = m  # mass [kg]
        self.r = r  # pendulum radius [m]
        self.g = g  # gravity [m/s^2]
        self.c = c  # torque coefficient [kg*m^2/s]

        self.alpha = alpha  # pendulum's angle [rad]
        self.omega = omega  # pendulum's angular velocity [rad/s]
        self.epsilon = epsilon  # pendulum's angular acceleration [rad/s^2]

        self.time_list = [0.0]
        self.alpha_List = [alpha]
        self.omega_list = [omega]
        self.epsilon_list = [epsilon]

    def calc_ft(self, u=0.0):
        k = 5  #linear coefficient
        return k * u  # force of thrust [N]

    def calc_epsilon(self, u=0.0):
        ft = self.calc_ft(u)
        self.epsilon = (ft * self.r - self.m * self.g * self.r * math.sin(self.alpha) - self.c * self.omega) / \
                       (self.m * math.pow(self.r, 2))

        self.epsilon_list.append(self.epsilon)

    def calc_omega(self):
        self.omega = self.omega + self.time_delta_sim * self.epsilon
        self.omega_list.append(self.omega)

    def calc_alpha(self):
        alpha_delta = (self.omega + self.omega_list[-2]) * self.time_delta_sim / 2.0
        self.alpha = normalize_angle(self.alpha + alpha_delta)
        self.alpha_List.append(self.alpha)

    def append_time(self):
        self.time_list.append(self.time_list[-1] + self.time_delta_sim)
        return self.time_list[-1]

    def simulate_step(self, u=0.0):
        self.calc_epsilon(u)
        self.calc_omega()
        self.calc_alpha()
        return self.append_time()
