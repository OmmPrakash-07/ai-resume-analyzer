import re


SECTION_ALIASES = {
    "summary": {
        "summary",
        "professional summary",
        "career summary",
        "profile",
        "professional profile",
        "career objective",
        "objective",
    },
    "skills": {
        "skills",
        "technical skills",
        "key skills",
        "core skills",
        "core competencies",
        "areas of expertise",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "internship",
        "internships",
    },
    "education": {
        "education",
        "academic background",
        "academic qualifications",
        "educational qualifications",
        "qualifications",
    },
    "projects": {
        "projects",
        "academic projects",
        "personal projects",
        "key projects",
        "project experience",
    },
    "certifications": {
        "certifications",
        "certificates",
        "licenses and certifications",
        "courses and certifications",
    },
}


EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

ONLINE_PROFILE_PATTERN = (
    r"(linkedin\.com|github\.com|portfolio|https?://|www\.)"
)

DATE_PATTERN = (
    r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
    r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|"
    r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"\s+(?:19|20)\d{2}\b|"
    r"\b(?:19|20)\d{2}\b"
)


def normalize_heading(line: str) -> str:
    """Normalize a possible section heading."""

    line = line.casefold().strip()
    line = re.sub(r"[^a-z\s]", "", line)
    line = re.sub(r"\s+", " ", line)

    return line.strip()


def find_sections(resume_text: str) -> dict:
    """Find standard resume headings."""

    lines = [
        normalize_heading(line)
        for line in resume_text.splitlines()
        if 0 < len(line.strip()) <= 50
    ]

    sections_found = {}

    for section_name, aliases in SECTION_ALIASES.items():
        sections_found[section_name] = any(
            line in aliases
            for line in lines
        )

    return sections_found


def contains_phone_number(text: str) -> bool:
    """Find a possible telephone number."""

    candidates = re.findall(
        r"\+?(?:\d[\s().-]*){10,13}",
        text,
    )

    for candidate in candidates:
        digits = re.sub(r"\D", "", candidate)

        if 10 <= len(digits) <= 13:
            return True

    return False


def calculate_unusual_character_ratio(text: str) -> float:
    """Measure characters that may cause parsing problems."""

    allowed_symbols = set(
        ".,:;!?()[]{}+-_/@#%&'\"|•–—"
    )

    unusual_characters = sum(
        1
        for character in text
        if not character.isalnum()
        and not character.isspace()
        and character not in allowed_symbols
    )

    if not text:
        return 1.0

    return unusual_characters / len(text)


