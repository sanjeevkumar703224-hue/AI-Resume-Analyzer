import streamlit as st
import fitz
import re
from collections import Counter

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DATA
# ============================================================

SKILLS = {
    "Programming": [
        "python", "java", "c++", "c", "javascript", "typescript",
        "sql", "r", "go", "php"
    ],
    "AI / ML": [
        "machine learning", "deep learning", "artificial intelligence",
        "natural language processing", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn",
        "hugging face", "transformers", "opencv"
    ],
    "Data": [
        "pandas", "numpy", "matplotlib", "seaborn",
        "data analysis", "data science", "power bi", "tableau",
        "excel"
    ],
    "Web": [
        "html", "css", "react", "node.js", "express",
        "django", "flask", "fastapi", "streamlit"
    ],
    "Cloud / DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes",
        "git", "github", "linux", "jenkins"
    ],
    "Databases": [
        "mysql", "postgresql", "mongodb", "sqlite",
        "oracle", "redis"
    ]
}

SECTIONS = {
    "Contact Information": [
        "email", "@", "phone", "linkedin", "github"
    ],
    "Summary / Objective": [
        "summary", "objective", "profile"
    ],
    "Education": [
        "education", "academic", "degree", "b.tech", "btech",
        "bachelor", "master"
    ],
    "Skills": [
        "skills", "technical skills", "technologies"
    ],
    "Experience": [
        "experience", "work experience", "employment",
        "internship", "internships"
    ],
    "Projects": [
        "projects", "project"
    ],
    "Certifications": [
        "certifications", "certificates", "certification"
    ],
    "Achievements": [
        "achievements", "awards", "honors"
    ]
}

ACTION_WORDS = [
    "developed", "built", "created", "implemented",
    "designed", "optimized", "improved", "automated",
    "deployed", "managed", "led", "engineered",
    "analyzed", "integrated", "reduced", "increased"
]

# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_text(uploaded_file):
    try:
        document = fitz.open(
            stream=uploaded_file.read(),
            filetype="pdf"
        )

        text = ""

        for page in document:
            text += page.get_text() + "\n"

        document.close()

        return text.strip()

    except Exception as e:
        st.error(f"Could not read PDF: {e}")
        return ""


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# SKILL DETECTION
# ============================================================

def detect_skills(text):
    text_lower = clean_text(text)

    detected = {}

    for category, skills in SKILLS.items():

        found = []

        for skill in skills:

            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

            if re.search(pattern, text_lower):
                found.append(skill)

        if found:
            detected[category] = sorted(set(found))

    return detected


# ============================================================
# SECTION DETECTION
# ============================================================

def detect_sections(text):
    text_lower = clean_text(text)

    result = {}

    for section, keywords in SECTIONS.items():

        found = False

        for keyword in keywords:

            if keyword.lower() in text_lower:
                found = True
                break

        result[section] = found

    return result


# ============================================================
# CONTACT ANALYSIS
# ============================================================

def contact_analysis(text):

    email = bool(
        re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            text
        )
    )

    phone = bool(
        re.search(
            r"(\+?\d[\d\s\-]{8,}\d)",
            text
        )
    )

    linkedin = "linkedin.com" in text.lower()

    github = "github.com" in text.lower()

    return {
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github
    }


# ============================================================
# ACTION VERBS
# ============================================================

def find_action_words(text):

    lower = text.lower()

    found = []

    for word in ACTION_WORDS:

        if re.search(
            r"(?<!\w)" + re.escape(word) + r"(?!\w)",
            lower
        ):
            found.append(word)

    return found


# ============================================================
# NUMBER / METRIC ANALYSIS
# ============================================================

def find_metrics(text):

    patterns = [
        r"\b\d+%",
        r"\b\d+\+",
        r"\b\d+\s*(users|customers|projects|models|records|employees)",
        r"\$\s*\d+",
        r"₹\s*\d+"
    ]

    matches = []

    for pattern in patterns:

        matches.extend(
            re.findall(pattern, text, flags=re.IGNORECASE)
        )

    return matches


# ============================================================
# RESUME SCORE
# ============================================================

def calculate_score(
    text,
    sections,
    skills,
    contacts,
    action_words,
    metrics
):

    score = 0
    reasons = []

    # ---------------- CONTACT ----------------

    contact_score = sum(contacts.values())

    score += min(contact_score * 4, 16)

    if contact_score >= 3:
        reasons.append("Good contact information coverage.")
    else:
        reasons.append("Improve contact information.")

    # ---------------- SECTIONS ----------------

    important_sections = [
        "Education",
        "Skills",
        "Experience",
        "Projects"
    ]

    section_score = sum(
        sections.get(x, False)
        for x in important_sections
    )

    score += section_score * 8

    # ---------------- SKILLS ----------------

    skill_count = sum(
        len(values)
        for values in skills.values()
    )

    skill_points = min(skill_count * 2, 20)

    score += skill_points

    # ---------------- ACTION WORDS ----------------

    action_points = min(
        len(action_words) * 2,
        10
    )

    score += action_points

    # ---------------- METRICS ----------------

    metric_points = min(
        len(metrics) * 3,
        12
    )

    score += metric_points

    # ---------------- LENGTH ----------------

    words = len(text.split())

    if 300 <= words <= 900:
        score += 10

    elif 200 <= words < 300:
        score += 5

    elif words > 900:
        score += 3

    score = min(score, 100)

    return score


