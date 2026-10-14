from datetime import datetime

# (field name, label shown in the error message, max length)
REQUIRED_TEXT = [
    ("title", "Research title", 200),
    ("description", "Research description", 5000),
    ("research_area", "Research area", 100),
    ("faculty_name", "Faculty member's name", 100),
    ("department", "Department", 100),
    ("required_skills", "Required skills", 300),
]


def validate_opportunity(body):
    """Check the data. Returns (errors, clean_data)."""
    errors = []
    data = {}

    # 1. text fields must be present, not empty, and not too long
    for key, label, max_len in REQUIRED_TEXT:
        value = body.get(key)
        value = value.strip() if isinstance(value, str) else ""
        if not value:
            errors.append(f"{label} is required")
        elif len(value) > max_len:
            errors.append(f"{label} must be at most {max_len} characters")
        data[key] = value

    # 2. positions must be a whole number >= 1
    raw = body.get("positions")
    positions = None
    if raw is None or raw == "":
        errors.append("Number of available positions is required")
    else:
        try:
            if isinstance(raw, bool):
                raise ValueError
            if isinstance(raw, float) and not raw.is_integer():
                raise ValueError
            positions = int(raw)
            if positions < 1:
                raise ValueError
        except (ValueError, TypeError):
            positions = None
            errors.append("Number of available positions must be a whole number of at least 1")
    data["positions"] = positions

    # 3. deadline must be a real date in YYYY-MM-DD format
    deadline = body.get("deadline")
    deadline = deadline.strip() if isinstance(deadline, str) else ""
    if not deadline:
        errors.append("Application deadline is required")
    else:
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            errors.append("Application deadline must be a valid date in YYYY-MM-DD format")
    data["deadline"] = deadline

    # 4. status must be Open or Closed (Open if not given)
    status = body.get("status")
    if status is None or status == "":
        status = "Open"
    if status not in ("Open", "Closed"):
        errors.append("Status must be either 'Open' or 'Closed'")
    data["status"] = status

    return errors, data
