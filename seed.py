"""Seed the database with sample data."""
from app import app, db, Investor, Property
from datetime import date

with app.app_context():
    db.create_all()
    db.session.query(Property).delete()
    db.session.query(Investor).delete()

    investors = [
        Investor(name='Margaret Holloway', email='margaret@hollowaygroup.com',
                 phone='(212) 555-0101', company='Holloway Group',
                 investor_type='institutional', status='active',
                 notes='High-net-worth client focused on NYC multifamily assets.'),
        Investor(name='Derek Nolan', email='derek.nolan@privatecap.com',
                 phone='(310) 555-0202', company='Private Capital Partners',
                 investor_type='fund', status='active',
                 notes='Fund manager. Prefers commercial / mixed-use in LA basin.'),
        Investor(name='Sandra Kim', email='sandra.kim@gmail.com',
                 phone='(415) 555-0303', company=None,
                 investor_type='individual', status='active',
                 notes='Self-directed investor. Buy-and-hold residential strategy.'),
        Investor(name='Apex Realty Fund III', email='invest@apexfund.com',
                 phone='(888) 555-0404', company='Apex Real Estate Capital',
                 investor_type='fund', status='active', notes=''),
        Investor(name='Thomas Vega', email='tvega@outlook.com',
                 phone='(713) 555-0505', company=None,
                 investor_type='individual', status='prospect',
                 notes='Interested in Houston single-family rentals.'),
    ]
    db.session.add_all(investors)
    db.session.flush()

    properties = [
        # Margaret Holloway
        Property(investor=investors[0], address='245 Riverside Dr', city='New York', state='NY',
                 zip_code='10025', property_type='residential', purchase_price=2800000,
                 current_value=3400000, purchase_date=date(2019, 6, 15),
                 square_feet=3200, units=8, monthly_rent=22000, status='owned'),
        Property(investor=investors[0], address='88 West 10th St', city='New York', state='NY',
                 zip_code='10011', property_type='residential', purchase_price=1500000,
                 current_value=1950000, purchase_date=date(2020, 3, 1),
                 square_feet=1800, units=4, monthly_rent=11000, status='owned'),
        Property(investor=investors[0], address='530 Park Ave', city='New York', state='NY',
                 zip_code='10021', property_type='commercial', purchase_price=5200000,
                 current_value=6100000, purchase_date=date(2018, 9, 20),
                 square_feet=8500, units=None, monthly_rent=38000, status='owned'),

        # Derek Nolan
        Property(investor=investors[1], address='4500 Wilshire Blvd', city='Los Angeles', state='CA',
                 zip_code='90010', property_type='commercial', purchase_price=3100000,
                 current_value=3800000, purchase_date=date(2021, 1, 10),
                 square_feet=12000, units=None, monthly_rent=28000, status='owned'),
        Property(investor=investors[1], address='1120 Venice Blvd', city='Los Angeles', state='CA',
                 zip_code='90291', property_type='residential', purchase_price=950000,
                 current_value=1250000, purchase_date=date(2022, 5, 5),
                 square_feet=2200, units=6, monthly_rent=9500, status='owned'),

        # Sandra Kim
        Property(investor=investors[2], address='820 Fillmore St', city='San Francisco', state='CA',
                 zip_code='94117', property_type='residential', purchase_price=1100000,
                 current_value=1380000, purchase_date=date(2020, 8, 14),
                 square_feet=1400, units=2, monthly_rent=7200, status='owned'),
        Property(investor=investors[2], address='360 Oak Grove Ave', city='Menlo Park', state='CA',
                 zip_code='94025', property_type='residential', purchase_price=1450000,
                 current_value=1700000, purchase_date=date(2021, 11, 30),
                 square_feet=1900, units=1, monthly_rent=6500, status='owned'),

        # Apex
        Property(investor=investors[3], address='1200 Brickell Ave', city='Miami', state='FL',
                 zip_code='33131', property_type='commercial', purchase_price=7500000,
                 current_value=9200000, purchase_date=date(2017, 4, 22),
                 square_feet=22000, units=None, monthly_rent=65000, status='owned'),
        Property(investor=investors[3], address='3300 NW 36th St', city='Miami', state='FL',
                 zip_code='33142', property_type='industrial', purchase_price=2200000,
                 current_value=2700000, purchase_date=date(2019, 7, 8),
                 square_feet=35000, units=None, monthly_rent=18000, status='owned'),
        Property(investor=investors[3], address='500 Collins Ave', city='Miami Beach', state='FL',
                 zip_code='33139', property_type='residential', purchase_price=4100000,
                 current_value=3900000, purchase_date=date(2023, 2, 1),
                 square_feet=6000, units=12, monthly_rent=30000, status='owned'),
    ]
    db.session.add_all(properties)
    db.session.commit()
    print(f'Seeded {len(investors)} investors and {len(properties)} properties.')
