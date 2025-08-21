import streamlit as st
import subprocess
import tempfile
import os

# Optional: OpenAI for AI feedback
try:
    from openai import OpenAI
    client = OpenAI()
except ImportError:
    client = None

st.title("🤖 AI Code Review Bot (Lite Version)")
st.write("Upload or paste Python code to get bug/style feedback and AI suggestions.")

# --- Input section ---
uploaded_file = st.file_uploader("Upload a Python file", type=["py"])
code_input = st.text_area("Or paste your code here", height=200)

if uploaded_file:
    code = uploaded_file.read().decode("utf-8")
else:
    code = code_input

# --- Review button ---
if st.button("🔍 Review Code"):
    if not code.strip():
        st.warning("Please upload or paste some Python code first.")
    else:
        # Handle pasted code vs uploaded file
        if not uploaded_file:
            tmp_path = "temp_code.py"
            with open(tmp_path, "w") as f:
                f.write(code)
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmp:
                tmp.write(code)
                tmp.flush()
                tmp_path = tmp.name

        # Run pylint
        st.subheader("📋 Pylint Results")
        try:
            pylint_out = subprocess.run(
                ["pylint", tmp_path, "--disable=all", "--enable=E,W"],
                capture_output=True,
                text=True,
                timeout=10
            )
            st.code(pylint_out.stdout if pylint_out.stdout else "No major issues found.")
        except Exception as e:
            st.error(f"Pylint failed: {e}")

        # Run flake8
        st.subheader("✨ Flake8 Results")
        try:
            flake8_out = subprocess.run(
                ["flake8", tmp_path, "--max-line-length=100"],
                capture_output=True,
                text=True,
                timeout=10
            )
            st.code(flake8_out.stdout if flake8_out.stdout else "No style issues found.")
        except Exception as e:
            st.error(f"Flake8 failed: {e}")

        # Optional: AI review
        if client:
            st.subheader("🤖 AI Feedback (OpenAI)")
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert code reviewer."},
                        {"role": "user", "content": f"Review this Python code for bugs and improvements:\n\n{code}"}
                    ],
                    max_tokens=300
                )
                ai_feedback = response.choices[0].message.content
                st.write(ai_feedback)
            except Exception as e:
                st.error(f"AI review failed: {e}")

        # Clean up only if uploaded file was used
        if uploaded_file:
            os.unlink(tmp_path)
