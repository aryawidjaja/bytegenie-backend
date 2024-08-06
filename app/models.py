from . import db

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String)
    company_logo_url = db.Column(db.String)
    relation_to_event = db.Column(db.String)
    company_revenue = db.Column(db.String)
    n_employees = db.Column(db.String)
    company_phone = db.Column(db.String)
    company_founding_year = db.Column(db.Float)
    company_address = db.Column(db.String)
    company_industry = db.Column(db.String)
    homepage_base_url = db.Column(db.String, unique=True)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String)
    event_start_date = db.Column(db.Date)
    event_end_date = db.Column(db.Date)
    event_city = db.Column(db.String)
    event_state = db.Column(db.String)
    event_country = db.Column(db.String)
    event_description = db.Column(db.String)
    event_url = db.Column(db.String, unique=True)

class Person(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    middle_name = db.Column(db.String)
    last_name = db.Column(db.String)
    job_title = db.Column(db.String)
    person_city = db.Column(db.String)
    person_state = db.Column(db.String)
    person_country = db.Column(db.String)
    email_pattern = db.Column(db.String)
    homepage_base_url = db.Column(db.String, db.ForeignKey('companies.homepage_base_url'))
