from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import pymysql
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# Install pymysql as MySQLdb
pymysql.install_as_MySQLdb()

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Database Configuration (MySQL)
# Default MySQL local connection. Password is usually empty for Homebrew installs.
basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'blood_donation.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:likith07@localhost/bloodconnect'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(basedir, 'database'), exist_ok=True)

db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False)  # donor, bank, hospital, admin
    donation_type = db.Column(db.String(20), default='Free') # Free, Paid
    phone = db.Column(db.String(20))
    blood_group = db.Column(db.String(5))
    medical_conditions = db.Column(db.Text)
    account_status = db.Column(db.String(20), default='active') # active, pending, suspended
    
    contact_person = db.Column(db.String(100))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    license_id = db.Column(db.String(50)) # For Blood Banks
    registration_id = db.Column(db.String(50)) # For Hospitals
    operating_hours = db.Column(db.String(50))
    capacity = db.Column(db.Integer)
    hospital_type = db.Column(db.String(20)) # Government, Private, etc.
    
    # AI Verification fields
    ai_verification_status = db.Column(db.String(20), default='pending') # pending, auto_approved, flagged, manual_approved, rejected
    ai_confidence_score = db.Column(db.Integer, default=0) # 0-100
    ai_verification_notes = db.Column(db.Text) # JSON with verification details
    verified_at = db.Column(db.DateTime)
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id')) # Admin who verified
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text)
    
    donor = db.relationship('User', backref=db.backref('reports', lazy=True))

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_id = db.Column(db.String(50), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.String(20), nullable=False) # emergency, urgent, routine
    reason = db.Column(db.String(255), nullable=False)
    blood_bank_id = db.Column(db.String(50)) # Simply storing the bank identifier for now
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    hospital = db.relationship('User', backref=db.backref('requests', lazy=True))

class BloodInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units = db.Column(db.Integer, default=0)
    expiry_date = db.Column(db.DateTime, nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    bank = db.relationship('User', backref=db.backref('inventory', lazy=True))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(20), nullable=False) # shortage, emergency, expiry
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    status = db.Column(db.String(20), default='scheduled') # scheduled, completed, cancelled
    target_blood_groups = db.Column(db.String(50)) # e.g., "A+, O-"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    organizer = db.relationship('User', backref=db.backref('campaigns', lazy=True))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    camp_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=True) # Optional if booking with bank
    bank_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Optional if booking with camp
    date = db.Column(db.DateTime, nullable=False)
    time_slot = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='scheduled') # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    donor = db.relationship('User', foreign_keys=[donor_id], backref=db.backref('appointments', lazy=True))
    camp = db.relationship('Campaign', backref=db.backref('appointments', lazy=True))
    bank = db.relationship('User', foreign_keys=[bank_id], backref=db.backref('bank_appointments', lazy=True))


# --- Routes ---

