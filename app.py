from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import unifi

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ubiquiti.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)


class AccessPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ap_name = db.Column(db.String(100), unique=True, nullable=False)
    ip_address = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Active')
    

with app.app_context():
    db.create_all()


controller = unifi.Controller('https://your.unifi.controller', 'username', 'password', 'site_id')


@app.route('/')
def index():
    aps = AccessPoint.query.all()
    return render_template('index.html', aps=aps)


@app.route('/add_ap', methods=['POST'])
def add_ap():
    ap_name = request.form.get('ap_name')
    ip_address = request.form.get('ip_address')
    
    ap = AccessPoint(ap_name=ap_name, ip_address=ip_address)
    db.session.add(ap)
    db.session.commit()
    
    return redirect(url_for('index'))


@app.route('/update_status/<int:ap_id>')
def update_status(ap_id):
    ap = AccessPoint.query.get(ap_id)
    if ap:
        status = controller.get_device(ap.ip_address).status
        ap.status = status
        db.session.commit()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
