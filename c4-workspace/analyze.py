import os
import subprocess
import json
from pathlib import Path

print("=== Spring Boot C4 Model Generator ===")
print("This tool creates C4 architecture diagrams for Spring Boot microservices")

input_dir = "/workspace/input"
output_dir = "/workspace/output"

# Create directories if they don't exist
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Check for projects
projects = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]

if not projects:
    print("No Spring Boot projects found in input directory!")
    print("Creating a sample diagram to demonstrate...")
    
    # Create a sample diagram
    sample_puml = """@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Sample Spring Boot Microservice

Person(user, "User", "Uses the application")
Container(webapp, "Web Application", "Spring Boot", "Provides REST API")
ContainerDb(database, "Database", "MySQL", "Stores application data")

Rel(user, webapp, "Uses", "HTTPS/REST")
Rel(webapp, database, "Reads/Writes", "JDBC")

note right of webapp
  **Technology Stack:**
  - Spring Boot
  - Spring MVC
  - Spring Data JPA
  - MySQL Database
end note
@enduml"""
    
    sample_file = os.path.join(output_dir, "sample_architecture.puml")
    with open(sample_file, "w") as f:
        f.write(sample_puml)
    
    # Generate PNG
    try:
        subprocess.run(["java", "-jar", "/plantuml.jar", "-tpng", sample_file], check=True)
        print("✓ Created sample diagram: sample_architecture.png")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error generating PNG: {e}")
    
else:
    print(f"Found {len(projects)} project(s): {', '.join(projects)}")
    
    for project in projects:
        print(f"\n--- Processing: {project} ---")
        project_path = os.path.join(input_dir, project)
        
        # Count Java files to show we found something
        java_files = list(Path(project_path).rglob("*.java"))
        print(f"Found {len(java_files)} Java files")
        
        # Look for Spring components
        controllers = []
        services = []
        repositories = []
        
        for java_file in Path(project_path).rglob("*.java"):
            try:
                content = java_file.read_text(encoding='utf-8', errors='ignore')
                if '@RestController' in content or '@Controller' in content:
                    controllers.append(java_file.stem)
                elif '@Service' in content:
                    services.append(java_file.stem)
                elif '@Repository' in content or 'JpaRepository' in content:
                    repositories.append(java_file.stem)
            except:
                pass
        
        print(f"Found {len(controllers)} controllers, {len(services)} services, {len(repositories)} repositories")
        
        # Create C4 diagram
        puml_content = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Spring Boot Microservice: {project}

Person(user, "User", "Uses the application")
Container(webapp, "Web Application", "Spring Boot", "Handles business logic")
ContainerDb(database, "Database", "MySQL", "Stores application data")

Rel(user, webapp, "Uses", "HTTPS/REST")
Rel(webapp, database, "Reads/Writes", "JDBC")

note right of webapp
  **Project:** {project}
  **Java Files:** {len(java_files)}
  **Controllers:** {len(controllers)}
  **Services:** {len(services)}
  **Repositories:** {len(repositories)}
  **Framework:** Spring Boot
end note
@enduml"""
        
        # Save diagram
        puml_file = os.path.join(output_dir, f"{project}_architecture.puml")
        with open(puml_file, "w") as f:
            f.write(puml_content)
        
        # Generate PNG
        try:
            subprocess.run(["java", "-jar", "/plantuml.jar", "-tpng", puml_file], check=True)
            print(f"✓ Created diagram: {project}_architecture.png")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error creating diagram: {e}")

print("\n" + "="*50)
print("ANALYSIS COMPLETE!")
print("Check the 'output' folder for your C4 diagrams:")
print("- .puml files: PlantUML source code")
print("- .png files: Generated diagram images")
print("="*50)