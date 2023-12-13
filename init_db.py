from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table

engine = create_engine('sqlite:///github_events.db')
metadata = MetaData()

events = Table(
    'events', metadata,
    Column('id', Integer, primary_key=True),
    Column('event_type', String),
    Column('repository_name', String),
    Column('timestamp', DateTime)
)

metadata.create_all(engine)
