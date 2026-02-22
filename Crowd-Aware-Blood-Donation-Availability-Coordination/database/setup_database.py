"""
Database Setup Script for BloodConnect
Automatically creates and initializes the database schema
"""

import mysql.connector
from mysql.connector import Error
import os

def read_sql_file(filepath):
    """Read SQL file and return statements"""
    with open(filepath, 'r', encoding='utf-8') as file:
        sql_content = file.read()
    return sql_content

def execute_sql_script(connection, sql_script):
    """Execute SQL script with multiple statements"""
    cursor = connection.cursor()
    
    # Split by delimiter and execute
    statements = sql_script.split(';')
    
    for statement in statements:
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            try:
                # Handle DELIMITER changes for triggers
                if 'DELIMITER' in statement:
                    continue
                cursor.execute(statement)
                print(f"✓ Executed: {statement[:50]}...")
            except Error as e:
                print(f"✗ Error executing statement: {e}")
                print(f"  Statement: {statement[:100]}...")
    
    connection.commit()
    cursor.close()

def setup_database():
    """Main function to set up the database"""
    print("=" * 60)
    print("BloodConnect Database Setup")
    print("=" * 60)
    
    # Database configuration
    host = input("Enter MySQL host (default: localhost): ").strip() or "localhost"
    user = input("Enter MySQL username (default: root): ").strip() or "root"
    password = input("Enter MySQL password: ").strip()
    
    try:
        # Connect to MySQL server (without database)
        print("\n📡 Connecting to MySQL server...")
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            print("✓ Connected to MySQL server successfully!")
            
            # Read and execute schema
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            print(f"\n📄 Reading schema from: {schema_path}")
            
            if not os.path.exists(schema_path):
                print(f"✗ Error: schema.sql not found at {schema_path}")
                return
            
            sql_script = read_sql_file(schema_path)
            
            print("\n🔨 Creating database and tables...")
            execute_sql_script(connection, sql_script)
            
            print("\n" + "=" * 60)
            print("✅ Database setup completed successfully!")
            print("=" * 60)
            print("\nDatabase: bloodconnect")
            print("Sample Accounts Created:")
            print("  Blood Bank: city@bloodbank.com (password: password123)")
            print("  Hospital: city@hospital.com (password: password123)")
            print("\n⚠️  IMPORTANT: Change default passwords in production!")
            print("=" * 60)
            
    except Error as e:
        print(f"\n✗ Error: {e}")
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n📡 MySQL connection closed.")

if __name__ == "__main__":
    setup_database()
