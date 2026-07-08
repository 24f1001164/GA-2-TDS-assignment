from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from collections import defaultdict
import app

API_KEY = "ak_syczabztn8fie3a69o0y5gov"

# CHANGE THIS TO YOUR IITM EMAIL
EMAIL = "YOUR_EMAIL@ds.study.iitm.ac.in"

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: List[Event]


@app.post("/analytics")
def analytics(
    data: AnalyticsRequest,
    x_api_key: str = Header(None)
):
    # Authentication
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    total_events = len(data.events)

    unique_users = len(set(event.user for event in data.events))

    revenue = 0.0

    user_totals = defaultdict(float)

    for event in data.events:
        if event.amount > 0:
            revenue += event.amount
            user_totals[event.user] += event.amount

    top_user = ""

    if user_totals:
        top_user = max(user_totals, key=user_totals.get)

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user
    }
