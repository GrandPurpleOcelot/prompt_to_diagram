import streamlit as st
import subprocess
import os
from pathlib import Path
import openai
import tempfile

# Path to the PlantUML .jar file
plantuml_jar_path = './plantuml.jar'

# Connect to OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Initialize session state for PlantUML code
if 'plantuml_code' not in st.session_state:
    st.session_state['plantuml_code'] = ""

# Function to convert natural language instruction to PlantUML code using OpenAI
def nl_to_plantuml(nl_instruction):
    try:
        # Use the OpenAI API to generate a response
        openai_response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional PlantUML coder. Include a title. Use aws-orange theme. Use note if needed to explain more details. You MUST Output PlantUML code only and explain nothing."},
                {"role": "user", "content": nl_instruction}
            ],
            temperature=0.5,
            stream=False,
        )
        plantuml_code = openai_response.choices[0].message.content
        print(openai_response)
        return plantuml_code
    except Exception as e:
        st.error(f"An error occurred with the OpenAI API: {e}")
        return None

# Function to generate UML diagram from PlantUML code
def generate_uml_diagram(plantuml_code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".puml") as temp_file:
        temp_file.write(plantuml_code.encode())
        temp_file_path = temp_file.name
    
    # Generate the diagram using the PlantUML .jar
    output_dir = tempfile.gettempdir()  # Use temp directory for output
    subprocess_result = subprocess.run(
        ['java', '-jar', './plantuml.jar', temp_file_path, '-o', output_dir],
        capture_output=True, text=True
    )
    
    # Remove the temporary file
    os.remove(temp_file_path)
    
    # Check if PlantUML process ran successfully
    if subprocess_result.returncode != 0:
        # Display error message
        st.error(f"An error occurred while generating the diagram: {subprocess_result.stderr}")
        return None
    
    # Construct the output file path
    output_file = Path(output_dir) / (Path(temp_file_path).stem + '.png')
    
    # Check if the output file was created
    if not output_file.exists():
        st.error("Failed to create the output diagram.")
        return None
    
    # Return the path to the generated diagram
    return output_file

# Function to create a download link for the image
def get_image_download_link(img_path):
    with open(img_path, "rb") as file:
        btn = st.download_button(
            label="Download image",
            data=file,
            file_name="diagram.png",
            mime="image/png"
        )
    return btn

# Streamlit application layout
st.title('Diagram Generator')

with st.sidebar:
    st.header("Instructions")
    st.write("1. Describe your requirements in natural language.")
    st.write("2. Click 'Convert to PlantUML' to generate code.")
    st.write("3. Edit the PlantUML code if needed.")
    st.write("4. Download the generated diagram.")

# ...

# Text area for user to enter natural language instructions
nl_instruction = st.text_area(
    label="Describe your requirements in natural language:",
    height=150,
    value=st.session_state.get('nl_instruction', ''),
    placeholder="Help me create an instruction on how to bake a brownie"
)

# Button to convert natural language to PlantUML code
convert_button = st.button("Convert to PlantUML", type="primary")

# When the button is clicked, convert the natural language to PlantUML code
if convert_button:
    generated_code = nl_to_plantuml(nl_instruction)
    if generated_code:
        st.session_state['plantuml_code'] = generated_code
        st.session_state['nl_instruction'] = nl_instruction
        st.success("Successfully converted to PlantUML code.")
    else:
        st.session_state['plantuml_code'] = ''

# Text area for user to enter or edit PlantUML code
# The key parameter is used to create a unique identifier for this widget
plantuml_code = st.text_area(
    "Edit the PlantUML code here:",
    value=st.session_state['plantuml_code'],
    height=300,
    key="plantuml_code_area"
)

# Update session state when the user edits the code
st.session_state['plantuml_code'] = plantuml_code

# Generate and display the diagram after the PlantUML code is updated (either by conversion or by manual edit)
if st.session_state['plantuml_code']:
    output_file_path = generate_uml_diagram(st.session_state['plantuml_code'])
    if output_file_path:
        # Display the generated diagram
        st.image(str(output_file_path), caption='Generated UML Diagram', use_column_width=True)
        
        # Provide a download button for the image
        get_image_download_link(str(output_file_path))
        
        # Remove the output diagram file after displaying it
        os.remove(output_file_path)