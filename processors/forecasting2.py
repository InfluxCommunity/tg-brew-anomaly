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
maxbatchlen = 120
predictions = 20
threshold = 0.5

# df = pd.DataFrame(columns = ['time','bv_1','haze_v5'])
timestamps = []
bv_1 = []
haze_v5 = []
for line in sys.stdin:
    line = line.rstrip('\n')  
    print(line)
    sys.stdout.flush()
    parsed = parse_line(line)
    brew = parsed['tags']['brew']
    field = parsed['fields']['temperature']
    time = parsed['time']
    time = pd.to_datetime(time, unit='ns', exact=True)
    timestamps.append(time)
    if brew == 'bv_1':
        bv_1.append(field)
        haze_v5.append(Nan)
    else:
        bv_1.append(Nan)
        haze_v5.append(field)
    timestamps = timestamps[-maxbatchlen:]
    bv_1 = bv_1[-maxbatchlen:]
    haze_v5 = haze_v5[-maxbatchlen:]

    if len(timestamps) >= minbatchlen and len(timestamps) == len(haze_v5) and len(haze_v5) == len(bv_1):
        d={'haze_v5': haze_v5, 'bv_1' : bv_1}
        df = pd.DataFrame(data=d, index=pd.DatetimeIndex(timestamps, freq='s'))
        currentlen = len(df)
        # Create 2d series for each field column
        n = len(df.columns) 
        fcastdict = {}
        col = list(df.columns)
        for i in range(0,n):
            s = df.tail(currentlen).iloc[:,i]
            if all(np.isnan(s)):
                continue
            else: 
                s = s[~np.isnan(s)]
                lastvalue = s[-1]
            fit = Holt(s,damped_trend=True,initialization_method="estimated").fit(optimized=True)
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