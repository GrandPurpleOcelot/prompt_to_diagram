import streamlit as st
import subprocess
import os
import re
from pathlib import Path
import openai

# Directory for storing output diagrams
output_dir = Path('./diagrams')
output_dir.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists

# Path to the PlantUML .jar file
plantuml_jar_path = './plantuml.jar'

# Connect to OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Initialize session state for PlantUML code
if 'plantuml_code' not in st.session_state:
    st.session_state['plantuml_code'] = ""

def nl_to_plantuml(nl_instruction, diagram_type, include_title, use_aws_orange_theme, use_note):
    instruction_message = "You are a professional PlantUML coder."
    instruction_message += " Include a title." if include_title else ""
    instruction_message += " Use aws-orange theme." if use_aws_orange_theme else ""
    instruction_message += " Use note if needed to explain more details." if use_note else ""
    instruction_message += f" You MUST Output PlantUML code for a {diagram_type} only and explain nothing."

    try:
        openai_response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": instruction_message},
                {"role": "user", "content": nl_instruction}
            ],
            temperature=0.5,
            stream=False,
        )
        return openai_response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred with the OpenAI API: {e}")
        return None

def generate_uml_diagram(plantuml_code):
    output_puml_file = output_dir / "output.puml"
    output_png_file = output_dir / "output.png"

    with open(output_puml_file, 'w') as file:
        file.write(plantuml_code)

    subprocess_result = subprocess.run(
        ['java', '-jar', plantuml_jar_path, str(output_puml_file)],
        capture_output=True, text=True
    )

    if subprocess_result.returncode == 0 and output_png_file.exists():
        return str(output_puml_file), str(output_png_file), None
    else:
        return None, None, "Failed to create the diagram or PlantUML error."

def extract_plantuml_code(full_code):
    pattern = re.compile(r"@start\w+.*?@end\w+", re.DOTALL)
    match = pattern.search(full_code)
    return match.group(0) if match else None

def get_image_download_link(img_path):
    with open(img_path, "rb") as file:
        return st.download_button("Download image", data=file, file_name="diagram.png", mime="image/png")

# Streamlit application layout
st.title('Agent Peter - Diagram Generator')

with st.sidebar:
    st.header("How to use Peter:")
    st.write("1. Select the type of diagram you want to create.")
    st.write("2. Describe your requirements in natural language.")
    st.write("3. Click **Convert to PlantUML** to generate code.")
    st.write("4. You can **Edit** the PlantUML code if needed.")
    st.write("5. You can **Download** the generated diagram.")

    st.header("Agent controls:")
    selected_diagram_type = st.selectbox("Choose diagram type:", ['Sequence', 'Class', 'Use Case', 'Activity'], index=0)
    include_title = st.checkbox("Include a title.", value=True)
    use_aws_orange_theme = st.checkbox("Use aws-orange theme.", value=True)
    use_note = st.checkbox("Use note if needed to explain more details.", value=True)

nl_instruction = st.text_area("Describe your requirements in natural language:", height=150)

if st.button("Convert to PlantUML"):
    plantuml_code = nl_to_plantuml(nl_instruction, selected_diagram_type, include_title, use_aws_orange_theme, use_note)
    if plantuml_code:
        valid_plantuml_code = extract_plantuml_code(plantuml_code)
        if valid_plantuml_code:
            st.session_state['plantuml_code'] = valid_plantuml_code
            puml_file, png_file, error_message = generate_uml_diagram(valid_plantuml_code)
            if png_file:
                st.image(png_file, caption='Generated UML Diagram')
                get_image_download_link(png_file)
                os.remove(png_file)
            else:
                st.error(error_message)
        else:
            st.error("No valid PlantUML code block found.")
    else:
        st.error("Failed to convert to PlantUML code.")