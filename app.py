# app.py
from flask import Flask, jsonify
from sqlalchemy import func
from main import engine, events

app = Flask(__name__)


@app.route("/statistics")
def get_statistics():
    result = []
    for repo in REPOSITORIES:
        for event_type in session.query(events.c.event_type).distinct():
            avg_time = (
                session.query(func.avg(events.c.timestamp - events.c.timestamp))
                .filter_by(event_type=event_type[0], repository_name=repo)
                .scalar()
            )
            result.append(
                {
                    "repository": repo,
                    "event_type": event_type[0],
                    "average_time": avg_time,
                }
            )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
