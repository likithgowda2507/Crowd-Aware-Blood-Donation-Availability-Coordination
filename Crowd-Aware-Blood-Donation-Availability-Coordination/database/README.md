# Database Setup Instructions

## BloodConnect Database Schema

The complete database schema has been created in `database/schema.sql`.

### Database Structure

**Tables Created:**
- `donors` - Donor user accounts and profiles
- `blood_banks` - Blood bank organizations
- `hospitals` - Hospital organizations
- `blood_inventory` - Blood unit inventory tracking
- `donation_camps` - Blood donation camp events
- `camp_bookings` - Donor bookings for camps
- `blood_requests` - Hospital blood requests
- `request_fulfillments` - Request fulfillment tracking
- `donation_records` - Historical donation records
- `notifications` - User notifications
- `shortage_alerts` - Blood shortage alerts
- `bank_connections` - Blood bank network connections
- `inter_bank_transfers` - Inter-bank blood transfers
- `demand_predictions` - AI/ML demand predictions
- `activity_logs` - System activity logs

**Views Created:**
- `v_blood_stock_summary` - Blood stock summary by bank and group
- `v_donor_stats` - Donor statistics and eligibility
- `v_hospital_request_summary` - Hospital request summaries

**Triggers:**
- `update_donor_eligibility` - Auto-update donor eligibility after donation

### Setup Options

#### Option 1: MySQL Command Line (Recommended)
```bash
# Navigate to project directory
cd /Users/likith/Downloads/Crowd-Aware-Blood-Donation-Availability-Coordination

# Execute schema
mysql -u root -p < database/schema.sql
```

#### Option 2: MySQL Workbench
1. Open MySQL Workbench
2. Connect to your MySQL server
3. File → Open SQL Script
4. Select `database/schema.sql`
5. Execute the script

#### Option 3: Python Script
```bash
# Use the Python database setup script
python database/setup_database.py
```

### Sample Data Included

The schema includes sample data for testing:
- **Blood Bank**: City Blood Bank (email: city@bloodbank.com)
- **Hospital**: City Hospital (email: city@hospital.com)
- **Password**: `password123` (hashed with bcrypt)

> **⚠️ IMPORTANT**: Change the default passwords in production!

### Next Steps

After running the schema:
1. Verify all tables are created: `SHOW TABLES;`
2. Check sample data: `SELECT * FROM blood_banks;`
3. Update `app.py` database connection settings if needed
4. Test the application with the new database

### Database Connection in app.py

Make sure your `app.py` has the correct database configuration:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'bloodconnect'
}
```
