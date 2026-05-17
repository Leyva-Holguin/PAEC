from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import math

app = Flask(__name__)
app.secret_key = ''

USUARIO = "yo"
CONTRASEÑA = "PROYECTO2026cetis"

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USUARIO}:{CONTRASEÑA}@localhost/imc_calculadora'
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
@app.route('/')
def index():
    return render_template('imc.html', datos_usuario=None, resultado_imc=None)

@app.route('/cal_imc', methods=['POST'])
def cal_imc():
    resultado = None
    try:
        nombre = request.form.get('nombre', 'Usuario')
        edad = request.form.get('edad', type=int)
        peso = float(request.form.get('peso_imc'))
        altura_cm = float(request.form.get('altura_imc'))
        if peso <= 0 or altura_cm <= 0:
            resultado = 'Por favor ingresa valores validos (positivos)'
            return render_template('imc.html', datos_usuario=None, resultado_imc=resultado)
        altura_m = altura_cm / 100
        imc = peso / (altura_m ** 2)
        if imc < 18.5:
            clasificacion = "Bajo peso"
        elif imc < 25:
            clasificacion = "Peso normal"
        elif imc < 30:
            clasificacion = "Sobrepeso"
        elif imc < 35:
            clasificacion = "Obesidad grado I"
        elif imc < 40:
            clasificacion = "Obesidad grado II"
        else:
            clasificacion = "Obesidad grado III"
        resultado = f'{nombre}, tu IMC es: {imc:.1f} - {clasificacion}'
        nuevo_registro = RegistroIMC(
            nombre=nombre,
            edad=edad if edad else None,
            peso=peso,
            altura=altura_m,
            imc=round(imc, 2),
            clasificacion=clasificacion
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        flash(f'Calculo guardado exitosamente', 'success')
    except (ValueError, TypeError):
        resultado = 'Por favor ingresa valores numericos validos'
    except ZeroDivisionError:
        resultado = 'La altura no puede ser 0'
    return render_template('imc.html', datos_usuario=None, resultado_imc=resultado)

@app.route('/historial')
def historial():
    query = request.args.get('q', '')
    
    if query:
        registros = RegistroIMC.query.filter(RegistroIMC.nombre.contains(query)).order_by(RegistroIMC.fecha_registro.desc()).all()
    else:
        registros = RegistroIMC.query.order_by(RegistroIMC.fecha_registro.desc()).all()
    total_registros = len(registros)
    if total_registros > 0:
        imc_promedio = round(sum(r.imc for r in registros) / total_registros, 2)
        peso_minimo = min(r.peso for r in registros)
        peso_maximo = max(r.peso for r in registros)
    else:
        imc_promedio = 0
        peso_minimo = 0
        peso_maximo = 0
    bajo_peso = len([r for r in registros if r.clasificacion == 'Bajo peso'])
    peso_normal = len([r for r in registros if r.clasificacion == 'Peso normal'])
    sobrepeso = len([r for r in registros if r.clasificacion == 'Sobrepeso'])
    obesidad = len([r for r in registros if 'Obesidad' in r.clasificacion])
    distribucion = []
    if bajo_peso > 0:
        porcentaje = round((bajo_peso / total_registros) * 100, 1) if total_registros > 0 else 0
        distribucion.append({
            'clasificacion': 'Bajo peso',
            'cantidad': bajo_peso,
            'porcentaje': porcentaje
        })
    if peso_normal > 0:
        porcentaje = round((peso_normal / total_registros) * 100, 1) if total_registros > 0 else 0
        distribucion.append({
            'clasificacion': 'Peso normal',
            'cantidad': peso_normal,
            'porcentaje': porcentaje
        })
    if sobrepeso > 0:
        porcentaje = round((sobrepeso / total_registros) * 100, 1) if total_registros > 0 else 0
        distribucion.append({
            'clasificacion': 'Sobrepeso',
            'cantidad': sobrepeso,
            'porcentaje': porcentaje
        })
    if obesidad > 0:
        porcentaje = round((obesidad / total_registros) * 100, 1) if total_registros > 0 else 0
        distribucion.append({
            'clasificacion': 'Obesidad',
            'cantidad': obesidad,
            'porcentaje': porcentaje
        })
    return render_template('historial.html',registros=registros,total_registros=total_registros,imc_promedio=imc_promedio,peso_minimo=peso_minimo,peso_maximo=peso_maximo,distribucion=distribucion)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    registro = RegistroIMC.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    flash('Registro eliminado correctamente', 'success')
    return redirect(url_for('historial'))

with app.app_context():
    db.create_all()
    print("Base de datos lista")

if __name__ == '__main__':
    print("Servidor en http://localhost:5000")
    app.run(debug=True)