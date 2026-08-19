import streamlit as st

from analyzers.ats_analyzer import analyze_ats
from analyzers.match_analyzer import analyze_match
from parsers.resume_parser import extract_resume_text
from services.gemini_service import analyze_with_gemini


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)


# Store results between Streamlit reruns.
if "analysis_bundle" not in st.session_state:
    st.session_state.analysis_bundle = None

if "gemini_result" not in st.session_state:
    st.session_state.gemini_result = None


def display_list(
    items: list,
    icon: str,
    empty_message: str,
) -> None:
    """Display a list safely."""

    if items:
        for item in items:
            st.write(f"{icon} {item}")
    else:
        st.write(empty_message)


def safe_score(data: dict, *keys: str) -> int:
    """Return the first available numeric score."""

    for key in keys:
        value = data.get(key)

        if isinstance(value, (int, float)):
            return max(
                0,
                min(100, round(value)),
            )

    return 0


# ---------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------

st.title("📄 AI Resume Analyzer")

st.write(
    "Upload your resume and paste a job description to check "
    "job compatibility, ATS friendliness and receive optional "
    "AI-powered recommendations."
)


# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------

resume_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"],
    help="Text-based PDF and DOCX resumes are supported.",
)

job_description = st.text_area(
    "Paste the job description",
    height=300,
    placeholder="Paste the complete job description here...",
)

analyze_button = st.button(
    "Analyze Resume",
    type="primary",
    use_container_width=True,
)


# ---------------------------------------------------------
# RUN LOCAL ATS AND JOB-MATCH ANALYSIS
# ---------------------------------------------------------

if analyze_button:
    if resume_file is None:
        st.error(
            "Please upload a PDF or DOCX resume."
        )

    elif not job_description.strip():
        st.error(
            "Please paste the job description."
        )

    else:
        try:
            resume_data = extract_resume_text(
                resume_file
            )

            match_result = analyze_match(
                resume_text=resume_data["text"],
                job_description=job_description,
            )

            ats_result = analyze_ats(
                resume_text=resume_data["text"],
                filename=resume_data["filename"],
                extension=resume_data["extension"],
            )

        except Exception as error:
            st.error(
                f"Resume analysis failed: {error}"
            )

        else:
            st.session_state.analysis_bundle = {
                "resume_data": resume_data,
                "job_description": job_description,
                "match_result": match_result,
                "ats_result": ats_result,
            }

            # Clear old Gemini results for a new analysis.
            st.session_state.gemini_result = None


# ---------------------------------------------------------
# DISPLAY LOCAL ANALYSIS
# ---------------------------------------------------------

analysis_bundle = st.session_state.analysis_bundle

