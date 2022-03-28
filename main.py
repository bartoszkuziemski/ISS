import math
from bokeh.io import output_notebook, show
from bokeh.plotting import figure
from bokeh.models import Div, RangeSlider, Spinner
from dash import dcc
from dash import html
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output

h_zad = 1.5 #wysokosc zadana [m]

A = 1.5 #pole powierzchni przekroju poprzecznego zbiornika [m^2]
B = 0.035 #wspolczynnik wyplywu [m^5/2 / s]
# Qd = 0.05 #natezenie doplywu [m^3 / s]
Tp = 0.1 #okres probkowania [s]
t_sym = 3600 #czas symulacji
N = int(t_sym/Tp) #liczba probek
# t_list = [0.0] #lista z wartosciami czasu [s]
# h_list = [0.0] #lista poziomu substancji w zbiorniku [m]
# kp = 0.025
# Ti = 2.5
# Td = 0.2


def time_list():
    t_list = [0.0]
    for n in range(0, N):
        t_list.append(n*Tp)
    return t_list


def height_list(kp, Ti, Td):
    h_list = [0.0]
    e = [h_zad - h_list[0]]
    I = 0
    de = 0
    for n in range(0, N):
        e.append(h_zad - h_list[n])
        I = I + e[n] * Tp
        if n>0:
            de = (e[n] - e[n-1])/Tp
        un = kp*(e[n] + 1/Ti*I + Td * de)  # napiecie [V]
        if un > 10.0:
            un = 10.0
        elif un < 0.0:
            un = 0.0

        Qd = 0.005 * un  # natezenie doplywu [m^3 / s]

        res = Tp / A * (Qd - B * math.sqrt(h_list[n])) + h_list[n]
        if res < 5.0 or res > 0.0:
            h_list.append(res)
        else:
            h_list.append(5.0)
            print('bledny odczyt')
        # t_list.append(n * Tp)
    return h_list


app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div(children=[
        # html.Label('Wykres'),
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
    fig = go.Figure(
        layout=dict(
            title="Regulator PID",
            xaxis_title="Czas [s]",
            yaxis_title="Wysokość słupa wody[m]"
    ))
    fig.add_trace(go.Scatter(
        x=time_list(),
        y=height_list(sliderKp, sliderTi, sliderTd),
        name="Wyjście obiektu",
        line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=time_list(),
        y=[h_zad] * N,
        name="Wartość zadana",
        line=dict(color='red', width=1, dash='dash')
    ))

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