from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_123'

DATOS_FREESQL = {
    'host': 'sql3.freesqldatabase.com',
    'user': 'sql3827338',
    'password': 'kbTclCqvJj',
    'database': 'sql3827338'
}

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DATOS_FREESQL['user']}:{DATOS_FREESQL['password']}@{DATOS_FREESQL['host']}/{DATOS_FREESQL['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class RegistroIMC(db.Model):
    __tablename__ = 'registros_imc'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer)
    peso = db.Column(db.Float, nullable=False)
    altura = db.Column(db.Float, nullable=False)
    imc = db.Column(db.Float, nullable=False)
    clasificacion = db.Column(db.String(50))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

def calcular_imc(peso, altura_cm):
    altura_m = altura_cm / 100
    imc = peso / (altura_m ** 2)
    
    if imc < 18.5:
        return round(imc, 2), "Bajo peso"
    elif imc < 25:
        return round(imc, 2), "Peso normal"
    elif imc < 30:
        return round(imc, 2), "Sobrepeso"
    elif imc < 35:
        return round(imc, 2), "Obesidad grado I"
    elif imc < 40:
        return round(imc, 2), "Obesidad grado II"
    else:
        return round(imc, 2), "Obesidad grado III"

@app.route('/')
def index():
    return render_template('imc.html', datos_usuario=None, resultado_imc=None)

@app.route('/cal_imc', methods=['POST'])
def cal_imc():
    try:
        nombre = request.form.get('nombre', 'Usuario')
        edad = request.form.get('edad', type=int)
        peso = float(request.form.get('peso_imc'))
        altura_cm = float(request.form.get('altura_imc'))
        
        imc, clasificacion = calcular_imc(peso, altura_cm)
        
        nuevo_registro = RegistroIMC(
            nombre=nombre,
            edad=edad,
            peso=peso,
            altura=altura_cm / 100,
            imc=imc,
            clasificacion=clasificacion
        )
        
        db.session.add(nuevo_registro)
        db.session.commit()
        
        flash(f'{nombre}, tu IMC es: {imc} - {clasificacion}', 'success')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/historial')
def historial():
    registros = RegistroIMC.query.order_by(RegistroIMC.fecha_registro.desc()).all()
    
    total_registros = len(registros)
    
    if total_registros > 0:
        imc_promedio = round(sum(r.imc for r in registros) / total_registros, 2)
        peso_minimo = min(r.peso for r in registros)
        peso_maximo = max(r.peso for r in registros)
        
        bajo_peso = len([r for r in registros if r.clasificacion == 'Bajo peso'])
        peso_normal = len([r for r in registros if r.clasificacion == 'Peso normal'])
        sobrepeso = len([r for r in registros if r.clasificacion == 'Sobrepeso'])
        obesidad = len([r for r in registros if 'Obesidad' in r.clasificacion])
        
        distribucion = []
        
        if bajo_peso > 0:
            distribucion.append({'clasificacion': 'Bajo peso', 'cantidad': bajo_peso, 'porcentaje': round(bajo_peso / total_registros * 100, 1)})
        if peso_normal > 0:
            distribucion.append({'clasificacion': 'Peso normal', 'cantidad': peso_normal, 'porcentaje': round(peso_normal / total_registros * 100, 1)})
        if sobrepeso > 0:
            distribucion.append({'clasificacion': 'Sobrepeso', 'cantidad': sobrepeso, 'porcentaje': round(sobrepeso / total_registros * 100, 1)})
        if obesidad > 0:
            distribucion.append({'clasificacion': 'Obesidad', 'cantidad': obesidad, 'porcentaje': round(obesidad / total_registros * 100, 1)})
    else:
        imc_promedio = 0
        peso_minimo = 0
        peso_maximo = 0
        distribucion = []
    
    return render_template('historial.html',
                         registros=registros,
                         total_registros=total_registros,
                         imc_promedio=imc_promedio,
                         peso_minimo=peso_minimo,
                         peso_maximo=peso_maximo,
                         distribucion=distribucion)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    registro = RegistroIMC.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    flash('Registro eliminado', 'success')
    return redirect(url_for('historial'))

with app.app_context():
    db.create_all()
    print("Conectado a FreeSQLDatabase")

if __name__ == '__main__':
    print("Servidor en http://localhost:5000")
    app.run(debug=True)