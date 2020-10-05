# Forecasting and Anomaly Detection with the Execd processor plugin

[statsmodels](https://www.statsmodels.org/stable/about.html#about-statsmodels) "is a Python module that provides classes and functions for the estimation of many different statistical models, as well as for conducting statistical tests, and statistical data exploration". The [statsmodels Holt's method](https://www.statsmodels.org/stable/examples/notebooks/generated/exponential_smoothing.html#Holt's-Method) is used to generate forecasts.  Holt's method is also known as double exponential smoothing. Double exponential smoothing is an exponentially weighted average of the trend and values of the data together. 

## Implementation 

`forecasting.py` and `forecasting2.py` are Python scripts that use Holt's method to generate forecasts and perform anomaly detection. The scripts follow the general procedure: 
- read points from STDIN. 
- parse from line protocol. 
- accumulate points in a minibatch. 
- continuously generate a forecast with each new point from STDIN.
- continuously calculate the residuals (or difference between the last point in the forecast and the current temperature value) with each new point in STDIN. This difference reflects the degree to which a point is anomalous.
- serialize points back to line protocol 
- return points over STDOUT. 

`forecasting.py` and `forecasting2.py` both implement a [damped version of Holt's method](https://www.statsmodels.org/stable/generated/statsmodels.tsa.holtwinters.Holt.html?highlight=damped%20holt). However they differ in one way:
- `forecasting.py` generates one forecasts with the exponential trend (or multiplicative) version of Holt's method. 
- `forecasting2.py` generates one forecasts with the linear trend (or additive) version of Holt's method.

`telegraf.conf` contains one Execd processor plugin configuration which runs `forecasting.py`. `telegraf2.conf` contains two Execd processor plugin configurations which run `forecasting.py` and `forecasting2.py`. `telegraf2.conf` also takes advantage of the namepass configuration option to execute [measurement filtering](https://docs.influxdata.com/telegraf/v1.15/administration/configuration/#measurement-filtering). 

*Note: You can also generate double exponential smoothing forecasts with the [holtWinters()](https://docs.influxdata.com/influxdb/v2.0/reference/flux/stdlib/built-in/transformations/holtwinters/) and [tasks](https://docs.influxdata.com/influxdb/v2.0/process-data/manage-tasks). However, this implementation allows users to take advantage of the languages and libraries they're already familiar with. Finally, the statsmodels Holt method has more algorithm configuration options than the InfluxDB holtWinters() function.* 

## Dataset Examination and Algorithm Selection

The line graphs below show the temperature data for the "have_v5" and "bv_1" beers respectively. 

haze_v5

![haze_v5](/img/haze_v5.png?raw=true)

bv_1

![bv_1](/img/bv_1.png?raw=true)

Through visual inspection we make the following observations: 
- Forecasts need to be generated almost immediately because spikes in beer temperature occur almost immediately. There simply isn't enough data to train a neural net, for example. 
- No clear seasonality is present, thereby excluding other classical forecasting algorithms (like ARIMA or ETS, for example) from consideration. 

Double exponential smoothing (or Holt's method) was selected to generate forecasts because the algorithm has the following advantages: 
- Little data (>10 points) is required to generate forecasts with Holt's method. 
- Seasonality isn't required. 
- It is computationally efficient. 
- It is an extremely accurate univariate time series forecasting method. 
