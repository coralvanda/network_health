"""
Principal Author: Eric Linden
Description :

Notes :
November 02, 2020
"""

import os

from datetime import datetime
from typing import List

import dash
import dash_core_components as dcc
import dash_html_components as html
import speedtest

from pythonping import ping

COLORS = ['green'] + ['yellow'] * 4 + ['orange'] * 5 + ['red'] * 11  # total len 20
BASE_FILE_PATH = os.path.join(os.getcwd(), 'history')
Speed_Test = speedtest.Speedtest()

app = dash.Dash()


def get_layout():
    return html.Div([
        dcc.Interval(id='interval-id', interval=1000 * 30),  # 30 second ticks
        dcc.Store(id='store', data=dict(pings=[], pass_fail='')),
        html.H2('Ping results:'),
        html.Div(id='ping-output', children=[]),
    ], id='top-level-container')


app.layout = get_layout()


@app.callback(
    [
        dash.dependencies.Output('ping-output', 'children'),
        dash.dependencies.Output('store', 'data'),
    ],
    [
        dash.dependencies.Input('interval-id', 'n_intervals'),
    ],
    [
        dash.dependencies.State('store', 'data'),
    ]
)
def callback_func(tick, store_state):
    speed_test_results = ''
    response = ping('204.2.229.9', verbose=False)
    good_response = all(r.success for r in response)

    current_time = datetime.now()
    ping_time = current_time.strftime('%H:%M:%S')
    response_elements = [html.P(ping_time)] + [html.P(str(r)) for r in response]

    response_as_str = '1' if good_response else '0'

    if len(store_state['pings']) >= 120:  # one hour of pings
        speed_test_results = run_speed_test()

        write_out_data(
            current_time=current_time,
            speed_test_results=speed_test_results,
            ping_results=store_state['pings'])

        store_state['pings'] = []

    store_state['pass_fail'] = response_as_str + store_state['pass_fail'][:19]  # 10 min history
    store_state['pings'] = update_stored_results(
        ping_time=ping_time,
        ping_result=response,
        history=store_state['pings'])

    return (
        html.Div(
            id='callback-output-container',
            children=[
                html.Div(id='responses-container', children=response_elements),
                html.P(speed_test_results),
                html.P(store_state['pass_fail']),
                html.Div(
                    id='response-color',
                    children='',
                    style=dict(
                        height=200,
                        width=200,
                        backgroundColor=COLORS[store_state['pass_fail'].count('0')]
                    ))
            ]),
        store_state
    )


def update_stored_results(ping_time: str, ping_result, history: List[str]):
    formatted_str = f'{ping_time}: '
    formatted_str += ' - '.join([str(r) for r in ping_result])

    updated_history = history + [formatted_str]

    return updated_history


def write_out_data(current_time, speed_test_results, ping_results):
    formatted_datetime_for_filename = current_time.strftime('%Y-%m-%d-%Hh%Mm')
    file_path = os.path.join(BASE_FILE_PATH, f'{formatted_datetime_for_filename}.txt')

    with open(file_path, 'w') as f:
        f.write(speed_test_results)
        f.write('\n')
        for result in ping_results:
            f.write(result)
            f.write('\n')


def run_speed_test() -> str:
    down_speed = round((round(Speed_Test.download()) / 1048576), 2)
    up_speed = round((round(Speed_Test.upload()) / 1048576), 2)

    return f'Download speed: {down_speed}, Upload speed: {up_speed}'


if __name__ == '__main__':
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=False)
