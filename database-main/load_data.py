import pyodbc
import os
from dotenv import load_dotenv

def connect_to_sql_server():
    # Cargar las variables de entorno
    load_dotenv(dotenv_path='C:/Users/leoal/Desktop/databasework/database-main/.env')
    
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    user = os.getenv("SQL_USER")
    password = os.getenv("SQL_PASSWORD")
    
    if not server or not database or not user or not password:
        print("Environment variables are not loaded properly.")
        print(f"SQL_SERVER: {server}, SQL_DATABASE: {database}, SQL_USER: {user}, SQL_PASSWORD: {password}")
        return None
    
    connection_string = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={user};'
        f'PWD={password}'
    )
    print("Connection String:", connection_string)  # Agregar este print para verificar el connection string
    return pyodbc.connect(connection_string)
