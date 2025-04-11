
from flask import Flask, render_template_string, request, send_file, redirect, url_for
from fpdf import FPDF
import os
from datetime import datetime

app = Flask(__name__)
clients = {}

INVOICE_FOLDER = "invoices"
os.makedirs(INVOICE_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!doctype html>
<title>Facturación Médica</title>
<h2>Registrar Cliente</h2>
<form method=post action="/add_client">
  Nombre: <input type=text name=name required>
  <br>
  DNI: <input type=text name=dni required>
  <br>
  Dirección: <input type=text name=address required>
  <br><br>
  <input type=submit value=Registrar>
</form>

<h2>Generar Factura</h2>
<form method=post action="/generate_invoice">
  Cliente:
  <select name=client required>
    {% for dni, data in clients.items() %}
      <option value="{{ dni }}">{{ data['name'] }} ({{ dni }})</option>
    {% endfor %}
  </select>
  <br>
  Descripción: <input type=text name=description required>
  <br>
  Importe (€): <input type=number name=amount step="0.01" required>
  <br><br>
  <input type=submit value="Generar Factura">
</form>

<h2>Facturas Generadas</h2>
<ul>
{% for file in files %}
  <li><a href="/invoices/{{ file }}">{{ file }}</a></li>
{% endfor %}
</ul>
"""

@app.route("/")
def index():
    files = os.listdir(INVOICE_FOLDER)
    return render_template_string(HTML_TEMPLATE, clients=clients, files=files)

@app.route("/add_client", methods=["POST"])
def add_client():
    name = request.form["name"]
    dni = request.form["dni"]
    address = request.form["address"]
    clients[dni] = {"name": name, "address": address}
    return redirect(url_for('index'))

@app.route("/generate_invoice", methods=["POST"])
def generate_invoice():
    dni = request.form["client"]
    description = request.form["description"]
    amount = float(request.form["amount"])
    client = clients[dni]

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"Factura_{client['name'].replace(' ', '_')}_{date_str}.pdf"
    filepath = os.path.join(INVOICE_FOLDER, filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Factura Médica", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Fecha: {date_str}", ln=True)
    pdf.cell(200, 10, txt=f"Cliente: {client['name']}", ln=True)
    pdf.cell(200, 10, txt=f"DNI: {dni}", ln=True)
    pdf.cell(200, 10, txt=f"Dirección: {client['address']}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Concepto: {description}", ln=True)
    pdf.cell(200, 10, txt=f"Importe bruto: {amount:.2f} €", ln=True)
    irpf = amount * 0.15
    total = amount - irpf
    pdf.cell(200, 10, txt=f"Retención IRPF (15%): -{irpf:.2f} €", ln=True)
    pdf.cell(200, 10, txt=f"Importe neto: {total:.2f} €", ln=True)

    pdf.output(filepath)
    return redirect(url_for('index'))

@app.route("/invoices/<filename>")
def get_invoice(filename):
    return send_file(os.path.join(INVOICE_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
  app.run(port=8080, debug=True)
