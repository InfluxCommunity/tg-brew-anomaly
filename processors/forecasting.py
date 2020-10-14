# Parses line protocol data from stdin and uses statsmodels' Holt to make a forecast. 
# Uses the multiplicative version of Holt's method. 
# Residuals are also calculated.  
import sys
import pandas as pd
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
import numpy as np
from numpy import nan as Nan
from line_protocol_parser import parse_line
from datetime import datetime, timedelta
import time as t 

#A minibatch is created each time a new point is written to stdin. 
minbatchlen = 10
maxbatchlen = 120
predictions = 40
threshold = 0.5

timestamps = []
bv_1 = []
haze_v5 = []
for line in sys.stdin:
    line = line.rstrip('\n')  
    print(line)
    #lines are flushed after each loop
    sys.stdout.flush()
    #line protocol is parsed and added to the minibatch 
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


    #When the minimum batch length is reached then forecasts are made. 
    if len(timestamps) >= minbatchlen and len(timestamps) == len(haze_v5) and len(haze_v5) == len(bv_1):
        d={'haze_v5': haze_v5, 'bv_1' : bv_1}
        #Create a DataFrame and specify the timestamp index frequency for the statsmodels forecast. 
        df = pd.DataFrame(data=d, index=pd.DatetimeIndex(timestamps, freq='s'))
        currentlen = len(df)
        n = len(df.columns) 
        fcastdict = {}
        col = list(df.columns)
        for i in range(0,n):
            s = df.tail(currentlen).iloc[:,i]
            #If the data is irregular or values are missing, continue until the timeseries is regular again. 
            if all(np.isnan(s)):
                continue
            else: 
                s = s[~np.isnan(s)]
                lastvalue = s[-1]
            #Use the Holt function to fit the data.  
            fit = Holt(s,damped_trend=True,initialization_method="estimated").fit(optimized=True)
            col = col[i]
            #Make a forecast with the forecast method. 
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
            
                    #Calculate residuals  
                    residual = abs(fcast[-1] - lastvalue) 
                    anomalylineout = "anomaly" + "," + "brew" + "=" + tag + " temperature=" + str(residual) + " " + timestr 
                    print(anomalylineout)