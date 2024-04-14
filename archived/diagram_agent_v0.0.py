import streamlit as st
import subprocess
import os
from pathlib import Path
import base64
from data import sample_plantuml

# Path to the PlantUML .jar file
plantuml_jar_path = './plantuml.jar'

#  Function to generate UML diagram from PlantUML code
def generate_uml_diagram(plantuml_code):
    # Write the PlantUML code to a temporary file
    temp_file = 'temp.puml'
    with open(temp_file, 'w') as file:
        file.write(plantuml_code)

    # Generate the diagram using the PlantUML .jar
    output_dir = '.'  # Use current directory for output
    subprocess_result = subprocess.run(
        ['java', '-jar', plantuml_jar_path, temp_file, '-o', output_dir],
        capture_output=True, text=True
    )

    # Check if PlantUML process ran successfully
    if subprocess_result.returncode != 0:
        # Remove the temporary file
        os.remove(temp_file)
        # Display error message
        st.error(f"An error occurred while generating the diagram: {subprocess_result.stderr}")
        return None

    # Construct the output file path
    output_file = Path(output_dir) / (Path(temp_file).stem + '.png')

    # Check if the output file was created
    if not output_file.exists():
        # Remove the temporary file
        os.remove(temp_file)
        # Display error message
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
st.title('PlantUML Diagram Generator')

# Text area for user to enter PlantUML code
plantuml_code = st.text_area(label= "Your PlantUML code:", value=sample_plantuml, height=300)

# Automatically generate and display the diagram when the code changes
output_file_path = generate_uml_diagram(plantuml_code)
if output_file_path:
    # Display the generated diagram
    st.image(str(output_file_path), caption='Generated UML Diagram', use_column_width=True)
    
    # Provide a download button for the image
    get_image_download_link(str(output_file_path))
    
    # Remove the output diagram file after displaying it
    os.remove(output_file_path)