import json
from enum import Enum
from src.config import SCHEMA_REGISTRY


class ErrorType(Enum):
    INVALID_JSON = "invalid_json"
    MISSING_FIELD = "missing_field"
    EXTRA_FIELD = "extra_field"
    WRONG_TYPE = "wrong_type"


class ValidationError:
    def __init__(self, error_type, message, field=None):
        self.error_type = error_type
        self.message = message
        self.field = field

    def to_dict(self):
        return {"type": self.error_type.value, "message": self.message, "field": self.field}

    def __str__(self):
        return self.message


class ValidationResult:
    def __init__(self, is_valid, data=None, errors=None):
        self.is_valid = is_valid
        self.data = data
        self.errors = errors or []

    def to_dict(self):
        return {
            "is_valid": self.is_valid,
            "data": self.data,
            "errors": [e.to_dict() for e in self.errors],
        }


def _extract_json_from_markdown(text):
    """If the model wraps output in ```json ... ```, extract the inner content."""
    lines = text.split("\n")
    json_lines = []
    in_block = False
    for line in lines:
        if line.startswith("```") and not in_block:
            in_block = True
            continue
        elif line.startswith("```") and in_block:
            break
        elif in_block:
            json_lines.append(line)
    return "\n".join(json_lines) if json_lines else text


def validate_output(raw_output, category):
    """Run 4 validation layers on model output and return a ValidationResult."""
    errors = []
    raw_output = raw_output.strip()

    if raw_output.startswith("```"):
        raw_output = _extract_json_from_markdown(raw_output)

    # layer 1: parse JSON
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as e:
        errors.append(ValidationError(ErrorType.INVALID_JSON, f"Not valid JSON: {e}"))
        return ValidationResult(False, errors=errors)

    if not isinstance(data, dict):
        errors.append(ValidationError(ErrorType.INVALID_JSON, f"Expected object, got {type(data).__name__}"))
        return ValidationResult(False, errors=errors)

    schema = SCHEMA_REGISTRY.get(category)
    if schema is None:
        return ValidationResult(True, data=data)

    # layer 2: check required fields
    for field in schema["required_fields"]:
        if field not in data:
            errors.append(ValidationError(ErrorType.MISSING_FIELD, f"Missing required field: '{field}'", field))

    # layer 3: reject extra fields
    allowed = set(schema["field_types"].keys())
    for field in data:
        if field not in allowed:
            errors.append(ValidationError(ErrorType.EXTRA_FIELD, f"Unexpected field: '{field}'", field))

    # layer 4: type checking
    for field, expected in schema["field_types"].items():
        if field not in data or data[field] is None:
            continue
        if isinstance(expected, tuple):
            if not isinstance(data[field], expected):
                errors.append(ValidationError(
                    ErrorType.WRONG_TYPE, f"'{field}' should be {expected}, got {type(data[field]).__name__}", field
                ))
        elif not isinstance(data[field], expected):
            errors.append(ValidationError(
                ErrorType.WRONG_TYPE, f"'{field}' should be {expected.__name__}, got {type(data[field]).__name__}", field
            ))

    return ValidationResult(len(errors) == 0, data=data, errors=errors)


def get_error_summary(errors):
    """Return list of error message strings (used for retry prompt)."""
    return [str(e) for e in errors]


def get_error_taxonomy(errors):
    """Count errors by type."""
    taxonomy = {et.value: 0 for et in ErrorType}
    for e in errors:
        taxonomy[e.error_type.value] += 1
    return taxonomy
