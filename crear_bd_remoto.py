import pymysql


host = 'sql3.freesqldatabase.com'
user = 'sql3827338'
password = 'kbTclCqvJj'
database ='sql3827338'
try:
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros_imc (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            edad INT,
            peso FLOAT NOT NULL,
            altura FLOAT NOT NULL,
            imc FLOAT NOT NULL,
            clasificacion VARCHAR(50),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("Tabla creada correctamente")
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")