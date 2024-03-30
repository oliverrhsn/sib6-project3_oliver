import connection
import os
import sqlparse
import pandas as pd

if __name__ == '__main__':

    #connection to data source
    conf = connection.config('marketplace_prod')
    conn, engine = connection.get_conn(conf, 'DataSource')
    cursor = conn.cursor()

    #connection to dwh
    conf_dwh = connection.config('dwh')
    conn_dwh, engine_dwh = connection.get_conn(conf_dwh, 'DataWarehouse')
    cursor_dwh = conn_dwh.cursor()

    # get query string
    path_query = os.getcwd()+'/query/'
    query = sqlparse.format(
        open(path_query + 'query.sql', 'r').read(), strip_comments=True
    ).strip()
    dwh_design = sqlparse.format(
        open(path_query + 'dwh_design.sql', 'r').read(), strip_comments=True
    ).strip()

try:
    #get data from data source
    print('[INFO] service etl is running')
    df = pd.read_sql(query, engine)

    #create schema dwh
    cursor_dwh.execute(dwh_design)
    conn_dwh.commit()

    #ingest data to dwh
    df.to_sql(
        'dim_orders',
        engine_dwh,
        schema='oliver_dwh',
        if_exists='append',
        index=False
    )

    print('[INFO] service etl is success...')
except Exception as e:
    print(f"[INFO] service etl is failed")
    print(str(e))
