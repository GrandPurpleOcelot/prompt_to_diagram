import streamlit as st
import subprocess
import os
import re
from pathlib import Path
import openai
import tempfile
from data import diagram_types
import glob

# Directory for storing output diagrams
output_dir = Path('./diagrams')

# Path to the PlantUML .jar file
plantuml_jar_path = './plantuml.jar'

# Connect to OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Initialize session state for PlantUML code
if 'plantuml_code' not in st.session_state:
    st.session_state['plantuml_code'] = ""

# Function to convert natural language instruction to PlantUML code using OpenAI
def nl_to_plantuml(nl_instruction, diagram_type, include_title, use_aws_orange_theme, use_note, error_details=None, failed_code=None):
    if diagram_type == "Let AI decide best Diagram":
        diagram_type = 'most appropriate diagram'
    # Construct the instruction message based on toggles
    instruction_message = f"You are a professional PlantUML coder."
    if include_title:
        instruction_message += " Include a title."
    if use_aws_orange_theme:
        instruction_message += " Use aws-orange theme."
    if use_note:
        instruction_message += " Use note if needed to explain more details."
    instruction_message += f" You MUST Output PlantUML code for a {diagram_type} only and explain nothing."

    if error_details and failed_code:
        nl_instruction += f"\n\nPrevious error details: {error_details}\n\nFailed PlantUML code:\n{failed_code}"

    try:
        # Use the OpenAI API to generate a response
        openai_response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": instruction_message},
                {"role": "user", "content": nl_instruction}
            ],
            temperature=0.5,
            stream=False,
        )
        plantuml_code = openai_response.choices[0].message.content
        return plantuml_code
    except Exception as e:
        st.error(f"An error occurred with the OpenAI API: {e}")
        return None

# Function to generate UML diagram from PlantUML code
def generate_uml_diagram(plantuml_code, output_dir, plantuml_jar_path):
    retries = 2
    error_message = None

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists

    # Define the path for the .puml file
    output_puml_file = output_dir / "output.puml"

    # Write the PlantUML code to the .puml file
    with open(output_puml_file, 'w') as file:
        file.write(plantuml_code)

    while retries >= 0:
        try:
            subprocess_result = subprocess.run(
                ['java',
                 '-jar', plantuml_jar_path,
                 str(output_puml_file)],
                capture_output=True, text=True
            )

            # Find the generated PNG file
            png_files = list(output_dir.glob('*.png'))
            if subprocess_result.returncode == 0 and png_files:
                # Assume the newest PNG file is the one we just created
                generated_png_file = max(png_files, key=os.path.getctime)
                output_png_file = output_dir / "output.png"
                # Rename the file to output.png
                generated_png_file.rename(output_png_file)
                return str(output_puml_file), str(output_png_file), None
            else:
                error_message = "Failed to create the output diagram or PlantUML error."
                if subprocess_result.stderr:
                    print(subprocess_result.stderr)
                retries -= 1
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            retries -= 1

    return None, None, error_message

def extract_plantuml_code(full_code):
    """
    Extracts the PlantUML code between @startXXX and @endXXX tags.
    
    Args:
    - full_code (str): The full PlantUML code including unwanted text.
    
    Returns:
    - str: The extracted PlantUML code or None if no valid code block is found.
    """
    # Regular expression to find blocks starting with @start and ending with @end
    pattern = re.compile(r"@start\w+.*?@end\w+", re.DOTALL)
    match = pattern.search(full_code)
    
    if match:
        return match.group(0)  # Return the matched block, including start and end tags
    else:
        return None  # Return None if no valid block is found

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
st.title('Agent Peter - Diagram Generator')

