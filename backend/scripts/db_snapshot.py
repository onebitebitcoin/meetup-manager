#!/usr/bin/env python3
"""Generate a compact DB snapshot for migration verification."""
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get("DJANGO_SETTINGS_MODULE", "meetup_backend.settings"))

import django  # noqa: E402
from django.apps import apps  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402
from django.db import connection  # noqa: E402
from django.db.models import Max  # noqa: E402


def model_snapshot(model):
    data = {
        "count": model.objects.count(),
    }
    if any(field.name == "id" for field in model._meta.fields):
        data["max_id"] = model.objects.aggregate(value=Max("id"))["value"]
    for field_name in ("created_at", "updated_at", "submitted_at", "registered_at", "waitlisted_at"):
        if any(field.name == field_name for field in model._meta.fields):
            value = model.objects.aggregate(value=Max(field_name))["value"]
            data[f"max_{field_name}"] = value.isoformat() if value else None
            break
    return data


def main():
    django.setup()
    selected = [
        get_user_model(),
        apps.get_model("meetups", "MeetupUser"),
        apps.get_model("meetups", "Meetup"),
        apps.get_model("meetups", "Registration"),
        apps.get_model("meetups", "Waitlist"),
        apps.get_model("meetups", "Notification"),
        apps.get_model("meetups", "Task"),
        apps.get_model("meetups", "TaskSubmission"),
        apps.get_model("meetups", "Review"),
        apps.get_model("meetups", "MeetupPaymentLink"),
    ]
    payload = {
        "engine": connection.settings_dict["ENGINE"],
        "database": connection.settings_dict["NAME"],
        "models": {model._meta.label: model_snapshot(model) for model in selected},
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