if analysis_bundle is not None:
    resume_data = analysis_bundle["resume_data"]

    current_job_description = analysis_bundle[
        "job_description"
    ]

    match_result = analysis_bundle["match_result"]
    ats_result = analysis_bundle["ats_result"]

    job_match_score = safe_score(
        match_result,
        "overall_score",
        "match_score",
    )

    technical_score = safe_score(
        match_result,
        "technical_score",
        "skill_score",
    )

    similarity_score = safe_score(
        match_result,
        "similarity_score",
    )

    ats_score = safe_score(
        ats_result,
        "ats_score",
        "overall_score",
        "score",
    )

    st.success(
        "Resume analyzed successfully!"
    )

    st.caption(
        f"Uploaded file: {resume_data['filename']}"
    )

    st.divider()
    st.subheader("Analysis Overview")

    score1, score2, score3, score4 = st.columns(4)

    score1.metric(
        "Estimated Job Match",
        f"{job_match_score}%",
    )

    score2.metric(
        "ATS Readability",
        f"{ats_score}%",
    )

    score3.metric(
        "Technical Skill Match",
        f"{technical_score}%",
    )

    score4.metric(
        "Text Similarity",
        f"{similarity_score}%",
    )

    st.write("Job match")
    st.progress(job_match_score / 100)

    st.write("ATS friendliness")
    st.progress(ats_score / 100)

    st.divider()

    technical_tab, soft_tab, ats_tab = st.tabs(
        [
            "Technical Skills",
            "Soft Skills",
            "ATS Checks",
        ]
    )

    # -----------------------------------------------------
    # TECHNICAL SKILLS TAB
    # -----------------------------------------------------

    with technical_tab:
        matched_column, missing_column = st.columns(2)

        with matched_column:
            st.success(
                "Matched technical skills"
            )

            display_list(
                match_result.get(
                    "matched_technical",
                    [],
                ),
                "✅",
                (
                    "No matching technical skills "
                    "were detected."
                ),
            )

        with missing_column:
            st.error(
                "Missing technical skills"
            )

            display_list(
                match_result.get(
                    "missing_technical",
                    [],
                ),
                "❌",
                (
                    "No missing technical skills "
                    "were detected."
                ),
            )

    # -----------------------------------------------------
    # SOFT SKILLS TAB
    # -----------------------------------------------------

    with soft_tab:
        matched_column, missing_column = st.columns(2)

        with matched_column:
            st.success(
                "Matched soft skills"
            )

            display_list(
                match_result.get(
                    "matched_soft",
                    [],
                ),
                "✅",
                (
                    "No matching soft skills "
                    "were detected."
                ),
            )

        with missing_column:
            st.warning(
                "Missing soft skills"
            )

            display_list(
                match_result.get(
                    "missing_soft",
                    [],
                ),
                "⚠️",
                (
                    "No missing soft skills "
                    "were detected."
                ),
            )

    # -----------------------------------------------------
    # ATS CHECKS TAB
    # -----------------------------------------------------

    with ats_tab:
        sections = ats_result.get(
            "sections",
            {},
        )

        checks = ats_result.get(
            "checks",
            [],
        )

        found_sections = [
            section_name.title()
            for section_name, found in sections.items()
            if found
        ]

        missing_sections = [
            section_name.title()
            for section_name, found in sections.items()
            if not found
        ]

        ats1, ats2, ats3 = st.columns(3)

        ats1.metric(
            "ATS Score",
            f"{ats_score}%",
        )

        ats2.metric(
            "ATS Rating",
            ats_result.get(
                "rating",
                "Not available",
            ),
        )

        ats3.metric(
            "Resume Word Count",
            ats_result.get(
                "word_count",
                resume_data["words"],
            ),
        )

        section1, section2 = st.columns(2)

        with section1:
            st.success(
                "Detected resume sections"
            )

            display_list(
                found_sections,
                "✅",
                (
                    "No standard resume sections "
                    "were detected."
                ),
            )

        with section2:
            st.warning(
                "Missing or unclear sections"
            )

            display_list(
                missing_sections,
                "⚠️",
                (
                    "No important resume sections "
                    "appear to be missing."
                ),
            )

        st.markdown(
            "#### Detailed ATS checks"
        )

        if checks:
            for check in checks:
                check_name = check.get(
                    "name",
                    "ATS check",
                )

                points = check.get(
                    "points",
                    0,
                )

                maximum = check.get(
                    "maximum",
                    0,
                )

                message = check.get(
                    "message",
                    "",
                )

                passed = check.get(
                    "passed",
                    False,
                )

                icon = "✅" if passed else "⚠️"

                st.write(
                    f"{icon} **{check_name}** — "
                    f"{points}/{maximum} points"
                )

                if message:
                    st.caption(message)

        else:
            st.write(
                "No ATS checks were generated."
            )

        recommendations = [
            check.get("message", "")
            for check in checks
            if not check.get("passed", False)
            and check.get("message")
        ]

        if recommendations:
            st.markdown(
                "#### ATS recommendations"
            )

            display_list(
                recommendations,
                "💡",
                (
                    "No ATS recommendations "
                    "were generated."
                ),
            )

        with st.expander(
            "View complete ATS analysis data"
        ):
            st.json(ats_result)

    # -----------------------------------------------------
    # DOCUMENT STATISTICS
    # -----------------------------------------------------

    st.divider()

    document1, document2, document3 = st.columns(3)

    document1.metric(
        "Resume Words",
        resume_data["words"],
    )

    document2.metric(
        "Resume Characters",
        resume_data["characters"],
    )

    document3.metric(
        "Job Description Words",
        len(
            current_job_description.split()
        ),
    )

    # -----------------------------------------------------
    # GEMINI AI ANALYSIS
    # -----------------------------------------------------

    st.divider()
    st.subheader(
        "✨ Gemini AI Recommendations"
    )

    st.info(
        "This step is optional. Your resume is anonymized "
        "before being sent to Gemini. Names, email addresses, "
        "phone numbers and other detected personal information "
        "are removed."
    )

    consent_to_ai = st.checkbox(
        "I consent to sending the anonymized resume and job "
        "description to Google Gemini for AI analysis."
    )

    if not consent_to_ai:
        st.caption(
            "Enable the checkbox to generate "
            "AI recommendations."
        )

    gemini_button = st.button(
        "Generate AI Recommendations",
        type="secondary",
        use_container_width=True,
        disabled=not consent_to_ai,
    )

    if gemini_button:
        try:
            with st.spinner(
                "Gemini is analyzing the resume. "
                "This can take several seconds..."
            ):
                gemini_result = analyze_with_gemini(
                    resume_text=resume_data["text"],
                    job_description=(
                        current_job_description
                    ),
                )

                st.session_state.gemini_result = (
                    gemini_result
                )

        except Exception as error:
            error_message = str(error)

            rate_limit_error = (
                "429" in error_message
                or "too_many_requests"
                in error_message.lower()
                or "quota exceeded"
                in error_message.lower()
                or "resource_exhausted"
                in error_message.lower()
            )

            if rate_limit_error:
                st.warning(
                    "Gemini free-tier request limit was "
                    "temporarily reached. Please wait about "
                    "60 seconds and click the button once again."
                )

            elif "GEMINI_API_KEY" in error_message:
                st.error(
                    "Gemini API key is not configured. "
                    "Add GEMINI_API_KEY to your .env file."
                )

            else:
                st.error(
                    f"Gemini analysis failed: {error}"
                )

    # -----------------------------------------------------
    # DISPLAY GEMINI RESULTS
    # -----------------------------------------------------

    gemini_result = st.session_state.gemini_result

    if gemini_result is not None:
        analysis = gemini_result["analysis"]
        privacy = gemini_result["privacy"]

        st.success(
            "Gemini recommendations generated successfully!"
        )

        ai1, ai2, ai3 = st.columns(3)

        ai1.metric(
            "Target Role",
            analysis.get(
                "target_role",
                "Not identified",
            ),
        )

        ai2.metric(
            "AI Model",
            gemini_result.get(
                "model",
                "Gemini",
            ),
        )

        ai3.metric(
            "Personal Details Removed",
            privacy.get(
                "total_redactions",
                0,
            ),
        )

        (
            overview_tab,
            skills_tab,
            bullets_tab,
            evidence_tab,
            interview_tab,
        ) = st.tabs(
            [
                "AI Overview",
                "Skills & Keywords",
                "Bullet Improvements",
                "Evidence Checks",
                "Interview Preparation",
            ]
        )

        # -------------------------------------------------
        # GEMINI OVERVIEW
        # -------------------------------------------------

        with overview_tab:
            st.markdown(
                "#### Overall assessment"
            )

            st.write(
                analysis.get(
                    "overall_assessment",
                    "No assessment was generated.",
                )
            )

            st.markdown(
                "#### ATS-friendly summary"
            )

            st.info(
                analysis.get(
                    "tailored_summary",
                    "No summary was generated.",
                )
            )

            st.caption(
                "Review this summary before adding it to "
                "your resume. Keep only statements that "
                "are accurate."
            )

            st.markdown(
                "#### Supported strengths"
            )

            display_list(
                analysis.get(
                    "matched_strengths",
                    [],
                ),
                "✅",
                (
                    "No supported strengths "
                    "were identified."
                ),
            )

            warnings = analysis.get(
                "warnings",
                [],
            )

            if warnings:
                st.markdown(
                    "#### Important warnings"
                )

                for warning in warnings:
                    st.warning(warning)

        # -------------------------------------------------
        # GEMINI SKILLS
        # -------------------------------------------------

        with skills_tab:
            required_column, preferred_column = (
                st.columns(2)
            )

            with required_column:
                st.markdown(
                    "#### Required skills"
                )

                display_list(
                    analysis.get(
                        "required_skills",
                        [],
                    ),
                    "📌",
                    (
                        "No required skills "
                        "were identified."
                    ),
                )

            with preferred_column:
                st.markdown(
                    "#### Preferred skills"
                )

                display_list(
                    analysis.get(
                        "preferred_skills",
                        [],
                    ),
                    "⭐",
                    (
                        "No preferred skills "
                        "were identified."
                    ),
                )

            st.markdown(
                "#### Missing requirements"
            )

            display_list(
                analysis.get(
                    "missing_requirements",
                    [],
                ),
                "❌",
                (
                    "No missing requirements "
                    "were identified."
                ),
            )

            st.markdown(
                "#### Recommended keywords"
            )

            st.warning(
                "Add these keywords only if they "
                "truthfully represent your skills "
                "or experience."
            )

            display_list(
                analysis.get(
                    "recommended_keywords",
                    [],
                ),
                "🔑",
                (
                    "No additional keywords "
                    "were recommended."
                ),
            )

        # -------------------------------------------------
        # GEMINI BULLET IMPROVEMENTS
        # -------------------------------------------------

        with bullets_tab:
            bullet_improvements = analysis.get(
                "bullet_improvements",
                [],
            )

            if bullet_improvements:
                for number, improvement in enumerate(
                    bullet_improvements,
                    start=1,
                ):
                    with st.expander(
                        f"Bullet improvement {number}",
                        expanded=True,
                    ):
                        st.markdown(
                            "**Original**"
                        )

                        st.write(
                            improvement.get(
                                "original",
                                "Not found",
                            )
                        )

                        st.markdown(
                            "**Improved version**"
                        )

                        st.success(
                            improvement.get(
                                "improved",
                                "Not generated",
                            )
                        )

                        st.markdown(
                            "**Why it is better**"
                        )

                        st.write(
                            improvement.get(
                                "reason",
                                (
                                    "No explanation "
                                    "was generated."
                                ),
                            )
                        )

            else:
                st.write(
                    "No resume bullet improvements "
                    "were generated."
                )

        # -------------------------------------------------
        # GEMINI EVIDENCE CHECKS
        # -------------------------------------------------

        with evidence_tab:
            evidence_checks = analysis.get(
                "evidence_checks",
                [],
            )

            status_icons = {
                "matched": "✅",
                "partial": "⚠️",
                "missing": "❌",
            }

            if evidence_checks:
                for number, check in enumerate(
                    evidence_checks,
                    start=1,
                ):
                    status = check.get(
                        "status",
                        "missing",
                    )

                    icon = status_icons.get(
                        status,
                        "ℹ️",
                    )

                    requirement = check.get(
                        "requirement",
                        "Requirement",
                    )

                    with st.expander(
                        f"{icon} {number}. {requirement}"
                    ):
                        st.write(
                            f"**Status:** "
                            f"{status.title()}"
                        )

                        st.write(
                            "**Resume evidence:** "
                            f"{check.get('evidence', 'Not found')}"
                        )

                        st.write(
                            "**Recommendation:** "
                            f"{check.get('recommendation', '')}"
                        )

            else:
                st.write(
                    "No evidence checks were generated."
                )

        # -------------------------------------------------
        # GEMINI INTERVIEW PREPARATION
        # -------------------------------------------------

        with interview_tab:
            st.markdown(
                "#### Interview preparation topics"
            )

            display_list(
                analysis.get(
                    "interview_focus",
                    [],
                ),
                "🎯",
                (
                    "No interview topics "
                    "were generated."
                ),
            )

        # -------------------------------------------------
        # PRIVACY REPORT
        # -------------------------------------------------

        with st.expander("Privacy report"):
            st.write(
                "Candidate name detected:",
                privacy.get(
                    "candidate_name_detected",
                    False,
                ),
            )

            st.write(
                "Total personal details removed:",
                privacy.get(
                    "total_redactions",
                    0,
                ),
            )

            st.json(
                privacy.get(
                    "redactions",
                    {},
                )
            )

    # -----------------------------------------------------
    # EXTRACTED CONTENT
    # -----------------------------------------------------

    st.divider()
    st.subheader("Extracted Content")

    with st.expander(
        "View extracted resume text"
    ):
        st.text(
            resume_data["text"]
        )

    with st.expander(
        "View job description"
    ):
        st.text(
            current_job_description
        )