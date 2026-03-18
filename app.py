from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ── Models ────────────────────────────────────────────────────────────────────

class Investor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    company = db.Column(db.String(120))
    investor_type = db.Column(db.String(50))   # individual, institutional, fund
    status = db.Column(db.String(30), default='active')  # active, inactive, prospect
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    properties = db.relationship('Property', back_populates='investor', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'investor_type': self.investor_type,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'property_count': len(self.properties),
            'portfolio_value': sum(p.current_value or 0 for p in self.properties),
        }


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.Integer, db.ForeignKey('investor.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    property_type = db.Column(db.String(50))   # residential, commercial, industrial, land
    purchase_price = db.Column(db.Float)
    current_value = db.Column(db.Float)
    purchase_date = db.Column(db.Date)
    square_feet = db.Column(db.Integer)
    units = db.Column(db.Integer)              # for multi-family
    monthly_rent = db.Column(db.Float)
    status = db.Column(db.String(30), default='owned')  # owned, sold, under-contract
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    investor = db.relationship('Investor', back_populates='properties')

    def to_dict(self):
        return {
            'id': self.id,
            'investor_id': self.investor_id,
            'investor_name': self.investor.name if self.investor else None,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'property_type': self.property_type,
            'purchase_price': self.purchase_price,
            'current_value': self.current_value,
            'equity': (self.current_value or 0) - (self.purchase_price or 0),
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'square_feet': self.square_feet,
            'units': self.units,
            'monthly_rent': self.monthly_rent,
            'annual_rent': (self.monthly_rent or 0) * 12,
            'cap_rate': round(((self.monthly_rent or 0) * 12 / self.current_value * 100), 2)
                        if self.current_value and self.monthly_rent else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
        }


# ── Investors API ─────────────────────────────────────────────────────────────

@app.route('/api/investors', methods=['GET'])
def get_investors():
    q = request.args.get('q', '')
    status = request.args.get('status', '')
    query = Investor.query
    if q:
        query = query.filter(
            db.or_(Investor.name.ilike(f'%{q}%'),
                   Investor.email.ilike(f'%{q}%'),
                   Investor.company.ilike(f'%{q}%'))
        )
    if status:
        query = query.filter_by(status=status)
    investors = query.order_by(Investor.name).all()
    return jsonify([i.to_dict() for i in investors])


@app.route('/api/investors/<int:id>', methods=['GET'])
def get_investor(id):
    investor = Investor.query.get_or_404(id)
    data = investor.to_dict()
    data['properties'] = [p.to_dict() for p in investor.properties]
    return jsonify(data)


@app.route('/api/investors', methods=['POST'])
def create_investor():
    d = request.json
    investor = Investor(
        name=d['name'],
        email=d['email'],
        phone=d.get('phone'),
        company=d.get('company'),
        investor_type=d.get('investor_type', 'individual'),
        status=d.get('status', 'active'),
        notes=d.get('notes'),
    )
    db.session.add(investor)
    db.session.commit()
    return jsonify(investor.to_dict()), 201


@app.route('/api/investors/<int:id>', methods=['PUT'])
def update_investor(id):
    investor = Investor.query.get_or_404(id)
    d = request.json
    for field in ['name', 'email', 'phone', 'company', 'investor_type', 'status', 'notes']:
        if field in d:
            setattr(investor, field, d[field])
    db.session.commit()
    return jsonify(investor.to_dict())


@app.route('/api/investors/<int:id>', methods=['DELETE'])
def delete_investor(id):
    investor = Investor.query.get_or_404(id)
    db.session.delete(investor)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


# ── Properties API ────────────────────────────────────────────────────────────

@app.route('/api/properties', methods=['GET'])
def get_properties():
    investor_id = request.args.get('investor_id')
    status = request.args.get('status', '')
    prop_type = request.args.get('property_type', '')
    query = Property.query
    if investor_id:
        query = query.filter_by(investor_id=investor_id)
    if status:
        query = query.filter_by(status=status)
    if prop_type:
        query = query.filter_by(property_type=prop_type)
    properties = query.order_by(Property.created_at.desc()).all()
    return jsonify([p.to_dict() for p in properties])


@app.route('/api/properties/<int:id>', methods=['GET'])
def get_property(id):
    return jsonify(Property.query.get_or_404(id).to_dict())


@app.route('/api/properties', methods=['POST'])
def create_property():
    d = request.json
    prop = Property(
        investor_id=d['investor_id'],
        address=d['address'],
        city=d.get('city'),
        state=d.get('state'),
        zip_code=d.get('zip_code'),
        property_type=d.get('property_type', 'residential'),
        purchase_price=d.get('purchase_price'),
        current_value=d.get('current_value'),
        purchase_date=datetime.strptime(d['purchase_date'], '%Y-%m-%d').date()
                      if d.get('purchase_date') else None,
        square_feet=d.get('square_feet'),
        units=d.get('units'),
        monthly_rent=d.get('monthly_rent'),
        status=d.get('status', 'owned'),
        notes=d.get('notes'),
    )
    db.session.add(prop)
    db.session.commit()
    return jsonify(prop.to_dict()), 201


@app.route('/api/properties/<int:id>', methods=['PUT'])
def update_property(id):
    prop = Property.query.get_or_404(id)
    d = request.json
    for field in ['address', 'city', 'state', 'zip_code', 'property_type',
                  'purchase_price', 'current_value', 'square_feet', 'units',
                  'monthly_rent', 'status', 'notes', 'investor_id']:
        if field in d:
            setattr(prop, field, d[field])
    if 'purchase_date' in d and d['purchase_date']:
        prop.purchase_date = datetime.strptime(d['purchase_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify(prop.to_dict())


@app.route('/api/properties/<int:id>', methods=['DELETE'])
def delete_property(id):
    prop = Property.query.get_or_404(id)
    db.session.delete(prop)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


# ── Dashboard / Stats API ─────────────────────────────────────────────────────

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_investors = Investor.query.count()
    active_investors = Investor.query.filter_by(status='active').count()
    total_properties = Property.query.count()
    owned = Property.query.filter_by(status='owned').all()
    total_value = sum(p.current_value or 0 for p in owned)
    total_rent = sum(p.monthly_rent or 0 for p in owned)
    total_equity = sum((p.current_value or 0) - (p.purchase_price or 0) for p in owned)

    by_type = {}
    for p in Property.query.all():
        t = p.property_type or 'unknown'
        by_type[t] = by_type.get(t, 0) + 1

    return jsonify({
        'total_investors': total_investors,
        'active_investors': active_investors,
        'total_properties': total_properties,
        'owned_properties': len(owned),
        'total_portfolio_value': total_value,
        'total_monthly_rent': total_rent,
        'total_annual_rent': total_rent * 12,
        'total_equity': total_equity,
        'properties_by_type': by_type,
    })


# ── Static / SPA ──────────────────────────────────────────────────────────────

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
