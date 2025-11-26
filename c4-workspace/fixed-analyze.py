import os
import subprocess
import json
from pathlib import Path

print("=== Enhanced Spring Boot C4 Model Generator ===")

input_dir = "/workspace/input"
output_dir = "/workspace/output"

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

projects = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]

for project in projects:
    print(f"\n--- Analyzing: {project} ---")
    project_path = os.path.join(input_dir, project)
    
    # Enhanced Spring component detection
    components = {
        'controllers': [],
        'services': [], 
        'repositories': [],
        'entities': [],
        'configs': [],
        'rest_controllers': [],
        'mvc_controllers': []
    }
    
    java_files = list(Path(project_path).rglob("*.java"))
    print(f"Found {len(java_files)} Java files")
    
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            
            # More comprehensive Spring annotation detection
            if '@RestController' in content:
                components['rest_controllers'].append(java_file.stem)
                components['controllers'].append(java_file.stem)
                print(f"  ✓ REST Controller: {java_file.stem}")
            elif '@Controller' in content:
                components['mvc_controllers'].append(java_file.stem)
                components['controllers'].append(java_file.stem)
                print(f"  ✓ MVC Controller: {java_file.stem}")
            elif '@Service' in content:
                components['services'].append(java_file.stem)
                print(f"  ✓ Service: {java_file.stem}")
            elif '@Repository' in content:
                components['repositories'].append(java_file.stem)
                print(f"  ✓ Repository: {java_file.stem}")
            elif '@Entity' in content:
                components['entities'].append(java_file.stem)
                print(f"  ✓ Entity: {java_file.stem}")
            elif '@Configuration' in content or '@Bean' in content:
                components['configs'].append(java_file.stem)
                print(f"  ✓ Configuration: {java_file.stem}")
                
        except Exception as e:
            pass
    
    # Create detailed C4 diagram
    puml_content = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Container Diagram for {project}

Person(user, "User", "Uses the application")
Container(webapp, "Web Application", "Spring Boot", "Provides REST API")
ContainerDb(database, "Database", "MySQL", "Stores application data")

Rel(user, webapp, "Uses", "HTTPS/REST")
Rel(webapp, database, "Reads/Writes", "JDBC")

' Add components to the webapp container
Container_Boundary(webapp, "Web Application") {{
"""
    
    # Add components
    if components['controllers']:
        puml_content += "    ' === Controllers ===\\n"
        for controller in components['controllers'][:5]:  # Limit to first 5
            puml_content += f'    Component({controller.lower()}, "{controller}", "Spring Controller")\\n'
    
    if components['services']:
        puml_content += "    ' === Services ===\\n"
        for service in components['services'][:5]:
            puml_content += f'    Component({service.lower()}, "{service}", "Spring Service")\\n'
    
    if components['repositories']:
        puml_content += "    ' === Repositories ===\\n"
        for repo in components['repositories'][:5]:
            puml_content += f'    Component({repo.lower()}, "{repo}", "Spring Repository")\\n'
    
    puml_content += """}

' Add relationships
"""
    
    # Add relationships between components
    for controller in components['controllers'][:3]:
        for service in components['services'][:2]:
            puml_content += f'Rel({controller.lower()}, {service.lower()}, "calls")\\n'
    
    for service in components['services'][:2]:
        for repo in components['repositories'][:2]:
            puml_content += f'Rel({service.lower()}, {repo.lower()}, "uses")\\n'
    
    for repo in components['repositories'][:2]:
        puml_content += f'Rel({repo.lower()}, database, "reads/writes")\\n'
    
    puml_content += f"""
note right of webapp
  **Project:** {project}
  **Java Files:** {len(java_files)}
  **Controllers:** {len(components['controllers'])}
  **Services:** {len(components['services'])}
  **Repositories:** {len(components['repositories'])}
  **Entities:** {len(components['entities'])}
  **Configurations:** {len(components['configs'])}
end note

@enduml"""
    
    # Save and generate diagram
    puml_file = os.path.join(output_dir, f"{project}_detailed_architecture.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    try:
        subprocess.run(["java", "-jar", "/plantuml.jar", "-tpng", puml_file], check=True)
        print(f"✓ Created detailed diagram: {project}_detailed_architecture.png")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating diagram: {e}")
    
    # Print summary
    print(f"\\n=== Analysis Summary for {project} ===")
    print(f"Controllers: {len(components['controllers'])}")
    print(f"Services: {len(components['services'])}")
    print(f"Repositories: {len(components['repositories'])}")
    print(f"Entities: {len(components['entities'])}")
    print(f"Configurations: {len(components['configs'])}")

print("\\n" + "="*50)
print("ENHANCED ANALYSIS COMPLETE!")
print("Check the 'output' folder for detailed diagrams")
print("="*50)