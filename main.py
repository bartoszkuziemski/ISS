from AeroPendulum import *
from PIDRegulator import *
from FuzzyPIDRegulator import *
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

    def simulate(self, aero_pendulum, classic_regulator, fuzzy_regulator, simulation_time=10.0, mode=0, f=1.0, ref_val=math.pi / 2):
        simulation_samples = int(simulation_time / aero_pendulum.time_delta_sim)
        t = 0.0
        u = 0.0

        for n in range(0, simulation_samples):
            t = aero_pendulum.simulate_step(u)
            if mode == 0:
                ref_signal = ref_val
            elif mode == 1:
                ref_signal = ref_val * math.sin(2 * math.pi * f * t)
            else:
                ref_signal = math.pi / 2

            #wybierz jeden xd
            #u = classic_regulator.control(ref_signal, aero_pendulum.alpha, t)
            u = fuzzy_regulator.control(ref_signal, aero_pendulum.alpha, t)

            self.time.append(t)
            self.ref_signal.append(ref_signal)


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


@app.callback(Output('plot_graph', 'figure'),
              Input('sliderKp', 'value'),
              Input('sliderTi', 'value'),
              Input('sliderTd', 'value'),
              Input('simulation_time', 'value'))
def plot_graph(sliderKp, sliderTi, sliderTd, simulation_time):
    aero_pendulum = AeroPendulum()
    classic_regulator = PIDRegulator(sliderKp, sliderTi, sliderTd)
    fuzzy_regulator = FuzzyPIDRegulator()
    simulation = Simulation()
    simulation.simulate(aero_pendulum, classic_regulator, fuzzy_regulator, simulation_time, mode=0, f=0.2)
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
        x=aero_pendulum.time_list[1:],
        y=aero_pendulum.epsilon_list[1:],
        name="Epsilon",
        line=dict(color='purple', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=simulation.time,
        y=simulation.ref_signal,
        name="Wartość zadana",
        line=dict(color='red', width=1, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=classic_regulator.time_list,
        y=classic_regulator.de_list,
        name="deriv error",
        line=dict(color='yellow', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=classic_regulator.time_list,
        y=classic_regulator.error_list,
        name="error",
        line=dict(color='magenta', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=classic_regulator.time_list,
        y=classic_regulator.i_list,
        name="integral",
        line=dict(color='magenta', width=1)
    ))
    fig.update_layout(
        margin=dict(b=50, t=50, l=50, r=50),
        width=1000,
        height=500
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

# 3 wykresy - wysokosc slupa wody, natezenie doplywu, sygnal sterujący
# 4 slidery Tp, Ti, Td,
# wartości wskaxnikow calkowych
