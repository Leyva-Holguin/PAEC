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
    flash('Registro eliminado correctamente', 'success')
    return redirect(url_for('historial'))

with app.app_context():
    db.create_all()
    print("✓ Conectado a FreeSQLDatabase")

if __name__ == '__main__':
    app.run(debug=True)