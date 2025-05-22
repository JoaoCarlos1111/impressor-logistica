
import os
import platform
from flask import Flask, render_template, request, jsonify, session
import requests
from dotenv import load_dotenv

# Sistema de impressão específico para cada OS
if platform.system() == 'Windows':
    import win32print
    def get_printers():
        return [printer[2] for printer in win32print.EnumPrinters(2)]
        
    def print_document(printer_name, file_path):
        try:
            handle = win32print.OpenPrinter(printer_name)
            win32print.StartDocPrinter(handle, 1, ("document", None, "RAW"))
            with open(file_path, 'rb') as f:
                data = f.read()
            win32print.WritePrinter(handle, data)
            win32print.EndDocPrinter(handle)
            win32print.ClosePrinter(handle)
            return True
        except Exception as e:
            print(f"Error printing: {e}")
            return False
else:
    import cups
    def get_printers():
        conn = cups.Connection()
        printers = conn.getPrinters()
        return list(printers.keys())
        
    def print_document(printer_name, file_path):
        try:
            conn = cups.Connection()
            conn.printFile(printer_name, file_path, "Document", {})
            return True
        except Exception as e:
            print(f"Error printing: {e}")
            return False

app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL')

def get_print_queue():
    headers = {'Authorization': f'Bearer {API_TOKEN}'}
    response = requests.get(f"{API_BASE_URL}/print-queue", headers=headers)
    return response.json() if response.status_code == 200 else []

def mark_as_printed(case_id):
    headers = {'Authorization': f'Bearer {API_TOKEN}'}
    response = requests.post(
        f"{API_BASE_URL}/cases/{case_id}/mark-printed",
        headers=headers
    )
    return response.status_code == 200

@app.route('/')
def index():
    if not session.get('authenticated'):
        return render_template('login.html')
    printers = get_printers()
    cases = get_print_queue()
    return render_template('index.html', printers=printers, cases=cases)

@app.route('/login', methods=['POST'])
def login():
    token = request.form.get('token')
    if token:
        session['authenticated'] = True
        global API_TOKEN
        API_TOKEN = token
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

@app.route('/view/<case_id>')
def view_case(case_id):
    if not session.get('authenticated'):
        return render_template('login.html')
    
    cases = get_print_queue()
    case = next((c for c in cases if c['id'] == case_id), None)
    
    if not case:
        return "Caso não encontrado", 404
        
    return render_template('view.html', case=case)

@app.route('/print', methods=['POST'])
def print_documents():
    if not session.get('authenticated'):
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    printer_name = request.form.get('printer')
    case_ids = request.form.getlist('cases[]')
    results = []
    
    for case_id in case_ids:
        case = next((c for c in get_print_queue() if c['id'] == case_id), None)
        if case:
            success = all([
                print_document(printer_name, doc) 
                for doc in [case['notification_pdf'], case['power_of_attorney_pdf'], case['ad_pdf']]
            ])
            if success:
                mark_as_printed(case_id)
            results.append({
                'case_id': case_id,
                'success': success
            })
    
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
