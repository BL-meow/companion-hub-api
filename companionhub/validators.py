def validate_companion_body(data, partial=False):
    if not isinstance(data, dict):
        return {}, {}, "invalid_json"

    details = {}
    normalized_data = {}

    for field in ("name", "personality"):
        if partial and field not in data:
            continue

        value = data.get(field)

        if not isinstance(value, str) or not value.strip():
            details[field] = f"{field.capitalize()} is required."
        elif field == "name" and len(value.strip()) > 100:
            details[field] = "Name must not exceed 100 characters."
        else:
            normalized_data[field] = value.strip()

    for field in ("backstory", "appearance", "greeting"):
        if partial and field not in data:
            continue

        value = data.get(field)

        if value is not None and not isinstance(value, str):
            details[field] = "Must be a string."
        else:
            normalized_data[field] = value

    if not partial or "is_public" in data:
        is_public = data.get("is_public", False)

        if not isinstance(is_public, bool):
            details["is_public"] = "Must be a boolean."
        else:
            normalized_data["is_public"] = is_public

    if details:
        return normalized_data, details, "validation_error"

    return normalized_data, {}, None