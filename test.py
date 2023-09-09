import psycopg2

username = 'vktinder2023'
password = 'NetologyVKTinder2023'
host = 'pgsql.ufa-net.ru'
port = "5432"
databasename = "vktinder2023"

connection = None
cursor = None

try:
   
    print(f"Попытка подключения с параметрами: user={username}, host={host}, port={port}, database={databasename}")

    
    connection = psycopg2.connect(
        user=username,
        password=password,
        host=host,
        port=port,
        database=databasename
    )

   
    cursor = connection.cursor()

    
    cursor.execute("SELECT version();")

    
    record = cursor.fetchone()
    print("Результат выполнения SQL-запроса:", record)

except psycopg2.OperationalError as e:
    print("Ошибка при подключении к базе данных:", e)
    print("Error details:", e.pgerror)
    print("Error code:", e.pgcode)
    print("Error severity:", e.diag.severity)
    print("Error message:", e.diag.message_primary)
except psycopg2.DatabaseError as e:
    print("Ошибка при работе с базой данных:", e)
except Exception as e:
    print("Произошла непредвиденная ошибка:", e)

finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()



