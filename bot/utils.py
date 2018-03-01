import requests
from db import Connect
from bot import notify

little_fsm = {}
target = 'http://calc.trendmining.biz/wex/get_kurs.php'


def get_data(data):
    result = []
    words = ['bfx', 'bhbt']
    for i in data:
        if isinstance(i, dict) and i.get('0') in words:
            result.append(i)
    return {'bfx': result[0], 'bhbt': result[1]}


def get_values():
    conn = Connect()
    results = (conn.get_percentage(), conn.get_step())
    conn.close_connection()
    return results


def collect():
    response = {}
    data = get_data(requests.get(target, timeout=(100, 100)).json())
    bfx_keys = ['btc_usd_last', 'bch_usd_last', 'dsh_usd_last',
                'eth_usd_last', 'zec_usd_last', 'ltc_usd_last']
    bhbt_keys = ['btc_last', 'bch_last', 'dsh_last',
                 'eth_last', 'zec_last', 'ltc_last']
    for i, j in zip(bfx_keys, bhbt_keys):
        currency_name = i[:3]
        bhbt_value, bfx_value = [data['bhbt'][j], data['bfx'][i]]
        result = ((bhbt_value - bfx_value) / bhbt_value) * 100
        response[currency_name] = round(result, 1)
    return response


def get_percentage(percentage):
    data = collect()
    step = get_values()[1]
    for i, j in data.items():  # TODO make of this piece of shit something normal
        if j > percentage and i not in little_fsm:
            little_fsm[i] = j
            notify(f'{i}/USD: {j}%')
        elif j < percentage and i in little_fsm:
            del little_fsm[i]
            notify(f'{i}/USD: упал до {j}%')
        elif i in little_fsm:
            diff = ((j - little_fsm[i]) / j) * 100
            if diff >= step:
                little_fsm[i] = j
                notify(f'{i}/USD вырос на {round(diff, 1)}%: {j}%')


def run_collecting():
    current_percentage = get_values()[0]
    while True:
        new_value = get_values()[0]
        if current_percentage != new_value:
            current_percentage = new_value
            little_fsm.clear()
        get_percentage(current_percentage)
