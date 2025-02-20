# streamlit_app.py
import streamlit as st
import asyncio
import os
import nest_asyncio

from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI # Optional: For Gemini support

nest_asyncio.apply()

st.title("Browser Automation Agent with Browser-Use")
st.markdown("Enter your OpenAI API key and a task for the agent to perform in a web browser.")

openai_api_key = st.text_input("OpenAI API Key", type="password")
task_query = st.text_area("Task for the Agent", "What is Langchain?")
model_name = st.selectbox("Choose OpenAI Model", ["gpt-4o-mini", "gpt-3.5-turbo"], index=0) # Added model selection

if st.button("Run Agent"):
    if not openai_api_key:
        st.error("Please enter your OpenAI API Key.")
    else:
        os.environ['OPENAI_API_KEY'] = openai_api_key
        llm = ChatOpenAI(model=model_name, temperature=0) # Using selected model

        config = BrowserConfig(headless=True)
        browser = Browser(config=config)

        agent = Agent(
            task=task_query,
            llm=llm,
            browser=browser,
            generate_gif=False
        )

        st.info(f"Running agent with task: '{task_query}'...")
        with st.spinner("Agent is working..."):
            try:
                result = asyncio.run(agent.run())
                output_text = ""
                for action in result.action_results():
                    if action.is_done:
                        output_text += action.extracted_content + "\n\n"

                st.success("Agent task completed successfully!")
                if output_text:
                    st.markdown("### Extracted Content:")
                    st.code(output_text, language="text") # Display output in code block for better readability
                else:
                    st.warning("No content extracted from the actions.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.error(e) # Display full error for debugging
            finally:
                asyncio.run(browser.close())
                st.info("Browser closed.")
