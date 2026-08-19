import streamlit as st

from analyzers.ats_analyzer import analyze_ats
from analyzers.match_analyzer import analyze_match
from parsers.resume_parser import extract_resume_text


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)


st.title("📄 AI Resume Analyzer")
st.write(
    "Upload your resume and paste a job description "
    "to check job compatibility and ATS friendliness."
)


resume_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"],
    help="Text-based PDF and DOCX files are supported.",
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


if analyze_button:
    if resume_file is None:
        st.error("Please upload a PDF or DOCX resume.")

    elif not job_description.strip():
        st.error("Please paste the job description.")

    else:
        try:
            # Extract resume text
            resume_data = extract_resume_text(resume_file)

            # Analyze job-description compatibility
            match_result = analyze_match(
                resume_text=resume_data["text"],
                job_description=job_description,
            )

            # Analyze ATS readability
            ats_result = analyze_ats(
                resume_text=resume_data["text"],
                filename=resume_data["filename"],
                extension=resume_data["extension"],
            )

        except Exception as error:
            st.error(f"Resume analysis failed: {error}")

        else:
            st.success("Resume analyzed successfully!")

            # Document information
            document_col1, document_col2, document_col3 = st.columns(3)

            document_col1.metric(
                "Resume Words",
                resume_data["words"],
            )

            document_col2.metric(
                "Resume Characters",
                resume_data["characters"],
            )

            document_col3.metric(
                "Job Description Words",
                len(job_description.split()),
            )

            st.write(
                f"**Uploaded file:** {resume_data['filename']}"
            )

            # Overall results
            st.divider()
            st.subheader("Overall Results")

            result1, result2, result3, result4 = st.columns(4)

            result1.metric(
                "Estimated Job Match",
                f"{match_result['overall_score']}%",
            )

            result2.metric(
                "ATS Readability",
                f"{ats_result['score']}%",
            )

            result3.metric(
                "Technical Match",
                f"{match_result['technical_score']}%",
            )

            result4.metric(
                "Text Similarity",
                f"{match_result['similarity_score']}%",
            )

            st.write("**Job-match progress**")
            st.progress(
                match_result["overall_score"] / 100
            )

            st.write("**ATS-readability progress**")
            st.progress(
                ats_result["score"] / 100
            )

            st.caption(
                "These are transparent estimates and do not represent "
                "the score of any specific employer's ATS."
            )

            # Job-match analysis
            st.divider()
            st.subheader("Job Match Analysis")

            technical_tab, soft_tab = st.tabs(
                ["Technical Skills", "Soft Skills"]
            )

            with technical_tab:
                matched_col, missing_col = st.columns(2)

                with matched_col:
                    st.success("Matched technical skills")

                    if match_result["matched_technical"]:
                        for skill in match_result["matched_technical"]:
                            st.write(f"✅ {skill}")
                    else:
                        st.write(
                            "No matching technical skills detected."
                        )

                with missing_col:
                    st.error("Missing technical skills")

                    if match_result["missing_technical"]:
                        for skill in match_result["missing_technical"]:
                            st.write(f"❌ {skill}")
                    else:
                        st.write(
                            "No missing technical skills detected."
                        )

            with soft_tab:
                matched_col, missing_col = st.columns(2)

                with matched_col:
                    st.success("Matched soft skills")

                    if match_result["matched_soft"]:
                        for skill in match_result["matched_soft"]:
                            st.write(f"✅ {skill}")
                    else:
                        st.write(
                            "No matching soft skills detected."
                        )

                with missing_col:
                    st.warning("Missing soft skills")

                    if match_result["missing_soft"]:
                        for skill in match_result["missing_soft"]:
                            st.write(f"⚠️ {skill}")
                    else:
                        st.write(
                            "No missing soft skills detected."
                        )

            # ATS analysis
            st.divider()
            st.subheader("ATS Readability Analysis")

            ats_col1, ats_col2, ats_col3 = st.columns(3)

            ats_col1.metric(
                "ATS Score",
                f"{ats_result['score']}%",
            )

            ats_col2.metric(
                "Rating",
                ats_result["rating"],
            )

            passed_checks = sum(
                1
                for check in ats_result["checks"]
                if check["passed"]
            )

            ats_col3.metric(
                "Checks Passed",
                f"{passed_checks}/{len(ats_result['checks'])}",
            )

            if ats_result["score"] >= 85:
                st.success(
                    "The résumé has excellent ATS readability."
                )
            elif ats_result["score"] >= 70:
                st.info(
                    "The résumé has good ATS readability, "
                    "but some improvements are possible."
                )
            elif ats_result["score"] >= 50:
                st.warning(
                    "The résumé needs several ATS improvements."
                )
            else:
                st.error(
                    "The résumé may have major ATS-readability problems."
                )

            with st.expander(
                "View all ATS checks",
                expanded=True,
            ):
                for check in ats_result["checks"]:
                    if check["passed"]:
                        icon = "✅"
                    elif check["points"] > 0:
                        icon = "⚠️"
                    else:
                        icon = "❌"

                    st.markdown(
                        f"{icon} **{check['name']}: "
                        f"{check['points']}/{check['maximum']}**"
                    )
                    st.write(check["message"])

            if ats_result["missing_sections"]:
                missing_section_names = ", ".join(
                    section.replace("_", " ").title()
                    for section in ats_result["missing_sections"]
                )

                st.warning(
                    f"Sections not detected: {missing_section_names}"
                )

            # Extracted content
            st.divider()
            st.subheader("Extracted Content")

            with st.expander("View extracted resume text"):
                st.text(resume_data["text"])

            with st.expander("View job description"):
                st.text(job_description)