@app.route('/api/donor/stats/<int:user_id>', methods=['GET'])
def get_donor_stats(user_id):
    """Get calculated stats for a donor"""
    # Count approved reports as donations for now
    donation_count = Report.query.filter_by(donor_id=user_id, status='approved').count()
    lives_saved = donation_count * 3
    
    # Calculate next eligible date (3 months after last approved donation)
    last_donation = Report.query.filter_by(donor_id=user_id, status='approved').order_by(Report.upload_date.desc()).first()
    next_eligible_date = None
    days_remaining = 0
    
    if last_donation:
        eligible_date = last_donation.upload_date + timedelta(days=90)
        next_eligible_date = eligible_date.strftime('%Y-%m-%d')
        days_remaining = (eligible_date - datetime.utcnow()).days
        if days_remaining < 0:
            days_remaining = 0
            
    achievement = "Bronze"
    if donation_count > 5: achievement = "Silver"
    if donation_count > 10: achievement = "Gold"
    if donation_count > 20: achievement = "Platinum"
    
    return jsonify({
        "total_donations": donation_count,
        "lives_saved": lives_saved,
        "next_eligible_date": next_eligible_date,
        "days_remaining": days_remaining,
        "achievement_level": achievement
    })

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get upcoming campaigns"""
    # For now return all, filter by date later
    camps = Campaign.query.order_by(Campaign.date).all()
    result = []
    for c in camps:
        result.append({
            "id": c.id,
            "name": c.name,
            "location": c.location,
            "date": c.date.strftime('%Y-%m-%d'),
            "start_time": c.start_time,
            "end_time": c.end_time,
            "status": c.status
        })
    return jsonify(result)

@app.route('/api/camps', methods=['POST'])
def create_camp():
    try:
        data = request.json
        # In a real app, get bank_id from session/token. For now, use the one passed or default.
        bank_id = data.get('organizer_id')
        
        new_camp = Campaign(
            organizer_id=bank_id,
            name=data.get('name'),
            location=data.get('location'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            target_blood_groups=data.get('target_blood_groups', 'All'),
            status='scheduled'
        )
        
        db.session.add(new_camp)
        db.session.commit()
        
        return jsonify({"message": "Camp created successfully", "id": new_camp.id}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/camps/<int:camp_id>', methods=['PUT'])
def update_camp(camp_id):
    try:
        camp = Campaign.query.get(camp_id)
        if not camp:
            return jsonify({"message": "Camp not found"}), 404
            
        data = request.json
        if 'name' in data: camp.name = data['name']
        if 'location' in data: camp.location = data['location']
        if 'date' in data: camp.date = datetime.strptime(data['date'], '%Y-%m-%d')
        if 'start_time' in data: camp.start_time = data['start_time']
        if 'end_time' in data: camp.end_time = data['end_time']
        
        db.session.commit()
        return jsonify({"message": "Camp updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/camps/<int:camp_id>', methods=['DELETE'])
def cancel_camp(camp_id):
    try:
        camp = Campaign.query.get(camp_id)
        if not camp:
            return jsonify({"message": "Camp not found"}), 404
            
        camp.status = 'cancelled'
        
        db.session.commit()
        return jsonify({"message": "Camp cancelled successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/camps/<int:camp_id>/slots', methods=['GET'])
def get_camp_slots(camp_id):
    try:
        # Get appointments for this camp
        appointments = Appointment.query.filter_by(camp_id=camp_id).all()
        
        slots = []
        for apt in appointments:
            donor = User.query.get(apt.donor_id)
            slots.append({
                "id": apt.id,
                "donor_name": donor.username if donor else "Unknown",
                "time": apt.time_slot,
                "status": apt.status
            })
            
        return jsonify(slots), 200
    except Exception as e:
         return jsonify({"message": str(e)}), 500

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.json
    try:
        new_appt = Appointment(
            donor_id=data['donor_id'],
            camp_id=data.get('camp_id'),
            bank_id=data.get('bank_id'),
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            time_slot=data['time_slot']
        )
        db.session.add(new_appt)
        db.session.commit()
        return jsonify({"message": "Appointment booked successfully", "id": new_appt.id}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/appointments/<int:user_id>', methods=['GET'])
def get_appointments(user_id):
    appts = Appointment.query.filter_by(donor_id=user_id).order_by(Appointment.date).all()
    result = []
    for a in appts:
        target_name = "Unknown"
        location = "Unknown"
        if a.camp:
            target_name = a.camp.name
            location = a.camp.location
        elif a.bank:
            target_name = a.bank.username
            location = a.bank.address
            
        result.append({
            "id": a.id,
            "title": target_name,
            "location": location,
            "date": a.date.strftime('%Y-%m-%d'),
            "time": a.time_slot,
            "status": a.status
        })
    return jsonify(result)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/init_db', methods=['POST'])
def init_db():
    """Helper to initialize DB and create an admin user if not exists"""
    with app.app_context():
        # Drop all tables to apply schema changes (since we are not using migrations for this rapid iterations)
        # WARNING: This deletes data using a secret key or just force for dev. 
        # For this context, we will simply create_all, but if schema changed, it might fail or not update.
        # Let's add a force reset flag/endpoint or just do it manually.
        pass # Created separate script for this
        
        db.create_all()
        # Create default admin if not exists
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', email='admin@bloodconnect.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            return jsonify({"message": "Database initialized and admin created"}), 201
        return jsonify({"message": "Database already initialized"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    user = User.query.filter_by(email=email, role=role).first()
    
    if user and user.check_password(password):
        if hasattr(user, 'account_status') and user.account_status == 'pending':
             return jsonify({
                 "message": "Your account is pending admin approval. You will be able to log in once an administrator reviews and approves your registration."
             }), 403
             
        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "redirect_url": f"{user.role}-dashboard.html" if user.role != 'admin' else 'admin-dashboard.html'
        }), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    # Check if request is multipart/form-data (for file upload) or JSON
    if request.is_json:
        data = request.json
    else:
        data = request.form

    username = data.get('username') or data.get('name') # Frontend uses 'name' for donor/bank/hospital
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    donation_type = data.get('donation_type') or 'Free'
    phone = data.get('phone')
    blood_group = data.get('blood_group')
    medical_conditions = data.get('medical_conditions')
    
    # Institution Fields
    contact_person = data.get('contact_person')
    address = data.get('address')
    city = data.get('city')
    state = data.get('state')
    pincode = data.get('pincode')
    license_id = data.get('license_id')
    registration_id = data.get('registration_id') or data.get('registration_number') # Bank uses reg_number
    operating_hours = data.get('operating_hours')
    capacity = data.get('capacity')
    hospital_type = data.get('hospital_type')
    
    # All roles (Donor, Hospital, Blood Bank) need approval except Admin
    if role in ['donor', 'hospital', 'blood_bank', 'bank']:
        account_status = 'pending'
    else:
        account_status = 'active'
    
    if not username or not email or not password or not role:
        return jsonify({"message": "Missing required fields"}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already taken"}), 400
        
    new_user = User(
        username=username, 
        email=email, 
        role=role, 
        donation_type=donation_type,
        phone=phone,
        blood_group=blood_group,
        medical_conditions=str(medical_conditions) if medical_conditions else None,
        account_status=account_status,
        contact_person=contact_person,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        license_id=license_id,
        registration_id=registration_id,
        operating_hours=operating_hours,
        capacity=capacity,
        hospital_type=hospital_type
    )
    new_user.set_password(password)
    
    # AI Verification for non-admin roles
    if role in ['donor', 'hospital', 'bank']:
        from ai_verifier import ai_verifier
        
        # Prepare data for AI verification
        verification_data = {
            'username': username,
            'email': email,
            'phone': phone,
            'blood_group': blood_group,
            'contact_person': contact_person,
            'address': address,
            'city': city,
            'state': state,
            'pincode': pincode,
            'license_id': license_id,
            'registration_id': registration_id,
            'operating_hours': operating_hours,
            'capacity': capacity,
            'hospital_type': hospital_type
        }
        
        # Run AI verification
        ai_status, ai_score, ai_notes = ai_verifier.verify_user(verification_data, role)
        
        # Update user with AI verification results
        new_user.ai_verification_status = ai_status
        new_user.ai_confidence_score = ai_score
        new_user.ai_verification_notes = ai_notes
        
        # All users remain pending until admin approval
        # AI score helps admin prioritize reviews, but doesn't auto-activate
        new_user.account_status = 'pending'
    
    db.session.add(new_user)
    db.session.commit()
    
    # Handle File Upload for Donors
    if role == 'donor' and 'report' in request.files:
        file = request.files['report']
        if file and file.filename != '':
            filename = secure_filename(f"{new_user.id}_{int(datetime.now().timestamp())}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_report = Report(donor_id=new_user.id, filename=filename)
            db.session.add(new_report)
            db.session.commit()
            return jsonify({"message": "Registration successful. Please wait for admin approval.", "user_id": new_user.id}), 201
            
    return jsonify({"message": "Registration successful", "user_id": new_user.id}), 201

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "donation_type": getattr(user, 'donation_type', 'Free')
    }), 200

@app.route('/api/upload_report', methods=['POST'])
def upload_report():
    if 'report' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['report']
    donor_id = request.form.get('donor_id')
    
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
        
    if file and donor_id:
        filename = secure_filename(f"{donor_id}_{int(datetime.now().timestamp())}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_report = Report(donor_id=donor_id, filename=filename)
        db.session.add(new_report)
        db.session.commit()
        
        return jsonify({"message": "Report uploaded successfully"}), 201
        
    return jsonify({"message": "Upload failed"}), 500

@app.route('/api/reports', methods=['GET'])
def get_reports():
    # In a real app, ensure the requester is an admin
    reports = Report.query.all() # Get all for now
    result = []
    for r in reports:
        result.append({
            "id": r.id,
            "donor_name": r.donor.username,
            "filename": r.filename,
            "upload_date": r.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
            "status": r.status,
            "donation_type": getattr(r.donor, 'donation_type', 'Free'),
            "phone": getattr(r.donor, 'phone', 'N/A'),
            "blood_group": getattr(r.donor, 'blood_group', 'N/A'),
            "medical_conditions": getattr(r.donor, 'medical_conditions', 'None'),
            "admin_notes": r.admin_notes
        })
    return jsonify(result), 200

@app.route('/api/verify_report/<int:report_id>', methods=['POST'])
def verify_report(report_id):
    data = request.json
    action = data.get('action') # 'approve' or 'reject'
    
    report = Report.query.get_or_404(report_id)
    
    if action == 'approve':
        report.status = 'approved'
        # Activate the user account
        if report.donor:
            report.donor.account_status = 'active'
            
    elif action == 'reject':
        report.status = 'rejected'
        # Optional: Keep user pending or suspend? For now, keep pending so they can re-upload.
        if report.donor:
             report.donor.account_status = 'pending'
    else:
        return jsonify({"message": "Invalid action"}), 400
        
    db.session.commit()
    return jsonify({"message": f"Report {action}d successfully"}), 200

@app.route('/api/request_blood', methods=['POST'])
def request_blood():
    data = request.json
    hospital_id = data.get('hospital_id')
    patient_name = data.get('patient_name')
    patient_id = data.get('patient_id')
    blood_group = data.get('blood_group')
    units = data.get('units')
    priority = data.get('priority')
    reason = data.get('reason')
    blood_bank_id = data.get('blood_bank')
    
    if not all([hospital_id, patient_name, patient_id, blood_group, units, priority]):
        return jsonify({"message": "Missing required fields"}), 400
        
    user = User.query.get(hospital_id)
    if not user:
        return jsonify({"message": "Hospital user not found"}), 404
        
    new_request = BloodRequest(
        hospital_id=hospital_id,
        patient_name=patient_name,
        patient_id=patient_id,
        blood_group=blood_group,
        units=units,
        priority=priority,
        reason=reason,
        blood_bank_id=blood_bank_id
    )
    
    db.session.add(new_request)
    
    # Emergency Logic
    if priority == 'emergency':
        # 1. Notify all Blood Banks
        banks = User.query.filter_by(role='blood_bank', account_status='active').all()
        for bank in banks:
            msg = f"EMERGENCY: Hospital {user.username} needs {units} units of {blood_group}! Please organize a drive."
            notif = Notification(user_id=bank.id, message=msg, type='emergency')
            db.session.add(notif)
            
            # Auto-Create Emergency Campaign (Draft)
            camp = Campaign(
                organizer_id=bank.id,
                name=f"Emergency Drive for {blood_group}",
                location=bank.address or "Bank Location",
                date=datetime.utcnow() + timedelta(days=1), # Tomorrow
                target_blood_groups=blood_group,
                status='scheduled'
            )
            db.session.add(camp)
            
    db.session.commit()
    
    return jsonify({"message": "Blood request submitted successfully"}), 201

@app.route('/api/hospital/requests', methods=['GET'])
def get_hospital_requests():
    hospital_id = request.args.get('hospital_id')
    if not hospital_id:
        return jsonify({"message": "Hospital ID required"}), 400
        
    requests = BloodRequest.query.filter_by(hospital_id=hospital_id).order_by(BloodRequest.request_date.desc()).all()
    result = []
    for r in requests:
        result.append({
            "id": r.id,
            "patient_name": r.patient_name,
            "patient_id": r.patient_id,
            "blood_group": r.blood_group,
            "units": r.units,
            "priority": r.priority,
            "status": r.status,
            "blood_bank": r.blood_bank_id,
            "date": r.request_date.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify(result), 200

@app.route('/api/admin/requests', methods=['GET'])
def get_admin_requests():
    # In real app, verify admin session
    requests = BloodRequest.query.filter_by(status='pending').order_by(BloodRequest.request_date.desc()).all()
    result = []
    for r in requests:
        result.append({
            "id": r.id,
            "hospital_name": r.hospital.username,
            "patient_name": r.patient_name,
            "blood_group": r.blood_group,
            "units": r.units,
            "priority": r.priority,
            "blood_bank": r.blood_bank_id,
            "reason": r.reason,
            "date": r.request_date.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify(result), 200

@app.route('/api/admin/verify_request/<int:request_id>', methods=['POST'])
def verify_request(request_id):
    data = request.json
    action = data.get('action') # 'approve' or 'reject'
    
    req = BloodRequest.query.get_or_404(request_id)
    
    if action == 'approve':
        req.status = 'approved'
    elif action == 'reject':
        req.status = 'rejected'
    else:
        return jsonify({"message": "Invalid action"}), 400
        
    db.session.commit()
    return jsonify({"message": f"Request {action}d successfully"}), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    # Admin only endpoint
    role_filter = request.args.get('role')
    
    query = User.query
    if role_filter:
        if role_filter == 'blood_bank':
             # Handle both 'bank' and 'blood_bank' if needed, or just assume frontend sends correct one
             query = query.filter(User.role.in_(['blood_bank', 'bank']))
        else:
             query = query.filter_by(role=role_filter)
             
    # Exclude admin from list
    users = query.filter(User.role != 'admin').order_by(User.id.desc()).all()
    
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "phone": getattr(u, 'phone', 'N/A'),
            "account_status": getattr(u, 'account_status', 'active'),
            "donation_type": getattr(u, 'donation_type', 'Free'),
            "contact_person": getattr(u, 'contact_person', None),
            "address": getattr(u, 'address', None),
            "city": getattr(u, 'city', None),
            "license_id": getattr(u, 'license_id', None),
            "registration_id": getattr(u, 'registration_id', None),
            "hospital_type": getattr(u, 'hospital_type', None),
            "capacity": getattr(u, 'capacity', None)
        })
    return jsonify(result), 200

@app.route('/api/verify_user/<int:user_id>', methods=['POST'])
def verify_user(user_id):
    data = request.json
    action = data.get('action') # 'approve' or 'reject'
    
    user = User.query.get_or_404(user_id)
    
    if action == 'approve':
        user.account_status = 'active'
    elif action == 'reject':
        user.account_status = 'rejected'
    else:
        return jsonify({"message": "Invalid action"}), 400
        
    db.session.commit()
    return jsonify({"message": f"User {user.username} {action}d successfully"}), 200

@app.route('/api/bank/stats/<int:bank_id>', methods=['GET'])
def get_bank_stats(bank_id):
    """Get statistics for a specific blood bank"""
    try:
        # 1. Total Blood Units
        total_units = db.session.query(db.func.sum(BloodInventory.units)).filter_by(bank_id=bank_id).scalar() or 0
        
        # 2. Today's Collections (Approximated by units added today)
        today = datetime.utcnow().date()
        todays_units = db.session.query(db.func.sum(BloodInventory.units))\
            .filter_by(bank_id=bank_id)\
            .filter(db.func.date(BloodInventory.added_date) == today)\
            .scalar() or 0
            
        # 3. Pending Requests (Assuming mapped by bank_id string/id match)
        # Note: BloodRequest.blood_bank_id is String currently. 
        # Attempting exact match on ID string or username.
        # For robustness, we'll check if bank_id matches the request's stored ID (as string)
        pending_requests = BloodRequest.query.filter_by(blood_bank_id=str(bank_id), status='pending').count()
        
        # 4. Expiring Soon (Within 7 days)
        week_from_now = datetime.utcnow() + timedelta(days=7)
        expiring = db.session.query(db.func.sum(BloodInventory.units))\
            .filter_by(bank_id=bank_id)\
            .filter(BloodInventory.expiry_date <= week_from_now)\
            .filter(BloodInventory.expiry_date >= datetime.utcnow())\
            .scalar() or 0
            
        return jsonify({
            "total_units": int(total_units),
            "todays_collections": int(todays_units),
            "pending_requests": pending_requests,
            "expiring_soon": int(expiring)
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/bank/inventory/details/<int:bank_id>', methods=['GET'])
def get_inventory_details(bank_id):
    """Get raw inventory rows for table view"""
    inventory = BloodInventory.query.filter_by(bank_id=bank_id).order_by(BloodInventory.expiry_date).all()
    result = []
    
    today = datetime.utcnow().date()
    warning_date = today + timedelta(days=7)
    
    for item in inventory:
        # Determine status
        expiry = item.expiry_date.date()
        status = "Available"
        status_class = "available"
        
        if expiry < today:
            status = "Expired"
            status_class = "expired"
        elif expiry <= warning_date:
            status = "Expiring Soon"
            status_class = "expiring"
        
        # Check if reserved (logic to be added if 'reserved' field exists, else simulated)
        # For now, we assume all valid stock is available unless Expired.
        
        result.append({
            "id": item.id,
            "bag_id": f"BB-{item.added_date.year}-{item.id:04d}", # Generate ID format
            "blood_group": item.blood_group,
            "units": item.units,
            "volume": f"{450 * item.units} ml" if item.units > 1 else "450 ml", # Show total volume or per bag? Image implies per bag.
            "collection_date": item.added_date.strftime('%b %d, %Y'),
            "expiry_date": item.expiry_date.strftime('%b %d, %Y'),
            "status": status,
            "status_class": status_class
        })
        
    return jsonify(result), 200

@app.route('/api/bank/inventory/<int:bank_id>', methods=['GET'])
def get_bank_inventory(bank_id):
    """Get detailed inventory for a bank"""
    inventory = db.session.query(
        BloodInventory.blood_group, 
        db.func.sum(BloodInventory.units)
    ).filter_by(bank_id=bank_id).group_by(BloodInventory.blood_group).all()
    
    result = {bg: 0 for bg in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']}
    for bg, units in inventory:
        result[bg] = int(units)
        
    return jsonify(result), 200

@app.route('/api/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    """Get notifications for a user"""
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    result = []
    
    # Calculate time ago helper
    def get_time_ago(dt):
        diff = datetime.utcnow() - dt
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

    for n in notifs:
        result.append({
            "id": n.id,
            "message": n.message,
            "type": n.type, # urgent, info, success, warning
            "is_read": n.is_read,
            "time_ago": get_time_ago(n.created_at),
            "created_at": n.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result)

@app.route('/api/notifications/mark-read/<int:user_id>', methods=['POST'])
def mark_notifications_read(user_id):
    """Mark all notifications as read for a user"""
    try:
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify({"message": "Notifications marked as read"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not User.query.filter_by(role='admin').first():
            print("Creating default admin user...")
            admin = User(username='admin', email='admin@bloodconnect.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created.")
            
@app.route('/api/inventory/update', methods=['POST'])
def update_inventory():
    data = request.json
    bank_id = data.get('bank_id')
    blood_group = data.get('blood_group')
    units = data.get('units') # Can be positive (add) or negative (remove)
    expiry_date_str = data.get('expiry_date')
    
    if not all([bank_id, blood_group, units]):
        return jsonify({"message": "Missing fields"}), 400
        
    try:
        units = int(units)
        if units > 0:
            if not expiry_date_str:
                 return jsonify({"message": "Expiry date required for adding stock"}), 400
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
            
            # Create individual records for each unit to simulate unique "Bag IDs"
            for _ in range(units):
                new_stock = BloodInventory(
                    bank_id=bank_id,
                    blood_group=blood_group,
                    units=1,
                    expiry_date=expiry_date
                )
                db.session.add(new_stock)
        else:
            # Remove stock (FIFO - First In First Out approx by expiry)
            to_remove = abs(units)
            stocks = BloodInventory.query.filter_by(bank_id=bank_id, blood_group=blood_group)\
                .order_by(BloodInventory.expiry_date).all()
            
            remaining = to_remove
            for stock in stocks:
                if stock.units >= remaining:
                    stock.units -= remaining
                    remaining = 0
                    if stock.units == 0:
                        db.session.delete(stock)
                    break
                else:
                    remaining -= stock.units
                    db.session.delete(stock)
            
            if remaining > 0:
                 db.session.rollback()
                 return jsonify({"message": "Insufficient stock to remove"}), 400
                 
        db.session.commit()
        return jsonify({"message": "Inventory updated successfully"}), 200
        
    except ValueError:
        return jsonify({"message": "Invalid data format"}), 400
        
@app.route('/api/campaigns', methods=['POST'])
def create_campaign():
    data = request.json
    organizer_id = data.get('organizer_id')
    name = data.get('name')
    location = data.get('location')
    date_str = data.get('date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    target_groups = data.get('target_blood_groups')
    
    if not all([organizer_id, name, location, date_str]):
         return jsonify({"message": "Missing required fields"}), 400
         
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        new_camp = Campaign(
            organizer_id=organizer_id,
            name=name,
            location=location,
            date=date,
            start_time=start_time,
            end_time=end_time,
            target_blood_groups=target_groups
        )
        db.session.add(new_camp)
        db.session.commit()
        return jsonify({"message": "Campaign created successfully", "id": new_camp.id}), 201
    except ValueError:
        return jsonify({"message": "Invalid date format"}), 400

@app.route('/api/bank/requests/<int:bank_id>', methods=['GET'])
def get_bank_requests(bank_id):
    # Get requests sent explicitly to this bank
    requests = BloodRequest.query.filter_by(blood_bank_id=str(bank_id)).order_by(BloodRequest.request_date.desc()).all()
    result = []
    for r in requests:
        result.append({
            "id": r.id,
            "hospital_name": r.hospital.username,
            "patient_name": r.patient_name,
            "blood_group": r.blood_group,
            "units": r.units,
            "priority": r.priority,
            "date": r.request_date.strftime('%Y-%m-%d %H:%M'),
            "status": r.status
        })
    return jsonify(result), 200

@app.route('/api/bank/request/<int:request_id>/action', methods=['POST'])
def bank_request_action(request_id):
    data = request.json
    action = data.get('action')
    bank_id = data.get('bank_id') # Security check ideally
    
    req = BloodRequest.query.get_or_404(request_id)
    
    if req.blood_bank_id != str(bank_id):
        return jsonify({"message": "Unauthorized"}), 403
        
    if action == 'approve':
        req.status = 'approved'
        # Optional: Deduct stock automatically? Let's leave manual for now or auto-deduct.
        # User asked for "properly working", auto-deduct is better.
        # Find matching stock
        stocks = BloodInventory.query.filter_by(bank_id=bank_id, blood_group=req.blood_group)\
                .order_by(BloodInventory.expiry_date).all()
        required = req.units
        for stock in stocks:
            if stock.units >= required:
                stock.units -= required
                required = 0
                if stock.units == 0: db.session.delete(stock)
                break
            else:
                required -= stock.units
                db.session.delete(stock)
                
        if required > 0:
            db.session.rollback()
            return jsonify({"message": "Insufficient stock to approve"}), 400
            
    elif action == 'reject':
        req.status = 'rejected'
    else:
        return jsonify({"message": "Invalid action"}), 400
        
    db.session.commit()
    return jsonify({"message": f"Request {action}d"}), 200

@app.route('/api/bank/donations/<int:bank_id>', methods=['GET'])
def get_bank_donations(bank_id):
    # Use Completed Appointments as proxy for Donations
    appts = Appointment.query.filter_by(bank_id=bank_id, status='completed').order_by(Appointment.date.desc()).all()
    result = []
    for a in appts:
        result.append({
            "id": a.id,
            "donor_name": a.donor.username,
            "date": a.date.strftime('%Y-%m-%d'),
            "blood_group": a.donor.blood_group,
            "type": a.donor.donation_type
        })
    return jsonify(result), 200

@app.route('/api/banks', methods=['GET'])
def get_all_banks():
    banks = User.query.filter(User.role.in_(['blood_bank', 'bank'])).all()
    result = []
    for b in banks:
        result.append({
            "id": b.id,
            "name": b.username,
            "city": b.city,
            "phone": b.phone,
            "address": b.address
        })
    return jsonify(result), 200

# Re-include the ML and existing inventory routes below if needed or just append
# NOTE: Replace the existing add_inventory stub if present or just append.
# The user's file had add_inventory at line 711. I will replace lines 711 onwards until I hit check_expiry or end.

@app.route('/api/inventory/check_expiry', methods=['GET'])
def check_expiry():
    """Checks for units expiring in next 7 days and notifies banks"""
    threshold_date = datetime.utcnow() + timedelta(days=7)
    expiring_units = BloodInventory.query.filter(
        BloodInventory.expiry_date <= threshold_date,
        BloodInventory.expiry_date >= datetime.utcnow()
    ).all()
    
    alerts_sent = 0
    for unit in expiring_units:
        msg = f"Warning: {unit.units} units of {unit.blood_group} expiring on {unit.expiry_date.strftime('%Y-%m-%d')}"
        existing_notif = Notification.query.filter_by(
            user_id=unit.bank_id, 
            message=msg,
            type='expiry'
        ).first()
        
        if not existing_notif:
            notif = Notification(user_id=unit.bank_id, message=msg, type='expiry')
            db.session.add(notif)
            alerts_sent += 1
            
    db.session.commit()
    return jsonify({"message": f"Expiry check complete. Alerts sent: {alerts_sent}"}), 200

from ml_predictor import predictor

@app.route('/api/analytics/run-prediction', methods=['POST'])
def run_prediction():
    """Runs ML prediction for next week's demand and generates automated alerts"""
    try:
        predictions = predictor.predict_next_week_demand()
        alerts_generated = 0
        reasons = [] # For debugging/response
        
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        total_shortage = 0
        
        for bg in blood_groups:
            # 1. Get current inventory
            current_stock = db.session.query(db.func.sum(BloodInventory.units))\
                .filter_by(blood_group=bg)\
                .filter(BloodInventory.expiry_date > datetime.utcnow())\
                .scalar() or 0
                
            predicted_demand = predictions.get(bg, 0)
            
            # 2. Check for shortage (Projected Stock = Current - Predicted)
            # If Projected Stock < Safety Buffer (e.g., 5 units), alert!
            safety_buffer = 5
            projected_balance = current_stock - predicted_demand
            
            if projected_balance < safety_buffer:
                shortage_amt = safety_buffer - projected_balance
                total_shortage += shortage_amt
                
                # 3. Notify Eligible Donors
                donors = User.query.filter_by(role='donor', blood_group=bg, account_status='active').all()
                count = 0
                for donor in donors:
                    # Check if already notified recently (prevent spam)
                    msg = f"AI Prediction: High demand expected for {bg} next week. {int(shortage_amt)} units needed. Please donate!"
                    existing = Notification.query.filter_by(user_id=donor.id, message=msg).first()
                    
                    if not existing:
                        notif = Notification(user_id=donor.id, message=msg, type='urgent')
                        db.session.add(notif)
                        count += 1
                
                if count > 0:
                    reasons.append(f"{bg}: Shortage of {int(shortage_amt)} units. Notified {count} donors.")
                    alerts_generated += count

        # 4. Notify Blood Banks if aggregate shortage is high
        if total_shortage > 20: # High aggregate shortage
            banks = User.query.filter(User.role.in_(['blood_bank', 'bank'])).all()
            for bank in banks:
                msg = f"AI Insight: High aggregate blood demand ({int(total_shortage)} units shortage) predicted for next week. Recommended to organize a donation camp."
                if not Notification.query.filter_by(user_id=bank.id, message=msg).first():
                    notif = Notification(user_id=bank.id, message=msg, type='warning')
                    db.session.add(notif)
                    alerts_generated += 1
            reasons.append("High aggregate shortage. Notified Blood Banks.")

        db.session.commit()
        return jsonify({
            "message": "Prediction analysis complete", 
            "predictions": predictions,
            "alerts_sent": alerts_generated,
            "details": reasons
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Prediction failed: {str(e)}"}), 500

@app.route('/api/admin/stats/advanced', methods=['GET'])
def advanced_stats():
    threshold_date = datetime.utcnow() + timedelta(days=7)
    expiring_count = BloodInventory.query.filter(
        BloodInventory.expiry_date <= threshold_date,
         BloodInventory.expiry_date >= datetime.utcnow()
    ).count()
    
    emergency_count = BloodRequest.query.filter_by(priority='emergency', status='pending').count()
    
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    current_shortages = []
    for bg in blood_groups:
        total = db.session.query(db.func.sum(BloodInventory.units)).filter_by(blood_group=bg).scalar() or 0
        if total < 10:
            current_shortages.append(bg)
            
    return jsonify({
        "expiring_units_7_days": expiring_count,
        "active_emergencies": emergency_count,
        "shortage_groups": current_shortages
    }), 200

    return jsonify({
        "expiring_units_7_days": expiring_count,
        "active_emergencies": emergency_count,
        "shortage_groups": current_shortages
    }), 200

@app.route('/api/analytics/monthly', methods=['GET'])
def analytics_monthly():
    """Returns aggregated blood units by month for the last 6 months"""
    bank_id = request.args.get('bank_id')
    
    query = BloodInventory.query
    if bank_id:
        query = query.filter_by(bank_id=bank_id)
        
    inventory = query.all()
    
    data = {} # "Jan 2024": 150
    
    for item in inventory:
        if item.added_date:
            month_key = item.added_date.strftime('%b %Y')
            data[month_key] = data.get(month_key, 0) + item.units
            
    # Sort by date
    sorted_keys = sorted(data.keys(), key=lambda x: datetime.strptime(x, '%b %Y'))
    
    return jsonify({
        "labels": sorted_keys,
        "data": [data.get(k) for k in sorted_keys]
    }), 200

@app.route('/api/analytics/distribution', methods=['GET'])
def analytics_distribution():
    """Returns total units per blood group"""
    bank_id = request.args.get('bank_id')
    
    query = db.session.query(
        BloodInventory.blood_group, 
        db.func.sum(BloodInventory.units)
    )
    
    if bank_id:
        query = query.filter(BloodInventory.bank_id == bank_id)
        
    results = query.group_by(BloodInventory.blood_group).all()
    
    data = {}
    for bg, total in results:
        data[bg] = int(total) if total else 0
        
    # Ensure all groups are present even if 0
    bg_list = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    final_labels = bg_list
    final_data = [data.get(bg, 0) for bg in bg_list]
    
    return jsonify({
        "labels": final_labels,
        "data": final_data
    }), 200


# Hospital API Endpoints

@app.route('/api/hospital/stats/<int:hospital_id>', methods=['GET'])
def get_hospital_stats(hospital_id):
    """Get hospital dashboard statistics"""
    try:
        # Get total active requests
        active_requests = BloodRequest.query.filter_by(
            hospital_id=hospital_id,
            status='pending'
        ).count()
        
        # Get fulfilled requests this month
        from datetime import datetime, timedelta
        first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fulfilled_this_month = BloodRequest.query.filter(
            BloodRequest.hospital_id == hospital_id,
            BloodRequest.status == 'completed',
            BloodRequest.request_date >= first_day_of_month
        ).count()
        
        # Get total units received this month
        units_received = db.session.query(db.func.sum(BloodRequest.units)).filter(
            BloodRequest.hospital_id == hospital_id,
            BloodRequest.status == 'completed',
            BloodRequest.request_date >= first_day_of_month
        ).scalar() or 0
        
        # Calculate average response time (simplified - using hours)
        avg_response_time = 24  # Default 24 hours
        
        stats = {
            'active_requests': active_requests,
            'fulfilled_this_month': fulfilled_this_month,
            'units_received': int(units_received),
            'avg_response_time': avg_response_time
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/hospital/requests/<int:hospital_id>', methods=['GET'])
def get_hospital_requests_by_id(hospital_id):
    """Get hospital blood requests with optional status filter"""
    try:
        status_filter = request.args.get('status')
        
        query = BloodRequest.query.filter_by(hospital_id=hospital_id)
        
        if status_filter:
            if status_filter == 'active':
                query = query.filter_by(status='pending')
            elif status_filter == 'completed':
                query = query.filter_by(status='completed')
        
        requests_list = query.order_by(BloodRequest.request_date.desc()).all()
        
        result = []
        for r in requests_list:
            result.append({
                "id": r.id,
                "patient_name": r.patient_name,
                "patient_id": r.patient_id,
                "blood_group": r.blood_group,
                "units": r.units,
                "priority": r.priority,
                "status": r.status,
                "reason": r.reason,
                "blood_bank_id": r.blood_bank_id,
                "request_date": r.request_date.strftime('%Y-%m-%d %H:%M') if r.request_date else None
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# Blood Stock Check API Endpoint

@app.route('/api/stock-check', methods=['GET'])
def stock_check():
    """Check blood stock availability across all blood banks"""
    try:
        blood_group = request.args.get('blood_group')
        
        if not blood_group:
            return jsonify({"message": "Blood group required"}), 400
        
        # Get all blood banks with inventory for the requested blood group
        # Join BloodInventory with User (blood banks)
        results = db.session.query(
            User.id.label('bank_id'),
            User.username.label('bank_name'),
            User.city,
            User.phone,
            db.func.sum(BloodInventory.units).label('units')
        ).join(
            BloodInventory, User.id == BloodInventory.bank_id
        ).filter(
            User.role == 'bank',
            BloodInventory.blood_group == blood_group,
            BloodInventory.units > 0
        ).group_by(
            User.id, User.username, User.city, User.phone
        ).all()
        
        stock_data = []
        for result in results:
            stock_data.append({
                'bank_id': result.bank_id,
                'bank_name': result.bank_name,
                'city': result.city,
                'phone': result.phone,
                'units': int(result.units)
            })
        
        return jsonify(stock_data), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# ===== ADMIN AI VERIFICATION ENDPOINTS =====

@app.route('/api/admin/pending-verifications', methods=['GET'])
def get_pending_verifications():
    """Get all pending verifications with AI scores"""
    try:
        # Get all users pending verification (flagged by AI or still pending)
        pending_users = User.query.filter(
            User.ai_verification_status.in_(['pending', 'flagged'])
        ).order_by(User.ai_confidence_score.asc()).all()
        
        result = []
        for user in pending_users:
            import json
            ai_notes = json.loads(user.ai_verification_notes) if user.ai_verification_notes else []
            
            result.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'phone': user.phone,
                'city': user.city,
                'ai_verification_status': user.ai_verification_status,
                'ai_confidence_score': user.ai_confidence_score,
                'ai_verification_notes': ai_notes,
                'account_status': user.account_status
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/admin/auto-approved', methods=['GET'])
def get_auto_approved():
    """Get all auto-approved registrations for admin review"""
    try:
        auto_approved = User.query.filter_by(
            ai_verification_status='auto_approved'
        ).order_by(User.id.desc()).limit(50).all()
        
        result = []
        for user in auto_approved:
            result.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'phone': user.phone,
                'city': user.city,
                'ai_confidence_score': user.ai_confidence_score,
                'account_status': user.account_status,
                'verified_at': user.verified_at.isoformat() if user.verified_at else None
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/admin/verify/<int:user_id>', methods=['POST'])
def admin_verify_user(user_id):
    """Admin manual verification of a user"""
    try:
        data = request.json
        decision = data.get('decision')  # 'approve' or 'reject'
        admin_id = data.get('admin_id')
        admin_notes = data.get('notes', '')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        if decision == 'approve':
            user.account_status = 'active'
            user.ai_verification_status = 'manual_approved'
            user.verified_at = datetime.utcnow()
            user.verified_by = admin_id
            message = f"User {user.username} approved successfully"
        elif decision == 'reject':
            user.account_status = 'suspended'
            user.ai_verification_status = 'rejected'
            user.verified_at = datetime.utcnow()
            user.verified_by = admin_id
            message = f"User {user.username} rejected"
        else:
            return jsonify({"message": "Invalid decision"}), 400
        
        # Add admin notes to AI verification notes
        if user.ai_verification_notes:
            import json
            notes = json.loads(user.ai_verification_notes)
            notes.append({
                'type': 'admin_review',
                'decision': decision,
                'notes': admin_notes,
                'admin_id': admin_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            user.ai_verification_notes = json.dumps(notes)
        
        db.session.commit()
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/admin/ai-stats', methods=['GET'])
def get_ai_stats():
    """Get AI verification statistics"""
    try:
        total_users = User.query.filter(User.role != 'admin').count()
        auto_approved = User.query.filter_by(ai_verification_status='auto_approved').count()
        flagged = User.query.filter_by(ai_verification_status='flagged').count()
        pending = User.query.filter_by(ai_verification_status='pending').count()
        manual_approved = User.query.filter_by(ai_verification_status='manual_approved').count()
        rejected = User.query.filter_by(ai_verification_status='rejected').count()
        
        # Calculate average confidence score
        from sqlalchemy import func
        avg_score = db.session.query(func.avg(User.ai_confidence_score)).filter(
            User.ai_confidence_score > 0
        ).scalar() or 0
        
        stats = {
            'total_registrations': total_users,
            'auto_approved': auto_approved,
            'flagged_for_review': flagged,
            'pending': pending,
            'manual_approved': manual_approved,
            'rejected': rejected,
            'average_confidence_score': round(avg_score, 2),
            'automation_rate': round((auto_approved / total_users * 100), 2) if total_users > 0 else 0
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
if __name__ == '__main__':
    app.run(debug=True, port=5001)

# ==========================================
# BANK DASHBOARD API ENDPOINTS
# ==========================================

@app.route('/api/bank/profile', methods=['GET'])
def get_bank_profile():
    # For demo purposes, we'll assume logged in user is ID 1 (City Blood Bank)
    # In production, use current_user.id
    bank_id = 1 
    bank = User.query.get(bank_id)
    if not bank:
        return jsonify({"message": "Bank not found"}), 404
        
    return jsonify({
        "name": bank.username,
        "city": "Pollachi", # This should be in DB model
        "logo": "images/bank-logo.png"
    })

@app.route('/api/inventory/summary', methods=['GET'])
def get_inventory_summary():
    bank_id = 1
    
    # Total units
    total_units = db.session.query(db.func.sum(BloodInventory.units)).filter_by(bank_id=bank_id).scalar() or 0
    
    # Expiring soon (next 7 days)
    seven_days_later = datetime.now() + timedelta(days=7)
    expiring = BloodInventory.query.filter(
        BloodInventory.bank_id == bank_id,
        BloodInventory.expiry_date <= seven_days_later,
        BloodInventory.expiry_date >= datetime.now()
    ).count()
    
    # Mock data for things we don't track yet
    today_collections = 12 
    pending_requests = BloodRequest.query.filter_by(blood_bank_id=str(bank_id), status='pending').count()
    
    return jsonify({
        "total": int(total_units),
        "today": today_collections,
        "pending": pending_requests,
        "expiring": expiring
    })

@app.route('/api/inventory/groups', methods=['GET'])
def get_inventory_groups():
    bank_id = 1
    inventory = BloodInventory.query.filter_by(bank_id=bank_id).all()
    
    result = []
    # Initialize all groups with 0
    all_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    group_counts = {g: 0 for g in all_groups}
    
    for item in inventory:
        if item.blood_group in group_counts:
            group_counts[item.blood_group] += item.units
            
    for group, count in group_counts.items():
        result.append({"group": group, "units": count})
        
    return jsonify(result)

@app.route('/api/inventory', methods=['GET'])
def get_inventory_list():
    bank_id = 1
    inventory = BloodInventory.query.filter_by(bank_id=bank_id).all()
    
    result = []
    for item in inventory:
        result.append({
            "bag_id": f"BAG-{item.id}",
            "group": item.blood_group,
            "volume": "350ml",
            "collected": item.added_date.strftime('%Y-%m-%d'),
            "expiry": item.expiry_date.strftime('%Y-%m-%d'),
            "status": "Available" if item.expiry_date > datetime.now() else "Expired"
        })
    return jsonify(result)

@app.route('/api/requests/urgent', methods=['GET'])
def get_urgent_requests():
    # Get pending requests for this bank
    bank_id = 1
    requests = BloodRequest.query.filter(
        (BloodRequest.blood_bank_id == str(bank_id)) | (BloodRequest.blood_bank_id == None),
        BloodRequest.status == 'pending',
        BloodRequest.priority.in_(['urgent', 'emergency', 'high'])
    ).limit(5).all()
    
    result = []
    for r in requests:
        hospital = User.query.get(r.hospital_id)
        result.append({
            "hospital": hospital.username if hospital else "Unknown Hospital",
            "group": r.blood_group,
            "units": r.units
        })
    
    if not result: # Add mock data if empty for demo
        result = [
            {"hospital": "City Hospital", "group": "O-", "units": 2},
            {"hospital": "General Hospital", "group": "A+", "units": 4}
        ]
        
    return jsonify(result)

# ==========================================
# CAMP MANAGEMENT ENDPOINTS (REAL DB)
# ==========================================

@app.route('/api/camps', methods=['GET'])
def get_camps():
    # Bank ID 1 for demo
    bank_id = 1
    camps = Campaign.query.filter_by(organizer_id=bank_id).order_by(Campaign.date).all()
    
    result = []
    for camp in camps:
        result.append({
            "id": camp.id,
            "name": camp.name,
            "location": camp.location,
            "date": camp.date.strftime('%Y-%m-%d'),
            "start_time": camp.start_time,
            "end_time": camp.end_time,
            "status": camp.status
        })
    return jsonify(result), 200

@app.route('/api/camps', methods=['POST'])
def create_camp():
    try:
        data = request.json
        bank_id = 1 # Demo
        
        new_camp = Campaign(
            organizer_id=bank_id,
            name=data.get('name'),
            location=data.get('location'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            target_blood_groups=data.get('target_groups', 'All'),
            status='scheduled'
        )
        
        db.session.add(new_camp)
        db.session.commit()
        
        return jsonify({"message": "Camp created successfully", "id": new_camp.id}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/camps/<int:camp_id>', methods=['PUT'])
def update_camp(camp_id):
    try:
        camp = Campaign.query.get(camp_id)
        if not camp:
            return jsonify({"message": "Camp not found"}), 404
            
        data = request.json
        if 'name' in data: camp.name = data['name']
        if 'location' in data: camp.location = data['location']
        if 'date' in data: camp.date = datetime.strptime(data['date'], '%Y-%m-%d')
        if 'start_time' in data: camp.start_time = data['start_time']
        if 'end_time' in data: camp.end_time = data['end_time']
        
        db.session.commit()
        return jsonify({"message": "Camp updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/camps/<int:camp_id>', methods=['DELETE'])
def cancel_camp_endpoint(camp_id):
    try:
        camp = Campaign.query.get(camp_id)
        if not camp:
            return jsonify({"message": "Camp not found"}), 404
            
        camp.status = 'cancelled'
        db.session.commit()
        return jsonify({"message": "Camp cancelled successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/camps/<int:camp_id>/slots', methods=['GET'])
def get_camp_slots(camp_id):
    # Get appointments for this camp
    appointments = Appointment.query.filter_by(camp_id=camp_id).all()
    
    slots = []
    for apt in appointments:
        donor = User.query.get(apt.donor_id)
        slots.append({
            "id": apt.id,
            "donor_name": donor.username if donor else "Unknown",
            "time": apt.time_slot,
            "status": apt.status
        })
        
    return jsonify(slots), 200

@app.route('/api/donations/today', methods=['GET'])
def get_todays_donations():
    # Mock data
    return jsonify([
        {"name": "John Doe", "group": "O+"},
        {"name": "Jane Smith", "group": "A-"},
        {"name": "Mike Ross", "group": "B+"}
    ])

@app.route('/api/network', methods=['GET'])
def get_network():
    # Return other blood banks
    banks = User.query.filter(User.role == 'bank', User.id != 1).limit(5).all()
    result = []
    for bank in banks:
        result.append({
            "name": bank.username,
            "city": bank.city if hasattr(bank, 'city') and bank.city else "Coimbatore"
        })
        
    if not result:
        result = [
            {"name": "District Blood Bank", "city": "Coimbatore"},
            {"name": "Red Cross Bank", "city": "Tiruppur"}
        ]
    return jsonify(result)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    # Generate alerts based on inventory
    alerts = []
    
    # Check low stock (mock logic)
    alerts.append({
        "title": "Low Stock: O-",
        "message": "Stock below 5 units. Organize a camp soon."
    })
    
    alerts.append({
        "title": "Expiring Units",
        "message": "3 units of AB+ expiring in 2 days."
    })
    
    return jsonify(alerts)

