import streamlit as st
import fitz  # PyMuPDF
import openai
import re

# --- Streamlit UI ---
st.title("PDF to Infographic Generator")
st.write("Upload a PDF and get topic-wise infographics using GPT-4 + DALL·E 3")

openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

# --- Process PDF ---
if uploaded_file and openai_api_key:
    st.success("PDF uploaded successfully!")
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    # Split into topics (you can change logic here based on your file)
    sections = re.split(r'\n(?=Chapter|Section|\d+\.)', text)
    sections = [s.strip() for s in sections if len(s.strip()) > 100]

    st.info(f"Found {len(sections)} sections. Generating infographics for first 3 topics...")

    openai.api_key = openai_api_key

    for i, section in enumerate(sections[:3]):
        with st.spinner(f"Generating infographic for Section {i+1}..."):

            # GPT-4 to create prompt
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Create an infographic prompt (not summary) from the following text. Make it visual, structured and descriptive."},
                    {"role": "user", "content": section}
                ]
            )
            prompt = response['choices'][0]['message']['content']

            st.subheader(f"Section {i+1} Prompt")
            st.text(prompt)

            # DALL·E 3 Image Generation
            image_response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            image_url = image_response['data'][0]['url']
            st.image(image_url, caption=f"Infographic {i+1}", use_column_width=True)
