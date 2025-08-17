#!/usr/bin/env python3
"""
Generate sample data for fraud detection system
"""

import json
import csv
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from faker import Faker

fake = Faker()

# Configuration
NUM_CARDS = 10000
NUM_MERCHANTS = 5000
NUM_DEVICES = 8000
NUM_TRANSACTIONS = 100000
FRAUD_RATE = 0.02

# Merchant Category Codes with risk levels
MCC_CODES = {
    '5411': ('Grocery Stores', 'LOW'),
    '5812': ('Eating Places', 'LOW'),
    '5541': ('Service Stations', 'LOW'),
    '5311': ('Department Stores', 'LOW'),
    '5912': ('Drug Stores', 'LOW'),
    '5732': ('Electronics Stores', 'MEDIUM'),
    '5499': ('Miscellaneous Food Stores', 'LOW'),
    '4121': ('Taxicabs/Limousines', 'MEDIUM'),
    '5814': ('Fast Food Restaurants', 'LOW'),
    '5999': ('Miscellaneous Retail', 'MEDIUM'),
    '7995': ('Betting/Casino Gambling', 'HIGH'),
    '6012': ('Customer Financial Institution', 'HIGH'),
    '5933': ('Pawn Shops', 'HIGH'),
    '4816': ('Computer Network Services', 'HIGH'),
    '7273': ('Dating/Personal Services', 'HIGH'),
}

COUNTRIES = [
    'US', 'CA', 'GB', 'DE', 'FR', 'IT', 'ES', 'JP', 'AU', 'BR', 
    'IN', 'CN', 'MX', 'NL', 'BE', 'SE', 'NO', 'DK', 'FI', 'CH'
]

CITIES = {
    'US': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami'],
    'GB': ['London', 'Manchester', 'Birmingham', 'Glasgow', 'Liverpool'],
    'DE': ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne'],
    'FR': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice'],
    'CA': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
    # Add more as needed
}

def generate_card_id():
    return f"card_{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"

def generate_merchant_id():
    return f"merch_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

def generate_device_id():
    return f"device_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}"

def generate_cards():
    """Generate card data"""
    print("Generating cards...")
    cards = []
    
    for _ in range(NUM_CARDS):
        country = random.choice(COUNTRIES)
        city = random.choice(CITIES.get(country, ['Unknown']))
        
        card = {
            'id': generate_card_id(),
            'account_id': f"acc_{fake.random_number(digits=10)}",
            'age_days': random.randint(1, 3650),  # Up to 10 years
            'home_country': country,
            'home_city': city,
            'risk_bucket': random.choices(['LOW', 'MEDIUM', 'HIGH'], weights=[0.7, 0.25, 0.05])[0],
            'is_active': True,
            'created_at': fake.date_time_between(start_date='-3y', end_date='now')
        }
        cards.append(card)
    
    return cards

def generate_merchants():
    """Generate merchant data"""
    print("Generating merchants...")
    merchants = []
    
    for _ in range(NUM_MERCHANTS):
        mcc, (category, risk_bucket) = random.choice(list(MCC_CODES.items()))
        country = random.choice(COUNTRIES)
        city = random.choice(CITIES.get(country, ['Unknown']))
        
        merchant = {
            'id': generate_merchant_id(),
            'name': fake.company(),
            'mcc': mcc,
            'category': category,
            'city': city,
            'country': country,
            'risk_bucket': risk_bucket,
            'avg_ticket_size': round(random.lognormvariate(3.0, 1.0), 2),
            'transaction_count': 0,
            'created_at': fake.date_time_between(start_date='-2y', end_date='now')
        }
        merchants.append(merchant)
    
    return merchants

def generate_devices():
    """Generate device data"""
    print("Generating devices...")
    devices = []
    
    device_types = ['mobile', 'desktop', 'tablet']
    
    for _ in range(NUM_DEVICES):
        device = {
            'id': generate_device_id(),
            'type': random.choice(device_types),
            'fingerprint': fake.sha256(),
            'risk_bucket': random.choices(['LOW', 'MEDIUM', 'HIGH'], weights=[0.8, 0.15, 0.05])[0],
            'is_proxy': random.random() < 0.05,
            'is_vpn': random.random() < 0.03,
            'first_seen': fake.date_time_between(start_date='-1y', end_date='now'),
            'last_seen': fake.date_time_between(start_date='-30d', end_date='now')
        }
        devices.append(device)
    
    return devices

