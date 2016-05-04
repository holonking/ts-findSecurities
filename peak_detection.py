import json

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri, r, Environment



base = importr('base')
stats = importr('stats')
pandas2ri.activate()

def test():
    with open('peak_test_data') as f:
        test = json.load(f)
        print(test.keys())

    df = pd.DataFrame({'x': test['x'], 'y': test['y']})
    lo = stats.loess('y~x', df, span=0.1)
    df['fitted'] = pd.Series(pandas2ri.ri2py(lo.rx2('fitted')))
    df['max'] = pd.rolling_max(df['fitted'], 5)
    df['delta'] = df['max'] - df['fitted']
    df['max_center'] = pd.rolling_max(df['fitted'], 5, center=True)
    df['delta_center'] = df['max_center'] - df['fitted']

    mx = df[df['delta_center']<=0]
    plt.plot(df['x'], df['y'], 'ko', markersize=6, alpha=0.4, mfc='none')
    plt.plot(df['x'], df['fitted'], 'b', lw=2)
    plt.plot(mx['x'], mx['fitted'], 'ro', markersize=9)

    globals()['test'] = test
    globals()['df'] = df

# TODO: split this function into two: fit and find extrema
def find_extrema(x, y, window=5, span_points=25):
    #df = pd.DataFrame({'x': mpl.dates.date2num(x), 'y': y})
    df = pd.DataFrame({'x': range(len(x)), 'y': y})

    span = span_points/len(df)
    lo = stats.loess('y~x', df, span=span, na_action=stats.na_exclude)
    # we have to use predict(lo) instead of lo.rx2('fitted') here, the latter 
    # doesn't not include NAs
    fitted = pd.Series(pandas2ri.ri2py(stats.predict(lo)), index=df.index)
    max_ = pd.rolling_max(fitted, window, center=True)
    min_ = pd.rolling_min(fitted, window, center=True)

    df['fitted'] = fitted
    df['max'] = max_
    df['min'] = min_

    delta = max_ - fitted
    highs = df[delta<=0]
    delta = min_ - fitted
    lows = df[delta>=0]

    #globals()['fe_df'] = df
    #globals()['x'] = x
    #globals()['y'] = y
    #globals()['lows'] = lows
    #globals()['highs'] = highs

    return fitted, lows, highs

def main():
    from pyplot import _get_x, _resample
    from pyplot import retrieve_data, prepare_data
    df = retrieve_data()
    df = prepare_data(df)
    df = _resample(df, '5s')

    df = df[:'2015-12-01 09:46:00']
    x = _get_x(df)
    y = df['close']
    #macd_, signal = macd(y)
    lows, highs = find_extrema(x, y)
    print("lows:", lows)
    print("highs:", highs)

    #test()

if __name__ == '__main__':
    main()
