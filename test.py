import subprocess
import os

# Path to the PlantUML .jar file
plantuml_jar_path = '/Users/macbookpro/Documents/GitHub/prompt_to_diagram/plantuml.jar'

# PlantUML code
plantuml_code = """
@startuml
Alice -> Bob: Hello, Bob!
Bob --> Alice: Hi, Alice!
@enduml
"""

# Write the PlantUML code to a temporary file
temp_file = 'temp.puml'
with open(temp_file, 'w') as file:
    file.write(plantuml_code)

# Generate the diagram using the PlantUML .jar
output_file = 'output_diagram.png'
subprocess.run(['java', '-jar', plantuml_jar_path, temp_file, '-o', '.'])

# Remove the temporary file
os.remove(temp_file)

print(f"Diagram generated: {output_file}")