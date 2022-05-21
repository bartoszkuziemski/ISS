from AeroPendulum import *
from PIDRegulator import *
from FuzzyPDRegulator import *
from dash import dcc
from dash import html
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output
import dash_daq as daq
import math
from Simulation import Simulation

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
            id='slider_kp',
            min=0,
            max=10,
            step=0.05,
            marks={0: '0', 10: '10'},
            value=0.95,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.Label('Wartość Ti'),
        dcc.Slider(
            id='slider_ti',
            min=0.1,
            max=20,
            step=0.05,
            marks={0.1: '0.1', 20: '20'},
            value=0.75,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.Label('Wartość Td'),
        dcc.Slider(
            id='slider_td',
            min=0,
            max=20,
            step=0.1,
            marks={0: '0', 20: '20'},
            value=0.5,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.Label('Wartość zadana regulatora PID'),
        dcc.RadioItems(
            id='radio_pid',
            options=[
                {'label': 'Skok jednostkowy', 'value': 3},
                {'label': 'Sinusoida', 'value': 4},
                {'label': 'Sygnał prostokątny', 'value': 5},
            ],
            value=3
        ),

        html.Br(),
        html.Label('Wartość zadana regulatora rozmytego'),
        dcc.RadioItems(
            id='radio_fuzzy',
            options=[
                {'label': 'Skok jednostkowy', 'value': 0},
                {'label': 'Sinusoida', 'value': 1},
                {'label': 'Sygnał prostokątny', 'value': 2},
            ],
            value=0
        ),

        html.Br(),
        html.Label('Wartość Ti regulatora rozmytego'),
        dcc.Slider(
            id='slider_fuzzy_Ti',
            min=0.1,
            max=20.0,
            step=0.05,
            marks={0.1: '0.1', 20.0: '20'},
            value=0.75,
            tooltip={"placement": "bottom", "always_visible": True}
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
        html.Label('Częstotliwość dodatkowego sygnału [Hz]'),
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
              Input('radio_fuzzy', 'value'),
              Input('setpoint', 'value'),
              Input('sine_frequency', 'value'),
              Input('slider_fuzzy_Ti', 'value'))
def plot_graph_fuzzy(simulation_time, radio_fuzzy, setpoint, sine_frequency, slider_fuzzy_Ti):
    aero_pendulum = AeroPendulum()
    fuzzy_regulator = FuzzyPDRegulator(ti=slider_fuzzy_Ti)
    simulation = Simulation()
    simulation.simulate(aero_pendulum, fuzzy_regulator, setpoint, simulation_time, radio_fuzzy, sine_frequency)
    fig = go.Figure(
        layout=dict(
            title="Regulator rozmyty",
            xaxis_title="Czas [s]",
            #yaxis_title="Kąt alfa [rad]"
        ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.alpha_List,
        name="Alpha [rad]",
        line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=simulation.time,
        y=simulation.ref_signal,
        name="Wartość zadana [rad]",
        line=dict(color='orange', width=1, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.omega_list,
        name="Omega [rad/s]",
        line=dict(color='red', width=1)
    ))
    fig.update_layout(
        margin=dict(b=50, t=50, l=50, r=50),
        width=1000,
        height=400
    )

    return fig


@app.callback(Output('plot_graph_pid', 'figure'),
              Input('slider_kp', 'value'),
              Input('slider_ti', 'value'),
              Input('slider_td', 'value'),
              Input('simulation_time', 'value'),
              Input('radio_pid', 'value'),
              Input('setpoint', 'value'),
              Input('sine_frequency', 'value'))
def plot_graph_pid(slider_kp, slider_ti, slider_td, simulation_time, radio_pid, setpoint, sine_frequency):
    aero_pendulum = AeroPendulum()
    classic_regulator = PIDRegulator(slider_kp, slider_ti, slider_td)
    simulation = Simulation()
    simulation.simulate(aero_pendulum, classic_regulator, setpoint, simulation_time, radio_pid, sine_frequency)
    fig = go.Figure(
        layout=dict(
            title="Regulator PID",
            xaxis_title="Czas [s]",
            #yaxis_title="Kąt alfa [rad]"
        ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.alpha_List,
        name="Alpha [rad]",
        line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=simulation.time,
        y=simulation.ref_signal,
        name="Wartość zadana [rad]",
        line=dict(color='orange', width=1, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=aero_pendulum.time_list,
        y=aero_pendulum.omega_list,
        name="Omega [rad/s]",
        line=dict(color='red', width=1)
    ))
    fig.update_layout(
        margin=dict(b=50, t=50, l=50, r=50),
        width=1000,
        height=400
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

