import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import csv
import json
from datetime import datetime
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'frauddb'),
    'user': os.getenv('DB_USER', 'fraud'),
    'password': os.getenv('DB_PASSWORD', 'fraud_password_2024')
}

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def create_tables(conn):
    """Create database tables"""
    print("Creating database tables...")
    
    with conn.cursor() as cur:
        # Read and execute schema
        schema_path = Path(__file__).parent / 'schema.sql'
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        cur.execute(schema_sql)
        conn.commit()
    
    print("✅ Tables created successfully")

def load_sample_data(conn):
    """Load sample data from CSV files"""
    print("Loading sample data...")
    
    data_dir = Path('data/sample')
    
    # Load data in order (respecting foreign keys)
    tables = [
        ('cards', 'cards.csv'),
        ('merchants', 'merchants.csv'),
        ('devices', 'devices.csv'),
        ('transactions', 'transactions.csv')
    ]
    
    with conn.cursor() as cur:
        for table_name, csv_file in tables:
            csv_path = data_dir / csv_file
            
            if not csv_path.exists():
                print(f"⚠️  Warning: {csv_file} not found, skipping...")
                continue
            
            print(f"Loading {table_name}...")
            
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    if table_name == 'transactions':
                        load_transaction(cur, row)
                    elif table_name == 'cards':
                        load_card(cur, row)
                    elif table_name == 'merchants':
                        load_merchant(cur, row)
                    elif table_name == 'devices':
                        load_device(cur, row)
        
        conn.commit()
    
    print("✅ Sample data loaded successfully")

def load_transaction(cur, row):
    """Load a transaction record"""
    sql = """
        INSERT INTO transactions 
        (id, ts, card_id, merchant_id, amount, mcc, currency, device_id, ip, city, country, label, raw)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    
    raw_data = json.loads(row['raw']) if row['raw'] else {}
    
    cur.execute(sql, (
        int(row['id']),
        datetime.fromisoformat(row['ts']),
        row['card_id'],
        row['merchant_id'],
        float(row['amount']),
        row['mcc'],
        row['currency'],
        row['device_id'] if row['device_id'] else None,
        row['ip'] if row['ip'] else None,
        row['city'] if row['city'] else None,
        row['country'] if row['country'] else None,
        int(row['label']),
        json.dumps(raw_data)
    ))

def load_card(cur, row):
    """Load a card record"""
    sql = """
        INSERT INTO cards 
        (id, account_id, age_days, home_country, home_city, risk_bucket, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    
    cur.execute(sql, (
        row['id'],
        row['account_id'],
        int(row['age_days']),
        row['home_country'],
        row['home_city'],
        row['risk_bucket'],
        row['is_active'].lower() == 'true',
        datetime.fromisoformat(row['created_at'])
    ))

def load_merchant(cur, row):
    """Load a merchant record"""
    sql = """
        INSERT INTO merchants 
        (id, name, mcc, city, country, risk_bucket, avg_ticket_size, transaction_count, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    
    cur.execute(sql, (
        row['id'],
        row['name'],
        row['mcc'],
        row['city'],
        row['country'],
        row['risk_bucket'],
        float(row['avg_ticket_size']),
        int(row['transaction_count']),
        datetime.fromisoformat(row['created_at'])
    ))

def load_device(cur, row):
    """Load a device record"""
    sql = """
        INSERT INTO devices 
        (id, type, fingerprint, risk_bucket, is_proxy, is_vpn, first_seen, last_seen)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    
    cur.execute(sql, (
        row['id'],
        row['type'],
        row['fingerprint'],
        row['risk_bucket'],
        row['is_proxy'].lower() == 'true',
        row['is_vpn'].lower() == 'true',
        datetime.fromisoformat(row['first_seen']),
        datetime.fromisoformat(row['last_seen'])
    ))

def create_initial_model_record(conn):
    """Create initial model registry entry"""
    print("Creating initial model registry entry...")
    
    with conn.cursor() as cur:
        sql = """
            INSERT INTO models 
            (version, type, path, metrics_json, stage, traffic_percentage, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """
        
        metrics = {
            'auc': 0.85,
            'precision': 0.82,
            'recall': 0.78,
            'f1_score': 0.80,
            'fpr_at_95_tpr': 0.15
        }
        
        cur.execute(sql, (
            'v1.0.0',
            'ensemble',
            'models/v1.0.0/',
            json.dumps(metrics),
            'production',
            100.0,
            datetime.now()
        ))
        
        conn.commit()
    
    print("✅ Initial model record created")

def main():
    """Main initialization function"""
    print("🗄️  Initializing PostgreSQL database...")
    
    conn = connect_db()
    
    try:
        create_tables(conn)
        load_sample_data(conn)
        create_initial_model_record(conn)
        
        # Print statistics
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) as count FROM transactions WHERE label = 1")
            fraud_count = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM transactions")
            total_count = cur.fetchone()['count']
            
            print(f"\n📊 Database statistics:")
            print(f"   Total transactions: {total_count}")
            print(f"   Fraud transactions: {fraud_count}")
            print(f"   Fraud rate: {(fraud_count/total_count*100):.2f}%" if total_count > 0 else "   Fraud rate: 0%")
        
        print("\n✅ Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
