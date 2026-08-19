import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

URL_PATTERN = re.compile(
    r"\b(?:https?://|www\.)\S+|"
    r"\b(?:linkedin\.com|github\.com)/\S+",
    re.IGNORECASE,
)

PHONE_CANDIDATE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?\d[\d ().-]{8,}\d)(?!\d)"
)

AADHAAR_PATTERN = re.compile(
    r"(?<!\d)\d{4}\s?\d{4}\s?\d{4}(?!\d)"
)

PAN_PATTERN = re.compile(
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    re.IGNORECASE,
)

INDIAN_PIN_PATTERN = re.compile(
    r"\b[1-9][0-9]{5}\b"
)

SENSITIVE_LINE_PATTERN = re.compile(
    r"^\s*(?:"
    r"date of birth|dob|birth date|gender|sex|marital status|"
    r"father(?:'s)? name|mother(?:'s)? name|nationality|"
    r"religion|aadhaar|aadhar|pan number|passport number"
    r")\s*[:\-].*$",
    re.IGNORECASE,
)

NAME_EXCLUSIONS = {
    "resume",
    "curriculum vitae",
    "professional profile",
    "professional summary",
    "career objective",
    "software engineer",
    "software developer",
    "web developer",
    "full stack developer",
    "frontend developer",
    "backend developer",
    "python developer",
    "java developer",
    "data analyst",
    "data scientist",
    "business analyst",
    "project manager",
}

ROLE_WORDS = {
    "developer",
    "engineer",
    "analyst",
    "manager",
    "intern",
    "designer",
    "consultant",
    "specialist",
    "student",
    "executive",
    "associate",
}

ADDRESS_WORDS = {
    "road",
    "street",
    "lane",
    "colony",
    "nagar",
    "apartment",
    "flat",
    "sector",
    "village",
    "district",
    "pincode",
    "pin code",
    "postal code",
}


def detect_candidate_name(text: str) -> str | None:
    """Conservatively detect a candidate name near the résumé header."""

    header_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ][:4]

    for line in header_lines:
        normalized_line = re.sub(
            r"\s+",
            " ",
            line,
        ).strip()

        lowercase_line = normalized_line.casefold()

        if lowercase_line in NAME_EXCLUSIONS:
            continue

        if any(
            word in lowercase_line.split()
            for word in ROLE_WORDS
        ):
            continue

        if "@" in normalized_line:
            continue

        if re.search(r"\d", normalized_line):
            continue

        if not re.fullmatch(
            r"[A-Za-z][A-Za-z .'’-]+",
            normalized_line,
        ):
            continue

        words = normalized_line.split()

        if not 2 <= len(words) <= 5:
            continue

        looks_like_name = (
            normalized_line.isupper()
            or all(
                word[0].isupper()
                for word in words
                if word
            )
        )

        if looks_like_name:
            return normalized_line

    return None


def redact_phone_numbers(
    text: str,
) -> tuple[str, int]:
    """Redact number sequences only when they resemble phone numbers."""

    replacement_count = 0

    def replace_candidate(match: re.Match) -> str:
        nonlocal replacement_count

        candidate = match.group(0)
        digits = re.sub(r"\D", "", candidate)

        if 10 <= len(digits) <= 13:
            replacement_count += 1
            return "[PHONE REDACTED]"

        return candidate

    redacted_text = PHONE_CANDIDATE_PATTERN.sub(
        replace_candidate,
        text,
    )

    return redacted_text, replacement_count


def redact_header_addresses(
    text: str,
) -> tuple[str, int]:
    """Redact likely address lines near the top of the résumé."""

    lines = text.splitlines()
    replacement_count = 0

    for index, line in enumerate(lines):
        if index >= 12:
            break

        lowercase_line = line.casefold()

        has_address_word = any(
            word in lowercase_line
            for word in ADDRESS_WORDS
        )

        has_postal_code = bool(
            INDIAN_PIN_PATTERN.search(line)
        )

        if has_address_word or has_postal_code:
            lines[index] = "[ADDRESS REDACTED]"
            replacement_count += 1

    return "\n".join(lines), replacement_count


def redact_sensitive_lines(
    text: str,
) -> tuple[str, int]:
    """Remove sensitive personal-profile fields."""

    lines = text.splitlines()
    replacement_count = 0

    for index, line in enumerate(lines):
        if SENSITIVE_LINE_PATTERN.match(line):
            lines[index] = "[PERSONAL DETAIL REDACTED]"
            replacement_count += 1

    return "\n".join(lines), replacement_count


def redact_personal_information(
    text: str,
) -> dict:
    """Return anonymized résumé text and a redaction report."""

    redacted_text = text
    redactions = {
        "name": 0,
        "email": 0,
        "phone": 0,
        "url": 0,
        "aadhaar": 0,
        "pan": 0,
        "address": 0,
        "sensitive_fields": 0,
    }

    candidate_name = detect_candidate_name(
        redacted_text
    )

    if candidate_name:
        name_pattern = re.compile(
            re.escape(candidate_name),
            re.IGNORECASE,
        )

        redacted_text, count = name_pattern.subn(
            "[NAME REDACTED]",
            redacted_text,
        )

        redactions["name"] = count

    redacted_text, count = EMAIL_PATTERN.subn(
        "[EMAIL REDACTED]",
        redacted_text,
    )
    redactions["email"] = count

    redacted_text, count = URL_PATTERN.subn(
        "[URL REDACTED]",
        redacted_text,
    )
    redactions["url"] = count

    redacted_text, count = AADHAAR_PATTERN.subn(
        "[AADHAAR REDACTED]",
        redacted_text,
    )
    redactions["aadhaar"] = count

    redacted_text, count = PAN_PATTERN.subn(
        "[PAN REDACTED]",
        redacted_text,
    )
    redactions["pan"] = count

    redacted_text, phone_count = redact_phone_numbers(
        redacted_text
    )
    redactions["phone"] = phone_count

    redacted_text, address_count = redact_header_addresses(
        redacted_text
    )
    redactions["address"] = address_count

    redacted_text, sensitive_count = redact_sensitive_lines(
        redacted_text
    )
    redactions["sensitive_fields"] = sensitive_count

    total_redactions = sum(redactions.values())

    return {
        "text": redacted_text,
        "redactions": redactions,
        "total_redactions": total_redactions,
        "candidate_name_detected": candidate_name is not None,
    }