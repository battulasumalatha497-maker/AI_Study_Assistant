import streamlit as st
from docx import Document
from pypdf import PdfReader
from pptx import Presentation
import re
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 AI Study Assistant")

st.write(
    "Upload your study material and use AI-powered tools "
    "to summarize, quiz yourself, and ask questions."
)

uploaded_file = st.file_uploader(
    "📚 Upload your study material",
    type=["docx", "pdf", "pptx"]
)

if uploaded_file:

    st.success(f"Uploaded: {uploaded_file.name}")

    text = ""

    if uploaded_file.name.lower().endswith(".docx"):

        doc = Document(uploaded_file)

        for paragraph in doc.paragraphs:

            if paragraph.text.strip():

                text += paragraph.text.strip() + "\n"

    elif uploaded_file.name.lower().endswith(".pdf"):

        pdf = PdfReader(uploaded_file)

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

    elif uploaded_file.name.lower().endswith(".pptx"):

        presentation = Presentation(uploaded_file)

        for slide in presentation.slides:

            for shape in slide.shapes:

                if hasattr(shape, "text") and shape.text.strip():

                    text += shape.text.strip() + "\n"

    if not text.strip():

        st.error(
            "⚠️ No readable text was found in this document."
        )

        st.stop()

    word_count = len(text.split())
    character_count = len(text)

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "📚 Words",
            word_count
        )

    with col2:

        st.metric(
            "🔤 Characters",
            character_count
        )

    with st.expander("📄 View Document Content"):

        st.text(text)

    st.subheader("📝 Document Summary")

    if st.button("Generate Key Points"):

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        if lines:

            st.success("📌 Key Points")

            for point in lines[:10]:

                st.write("• " + point)

        else:

            st.warning(
                "No content available for summary."
            )

    st.subheader("🧠 Study Quiz")

    st.write(
        "Generate questions from your uploaded document."
    )

    if st.button("🎯 Generate Quiz"):

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        useful_lines = [
            line
            for line in lines
            if len(line.split()) >= 3
        ]

        if not useful_lines:

            st.warning(
                "Not enough content to create a quiz."
            )

        else:

            question_count = min(
                5,
                len(useful_lines)
            )

            quiz_lines = random.sample(
                useful_lines,
                question_count
            )

            st.success("📚 Quiz Questions")

            for i, answer in enumerate(
                quiz_lines,
                start=1
            ):

                st.markdown(
                    f"### Question {i}"
                )

                st.write(
                    "What does the document mention about:"
                )

                with st.expander("💡 Show Answer"):

                    st.info(answer)

    st.subheader("🎯 Multiple-Choice Quiz")

    st.write(
        "Test your knowledge using multiple-choice questions."
    )

    if st.button("📝 Generate MCQ Quiz"):

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        useful_lines = [
            line
            for line in lines
            if len(line.split()) >= 5
        ]

        if not useful_lines:

            st.warning(
                "Not enough content to create multiple-choice questions."
            )

        else:

            question_count = min(
                5,
                len(useful_lines)
            )

            quiz_lines = random.sample(
                useful_lines,
                question_count
            )

            st.session_state.mcq_questions = quiz_lines
            st.session_state.mcq_submitted = False

    if "mcq_questions" in st.session_state:

        st.success("📚 Multiple-Choice Questions")

        for i, answer in enumerate(
            st.session_state.mcq_questions,
            start=1
        ):

            st.markdown(
                f"### Question {i}"
            )

            words = answer.split()

            if len(words) >= 4:

                correct_answer = words[
                    random.randint(
                        0,
                        len(words) - 1
                    )
                ]

                options = [correct_answer]

                other_words = [
                    word
                    for word in words
                    if word.lower() != correct_answer.lower()
                ]

                random.shuffle(other_words)

                for word in other_words:

                    if word not in options:

                        options.append(word)

                    if len(options) == 4:

                        break

                while len(options) < 4:

                    options.append(
                        "None of these"
                    )

                random.shuffle(options)

                st.write(
                    "Which of the following is mentioned in this document?"
                )

                selected = st.radio(
                    "Select an answer:",
                    options,
                    key=f"mcq_{i}"
                )

                st.session_state[
                    f"correct_{i}"
                ] = correct_answer

        if st.button("✅ Submit MCQ Quiz"):

            score = 0

            for i in range(
                1,
                len(st.session_state.mcq_questions) + 1
            ):

                selected = st.session_state.get(
                    f"mcq_{i}"
                )

                correct = st.session_state.get(
                    f"correct_{i}"
                )

                if selected == correct:

                    score += 1

            total = len(
                st.session_state.mcq_questions
            )

            st.success(
                f"🎉 Your Score: {score}/{total}"
            )

            if score == total:

                st.balloons()

                st.write(
                    "🌟 Excellent! You answered all questions correctly."
                )

            elif score >= total / 2:

                st.write(
                    "👍 Good job! Keep practicing."
                )

            else:

                st.write(
                    "📖 Keep studying and try the quiz again."
                )

    st.subheader("💬 Ask a Question")

    question = st.text_input(
        "Enter your question:",
        placeholder="Example: What are the skills?"
    )

    if question:

        q = question.lower()

        if any(
            word in q
            for word in [
                "email",
                "mail",
                "gmail"
            ]
        ):

            emails = re.findall(
                r'[\w\.-]+@[\w\.-]+\.\w+',
                text
            )

            if emails:

                st.success("🤖 Answer:")

                st.write(emails[0])

            else:

                st.warning(
                    "No email address found."
                )

        elif (
            "linkedin" in q
            or "linked in" in q
        ):

            linkedin = re.findall(
                r'https?://[^\s]+linkedin[^\s]+',
                text,
                re.IGNORECASE
            )

            if linkedin:

                st.success("🤖 Answer:")

                st.write(linkedin[0])

            else:

                st.warning(
                    "No LinkedIn link found."
                )

        elif any(
            word in q
            for word in [
                "phone",
                "mobile",
                "contact",
                "number"
            ]
        ):

            numbers = re.findall(
                r'\+?\d[\d\s-]{8,}\d',
                text
            )

            if numbers:

                st.success("🤖 Answer:")

                st.write(numbers[0])

            else:

                st.warning(
                    "No phone number found."
                )

        elif any(
            word in q
            for word in [
                "skill",
                "skills",
                "technical skill",
                "technical skills"
            ]
        ):

            chunks = [
                line.strip()
                for line in text.split("\n")
                if line.strip()
            ]

            matching_lines = []

            for line in chunks:

                line_lower = line.lower()

                if (
                    "skill" in line_lower
                    or "python" in line_lower
                    or "java" in line_lower
                    or "c++" in line_lower
                    or "sap" in line_lower
                    or "programming" in line_lower
                    or "database" in line_lower
                    or "web" in line_lower
                ):

                    matching_lines.append(line)

            if matching_lines:

                st.success("🤖 Skills found:")

                for line in matching_lines[:10]:

                    st.write("• " + line)

            else:

                st.warning(
                    "No specific skills found."
                )

        elif any(
            word in q
            for word in [
                "language",
                "languages",
                "programming language",
                "programming languages"
            ]
        ):

            languages = []

            language_names = [
                "Python",
                "Java",
                "C",
                "C++",
                "JavaScript",
                "HTML",
                "CSS",
                "SQL",
                "ABAP",
                "SAP ABAP"
            ]

            for language in language_names:

                if re.search(
                    r'\b' + re.escape(language) + r'\b',
                    text,
                    re.IGNORECASE
                ):

                    languages.append(language)

            if languages:

                st.success(
                    "🤖 Languages found:"
                )

                for language in languages:

                    st.write(
                        "• " + language
                    )

            else:

                st.warning(
                    "No programming languages found."
                )

        else:

            chunks = [
                line.strip()
                for line in text.split("\n")
                if line.strip()
            ]

            if not chunks:

                st.warning(
                    "No readable content found."
                )

            else:

                try:

                    documents = chunks + [question]

                    vectorizer = TfidfVectorizer(
                        stop_words="english"
                    )

                    vectors = vectorizer.fit_transform(
                        documents
                    )

                    similarities = cosine_similarity(
                        vectors[-1],
                        vectors[:-1]
                    ).flatten()

                    best_index = similarities.argmax()

                    best_score = similarities[
                        best_index
                    ]

                    if best_score > 0:

                        best_chunk = chunks[
                            best_index
                        ]

                        st.success(
                            "🤖 Answer found:"
                        )

                        st.write(
                            best_chunk
                        )

                        st.caption(
                            "Relevance score: "
                            + f"{best_score:.2f}"
                        )

                    else:

                        st.warning(
                            "I could not find relevant "
                            "information in the document."
                        )

                except Exception as e:

                    st.error(
                        "Something went wrong while "
                        "searching the document."
                    )

                    st.write(str(e))

else:

    st.info(
        "👆 Upload a DOCX, PDF, or PPTX file to get started."
    )