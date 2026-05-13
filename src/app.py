"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(Path(__file__).parent, "static")),
    name="static",
)

activities_file = current_dir / "activities.json"

DEFAULT_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
}


def load_activities():
    if not activities_file.exists():
        save_activities(DEFAULT_ACTIVITIES)

    with open(activities_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_activities(data):
    with open(activities_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


activities = load_activities()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    activity["participants"].append(email)
    save_activities(activities)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    activity["participants"].remove(email)
    save_activities(activities)
    return {"message": f"Unregistered {email} from {activity_name}"}


@app.post("/admin/activities")
def create_activity(activity: dict):
    """Create a new extracurricular activity."""
    name = activity.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Activity name is required")

    if name in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")

    description = activity.get("description", "")
    schedule = activity.get("schedule", "")
    max_participants = activity.get("max_participants")

    if max_participants is None or not isinstance(max_participants, int):
        raise HTTPException(status_code=400, detail="max_participants must be an integer")

    activities[name] = {
        "description": description,
        "schedule": schedule,
        "max_participants": max_participants,
        "participants": [],
    }
    save_activities(activities)
    return {"message": f"Created activity '{name}'"}


@app.put("/admin/activities/{activity_name}")
def update_activity(activity_name: str, update: dict):
    """Update an existing extracurricular activity."""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    if "description" in update:
        activity["description"] = update["description"]
    if "schedule" in update:
        activity["schedule"] = update["schedule"]
    if "max_participants" in update:
        if not isinstance(update["max_participants"], int):
            raise HTTPException(status_code=400, detail="max_participants must be an integer")
        if update["max_participants"] < len(activity["participants"]):
            raise HTTPException(
                status_code=400,
                detail="max_participants cannot be smaller than the current number of participants",
            )
        activity["max_participants"] = update["max_participants"]
    if "participants" in update:
        if not isinstance(update["participants"], list):
            raise HTTPException(status_code=400, detail="participants must be a list")
        activity["participants"] = update["participants"]

    save_activities(activities)
    return {"message": f"Updated activity '{activity_name}'"}


@app.delete("/admin/activities/{activity_name}")
def delete_activity(activity_name: str):
    """Delete an extracurricular activity."""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    del activities[activity_name]
    save_activities(activities)
    return {"message": f"Deleted activity '{activity_name}'"}
