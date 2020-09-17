# The simplest possible processor. It reads stdin and writes it to stdout.
import sys
import pandas as pd
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
import numpy as np
from numpy import nan as Nan
from line_protocol_parser import parse_line
from datetime import datetime
import time as t 

fileName = "metrics.txt"
minibatchlen = 10
predictions = 1

df = pd.DataFrame(columns = ['time','bv_1','haze_v5'])
for line in open(fileName):
    line.rstrip('\n')
    parsed = parse_line(line)
    brew = parsed['tags']['brew']
    field = parsed['fields']['temperature']
    time = parsed['time']
    time = pd.to_datetime(time, unit='ns')
    if brew == 'bv_1':
        df = df.append({'time' : time, 'bv_1' : field, 'haze_v5' : Nan}, ignore_index = True) 
    else:
        df = df.append({'time' : time, 'bv_1' : Nan, 'haze_v5' : field}, ignore_index = True) 
    
    df = df[-minibatchlen:]
    # print(df)
    
if len(df) == minibatchlen:
    print("minibatch filled")
    df = df.set_index("time")
    # Create 2d series for each field column
    n = len(df.columns) 
    print(n)
    fcastdict = {}
    col = list(df.columns)
    for i in range(0,n):
        s = df.tail(minibatchlen).iloc[:,i]
        if all(np.isnan(s)):
            continue
        else: 
            s = s[~np.isnan(s)]
        fit = SimpleExpSmoothing(s, initialization_method="heuristic").fit(optimized=True)
        col = col[i]
        fcast = fit.forecast(predictions)
        tag = col
        value = fcast[0]
        time = fcast.index[0]
        print(fcast)
        # print(fcast.index[0])

        lineout = "fcast" + "," + "brew" + "=" + tag + " temperature=" + str(value) + " " + str(int(t.mktime(time.timetuple()))) + "000000000"
        
        print(lineout)



