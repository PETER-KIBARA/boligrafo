# verify_notification_table.py
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postd.settings')
django.setup()

from django.db import connection

def verify_table():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'postd_notification'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print("Updated notification table columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}, nullable: {col[2]}, default: {col[3]})")
        
        # Check for all required columns
        required_columns = [
            'id', 'notification_type', 'title', 'message', 
            'bp_systolic', 'bp_diastolic', 'missed_days', 
            'is_read', 'created_at', 'doctor_id', 'patient_id'
        ]
        existing_columns = [col[0] for col in columns]
        
        print("\nColumn status:")
        for req_col in required_columns:
            if req_col in existing_columns:
                print(f"  ✅ {req_col}")
            else:
                print(f"  ❌ {req_col}")

if __name__ == "__main__":
    verify_table()