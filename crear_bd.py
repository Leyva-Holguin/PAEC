import pymysql
from getpass import getpass

host = 'localhost'
user = "yo"
password = "PROYECTO2026cetis"

try:
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password
    )  
    cursor = connection.cursor()  
    cursor.execute("CREATE DATABASE IF NOT EXISTS imc_calculadora")
    print("Base de datos 'imc_calculadora' creada exitosamente")
    cursor.execute(f"GRANT ALL PRIVILEGES ON imc_calculadora.* TO '{user}'@'localhost'")
    cursor.execute("FLUSH PRIVILEGES")
    print("Permisos asignados correctamente")
    cursor.close()
    connection.close()
    print("\n ¡Todo listo! Ahora puedes ejecutar")
except Exception as e:
    print(f"Error: {e}")