def generate_fraud_patterns():
    """Generate fraud patterns for realistic fraud simulation"""
    patterns = []
    
    # Velocity attack pattern
    patterns.append({
        'type': 'velocity_attack',
        'description': 'Multiple small transactions in short time',
        'probability': 0.3,
        'generate': lambda card, merchants, devices: generate_velocity_attack(card, merchants, devices)
    })
    
    # Geolocation jump pattern
    patterns.append({
        'type': 'geo_jump',
        'description': 'Transactions in impossible locations',
        'probability': 0.25,
        'generate': lambda card, merchants, devices: generate_geo_jump(card, merchants, devices)
    })
    
    # High-risk merchant pattern
    patterns.append({
        'type': 'high_risk_merchant',
        'description': 'Transactions at high-risk merchants',
        'probability': 0.2,
        'generate': lambda card, merchants, devices: generate_high_risk_merchant(card, merchants, devices)
    })
    
    # Device hijack pattern
    patterns.append({
        'type': 'device_hijack',
        'description': 'Same device used by multiple cards',
        'probability': 0.15,
        'generate': lambda card, merchants, devices: generate_device_hijack(card, merchants, devices)
    })
    
    # Large amount anomaly
    patterns.append({
        'type': 'amount_anomaly',
        'description': 'Unusually large transaction amounts',
        'probability': 0.1,
        'generate': lambda card, merchants, devices: generate_amount_anomaly(card, merchants, devices)
    })
    
    return patterns

def generate_velocity_attack(card, merchants, devices):
    """Generate velocity attack transactions"""
    transactions = []
    base_time = fake.date_time_between(start_date='-30d', end_date='now')
    
    # 3-8 transactions within 5 minutes
    num_transactions = random.randint(3, 8)
    
    for i in range(num_transactions):
        # Transactions within 5 minutes
        timestamp = base_time + timedelta(seconds=random.randint(0, 300))
        merchant = random.choice([m for m in merchants if m['risk_bucket'] in ['LOW', 'MEDIUM']])
        device = random.choice(devices)
        
        transaction = create_transaction(
            card=card,
            merchant=merchant,
            device=device,
            timestamp=timestamp,
            amount=round(random.uniform(10, 100), 2),  # Small amounts
            is_fraud=True
        )
        transactions.append(transaction)
    
    return transactions

def generate_geo_jump(card, merchants, devices):
    """Generate geographically impossible transactions"""
    transactions = []
    
    # Two transactions in different continents within impossible time
    base_time = fake.date_time_between(start_date='-30d', end_date='now')
    
    # First transaction in home country
    home_merchants = [m for m in merchants if m['country'] == card['home_country']]
    if home_merchants:
        merchant1 = random.choice(home_merchants)
        device1 = random.choice(devices)
        
        tx1 = create_transaction(
            card=card,
            merchant=merchant1,
            device=device1,
            timestamp=base_time,
            amount=round(random.uniform(20, 200), 2),
            is_fraud=False  # First transaction is legitimate
        )
        transactions.append(tx1)
        
        # Second transaction in distant country within 30 minutes
        distant_countries = [c for c in COUNTRIES if c != card['home_country']]
        distant_country = random.choice(distant_countries)
        distant_merchants = [m for m in merchants if m['country'] == distant_country]
        
        if distant_merchants:
            merchant2 = random.choice(distant_merchants)
            device2 = random.choice(devices)
            
            # Impossible travel time
            tx2_time = base_time + timedelta(minutes=random.randint(5, 30))
            
            tx2 = create_transaction(
                card=card,
                merchant=merchant2,
                device=device2,
                timestamp=tx2_time,
                amount=round(random.uniform(50, 500), 2),
                is_fraud=True
            )
            transactions.append(tx2)
    
    return transactions

