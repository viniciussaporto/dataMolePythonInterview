# main.py
import requests
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify

app = Flask(__name__)

DATABASE_URI = "sqlite:///github_events.db"  # Change this to your actual database URI
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"
REPOSITORIES = [
    "MartinSeeler/Advent-of-Code",
    "discordjs/discord.js",
    "torvalds/linux",
]  # Add or remove repositories as needed

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

        retries = 3
        for _ in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"Error fetching events for {repo}: {e}")
                time.sleep(5)

        else:
            print(f"Max retries exceeded for {repo}. Could not fetch events.")
            continue

        if response.status_code == 401:
            print(
                f"Error fetching events for {repo}: 401 Unauthorized. Response content: {response.content}"
            )
            continue

        if response.status_code == 200:
            data = response.json()

            # Filter events within the last 7 days or up to 500 events, whichever is less
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            recent_events = [
                event
                for event in data
                if datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                > cutoff_date
            ][:500]

            for event in recent_events:
                event_type = event["type"]
                timestamp = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")

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


def calculate_average_times():
    averages = []

    for repo in REPOSITORIES:
        for event_type in session.query(events.c.event_type).distinct():
            query_result = (
                session.query(events.c.timestamp)
                .filter_by(repository_name=repo, event_type=event_type[0])
                .order_by(events.c.timestamp)
                .all()
            )

            timestamps = [timestamp[0] for timestamp in query_result]

            if not timestamps:
                averages.append(
                    {
                        "average_time": None,
                        "event_type": event_type[0],
                        "repository": repo,
                        "message": "No events available",
                    }
                )
            else:
                if len(timestamps) > 1:
                    average_time = sum(
                        (timestamps[i + 1] - timestamps[i]).total_seconds()
                        for i in range(len(timestamps) - 1)
                    ) / (len(timestamps) - 1)
                else:
                    average_time = None

                averages.append(
                    {
                        "average_time": average_time,
                        "event_type": event_type[0],
                        "repository": repo,
                        "first_timestamp": timestamps[0],
                        "last_timestamp": timestamps[-1],
                    }
                )

    return averages


@app.route("/statistics")
def get_statistics():
    averages = calculate_average_times()
    return jsonify(averages)


if __name__ == "__main__":
    while True:
        fetch_github_events()
        time.sleep(15)  # Adjust the interval as needed
        app.run(debug=True, port=5000)
