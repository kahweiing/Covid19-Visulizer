from sqlalchemy import create_engine
from pandas.io import sql
import pandas as pd

def init_engine():
    engine = create_engine('mysql://admin:ict1002123@ict1002.ccn4uqz8mkb5.us-east-2.rds.amazonaws.com/ict1002')
    return engine

def execute_drop(finalname):
    sql.execute('DROP TABLE IF EXISTS %s' % finalname, init_engine())

def execute_select(finalname):
    db_engine = init_engine()
    return pd.read_sql("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='ict1002' AND TABLE_NAME='" + finalname + "'", db_engine.connect())