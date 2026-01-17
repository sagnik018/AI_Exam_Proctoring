#!/usr/bin/env python3
"""
Test script to verify database functionality
"""
import sqlite3
import os

def test_database():
    # Remove existing database for clean test
    if os.path.exists('proctoring.db'):
        os.remove('proctoring.db')
    
    try:
        # Connect to database
        conn = sqlite3.connect('proctoring.db')
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                location TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert test data
        cursor.execute('''
            INSERT INTO user_details (name, gender, location)
            VALUES (?, ?, ?)
        ''', ('Test User', 'male', 'Test Location'))
        
        conn.commit()
        
        # Query data
        cursor.execute('SELECT * FROM user_details')
        results = cursor.fetchall()
        
        print("✅ Database test successful!")
        print(f"📊 Results: {results}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database()
