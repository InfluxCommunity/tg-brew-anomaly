# The simplest possible processor. It reads stdin and writes it to stdout.
import sys
import pandas as pd
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
import numpy as np
from numpy import nan as Nan
from line_protocol_parser import parse_line
from datetime import datetime, timedelta
import time as t 

minbatchlen = 10
maxbatchlen = 30
predictions = 10
threshold = 0.5

df = pd.DataFrame(columns = ['time','bv_1','haze_v5'])

for line in sys.stdin:
    line = line.rstrip('\n')  
    print(line)
    sys.stdout.flush()
    parsed = parse_line(line)
    brew = parsed['tags']['brew']
    field = parsed['fields']['temperature']
    time = parsed['time']
    time = pd.to_datetime(time, unit='ns', exact=True)
    if brew == 'bv_1':
        df = df.append({'time' : time, 'bv_1' : field, 'haze_v5' : Nan}, ignore_index = True) 
    else:
        df = df.append({'time' : time, 'bv_1' : Nan, 'haze_v5' : field}, ignore_index = True) 
    
    df = df[-maxbatchlen:]

    if len(df) >= minbatchlen:
        df2 = df.copy()
        currentlen = len(df2)
        df2 = df2.set_index("time")
        # Create 2d series for each field column
        n = len(df2.columns) 
        fcastdict = {}
        col = list(df2.columns)
        for i in range(0,n):
            s = df2.tail(currentlen).iloc[:,i]
            if all(np.isnan(s)):
                continue
            else: 
                s = s[~np.isnan(s)]
                lastvalue = s[-1]
            fit = Holt(s, damped_trend=False, initialization_method="estimated").fit(optimized=True)
            col = col[i]
            fcast = fit.forecast(predictions)
            if len(fcast) > 0 : 
                tag = col
                time = s.index[-1]
                for i in range(len(fcast)):
                    value = fcast[i]
                    time = time + timedelta(seconds = 1)
                    timestr = str(time.value)
                    lineout = "fcast" + "," + "brew" + "=" + tag + " temperature=" + str(value) + " " + timestr 
                    print(lineout)
            
                    #detect anomalies 
                    residual = abs(fcast[-1] - lastvalue) 
                    if residual > threshold:
                        anomalylineout = "anomaly" + "," + "brew" + "=" + tag + " temperature=" + str(residual) + " " + timestr 
                        print(anomalylineout)