# github_event_tracker.py
import requests
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table
from sqlalchemy.orm import sessionmaker
from config import GITHUB_TOKEN, REPOSITORIES, DATABASE_URI

engine = create_engine(DATABASE_URI)
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()

events = Table(
    "events",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("event_type", String),
    Column("repository_name", String),
    Column("timestamp", DateTime),
)


def fetch_github_events():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    base_url = "https://api.github.com/repos/"

    for repo in REPOSITORIES:
        url = f"{base_url}{repo}/events"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            for event in data:
                event_type = event["type"]
                timestamp = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")

                # Check if the event is not already in the database
                if (
                    not session.query(events)
                    .filter_by(
                        event_type=event_type, repository_name=repo, timestamp=timestamp
                    )
                    .first()
                ):
                    session.execute(
                        events.insert().values(
                            event_type=event_type,
                            repository_name=repo,
                            timestamp=timestamp,
                        )
                    )

    session.commit()


if __name__ == "__main__":
    fetch_github_events()
