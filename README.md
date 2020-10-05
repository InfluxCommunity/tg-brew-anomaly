# Machine Learning with Telegraf Execd processor plugin

This repo contains an example of how to use the [Telegraf Execd processor plugin](https://github.com/influxdata/telegraf/tree/master/plugins/processors/execd) to continuously generate forecasts and perform anomaly detection. The algorithm selection and implementation is described [here](/processors/README.md).

This repo accompanies Anais and Steven's Nov 2020 Influx Days talk. 

![](/img/dashboard.png?raw=true)

## About the Telegraf Execd processor plugin 
The Execd processor plugin runs an external program as a separate process and pipes metrics in to the process's STDIN and reads processed metrics from its STDOUT. The programs must accept [influx line protocol](https://docs.influxdata.com/influxdb/v2.0/reference/syntax/line-protocol/) on standard in (STDIN) and output metrics in influx line protocol to standard output (STDOUT).

Program output on standard error is mirrored to the telegraf log.

![](/img/execd-diagram.png?raw=true)

The [example.py](/processors/example/example.py) script is a simple example of using the Execd processor plugin to read STDIN and print the metrics to STDOUT with Python. 

## Dataset  

The dataset for this repo comes from Luke, an InfluxData Engineer, who uses InfluxDB to [monitor his beer brewing setup at home](github.com/lukebond/homebrew-webcam-temperature). The dataset contains temperature data for two beers, "haze_v5" and "bv_1", early in their fermentation processes. At this point in fermentation it's important that the temperature remain constant. 

## Objective 

The objective of this repo is to use the Execd processor plugin to help Luke maintain a constant beer temperature. Specifically, the goal is to:
1. Forecast the temperature so that Luke can better regulate the temperature of his beer as needed. 
2. Calculate the prediction residuals so that Luke can be alerted if his beer temperature exhibits anomalous behavior. 

## Dependencies

Telegraf >= 1.15.2
Go >= 1.14 (earlier may work)

You'll also want to setup an Influx Cloud account to get an Influx Cloud token
https://cloud2.influxdata.com

The `requirements.txt` file contains all of the Python dependencies for this repo. To install the Python dependencies in your virtual environment run:

    pip install -r requirements.txt 

## Setup Instructions

1. build the `restamp` binary

This program assigns new timestamps to the influx line protocol data in data/temps

    go build ./cmd/restamp
    ./restamp --help # should see usage.

build the `metric-replayer` custom input.

    go build ./cmd/metric-replayer

We'll test that out later.

2. assign the data current timestamps.

This will amend the temperature data with current timestamps and store it to a new file.
You may want to repeat this step later to replay the data with new, current, timestamps.

    gunzip --stdout ./data/temps.txt.gz | ./restamp -filename - > ./data/temps-stamped.txt

You can verify it worked with this command:

    head -n3 ./data/temps-stamped.txt

You should see 3 lines of temperature data that look something like this

    temperature,brew=haze_v5 temperature=18.8 1596602228666886000
    temperature,brew=haze_v5 temperature=18.8 1596602229666886000
    temperature,brew=haze_v5 temperature=18.9 1596602230666886000

3. Create a bucket called "brew"

Set up a cloud account at cloud2.influxdata.com if you haven't yet.

Create a bucket called "brew". Set retention to 30 days, or your preference.


## Running the Project

try once in test mode.

    telegraf --config ./telegraf.conf --test

If it appears to be working, make sure your influx environment variables are set and try

    telegraf --config ./telegraf.conf