def generate_high_risk_merchant(card, merchants, devices):
    """Generate transactions at high-risk merchants"""
    high_risk_merchants = [m for m in merchants if m['risk_bucket'] == 'HIGH']
    
    if not high_risk_merchants:
        return []
    
    merchant = random.choice(high_risk_merchants)
    device = random.choice(devices)
    timestamp = fake.date_time_between(start_date='-30d', end_date='now')
    
    # High-risk merchants typically have higher amounts
    amount = round(random.uniform(100, 2000), 2)
    
    transaction = create_transaction(
        card=card,
        merchant=merchant,
        device=device,
        timestamp=timestamp,
        amount=amount,
        is_fraud=True
    )
    
    return [transaction]

def generate_device_hijack(card, merchants, devices):
    """Generate device hijacking pattern"""
    # Use a high-risk device
    high_risk_devices = [d for d in devices if d['risk_bucket'] == 'HIGH']
    device = random.choice(high_risk_devices) if high_risk_devices else random.choice(devices)
    
    merchant = random.choice(merchants)
    timestamp = fake.date_time_between(start_date='-7d', end_date='now')
    amount = round(random.uniform(50, 800), 2)
    
    transaction = create_transaction(
        card=card,
        merchant=merchant,
        device=device,
        timestamp=timestamp,
        amount=amount,
        is_fraud=True
    )
    
    return [transaction]

def generate_amount_anomaly(card, merchants, devices):
    """Generate unusually large amount transactions"""
    merchant = random.choice(merchants)
    device = random.choice(devices)
    timestamp = fake.date_time_between(start_date='-30d', end_date='now')
    
    # Very large amount (10x normal)
    normal_amount = merchant['avg_ticket_size']
    amount = round(normal_amount * random.uniform(8, 20), 2)
    
    transaction = create_transaction(
        card=card,
        merchant=merchant,
        device=device,
        timestamp=timestamp,
        amount=amount,
        is_fraud=True
    )
    
    return [transaction]

def create_transaction(card, merchant, device, timestamp, amount, is_fraud=False):
    """Create a transaction record"""
    return {
        'id': random.randint(100000, 999999),
        'ts': timestamp,
        'card_id': card['id'],
        'merchant_id': merchant['id'],
        'amount': amount,
        'mcc': merchant['mcc'],
        'currency': 'USD',
        'device_id': device['id'],
        'ip': fake.ipv4(),
        'city': merchant['city'],
        'country': merchant['country'],
        'label': 1 if is_fraud else 0,
        'raw': {
            'user_agent': fake.user_agent(),
            'session_id': fake.uuid4(),
            'merchant_name': merchant['name'],
            'device_type': device['type']
        }
    }

def generate_benign_transactions(cards, merchants, devices, num_transactions):
    """Generate benign/legitimate transactions"""
    print(f"Generating {num_transactions} benign transactions...")
    transactions = []
    
    for _ in range(num_transactions):
        card = random.choice(cards)
        
        # Prefer merchants in same country as card
        same_country_merchants = [m for m in merchants if m['country'] == card['home_country']]
        if same_country_merchants and random.random() < 0.8:  # 80% domestic
            merchant = random.choice(same_country_merchants)
        else:
            merchant = random.choice(merchants)
        
        device = random.choice(devices)
        
        # Realistic transaction timing (business hours bias)
        timestamp = fake.date_time_between(start_date='-90d', end_date='now')
        
        # Amount based on merchant average with some variance
        base_amount = merchant['avg_ticket_size']
        amount = round(max(1.0, np.random.lognormal(np.log(base_amount), 0.5)), 2)
        
        transaction = create_transaction(
            card=card,
            merchant=merchant,
            device=device,
            timestamp=timestamp,
            amount=amount,
            is_fraud=False
        )
        transactions.append(transaction)
    
    return transactions

def generate_fraud_transactions(cards, merchants, devices, num_fraud):
    """Generate fraud transactions using patterns"""
    print(f"Generating {num_fraud} fraud transactions...")
    fraud_patterns = generate_fraud_patterns()
    transactions = []
    
    for _ in range(num_fraud):
        card = random.choice(cards)
        pattern = random.choices(
            fraud_patterns,
            weights=[p['probability'] for p in fraud_patterns]
        )[0]
        
        pattern_transactions = pattern['generate'](card, merchants, devices)
        transactions.extend(pattern_transactions)
        
        # Ensure we don't exceed the target
        if len(transactions) >= num_fraud:
            break
    
    return transactions[:num_fraud]