def analyze_ats(
    resume_text: str,
    filename: str,
    extension: str,
) -> dict:
    """Calculate a transparent ATS-readability estimate."""

    checks = []
    word_count = len(resume_text.split())
    sections = find_sections(resume_text)

    def add_check(
        name: str,
        points: int,
        maximum: int,
        message: str,
    ) -> None:
        checks.append(
            {
                "name": name,
                "points": points,
                "maximum": maximum,
                "passed": points == maximum,
                "message": message,
            }
        )

    # 1. Text parseability: 20 points
    if word_count >= 100:
        add_check(
            "Text parseability",
            20,
            20,
            "The résumé contains enough extractable text.",
        )
    elif word_count >= 50:
        add_check(
            "Text parseability",
            10,
            20,
            "Only a limited amount of text was extracted.",
        )
    else:
        add_check(
            "Text parseability",
            0,
            20,
            "Very little text was extracted.",
        )

    # 2. Contact information: 15 points
    email_found = bool(
        re.search(EMAIL_PATTERN, resume_text)
    )
    phone_found = contains_phone_number(resume_text)
    online_profile_found = bool(
        re.search(
            ONLINE_PROFILE_PATTERN,
            resume_text,
            re.IGNORECASE,
        )
    )

    add_check(
        "Email address",
        7 if email_found else 0,
        7,
        (
            "An email address was detected."
            if email_found
            else "Add a professional email address."
        ),
    )

    add_check(
        "Phone number",
        6 if phone_found else 0,
        6,
        (
            "A phone number was detected."
            if phone_found
            else "Add a reachable phone number."
        ),
    )

    add_check(
        "Professional link",
        2 if online_profile_found else 0,
        2,
        (
            "A professional or portfolio link was detected."
            if online_profile_found
            else "Consider adding LinkedIn, GitHub or a portfolio."
        ),
    )

    # 3. Standard sections: 30 points
    section_scores = {
        "summary": 5,
        "skills": 7,
        "experience": 7,
        "education": 7,
    }

    for section_name, maximum_points in section_scores.items():
        found = sections[section_name]

        add_check(
            f"{section_name.title()} section",
            maximum_points if found else 0,
            maximum_points,
            (
                f"A standard {section_name} heading was detected."
                if found
                else f"Add a clearly labelled {section_name.title()} section."
            ),
        )

    optional_section_found = (
        sections["projects"]
        or sections["certifications"]
    )

    add_check(
        "Projects or certifications",
        4 if optional_section_found else 0,
        4,
        (
            "A Projects or Certifications section was detected."
            if optional_section_found
            else "Consider adding Projects or Certifications."
        ),
    )

    # 4. Employment or education dates: 10 points
    dates_found = re.findall(
        DATE_PATTERN,
        resume_text,
        re.IGNORECASE,
    )

    if len(dates_found) >= 2:
        date_points = 10
        date_message = "Multiple résumé dates were detected."
    elif len(dates_found) == 1:
        date_points = 5
        date_message = "Only one résumé date was detected."
    else:
        date_points = 0
        date_message = "Add clear dates to education and experience."

    add_check(
        "Dates and chronology",
        date_points,
        10,
        date_message,
    )

    # 5. Resume length: 10 points
    if 250 <= word_count <= 1000:
        length_points = 10
        length_message = "The résumé length is appropriate."
    elif 150 <= word_count <= 1500:
        length_points = 7
        length_message = "The résumé length is acceptable."
    else:
        length_points = 3
        length_message = "Review the résumé length and content density."

    add_check(
        "Resume length",
        length_points,
        10,
        length_message,
    )

    # 6. File format: 5 points
    supported_format = extension.lower() in {
        ".pdf",
        ".docx",
    }

    add_check(
        "File format",
        5 if supported_format else 0,
        5,
        (
            f"{extension.upper()} is a supported format."
            if supported_format
            else "Use a text-based PDF or DOCX file."
        ),
    )

    # 7. Formatting quality: 10 points
    unusual_ratio = calculate_unusual_character_ratio(
        resume_text
    )

    if unusual_ratio <= 0.01:
        character_points = 5
        character_message = "No problematic character usage detected."
    elif unusual_ratio <= 0.03:
        character_points = 3
        character_message = "Some unusual characters were detected."
    else:
        character_points = 0
        character_message = "Remove excessive decorative characters."

    add_check(
        "Character readability",
        character_points,
        5,
        character_message,
    )

    non_empty_lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    longest_line = max(
        (len(line) for line in non_empty_lines),
        default=0,
    )

    if len(non_empty_lines) >= 8 and longest_line <= 300:
        structure_points = 5
        structure_message = "The extracted text has a readable structure."
    elif len(non_empty_lines) >= 4:
        structure_points = 3
        structure_message = "The text structure may need improvement."
    else:
        structure_points = 0
        structure_message = "The résumé structure may be difficult to parse."

    add_check(
        "Text structure",
        structure_points,
        5,
        structure_message,
    )

    total_score = sum(
        check["points"]
        for check in checks
    )

    if total_score >= 85:
        rating = "Excellent"
    elif total_score >= 70:
        rating = "Good"
    elif total_score >= 50:
        rating = "Needs Improvement"
    else:
        rating = "Poor"

    missing_sections = [
        name
        for name, found in sections.items()
        if not found
    ]

    return {
        "score": total_score,
        "rating": rating,
        "checks": checks,
        "sections": sections,
        "missing_sections": missing_sections,
        "word_count": word_count,
        "filename": filename,
    }