# Sidebar content
with st.sidebar:
    st.header("How to use Peter:")
    st.write("1. Select the type of diagram you want to create.")
    st.write("2. Describe your requirements in natural language.")
    st.write("3. Click **Convert to PlantUML** to generate code. Sometimes it may throw an error; press button again to retry.")
    st.write("4. You can **Edit** the PlantUML code if needed.")
    st.write("5. You can **Download** the generated diagram.")

    st.header("Agent controls:")
    # Select box for choosing diagram type
    selected_diagram_type = st.selectbox("Choose diagram type:", diagram_types, index=0)

    # Toggles for instruction message content
    include_title = st.toggle("Include a title.",value=True)
    use_aws_orange_theme = st.toggle("Use aws-orange theme.", value=True)
    use_note = st.toggle("Use note if needed to explain more details.", value=True)

# Text area for user to enter natural language instructions
nl_instruction = st.text_area(
    label="Describe your requirements in natural language:",
    height=150,
    value=st.session_state.get('nl_instruction', ''),
    placeholder="Help me create an instruction on how to bake a brownie"
)

# Button to convert natural language to PlantUML code
convert_button = st.button("Convert to PlantUML", type="primary",use_container_width=True)

# Placeholder for PlantUML code text_area - this will be used to display the text_area conditionally
plantuml_code_placeholder = st.empty()

# When the button is clicked, convert the natural language to PlantUML code
if convert_button:
    retry_count = 0
    error_message = None
    while retry_count < 3:
        generated_code = nl_to_plantuml(
            nl_instruction,
            selected_diagram_type,
            include_title,
            use_aws_orange_theme,
            use_note,
            error_details=error_message,
            failed_code=st.session_state['plantuml_code'] if error_message else None
        )
        if generated_code:
            valid_plantuml_code = extract_plantuml_code(generated_code)
            if valid_plantuml_code:
                st.session_state['plantuml_code'] = valid_plantuml_code
                st.session_state['nl_instruction'] = nl_instruction

                plantuml_code = plantuml_code_placeholder.text_area(
                    "You can edit the diagram if you wish 👇, diagram will updated accordingly 🥳:",
                    value=st.session_state['plantuml_code'],
                    height=300,
                    key="plantuml_code_area"
                )
                output_puml_file, output_png_file, error_message = generate_uml_diagram(
                    st.session_state['plantuml_code'], output_dir=output_dir, plantuml_jar_path=plantuml_jar_path
                )
                if output_png_file:
                    st.success("Successfully converted to PlantUML code.")
                    # Display the generated diagram
                    st.image(str(output_png_file), caption='Generated UML Diagram', use_column_width=False)
                    
                    # Provide a download button for the image
                    get_image_download_link(str(output_png_file))
                    
                    # Remove the output diagram file after displaying it
                    os.remove(output_png_file)
                    break  # Exit loop on success
            else:
                st.error("No valid PlantUML code block found. Retrying...")
                retry_count += 1
        else:
            st.error("Failed to convert to PlantUML code.")
            break  # Exit loop on conversion failure
else:
    # Check if there is PlantUML code in the session state before creating the text_area
    if st.session_state['plantuml_code']:
        # Create the text_area for PlantUML code inside the placeholder
        plantuml_code = plantuml_code_placeholder.text_area(
            "You can edit the diagram if you wish 👇, diagram will updated accordingly 🥳:",
            value=st.session_state['plantuml_code'],
            height=300,
            key="plantuml_code_area"
        )
        # Update the session state when the user edits the code
        st.session_state['plantuml_code'] = plantuml_code
        
        st.subheader('Generated Diagram')
        # Generate and display the diagram
        output_puml_file, output_png_file, error_message = generate_uml_diagram(
            st.session_state['plantuml_code'], output_dir=output_dir, plantuml_jar_path=plantuml_jar_path
        )
        if output_png_file:
            # Display the generated diagram
            st.image(str(output_png_file), caption='Generated UML Diagram', use_column_width=False)
            
            # Provide a download button for the image
            get_image_download_link(str(output_png_file))
            
            # Remove the output diagram file after displaying it
            os.remove(output_png_file)