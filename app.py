import streamlit as st
from educhain import Educhain, LLMConfig
from educhain.utils.output_formatter import OutputFormatter  # For export functions
import json

# --- App Configuration ---
st.set_page_config(
    page_title="Personalized Quiz Generator",
    page_icon="❓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar for Settings ---
with st.sidebar:
    st.title("Quiz Settings")
    st.markdown("Customize your quiz generation:")
    st.markdown("---")

    # Input for Topic
    quiz_topic = st.text_area("Enter Quiz Topic:", placeholder="e.g., World History, Python Basics, Quantum Physics")

    # Number of Questions Slider
    num_questions = st.slider("Number of Questions:", min_value=1, max_value=20, value=5)

    # Question Type Selectbox
    question_type = st.selectbox("Question Type:",
                                 ["Multiple Choice", "Short Answer", "True/False", "Fill in the Blank"],
                                 index=0) # Default to Multiple Choice

    # Optional: Difficulty Level (You can add more customization options here later)
    difficulty_level = st.selectbox("Difficulty Level (Optional):",
                                     ["Beginner", "Intermediate", "Advanced", "Any"],
                                     index=3) # Default to Any

    st.markdown("---")

    # Button to Generate Quiz
    if st.button("Generate Quiz"):
        if quiz_topic:
            st.session_state.generate_quiz = True # Trigger quiz generation
        else:
            st.warning("Please enter a topic to generate a quiz.")
    else:
        st.session_state.generate_quiz = False

    st.markdown("---")
    st.markdown("Download Options:")
    export_format = st.selectbox("Choose Download Format:", ["JSON", "CSV", "PDF", "None"], index=0) # Default to JSON
    if export_format != "None" and st.session_state.get("generated_questions"):
        download_filename = st.text_input("Filename for Download:", value=f"quiz_{quiz_topic.replace(' ', '_')}.{export_format.lower()}")
        if st.download_button(
            label=f"Download Quiz as {export_format}",
            data="", # Placeholder - data will be dynamically updated below
            file_name=download_filename,
            mime="text/plain" # Placeholder MIME type - will be updated dynamically
        ):
            pass # Download button action is handled dynamically below


# --- Main App Content ---
st.title("❓ Personalized Quiz Generator")

if st.session_state.generate_quiz and quiz_topic:
    with st.spinner(f"Generating {question_type} quiz on '{quiz_topic}'..."):
        client = Educhain() # Initialize Educhain client

        try:
            questions = client.qna_engine.generate_questions(
                topic=quiz_topic,
                num=num_questions,
                question_type=question_type,
                custom_instructions=f"Difficulty level: {difficulty_level if difficulty_level != 'Any' else 'any'}. ", # Basic difficulty instruction
            )

            if questions and questions.questions:
                st.session_state.generated_questions = questions # Store generated questions in session state

                st.subheader(f"Generated {question_type} Quiz on: '{quiz_topic}'")

                for i, q in enumerate(questions.questions, 1):
                    st.markdown(f"**Question {i}:** {q.question}")
                    if isinstance(q, client.qna_engine._get_parser_and_model(question_type)[1].__args__[0]): # Check if it's MCQ
                        for j, option in enumerate(q.options):
                            st.write(f"  {chr(65 + j)}. {option}")
                        st.write(f"  *(Correct Answer: {q.answer})*") # Display correct answer for MCQs
                    else: # For other question types (Short Answer, True/False, Fill in Blank), just show answer
                         st.write(f"  *(Correct Answer: {q.answer})*")
                    st.write("---")

                st.success("Quiz generated successfully!")

            else:
                st.error("Could not generate quiz questions. Please try a different topic or adjust settings.")
                st.session_state.generated_questions = None # Clear any previous questions

        except Exception as e:
            st.error(f"An error occurred during quiz generation: {e}")
            st.error("Please check your API key and try again, or simplify your topic.")
            st.session_state.generated_questions = None # Clear any previous questions
            import traceback
            st.error(traceback.format_exc())


elif st.session_state.generate_quiz and not quiz_topic:
    st.warning("Please enter a topic to generate a quiz.")


# --- Dynamic Download Button Update ---
if st.session_state.get("generated_questions") and export_format != "None":
    output_formatter = OutputFormatter()
    if export_format == "JSON":
        quiz_output = output_formatter.to_json(st.session_state.generated_questions)
        mime_type = "application/json"
    elif export_format == "CSV":
        quiz_output = output_formatter.to_csv(st.session_state.generated_questions)
        mime_type = "text/csv"
    elif export_format == "PDF":
        quiz_output = output_formatter.to_pdf(st.session_state.generated_questions)
        mime_type = "application/pdf"
    else:
        quiz_output = "" # Should not reach here, but for safety
        mime_type = "text/plain"

    if quiz_output: # Only update download button if quiz output is generated
        download_button = st.sidebar.download_button( # Re-get the download button
            label=f"Download Quiz as {export_format}",
            data=open(quiz_output, "rb"), # Read file in binary mode for all formats
            file_name=download_filename,
            mime=mime_type,
            key="download_button" # Important: Use a key to update the existing button
        )
