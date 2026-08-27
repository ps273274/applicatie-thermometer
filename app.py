import sqlite3
import datetime
import os
import sys
from flask import Flask, render_template, request, redirect, session, jsonify
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecret"

# Dit is het pad BINNEN de container. 
# Via docker-compose is dit gekoppeld aan jouw I-schijf.
DB_PATH = "/app/database.db"

# ------- Debug Functie (Voor in je terminal) -------
def debug_log(bericht):
    """Print berichten direct naar de console zodat je ze ziet."""
    tijd = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[DEBUG {tijd}] {bericht}", file=sys.stdout, flush=True)

# ------- Database Helper -------
def query_db(query, params=(), one=False):
    try:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query, params)
        rv = cur.fetchall()
        con.commit()
        con.close()
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        debug_log(f"DATABASE ERROR: {e}")
        return []

# ------- Login Decorator -------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# ------- Routes -------
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/monitoring')
@login_required
def monitoring():
    return render_template('monitoring.html')

# 1. De HTML Pagina voor Logs
@app.route('/logs')
@login_required
def logs():
    return render_template('logs.html')

# 2. De LIVE API (Hier haalt Javascript de data vandaan)
@app.route('/api/logs')
@login_required
def api_logs():
    search_query = request.args.get('q')
    if search_query:
        data = query_db("SELECT * FROM logs WHERE melding LIKE ? ORDER BY id DESC", ('%' + search_query + '%',))
    else:
        # Haal de nieuwste 50 logs op
        data = query_db("SELECT * FROM logs ORDER BY id DESC LIMIT 50")
    
    # Zet database rijen om naar JSON voor de browser
    return jsonify([dict(row) for row in data])

# 3. De WEBHOOK (Hier komt Uptime Kuma binnen)
@app.route('/webhook', methods=['POST'])
def webhook():
    debug_log("--- NIEUWE MELDING ONTVANGEN ---")
    
    try:
        # Stap 1: Check JSON
        data = request.json
        if not data:
            debug_log("FOUT: Geen JSON data ontvangen! Check Uptime Kuma instelling.")
            return jsonify({"status": "error", "msg": "No JSON"}), 400
        
        debug_log("Stap 1 OK: JSON data ontvangen.")

        # Stap 2: Data uitpakken
        monitor_name = data.get('monitor', {}).get('name', 'Onbekend')
        status = data.get('msg', 'Status update')
        tijdstip = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_bericht = f"{monitor_name}: {status}"
        debug_log(f"Stap 2 OK: Bericht gemaakt -> '{log_bericht}'")

        # Stap 3: Opslaan in Database
        debug_log(f"Stap 3: Verbinden met database op {DB_PATH}...")
        
        with sqlite3.connect(DB_PATH) as con:
            con.execute("INSERT INTO logs (melding, datum) VALUES (?, ?)", (log_bericht, tijdstip))
            con.commit()
        
        debug_log("Stap 3 OK: Succesvol opgeslagen in database!")
        debug_log("--- EINDE MELDING ---")
        
        return jsonify({"status": "success"}), 200

    except Exception as e:
        debug_log(f"!!! KRITIEKE FOUT: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check of gebruiker bestaat
        user = query_db("SELECT * FROM users WHERE username=? AND password=?", (username, password), one=True)
        
        if user:
            session['user'] = username
            return redirect('/')
        else:
            return render_template('login.html', error="Ongeldige inloggegevens")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)