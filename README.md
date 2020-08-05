# tg-brew-anomaly

Anais and Steven's Nov 2020 influx days talk. WIP.

![](https://github.com/influxdata/tg-brew-anomaly/blob/master/dashboard.png?raw=true)

## dependencies

Telegraf >= 1.15.2
Go >= 1.14 (earlier may work)

You'll also want to setup an Influx Cloud account to get an Influx Cloud token
https://cloud2.influxdata.com

## setup instructions

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

    tar -Oxf data/temps.tar.gz | ./restamp -filename - > ./data/temps-stamped.txt

You can verify it worked with this command:

    head -n3 ./data/temps-stamped.txt

You should see 3 lines of temperature data that look something like this

    temperature,brew=haze_v5 temperature=18.8 1596602228666886000
    temperature,brew=haze_v5 temperature=18.8 1596602229666886000
    temperature,brew=haze_v5 temperature=18.9 1596602230666886000

3. Create a bucket called "brew"

Set up a cloud account at cloud2.influxdata.com if you haven't yet.

Create a bucket called "brew". Set retention to 30 days, or your preference.

## Running Project

try once in test mode.

    telegraf --config ./telegraf.conf --test

If it appears to be working, make sure your influx environment variables are set and try

    telegraf --config ./telegraf.conf