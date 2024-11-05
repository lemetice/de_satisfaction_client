import datetime
import pendulum
import time
import pandas as pd
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from psycopg2 import OperationalError, connect
from airflow.hooks.postgres_hook import PostgresHook

POSTGRES_DB = 'kafka_data'
POSTGRES_USER = 'user'
POSTGRES_PASSWORD = 'password'
POSTGRES_HOST = '127.0.0.1'
POSTGRES_PORT = '5434'

def test_connection():
    try:
        # Initialize PostgresHook using the connection ID from the UI
        postgres_hook = PostgresHook(postgres_conn_id='hussen')
        
        # Get a connection object
        conn = postgres_hook.get_conn()

        # Open a cursor to execute a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # Simple query to test connection
        
        # If query is successful, print OK
        print("OK")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()

    except Exception as e:
        # If there's an error, print it
        print(f"Connection failed: {e}")

def setup_postgres():
    while True:
        try:
            conn = connect(
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT
            )
            print("Connexion PostgreSQL réussie.")
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stock_data_update (
                    symbol VARCHAR(10),
                    date DATE,
                    open NUMERIC,
                    high NUMERIC,
                    low NUMERIC,
                    close NUMERIC,
                    volume BIGINT,
                    daily_change_pct NUMERIC, 
                    highest_volume_day NUMERIC, 
                    last_10_days_avg_close NUMERIC,
                    PRIMARY KEY (symbol, date)
                );
            ''')
            conn.commit()
            cursor.close()
            return conn
        except OperationalError:
            print("Échec de connexion à PostgreSQL, nouvelle tentative dans 5 secondes...")
            time.sleep(5)

# Fonction pour extraire et transformer les données
def extract_transform_data():
    conn = setup_postgres()
    query = 'SELECT * FROM daily_stock_data;'
    data = pd.read_sql(query, conn)
    conn.close()

    data['daily_change_pct'] = ((data['close'] - data['open']) / data['open']) * 100
    data['highest_volume_day'] = data['volume'].max()
    data['last_10_days_avg_close'] = data['close'].tail(10).mean()

    return data

# Fonction de chargement des données dans PostgreSQL
def load_data(**context):
    conn = setup_postgres()
    cursor = conn.cursor()
    data = context['ti'].xcom_pull(task_ids='transform_data')

    for index, row in data.iterrows():
        cursor.execute('''
            INSERT INTO daily_stock_data_update (symbol, date, open, high, low, close, volume, daily_change_pct, highest_volume_day, last_10_days_avg_close)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, date) DO NOTHING;
        ''', (row['symbol'], row['date'], row['open'], row['high'], row['low'], row['close'], row['volume'],
              row['daily_change_pct'], row['highest_volume_day'], row['last_10_days_avg_close']))
    conn.commit()
    cursor.close()
    conn.close()

# Définition du DAG
with DAG(
    dag_id="daily_stock_data_pipeline",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2023, 10, 29, tz="UTC"),
    catchup=False,
) as dag:

    start_task = EmptyOperator(task_id="start")

    
    extract_transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=test_connection,
        # python_callable=extract_transform_data,
    )

    load_task = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
        provide_context=True,
    )

    end_task = EmptyOperator(task_id="end")
    start_task >> extract_transform_task >> load_task >> end_task
