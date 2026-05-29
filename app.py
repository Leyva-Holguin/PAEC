from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'El_tipo_que_se_rie_mientras_come_un_flan'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'imc.db')
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
class RegistroSueno(db.Model):
    __tablename__ = 'registros_sueno'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    horas_sueno = db.Column(db.Float, nullable=False)
    fc_reposo = db.Column(db.Integer, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

def calcular_imc(peso, altura_cm):
    altura_m = altura_cm / 100
    imc = peso / (altura_m ** 2)
    if imc < 18.5:
        clasificacion = "Bajo peso"
        color = "warning"
    elif imc < 25:
        clasificacion = "Peso normal"
        color = "success"
    elif imc < 30:
        clasificacion = "Sobrepeso"
        color = "warning"
    elif imc < 35:
        clasificacion = "Obesidad grado I"
        color = "danger"
    elif imc < 40:
        clasificacion = "Obesidad grado II"
        color = "danger"
    else:
        clasificacion = "Obesidad grado III"
        color = "danger"
    return round(imc, 2), clasificacion, color

@app.route('/')
def index():
    return render_template('info.html')

@app.route('/quimica')
def quimica():
    return render_template('quimica.html')

@app.route('/conciencia')
def conciencia():
    return render_template('conciencia.html')

@app.route('/matematicas')
def matematicas():
    return render_template('matematicas.html')

@app.route('/ritmo_cardiaco')
def ritmo_cardiaco():
    registros = RegistroSueno.query.order_by(RegistroSueno.fecha_registro.desc()).all()
    grafica = grafica_sueno()
    return render_template('ritmo_cardiaco.html', registros=registros, grafica=grafica)

@app.route('/imc')
def imc_page():
    return render_template('imc.html', resultado=None)

@app.route('/calcular_imc', methods=['POST'])
def calcular_imc_route():
    try:
        nombre = request.form.get('nombre', 'Usuario').strip()
        if not nombre:
            nombre = "Usuario"   
        edad_str = request.form.get('edad')
        edad = int(edad_str) if edad_str and edad_str.strip() else None
        peso = float(request.form.get('peso'))
        altura_cm = float(request.form.get('altura'))
        if peso <= 0 or peso > 500:
            flash('El peso debe ser entre 1 y 500 kg', 'danger')
            return redirect(url_for('imc_page'))
        if altura_cm <= 0 or altura_cm > 300:
            flash('La altura debe ser entre 1 y 300 cm', 'danger')
            return redirect(url_for('imc_page'))
        if edad and (edad < 1 or edad > 120):
            flash('La edad debe ser entre 1 y 120 años', 'danger')
            return redirect(url_for('imc_page'))
        imc, clasificacion, color = calcular_imc(peso, altura_cm)
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
        resultado = {
            'nombre': nombre,
            'edad': edad,
            'peso': peso,
            'altura': altura_cm,
            'imc': imc,
            'clasificacion': clasificacion,
            'color': color,
            'es_menor': edad is not None and edad < 18
        }
        flash(f'¡Cálculo completado! Tu IMC es {imc}', 'success')
        return render_template('imc.html', resultado=resultado)
    except ValueError:
        flash('Por favor ingresa valores numéricos válidos', 'danger')
        return redirect(url_for('imc_page'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('imc_page'))

@app.route('/historial')
def historial():
    registros = RegistroIMC.query.order_by(RegistroIMC.fecha_registro.asc()).all()
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
    return render_template('historial.html',registros=registros,total_registros=total_registros,imc_promedio=imc_promedio,peso_minimo=peso_minimo,peso_maximo=peso_maximo,distribucion=distribucion)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    registro = RegistroIMC.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    flash('Registro eliminado correctamente', 'success')
    return redirect(url_for('historial'))

@app.route('/guardar_sueno', methods=['POST'])
def guardar_sueno():
    try:
        nombre = request.form.get('nombre', 'Usuario').strip()
        if not nombre:
            nombre = "Usuario"
        horas_sueno = float(request.form.get('horas_sueno'))
        fc_reposo = int(request.form.get('fc_reposo'))
        if horas_sueno < 0 or horas_sueno > 24:
            flash('Las horas de sueño deben ser entre 0 y 24', 'danger')
            return redirect(url_for('ritmo_cardiaco'))
        if fc_reposo < 30 or fc_reposo > 200:
            flash('La frecuencia cardíaca debe ser entre 30 y 200 lpm', 'danger')
            return redirect(url_for('ritmo_cardiaco'))
        nuevo_registro = RegistroSueno(
            nombre=nombre,
            horas_sueno=horas_sueno,
            fc_reposo=fc_reposo
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        flash(f'¡Registro guardado!', 'success')
        return redirect(url_for('ritmo_cardiaco'))
        
    except ValueError:
        flash('Por favor ingresa valores numéricos válidos', 'danger')
        return redirect(url_for('ritmo_cardiaco'))

@app.route('/eliminar_sueno/<int:id>')
def eliminar_sueno(id):
    registro = RegistroSueno.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    flash('Registro eliminado correctamente', 'success')
    return redirect(url_for('ritmo_cardiaco'))

def grafica_sueno():
    registros = RegistroSueno.query.order_by(RegistroSueno.fecha_registro.asc()).all()
    if len(registros) < 2:
        return None
    horas = [r.horas_sueno for r in registros]
    fc = [r.fc_reposo for r in registros]
    plt.figure(figsize=(10, 6))
    plt.scatter(horas, fc, color='#86B049', s=120, alpha=0.7, edgecolors='white', linewidth=2)
    plt.xlabel('Horas de sueño (hoy)', fontsize=12)
    plt.ylabel('Frecuencia cardíaca en reposo (lpm)', fontsize=12)
    plt.title('Relación entre horas de sueño y frecuencia cardíaca', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

@app.route('/registros_sueno_json')
def registros_sueno_json():
    registros = RegistroSueno.query.order_by(RegistroSueno.fecha_registro.desc()).limit(20).all()
    data = [{
        'id': r.id,
        'nombre': r.nombre,
        'horas_sueno': r.horas_sueno,
        'fc_reposo': r.fc_reposo,
        'fecha': r.fecha_registro.strftime('%d/%m/%Y %H:%M')
    } for r in registros]
    return jsonify(data)

with app.app_context():
    db.create_all()
    print("✓ Base de datos SQLite creada/verificada: imc.db")
    print("✓ Tablas: registros_imc, registros_sueno")

if __name__ == '__main__':
    app.run(debug=True)