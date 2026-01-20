#!/usr/bin/env python3
"""
Script to create the commitment_broker database.
Connects to PostgreSQL server and creates the database if it doesn't exist.
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys


def create_database():
    """Create commitment_broker database."""
    # Try to connect to postgres database first
    try:
        # Connect to default postgres database to create our database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='commitment_broker'")
        exists = cursor.fetchone()
        
        if exists:
            print("✅ Database 'commitment_broker' already exists!")
            cursor.close()
            conn.close()
            return True
        
        # Create database
        cursor.execute('CREATE DATABASE commitment_broker')
        print("✅ Database 'commitment_broker' created successfully!")
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        print("\nPossible solutions:")
        print("1. Make sure PostgreSQL is running:")
        print("   sudo systemctl status postgresql")
        print("   OR")
        print("   docker compose up -d postgres")
        print("\n2. If using Docker, check if port mapping is correct")
        print("\n3. Check your .env file has correct DATABASE_URL")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)