def save_to_csv(data, filename, fieldnames=None):
    """Save data to CSV file"""
    filepath = Path('data/sample') / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    if not data:
        print(f"No data to save for {filename}")
        return
    
    if fieldnames is None:
        fieldnames = data[0].keys() if data else []
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            # Handle datetime objects
            processed_row = {}
            for key, value in row.items():
                if isinstance(value, datetime):
                    processed_row[key] = value.isoformat()
                elif isinstance(value, dict):
                    processed_row[key] = json.dumps(value)
                else:
                    processed_row[key] = value
            writer.writerow(processed_row)
    
    print(f"Saved {len(data)} records to {filepath}")

def main():
    """Main function to generate all sample data"""
    print("🎲 Generating sample data for fraud detection system...")
    
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    fake.seed_instance(42)
    
    # Generate entities
    cards = generate_cards()
    merchants = generate_merchants()
    devices = generate_devices()
    
    # Generate transactions
    num_fraud = int(NUM_TRANSACTIONS * FRAUD_RATE)
    num_benign = NUM_TRANSACTIONS - num_fraud
    
    benign_transactions = generate_benign_transactions(cards, merchants, devices, num_benign)
    fraud_transactions = generate_fraud_transactions(cards, merchants, devices, num_fraud)
    
    # Combine and shuffle transactions
    all_transactions = benign_transactions + fraud_transactions
    random.shuffle(all_transactions)
    
    # Assign sequential IDs
    for i, tx in enumerate(all_transactions, 1):
        tx['id'] = i
    
    print(f"\n📊 Generated data summary:")
    print(f"   Cards: {len(cards)}")
    print(f"   Merchants: {len(merchants)}")
    print(f"   Devices: {len(devices)}")
    print(f"   Transactions: {len(all_transactions)} ({num_fraud} fraud, {num_benign} benign)")
    print(f"   Fraud rate: {(num_fraud/len(all_transactions)*100):.2f}%")
    
    # Save to CSV files
    save_to_csv(cards, 'cards.csv')
    save_to_csv(merchants, 'merchants.csv')
    save_to_csv(devices, 'devices.csv')
    save_to_csv(all_transactions, 'transactions.csv')
    
    # Generate additional reference data
    generate_reference_data()
    
    print("\n✅ Sample data generation completed!")

def generate_reference_data():
    """Generate additional reference data files"""
    print("Generating reference data...")
    
    # Country coordinates for distance calculations
    country_coordinates = {
        'US': (39.8283, -98.5795),
        'CA': (56.1304, -106.3468),
        'GB': (55.3781, -3.4360),
        'DE': (51.1657, 10.4515),
        'FR': (46.2276, 2.2137),
        'IT': (41.8719, 12.5674),
        'ES': (40.4637, -3.7492),
        'JP': (36.2048, 138.2529),
        'AU': (-25.2744, 133.7751),
        'BR': (-14.2350, -51.9253),
        'IN': (20.5937, 78.9629),
        'CN': (35.8617, 104.1954),
        'MX': (23.6345, -102.5528),
        'NL': (52.1326, 5.2913),
        'BE': (50.5039, 4.4699),
        'SE': (60.1282, 18.6435),
        'NO': (60.4720, 8.4689),
        'DK': (56.2639, 9.5018),
        'FI': (61.9241, 25.7482),
        'CH': (46.8182, 8.2275)
    }
    
    # Save reference data
    with open('data/sample/countries.json', 'w') as f:
        json.dump(country_coordinates, f, indent=2)
    
    with open('data/sample/mcc_codes.json', 'w') as f:
        json.dump(MCC_CODES, f, indent=2)
    
    # Holiday data (simplified)
    holidays = {
        '2024-01-01': 'New Year\'s Day',
        '2024-07-04': 'Independence Day (US)',
        '2024-12-25': 'Christmas Day',
        '2024-11-28': 'Thanksgiving (US)',
        '2024-02-14': 'Valentine\'s Day'
    }
    
    with open('data/sample/holidays.json', 'w') as f:
        json.dump(holidays, f, indent=2)

if __name__ == '__main__':
    main()