# ============================================================
# SUGGESTIONS
# ============================================================

def generate_suggestions(
    text,
    sections,
    skills,
    contacts,
    action_words,
    metrics
):

    suggestions = []

    if not contacts["linkedin"]:
        suggestions.append(
            "Add your LinkedIn profile URL."
        )

    if not contacts["github"]:
        suggestions.append(
            "Add your GitHub profile URL."
        )

    if not sections["Summary / Objective"]:
        suggestions.append(
            "Add a short professional summary focused on your target role."
        )

    if not sections["Projects"]:
        suggestions.append(
            "Add 2–4 strong projects with technologies and measurable results."
        )

    if not sections["Experience"]:
        suggestions.append(
            "Add internship, freelance, volunteer, or relevant practical experience."
        )

    skill_count = sum(
        len(values)
        for values in skills.values()
    )

    if skill_count < 6:
        suggestions.append(
            "Add more relevant technical skills that match your target job."
        )

    if len(action_words) < 5:
        suggestions.append(
            "Use stronger action verbs such as Built, Developed, Optimized, Automated, and Implemented."
        )

    if len(metrics) == 0:
        suggestions.append(
            "Add measurable achievements such as percentages, users, performance improvements, or project scale."
        )

    words = len(text.split())

    if words < 250:
        suggestions.append(
            "Your resume appears short. Add meaningful project or experience details."
        )

    if words > 1000:
        suggestions.append(
            "Your resume may be too long. Remove unnecessary details and keep important achievements."
        )

    if not suggestions:
        suggestions.append(
            "Your resume structure looks strong. Continue tailoring it to each job description."
        )

    return suggestions


# ============================================================
# JOB DESCRIPTION MATCHING
# ============================================================

def extract_keywords(text):

    lower = clean_text(text)

    keywords = set()

    all_skills = []

    for skills in SKILLS.values():
        all_skills.extend(skills)

    for skill in all_skills:

        if skill in lower:
            keywords.add(skill)

    return keywords


def job_match(resume_text, job_description):

    resume_keywords = extract_keywords(resume_text)

    job_keywords = extract_keywords(job_description)

    if not job_keywords:
        return 0, [], []

    matched = sorted(
        resume_keywords & job_keywords
    )

    missing = sorted(
        job_keywords - resume_keywords
    )

    score = int(
        len(matched) /
        len(job_keywords) *
        100
    )

    return score, matched, missing


# ============================================================
# REPORT GENERATION
# ============================================================

def generate_report(
    filename,
    score,
    words,
    skills,
    sections,
    suggestions
):

    report = []

    report.append("AI RESUME ANALYZER")
    report.append("=" * 50)
    report.append("")

    report.append(f"Resume: {filename}")
    report.append(f"Resume Score: {score}/100")
    report.append(f"Word Count: {words}")
    report.append("")

    report.append("SECTIONS")
    report.append("-" * 30)

    for section, found in sections.items():

        status = "Present" if found else "Missing"

        report.append(
            f"{section}: {status}"
        )

    report.append("")

    report.append("SKILLS")
    report.append("-" * 30)

    for category, values in skills.items():

        report.append(
            f"{category}: {', '.join(values)}"
        )

    report.append("")

    report.append("SUGGESTIONS")
    report.append("-" * 30)

    for suggestion in suggestions:

        report.append(
            f"- {suggestion}"
        )

    return "\n".join(report)


# ============================================================
# UI - HEADER
# ============================================================

st.title("📄 AI Resume Analyzer")

st.markdown(
    """
### Analyze your resume in seconds

Upload your PDF resume to get:

**Resume Score • Skills • Sections • ATS-style Analysis •
Job Match • Improvement Suggestions**
"""
)

st.divider()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Settings")

    st.info(
        "This tool performs rule-based resume analysis. "
        "It is designed as a portfolio project and should "
        "not be treated as a professional hiring decision."
    )

    st.markdown("### Supported")

    st.write("📄 PDF resumes")
    st.write("🧠 Skill detection")
    st.write("📊 Resume scoring")
    st.write("🎯 Job matching")
    st.write("💡 Suggestions")


# ============================================================
# UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📤 Upload your resume",
    type=["pdf"]
)

if uploaded_file is None:

    st.info(
        "Upload a PDF resume to start the analysis."
    )

    st.stop()


# ============================================================
# PROCESS
# ============================================================

with st.spinner("🔍 Analyzing your resume..."):

    resume_text = extract_text(uploaded_file)

if not resume_text:

    st.error(
        "No readable text was found in the PDF."
    )

    st.stop()


