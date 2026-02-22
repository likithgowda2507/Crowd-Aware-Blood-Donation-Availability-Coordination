
# ==========================================
# CAMP MANAGEMENT ENDPOINTS (REAL DB)
# ==========================================

@app.route('/api/camps', methods=['GET'])
def get_camps_real():
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
def cancel_camp(camp_id):
    try:
        camp = Campaign.query.get(camp_id)
        if not camp:
            return jsonify({"message": "Camp not found"}), 404
            
        camp.status = 'cancelled'
        # Or delete: db.session.delete(camp)
        # But keeping it as cancelled is better for records
        
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
