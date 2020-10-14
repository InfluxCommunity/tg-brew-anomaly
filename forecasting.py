def query():
    try:
        # Gather authentication parameters
        bucket = "brew"
        token = $INFLUX_TOKEN
        org = $ORG
        url = $URL
        # Initialize clients
        client = InfluxDBClient(url=url, token=token, org=org)
        query_api = client.query_api()
        # Prepare data with Flux for a pandas DataFrame. 
        query = 'from(bucket:"brew")\
                |> range(start: -30d)\
                |> filter(fn: (r) => r["_measurement"] == "temperature")\
                |> keep(columns:["_time", "_value", "brew"])\
                |> pivot(rowKey:["_time"], columnKey: ["brew"], valueColumn: "_value")'
        # Query Influx and return a pandas DataFrame
        query_api = client.query_api()
        data_frame = query_api.query_data_frame(query=query) 
    except ValueError:
        print('query error')
    return data_frame

def prepare_data_frame(df):
    # Prepare DataFrame to use forecasting libraries. Set the "_time" column as the index. 
    df = df.set_index("_time")
    df = df.drop(columns=["result", "table"])


def forecast(past,future):
    # Create 2d series for each field column
    n = len(df.columns) 
    fcastdict = {}
    col = list(df.columns)
    for i in range(0,n):
        s = df.tail(past).iloc[:,i]
        if all(np.isnan(s)):
            continue
        else: 
            s = s[~np.isnan(s)]
        fit = SimpleExpSmoothing(s, initialization_method="heuristic").fit(optimized=True)
        col = col[i]
        fcast = fit.forecast(future)
        fcastdict[col]=fcast
    fcastdf = pd.DataFrame.from_dict(fcastdict)
    return fcastdf

def write(record):
    try:
        _write_client = client.write_api()
        _write_client.write(bucket, record=record, data_frame_measurement_name='fcast')
    except ValueError:
        print('write error')

def main():
    df = query()
    df = prepare_data_frame(df)
    fcastdf = forecast(100,10)
    return fcastdf
#     write(fcastdf)

if __name__ == '__main__':
    main()