import time
import requests
from db import Connect
from bot import notify

little_fsm = {}
currency = ['btc', 'ltc', 'eth', 'dsh', 'zec', 'bch']
bfx_ticker = 'https://api.bitfinex.com/v1/pubticker/{}'
bhbt_ticker = 'https://api.bithumb.com/public/ticker/{}'
currency_converter = 'http://api.fixer.io/latest?base=USD'
target = 'http://calc.trendmining.biz/wex/get_kurs.php'


def make_request(to):
    while 1:
        try:
            return requests.get(to, timeout=1000).json()
        except Exception as Error:
            print(Error)
            time.sleep(1)


def get_bfx_data():
    result = {'bfx': {}}
    for i in currency:
        response = make_request(bfx_ticker.format(i+'usd'))
        if response.get('error'):
            return {'error': 'wait a minute'}
        result['bfx'][i] = float(response['bid'])
    return result


def make_json():
    result = {'bhbt': {}}
    for i in currency:
        i = ('dash', 'dsh') if i == 'dsh' else i
        response = make_request(bhbt_ticker.format(i[0] if isinstance(i, tuple) else i))
        KRW_value = float(make_request(currency_converter)['rates']['KRW'])
        result['bhbt'][i[1] if isinstance(i, tuple) else i] = float(response['data']['sell_price']) / KRW_value
    bfx_result = get_bfx_data()
    if bfx_result.get('error'):
        return bfx_result
    result.update(bfx_result)
    return result


def get_values():
    conn = Connect()
    results = (conn.get_percentage(), conn.get_step())
    conn.close_connection()
    return results


def collect():
    response = {}
    # data = get_data(make_request())
    data = make_json()
    if data.get('error'): return data
    for i in currency:
        bhbt_value, bfx_value = [data['bhbt'][i], data['bfx'][i]]
        result = ((bhbt_value - bfx_value) / bhbt_value) * 100
        response[i] = round(result, 1)
    return response


def get_percentage(percentage):
    data = collect()
    if data.get('error'):
        return print('Flood error')
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
        time.sleep(60)
