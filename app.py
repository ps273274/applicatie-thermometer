import sqlite3
import datetime
import os
import sys
import time
#import msal
#import requests
from flask import Flask, render_template, request, redirect, session, jsonify
from functools import wraps
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "supersecret"

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Dit is het pad BINNEN de container. 
# Via docker-compose is dit gekoppeld aan jouw I-schijf.
DB_PATH = "/app/database.db"

#_msal_app = none

#def _get_token():
#    global _msal_app
#    if _msal_app is None:
#        _msal_app = msal.ConfidentialClietApplication(
#            os.environ["GRAPH_CLIENT_ID"]
#            authority=f"https://login.microsoftonline.com/{os.environ['GRAPH_TENANT_ID']}",
#            client_credential=os.environ["GRAPH_CLIENT_SECRET"],
#        )
#    result = _msal_app.acquire_token_for_client(
#        scopes=["https://graph.microsoft.com/.default"]
#    )
#    if "access_token" not in result:
#        raise RuntimeError(result.get("error_description", "Geen token ontvangen"))+
#    return result["access_token"]
#
#    def Graph_mail_versturen(onderwerp, inhoud, ontvangers):
#        afzender = os.environ["GRAPH_SENDER"]
#        payload = {
#            Message: {
#                "Subject": onderwerp,
#                "Body": {"ContentType": "Text", "Content": inhoud}
#                "ToRecipients": [{"EmailAddress": {"Address": afzender}}],
#                "bccRecipients": [{"EmailAddress": {"Address": a}} for a in ontvangers]
#            },
#            "SaveToSentItems": "False",
#        }
#        r = requests.post(
#            f"https://graph.microsoft.com/v1.0/users/{afzender}/sendMail",
#            headers={"authorization": f"Bearer {_get_token()}"},
#            json=payload,
#            timeout=10,
#        )
#        r.raise_for_status()

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
        heartbeat = data.get('heartbeat') or {}


        rows = query_db("SELECT email FROM users WHERE email IS NOT NULL AND email != ''")
        ontvangers = [row['email'] for r in rows]
        if heartbeat.get('status') == 0:   # 0 = down, 1 = up
            try:
                alert = Message(f"STORING: {monitor_name}",
                                recipients=[APP.config["MAIL-DEFAULT-SENDER"]],
                                bcc=ontvangers,
                                )
                alert.body = f"{log_bericht}\nTijdstip: {tijdstip}"
                mail.send(alert)
            except Exception as e:
                debug_log(f"Mail versturen mislukt: {e}")
        debug_log("--- EINDE MELDING ---")
        
        heartbeat = data.get('heartbeat', {})
        rows = query_db("SELECT email FROM users WHERE email is NOT NULL AND email != ''")
        # ontvangers = [r['email'] for r in rows]

        # if heartbeat.get('status') == 0 and ontvangers:
        #     try:
        #         send_graph_mail(f"STORING {monitor_name}")
        #                         f"{log_bericht}\nTijdstip: {tijdstip}", ontvangers)
        
#        except Exception as e:
 #           debug_log(f"!!! MISLUKT OM DE MAIL TE VERZENDEN: {e}")

  #      debug_log(" ---EINDE MELDING ---")
        
   #     return jsonify({"status": "success"}), 200

    except Exception as e:
        debug_log(f"!!! KRITIEKE FOUT: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

from werkzeug.security import generate_password_hash
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit(
"5 per 15 minutes",
methods=["POST"],
deduct_when=lambda response: response.status_code == 200,
)
def login():
    if 'user' in session:
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check of gebruiker bestaat
        user = query_db("SELECT * FROM users WHERE username=?", (username,), one=True)
        
        if user and check_password_hash(user['password'], password):
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

@app.errorhandler(429)
def te_veel_pogingen(e):
    seconds_left = 15 * 60
    try:
        seconds_left = max(1, int(limiter.current_limit.reset_at - time.time()))
    except Exception:
        debug_log(f"Resterende tijd niet te bepalen: {ex}")

    if request.path == '/login':
        return render_template(
            'login.html',
            error="Te veel mislukte pogingen.",
            seconds_left=seconds_left,
        ), 429

    return "Te veel verzoeken, probeer het later opnieuw.", 429

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