sections = detect_sections(resume_text)

skills = detect_skills(resume_text)

contacts = contact_analysis(resume_text)

action_words = find_action_words(resume_text)

metrics = find_metrics(resume_text)

suggestions = generate_suggestions(
    resume_text,
    sections,
    skills,
    contacts,
    action_words,
    metrics
)

score = calculate_score(
    resume_text,
    sections,
    skills,
    contacts,
    action_words,
    metrics
)

word_count = len(resume_text.split())


# ============================================================
# SCORE
# ============================================================

st.subheader("📊 Resume Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Resume Score",
        f"{score}/100"
    )

with col2:

    st.metric(
        "Words",
        word_count
    )

with col3:

    skill_count = sum(
        len(values)
        for values in skills.values()
    )

    st.metric(
        "Skills Found",
        skill_count
    )

with col4:

    st.metric(
        "Metrics Found",
        len(metrics)
    )


# ============================================================
# SCORE BAR
# ============================================================

st.progress(
    score / 100
)

if score >= 80:

    st.success(
        "Excellent! Your resume has a strong overall structure."
    )

elif score >= 60:

    st.warning(
        "Good foundation. A few improvements can make it stronger."
    )

else:

    st.error(
        "Your resume needs improvement in several areas."
    )


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🧠 Skills",
        "📋 Sections",
        "💡 Suggestions",
        "🎯 Job Match",
        "📄 Resume Text"
    ]
)


# ============================================================
# SKILLS TAB
# ============================================================

with tab1:

    st.subheader("Detected Technical Skills")

    if skills:

        for category, values in skills.items():

            st.markdown(
                f"### {category}"
            )

            cols = st.columns(4)

            for index, skill in enumerate(values):

                with cols[index % 4]:

                    st.success(
                        skill.title()
                    )

    else:

        st.warning(
            "No recognized technical skills were detected."
        )


# ============================================================
# SECTIONS TAB
# ============================================================

with tab2:

    st.subheader(
        "Resume Section Analysis"
    )

    for section, found in sections.items():

        if found:

            st.success(
                f"✓ {section}"
            )

        else:

            st.error(
                f"✗ {section}"
            )

    st.subheader(
        "Contact Information"
    )

    for item, found in contacts.items():

        label = item.title()

        if found:

            st.success(
                f"✓ {label}"
            )

        else:

            st.warning(
                f"✗ {label}"
            )


# ============================================================
# SUGGESTIONS TAB
# ============================================================

with tab3:

    st.subheader(
        "💡 Improvement Suggestions"
    )

    for index, suggestion in enumerate(
        suggestions,
        start=1
    ):

        st.write(
            f"**{index}.** {suggestion}"
        )

    st.subheader(
        "📝 Writing Analysis"
    )

    if action_words:

        st.write(
            "Strong action words detected:"
        )

        st.write(
            ", ".join(
                word.title()
                for word in action_words
            )
        )

    else:

        st.warning(
            "Try using stronger action verbs in your bullet points."
        )

    if metrics:

        st.write(
            "Measurable achievements detected:"
        )

        st.write(
            ", ".join(metrics)
        )

    else:

        st.warning(
            "No measurable achievements detected."
        )


# ============================================================
# JOB MATCH TAB
# ============================================================

with tab4:

    st.subheader(
        "🎯 Job Description Matcher"
    )

    job_description = st.text_area(
        "Paste the job description here:",
        height=250,
        placeholder=(
            "Example:\n"
            "We are looking for a Python developer "
            "with SQL, AWS, Docker and machine learning experience..."
        )
    )

    if st.button(
        "🔍 Analyze Job Match"
    ):

        if not job_description.strip():

            st.warning(
                "Please paste a job description."
            )

        else:

            match_score, matched, missing = job_match(
                resume_text,
                job_description
            )

            st.metric(
                "Job Match Score",
                f"{match_score}%"
            )

            st.progress(
                match_score / 100
            )

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    "✅ Matched Skills"
                )

                if matched:

                    for skill in matched:

                        st.success(
                            skill.title()
                        )

                else:

                    st.write(
                        "No matching skills detected."
                    )

            with col2:

                st.subheader(
                    "❌ Missing Skills"
                )

                if missing:

                    for skill in missing:

                        st.error(
                            skill.title()
                        )

                else:

                    st.success(
                        "No major recognized skills are missing."
                    )


# ============================================================
# RESUME TEXT TAB
# ============================================================

with tab5:

    st.subheader(
        "Extracted Resume Text"
    )

    st.text_area(
        "Resume Content",
        resume_text,
        height=500
    )


# ============================================================
# DOWNLOAD REPORT
# ============================================================

st.divider()

report = generate_report(
    uploaded_file.name,
    score,
    word_count,
    skills,
    sections,
    suggestions
)

st.download_button(
    label="⬇️ Download Analysis Report",
    data=report,
    file_name="resume_analysis.txt",
    mime="text/plain"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Resume Analyzer • Built with Python + Streamlit + PyMuPDF"
)
