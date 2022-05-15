from AeroPendulum import *
from PIDRegulator import *
from FuzzyPDRegulator import *
from dash import dcc
from dash import html
import plotly.graph_objs as go
# import plotly
import dash
from dash.dependencies import Input, Output
import dash_daq as daq
import math


class Simulation:
    def __init__(self):
        self.time = []
        self.ref_signal = []

    def simulate(self, aero_pendulum, regulator, ref_val, simulation_time, mode, f):
        simulation_samples = int(simulation_time / aero_pendulum.time_delta_sim)
        t = 0.0
        u = 0.0

        # mode = 0 - unit step function fuzzy
        if mode == 0:
            ref_signal = ref_val
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                # u = classic_regulator.control(ref_signal, aero_pendulum.alpha, t)
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)

        # mode = 1 - ref_val * sin(2pi*f*t) fuzzy
        if mode == 1:
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                ref_signal = ref_val * math.sin(2 * math.pi * f * t)
                # u = classic_regulator.control(ref_signal, aero_pendulum.alpha, t)
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)

        # mode = 2 - pulse function (50/50, +ref_val, -ref_val) fuzzy
        if mode == 2:
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                if ref_val * math.sin(2 * math.pi * f * t) >= 0:
                    ref_signal = ref_val
                else:
                    ref_signal = -ref_val
                # u = classic_regulator.control(ref_signal, aero_pendulum.alpha, t)
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)

        # mode = 3 - unit step function PID
        if mode == 3:
            ref_signal = ref_val
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                # u = fuzzy_regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)

        # mode = 4 - ref_val * sin(2pi*f*t) PID
        if mode == 4:
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                ref_signal = ref_val * math.sin(2 * math.pi * f * t)
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                # u = fuzzy_regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)

        # mode = 5 - pulse function (50/50, +ref_val, -ref_val) PID
        if mode == 2:
            for n in range(0, simulation_samples):
                t = aero_pendulum.simulate_step(u)
                if ref_val * math.sin(2 * math.pi * f * t) >= 0:
                    ref_signal = ref_val
                else:
                    ref_signal = -ref_val
                u = regulator.control(ref_signal, aero_pendulum.alpha, t)
                # u = fuzzy_regulator.control(ref_signal, aero_pendulum.alpha, t)
                self.time.append(t)
                self.ref_signal.append(ref_signal)


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(children=[
        dcc.Graph(id='plot_graph_pid', config={'responsive': True}),
        dcc.Graph(id='plot_graph_fuzzy', config={'responsive': True})
    ]),

    html.Div(children=[
        html.Br(),
        html.Label('Wartość Kp'),
        dcc.Slider(
            id='sliderKp',
            min=0,
            max=1,
            step=0.005,
            marks={0: '0', 1: '1'},
            value=0.5,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.Label('Wartość Ti'),
        dcc.Slider(
            id='sliderTi',
            min=0.5,
            max=20,
            step=0.1,
            marks={0.5: '0.5', 20: '20'},
            value=20.0,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.Label('Wartość Td'),
        dcc.Slider(
            id='sliderTd',
            min=0,
            max=20,
            step=0.1,
            marks={0: '0', 20: '20'},
            value=0.0,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.Label('Wartość zadana regulatora rozmytego'),
        dcc.RadioItems(
            id='radioPID',
            options=[
                {'label': 'Skok jednostkowy', 'value': 0},
                {'label': 'Sinusoida', 'value': 1},
                # {'label': 'Sygnał prostokątny', 'value': 2},
            ],
            value=0
        ),

        html.Br(),
        html.Label('Wartość zadana regulatora PID'),
        dcc.RadioItems(
            id='radioFuzzy',
            options=[
                {'label': 'Skok jednostkowy', 'value': 3},
                {'label': 'Sinusoida', 'value': 4},
                # {'label': 'Sygnał prostokątny', 'value': 5},
            ],
            value=3
        ),

        html.Br(),
        html.Label('Wartość zadana [rad]'),
        dcc.Slider(
            id='setpoint',
            min=0.1,
            max=math.pi,
            step=0.01,
            marks={0.1: '0.1', math.pi: 'π'},
            value=1.0,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.Label('Częstotliwość sinusoidy [Hz]'),
        dcc.Slider(
            id='sine_frequency',
            min=0.02,
            max=0.2,
            step=0.01,
            marks={0.02: '0.02', 0.2: '0.2'},
            value=0.1,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.Label('Czas symulacji [s]'),
        daq.NumericInput(
            labelPosition='right',
            id='simulation_time',
            value=5.0,
            min=1.0,
            max=100.0
        ),
    ], style={'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flex-direction': 'row'})


@app.callback(Output('plot_graph_fuzzy', 'figure'),
              Input('simulation_time', 'value'),
              Input('radioFuzzy', 'value'),
              Input('setpoint', 'value'),
              Input('sine_frequency', 'value'))
def plot_graph_fuzzy(simulation_time, radioFuzzy, setpoint, sine_frequency):
    aero_pendulum = AeroPendulum()
    fuzzy_regulator = FuzzyPDRegulator()
    simulation = Simulation()
    simulation.simulate(aero_pendulum, fuzzy_regulator, setpoint, simulation_time, radioFuzzy, sine_frequency)
    fig = go.Figure(
        layout=dict(
            title="Regulator rozmyty",
            xaxis_title="Czas [s]",
            yaxis_title="Kąt alfa [rad]"
        ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.alpha_List,
        name="Alpha",
        line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.omega_list,
        name="Omega",
        line=dict(color='red', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list[1:],
        y=aero_pendulum.epsilon_list[1:],
        name="Epsilon",
        line=dict(color='purple', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=simulation.time,
        y=simulation.ref_signal,
        name="Wartość zadana",
        line=dict(color='orange', width=1, dash='dash')
    ))
    fig.update_layout(
        margin=dict(b=50, t=50, l=50, r=50),
        width=1000,
        height=400
    )

    return fig


@app.callback(Output('plot_graph_pid', 'figure'),
              Input('sliderKp', 'value'),
              Input('sliderTi', 'value'),
              Input('sliderTd', 'value'),
              Input('simulation_time', 'value'),
              Input('radioPID', 'value'),
              Input('setpoint', 'value'),
              Input('sine_frequency', 'value'))
def plot_graph_pid(sliderKp, sliderTi, sliderTd, simulation_time, radioPID, setpoint, sine_frequency):
    aero_pendulum = AeroPendulum()
    classic_regulator = PIDRegulator(sliderKp, sliderTi, sliderTd)
    simulation = Simulation()
    simulation.simulate(aero_pendulum, classic_regulator, setpoint, simulation_time, radioPID, sine_frequency)
    fig = go.Figure(
        layout=dict(
            title="Regulator PID",
            xaxis_title="Czas [s]",
            yaxis_title="Kąt alfa [rad]"
        ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.alpha_List,
        name="Alpha",
        line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.omega_list,
        name="Omega",
        line=dict(color='red', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list[1:],
        y=aero_pendulum.epsilon_list[1:],
        name="Epsilon",
        line=dict(color='purple', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=simulation.time,
        y=simulation.ref_signal,
        name="Wartość zadana",
        line=dict(color='orange', width=1, dash='dash')
    ))
    fig.update_layout(
        margin=dict(b=50, t=50, l=50, r=50),
        width=1000,
        height=400
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

# 3 wykresy - wysokosc slupa wody, natezenie doplywu, sygnal sterujący
# 4 slidery Tp, Ti, Td,
# wartości wskaxnikow calkowych
