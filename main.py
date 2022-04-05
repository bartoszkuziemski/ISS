from dash import dcc
from dash import html
import plotly.graph_objs as go
# import plotly
import dash
from dash.dependencies import Input, Output
import math
import matplotlib.pyplot as plt


def normalize_angle(angle: float):
    while angle >= math.pi or angle < -math.pi:
        if angle > math.pi:
            angle -= 2.0 * math.pi
        elif angle < -math.pi:
            angle += 2.0 * math.pi

    return float(angle)


def limit_saturation(value=0.0, min=-10.0, max=10.0):
    if value > max:
        value = max
    elif value < min:
        value = min

    return value


class AeroPendulum:
    #################################################################################################################
    # The AeroPendulum model is described with following equation:
    #          q                         q
    # m*r^2 * ---- = -m*g*r*sin(q) - c * -- + Ft(u)
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
    def __init__(self, time_delta_sim=0.001,
                 m=0.5, r=1, g=9.81, c=0.1,
                 alpha=0, omega=0.0, epsilon=0.0):

        self.time_delta_sim = time_delta_sim  # quantum of time [s]
        self.m = m  # mass [kg]
        self.r = r  # pendulum radius [m]
        self.g = g  # gravity [m/s^2]
        self.c = c  # torque coefficient [kg*m^2/s]

        self.alpha = alpha  # pendulum's angle [rad]
        self.omega = omega  # pendulum's angular velocity [rad/s]
        self.epsilon = epsilon  # pendulum's angular acceleration [rad/s^2]

        self.time_list = []
        self.alpha_List = []
        self.omega_list = []
        self.epsilon_list = []

    def calc_ft(self, u=0.0):
        # TODO: implement Ft as an interesting function of voltage, for now it's just linear function
        k = 5  # temporary linear coefficient
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

    def simulate_step(self, u=0.0):
        self.calc_epsilon(u)
        self.calc_omega()
        self.calc_alpha()
        self.append_time()


class PIDRegulator:
    integral = 0.0
    error_list = [0.0]
    u_list = [0.0]

    time_list = [0.0]

    def __init__(self, time_delta_reg=0.001,
                 kp=1.0, ti=99999999999.0, td=0.0,
                 u_min=-10.0, u_max=10.0):
        self.kp = kp
        self.ti = ti
        self.td = td
        self.time_delta_reg = time_delta_reg
        self.u_min = u_min
        self.u_max = u_max

    def control(self, reference_value, measured_value):
        error = reference_value - measured_value
        self.error_list.append(error)
        self.integral = self.integral + self.time_delta_reg * error
        de = (self.error_list[-1] - self.error_list[-2]) / self.time_delta_reg
        u = self.kp * (self.error_list[-1] + 1/self.ti * self.integral + self.td * de)
        u_sat = limit_saturation(u, self.u_min, self.u_max)
        self.u_list.append(u_sat)
        self.time_list.append(self.time_list[-1] + self.time_delta_reg)
        return u_sat

    def set_coefs(self, kp=1.0, ti=999999.9, td=0.0):
        self.kp = kp
        self.ti = ti
        self.td = td


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(children=[
        dcc.Graph(id='plot_graph', config={'responsive': True})]),

    html.Div(children=[
        html.Br(),
        html.Label('Wartość Kp'),
        dcc.Slider(
            id='sliderKp',
            min=0,
            max=1,
            step=0.005,
            marks={0: '0', 1: '1'},
            value=0.025,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.Label('Wartość Ti'),
        dcc.Slider(
            id='sliderTi',
            min=0,
            max=20,
            step=0.1,
            marks={0: '0', 20: '20'},
            value=2.5,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.Label('Wartość Td'),
        dcc.Slider(
            id='sliderTd',
            min=0,
            max=1000,
            step=1,
            marks={0: '0', 1000: '1000'},
            value=0.2,
            tooltip={"placement": "bottom", "always_visible": True}
        ),
    ], style={'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flex-direction': 'row'})

@app.callback(Output('plot_graph', 'figure'),
              Input('sliderKp', 'value'),
              Input('sliderTi', 'value'),
              Input('sliderTd', 'value'))
def plot_graph(sliderKp, sliderTi, sliderTd):
    aero_pendulum = AeroPendulum()
    pid_regulator = PIDRegulator(kp=sliderKp, ti=sliderTi, td=sliderTd)
    # TODO: simulation class or something
    for n in range(0, 100000):
        aero_pendulum.simulate_step(pid_regulator.control(math.pi/2, aero_pendulum.alpha))

    fig = go.Figure(
        layout=dict(
            title="Wykres położenia",
            xaxis_title="Czas [s]",
            yaxis_title="Kąt alfa [rad]"
        ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.alpha_List,
        name="Wyjście obiektu",
        line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.omega_list,
        name="Omega",
        line=dict(color='red', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.epsilon_list,
        name="epsilon",
        line=dict(color='purple', width=1)
    ))
    # fig.add_trace(go.Scatter(
    #     x=time_list(),
    #     y=[h_zad] * N,
    #     name="Wartość zadana",
    #     line=dict(color='red', width=1, dash='dash')
    # ))

    fig.update_layout(
        margin=dict(b=50, t=50, l=50, r=50),
        width=1000,
        height=500
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

##########################       bokeh
# chart = figure(plot_width=800,
#                plot_height=300,
#                title="Wysokość słupa wody",
#                x_axis_label = "Czas [s]",
#                y_axis_label = "Wysokość [m]"
#                )
#
# chart.line(t_list,
#            h,
#            legend_label="Wyjście regulatora",
#            color="blue",
#            line_width=2
#            )
# chart.line(t_list,
#            h_zad,
#            legend_label="Wartość zadana",
#            color="red",
#            line_dash= [5,5]
#            )
# chart.legend.location = "bottom_right"
# chart.title_location = "left"
#
# show(chart)


############################      matplotlib
# plt.grid()
# plt.plot(t_list, h)
# plt.xlabel("t [s]")
# plt.ylabel("h [m]")
# plt.show()


# 3 wykresy - wysokosc slupa wody, natezenie doplywu, sygnal sterujący
# 4 slidery Tp, Ti, Td,
# wartości wskaxnikow calkowych
