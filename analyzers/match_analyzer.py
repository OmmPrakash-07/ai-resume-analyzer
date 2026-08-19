import re
import unicodedata

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


TECHNICAL_SKILLS = {
    "Python": ["python"],
    "Java": ["java"],
    "C": ["c language", "programming in c", "c"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "c sharp"],
    "SQL": ["sql", "mysql", "postgresql", "sqlite", "oracle sql"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular"],
    "Vue.js": ["vue", "vue.js", "vuejs"],
    "Node.js": ["node", "node.js", "nodejs"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "Spring": ["spring framework", "spring"],
    "Spring Boot": ["spring boot"],
    "REST API": ["rest api", "restful api", "rest services"],
    "Web Services": ["web services", "web service"],
    "Database": ["database", "databases", "dbms"],
    "Linux": ["linux", "ubuntu"],
    "Git": ["git", "github", "gitlab"],
    "Docker": ["docker", "containers"],
    "Kubernetes": ["kubernetes", "k8s"],
    "DevOps": ["devops", "dev ops"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "Google Cloud": ["gcp", "google cloud"],
    "Machine Learning": ["machine learning", "ml"],
    "Artificial Intelligence": ["artificial intelligence", "generative ai"],
    "Data Structures": ["data structures", "dsa"],
    "OOP": ["object-oriented programming", "object oriented programming", "oop"],
    "MongoDB": ["mongodb", "mongo db"],
    "Firebase": ["firebase", "firestore"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
}


SOFT_SKILLS = {
    "Communication": [
        "communication",
        "verbal communication",
        "written communication",
    ],
    "Interpersonal Skills": ["interpersonal", "interpersonal skills"],
    "Presentation": ["presentation", "presentation skills"],
    "Analytical Skills": [
        "analytical",
        "analytical skills",
        "analytical thinking",
    ],
    "Problem Solving": ["problem solving", "problem-solving"],
    "Teamwork": ["teamwork", "team player", "collaboration"],
    "Leadership": ["leadership", "team management"],
    "Multitasking": ["multitasking", "multi task", "multi-task"],
    "Customer Service": ["customer service", "customer support"],
    "Adaptability": ["adaptability", "adaptable", "flexibility"],
    "Time Management": ["time management"],
}


def normalize_text(text: str) -> str:
    """Normalize text for consistent matching."""

    return unicodedata.normalize("NFKC", text).casefold()


def contains_alias(text: str, alias: str) -> bool:
    """Check for a complete skill name without partial-word matches."""

    normalized_text = normalize_text(text)
    normalized_alias = normalize_text(alias)
    escaped_alias = re.escape(normalized_alias)

    pattern = rf"(?<![\w+#]){escaped_alias}(?![\w+#])"

    return re.search(pattern, normalized_text) is not None


def find_skills(text: str, skill_catalog: dict) -> list[str]:
    """Return canonical skills detected in the supplied text."""

    detected_skills = []

    for skill_name, aliases in skill_catalog.items():
        if any(contains_alias(text, alias) for alias in aliases):
            detected_skills.append(skill_name)

    return sorted(detected_skills)


def calculate_match_percentage(
    required_skills: list[str],
    resume_skills: list[str],
) -> float:
    """Calculate how many job-description skills appear in the resume."""

    if not required_skills:
        return 0.0

    required_set = set(required_skills)
    resume_set = set(resume_skills)

    matched = required_set.intersection(resume_set)

    return round((len(matched) / len(required_set)) * 100, 2)


def calculate_text_similarity(
    resume_text: str,
    job_description: str,
) -> float:
    """Calculate TF-IDF cosine similarity between both documents."""

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
        )

        vectors = vectorizer.fit_transform(
            [resume_text, job_description]
        )

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2],
        )[0][0]

        return round(float(similarity) * 100, 2)

    except ValueError:
        return 0.0


def calculate_overall_score(
    technical_score: float,
    soft_skill_score: float,
    similarity_score: float,
    has_technical_skills: bool,
    has_soft_skills: bool,
) -> float:
    """Calculate a dynamically weighted estimated job-match score."""

    weighted_scores = []

    if has_technical_skills:
        weighted_scores.append((technical_score, 55))

    if has_soft_skills:
        weighted_scores.append((soft_skill_score, 15))

    weighted_scores.append((similarity_score, 30))

    total_weight = sum(weight for _, weight in weighted_scores)

    final_score = sum(
        score * weight
        for score, weight in weighted_scores
    ) / total_weight

    return round(final_score, 2)


def analyze_match(
    resume_text: str,
    job_description: str,
) -> dict:
    """Generate the complete initial matching result."""

    resume_technical = find_skills(
        resume_text,
        TECHNICAL_SKILLS,
    )
    job_technical = find_skills(
        job_description,
        TECHNICAL_SKILLS,
    )

    resume_soft = find_skills(
        resume_text,
        SOFT_SKILLS,
    )
    job_soft = find_skills(
        job_description,
        SOFT_SKILLS,
    )

    matched_technical = sorted(
        set(job_technical).intersection(resume_technical)
    )
    missing_technical = sorted(
        set(job_technical).difference(resume_technical)
    )

    matched_soft = sorted(
        set(job_soft).intersection(resume_soft)
    )
    missing_soft = sorted(
        set(job_soft).difference(resume_soft)
    )

    technical_score = calculate_match_percentage(
        job_technical,
        resume_technical,
    )
    soft_skill_score = calculate_match_percentage(
        job_soft,
        resume_soft,
    )
    similarity_score = calculate_text_similarity(
        resume_text,
        job_description,
    )

    overall_score = calculate_overall_score(
        technical_score=technical_score,
        soft_skill_score=soft_skill_score,
        similarity_score=similarity_score,
        has_technical_skills=bool(job_technical),
        has_soft_skills=bool(job_soft),
    )

    return {
        "overall_score": overall_score,
        "technical_score": technical_score,
        "soft_skill_score": soft_skill_score,
        "similarity_score": similarity_score,
        "job_technical_skills": job_technical,
        "resume_technical_skills": resume_technical,
        "matched_technical": matched_technical,
        "missing_technical": missing_technical,
        "job_soft_skills": job_soft,
        "resume_soft_skills": resume_soft,
        "matched_soft": matched_soft,
        "missing_soft": missing_soft,
    }