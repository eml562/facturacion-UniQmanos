from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facturas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para los clientes
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)

# Modelo para las facturas
class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    fecha = db.Column(db.String(100), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    retencion = db.Column(db.Float, nullable=False)

# Ruta para la página principal
@app.route('/')
def index():
    clientes = Cliente.query.all()
    return render_template('index.html', clientes=clientes)

# Ruta para registrar clientes
@app.route('/registrar_cliente', methods=['POST'])
def registrar_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        nuevo_cliente = Cliente(nombre=nombre, direccion=direccion)
        db.session.add(nuevo_cliente)
        db.session.commit()
        return redirect(url_for('index'))

# Ruta para generar factura
@app.route('/generar_factura/<int:cliente_id>', methods=['POST'])
def generar_factura(cliente_id):
    if request.method == 'POST':
        fecha = request.form['fecha']
        monto = float(request.form['monto'])
        retencion = monto * 0.15  # 15% de retención
        nueva_factura = Factura(cliente_id=cliente_id, fecha=fecha, monto=monto, retencion=retencion)
        db.session.add(nueva_factura)
        db.session.commit()
        return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()  # Crear tablas en la base de datos
    app.run(debug=True)
