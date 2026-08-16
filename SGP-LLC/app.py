from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sgp_llc_secret_gendarmerie_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app) #
with app.app_context():db.create_all()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    matricule = db.Column(db.String(50), unique=True)
    role = db.Column(db.String(50))
    bureau = db.Column(db.String(100))
    password = db.Column(db.String(200))

class Plainte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_plaignant = db.Column(db.String(100))
    tel = db.Column(db.String(20))
    type_plainte = db.Column(db.String(100))
    resume = db.Column(db.Text)
    statut = db.Column(db.String(50), default='NOUVEAU')
    date = db.Column(db.String(20), default=datetime.now().strftime('%d/%m/%Y'))
    affecte_a = db.Column(db.String(50), default='')
    bureau = db.Column(db.String(100))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(matricule='admin').first():
        admin = User(nom='ADMIN GENERAL', matricule='admin', role='ADMIN', bureau='LEGION', password=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(matricule=request.form['matricule']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['role'] = user.role
            session['nom'] = user.nom
            return redirect(url_for('dashboard'))
        flash('Matricule ou mot de passe incorrect')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    role = session['role']
    search = request.args.get('search','')
    query = Plainte.query
    if search:
        query = query.filter(Plainte.nom_plaignant.contains(search) | Plainte.tel.contains(search) | Plainte.type_plainte.contains(search) | Plainte.id.cast(db.String).contains(search))
    plaintes = query.order_by(Plainte.id.desc()).all()
    return render_template('dashboard.html', role=role, plaintes=plaintes, search=search, nom=session['nom'])

@app.route('/admin')
def admin():
    if session.get('role')!= 'ADMIN': return "Accès refusé - PC Bureau uniquement"
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
