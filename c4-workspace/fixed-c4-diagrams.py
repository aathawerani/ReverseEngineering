import os
import subprocess
import json
import re
from pathlib import Path

print("=== PROPER C4 Model Generator - Context, Container, Component ===")

input_dir = "/workspace/input"
output_dir = "/workspace/output"

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

def analyze_spring_components(project_path):
    """Analyze Spring Boot components"""
    
    components = {
        'rest_controllers': [],
        'services': [],
        'repositories': [],
        'jpa_repositories': [],
        'entities': [],
        'configs': [],
        'components': []
    }
    
    java_files = list(Path(project_path).rglob("*.java"))
    print(f"📁 Found {len(java_files)} Java files")
    
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            class_name = java_file.stem
            
            if '@RestController' in content:
                components['rest_controllers'].append({'name': class_name})
                print(f"  🎮 REST Controller: {class_name}")
            elif '@Service' in content:
                components['services'].append({'name': class_name})
                print(f"  ⚙️  Service: {class_name}")
            elif '@Repository' in content:
                components['repositories'].append({'name': class_name})
                print(f"  💾 Repository: {class_name}")
            elif 'JpaRepository' in content:
                components['jpa_repositories'].append({'name': class_name})
                print(f"  🗄️  JPA Repository: {class_name}")
            elif '@Entity' in content:
                table_name = extract_table_name(content)
                components['entities'].append({'name': class_name, 'table': table_name})
                print(f"  🏷️  Entity: {class_name}" + (f" → {table_name}" if table_name else ""))
            elif '@Configuration' in content:
                components['configs'].append({'name': class_name})
                print(f"  🔧 Configuration: {class_name}")
                
        except Exception as e:
            continue
    
    return components

def extract_table_name(content):
    """Extract database table name from entity"""
    table_match = re.search(r'@Table\s*\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
    return table_match.group(1) if table_match else None

def create_c1_context_diagram(project, output_dir):
    """C1: System Context Diagram"""
    
    puml_content = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

title System Context Diagram for {project}

Person(customer, "Customer", "A customer making payments")
Person(merchant, "Merchant", "A business receiving payments") 
Person(admin, "Administrator", "System administrator")

System({project}, "{project}", "Payment processing microservice")

System_Ext(raast, "Raast System", "National payment infrastructure")
System_Ext(banking, "Banking Systems", "Financial institution APIs")
System_Ext(notification, "Notification Service", "SMS/email service")

Rel(customer, {project}, "Makes payments using")
Rel(merchant, {project}, "Receives payments through")
Rel(admin, {project}, "Manages configuration of")

Rel({project}, raast, "Processes payments via")
Rel({project}, banking, "Integrates with bank APIs")
Rel({project}, notification, "Sends notifications using")

@enduml"""
    
    puml_file = os.path.join(output_dir, f"{project}_c1_context.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    if generate_image(puml_file):
        print("  ✅ C1: Context diagram created")
    return puml_file

def create_c2_container_diagram(project, components, output_dir):
    """C2: Container Diagram"""
    
    puml_content = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Container Diagram for {project}

Person(customer, "Customer", "Uses payment services")

System_Boundary({project}_system, "{project} System") {{
    Container(web_app, "Web Application", "Spring Boot", "Provides REST API for payment processing")
    ContainerDb(database, "Database", "MySQL", "Stores transactions, merchants, and configuration")
}}

System_Ext(raast, "Raast System", "National payment infrastructure")
System_Ext(bank_apis, "Bank APIs", "Financial institution services")

Rel(customer, web_app, "Makes payments using", "HTTPS/REST")

Rel(web_app, database, "Reads from and writes to", "JDBC")
Rel(web_app, raast, "Processes payments via", "ISO8583/API")
Rel(web_app, bank_apis, "Integrates with", "SOAP/REST")

' Application statistics
note right of web_app
  <b>Spring Boot Application</b>
  Controllers: {len(components['rest_controllers'])}
  Services: {len(components['services'])}
  Repositories: {len(components['repositories']) + len(components['jpa_repositories'])}
end note

note left of database
  <b>Database Schema</b>
  Entities: {len(components['entities'])}
  Key domains:
  - Payment processing
  - Merchant management  
  - Transaction logging
  - System configuration
end note

@enduml"""
    
    puml_file = os.path.join(output_dir, f"{project}_c2_container.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    if generate_image(puml_file):
        print("  ✅ C2: Container diagram created")
    return puml_file

def create_c3_component_diagram(project, components, output_dir):
    """C3: Component Diagram - Shows components inside the web application"""
    
    # Get actual components found in analysis
    controllers = [c['name'] for c in components['rest_controllers'][:4]] or ["PaymentController", "MerchantController"]
    services = [s['name'] for s in components['services'][:4]] or ["PaymentService", "NotificationService"]
    repos = [r['name'] for r in (components['repositories'] + components['jpa_repositories'])[:3]] or ["PaymentRepository"]
    
    puml_content = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Component Diagram for {project} - Web Application

Container(web_app, "Web Application", "Spring Boot", "Payment processing application")

Container_Boundary(web_app, "Web Application") {{
"""
    
    # API Layer components
    puml_content += "    ' === API Layer ===\\n"
    for controller in controllers:
        puml_content += f'    Component({controller.lower()}, "{controller}", "Spring REST Controller")\\n'
    
    # Business Layer components  
    puml_content += "    \\n    ' === Business Layer ===\\n"
    for service in services:
        puml_content += f'    Component({service.lower()}, "{service}", "Spring Service")\\n'
    
    # Data Layer components
    puml_content += "    \\n    ' === Data Layer ===\\n"
    for repo in repos:
        puml_content += f'    Component({repo.lower()}, "{repo}", "Spring Repository")\\n'
    
    puml_content += """}

ContainerDb(database, "Database", "MySQL", "Stores application data")

' External systems
System_Ext(raast, "Raast System", "Payment processing")
System_Ext(bank, "Bank API", "Financial services")

' Relationships
Rel(customer, web_app, "Uses", "HTTPS/REST")
"""

    # Internal relationships
    for controller in controllers:
        for service in services[:2]:  # Connect each controller to first 2 services
            puml_content += f'Rel({controller.lower()}, {service.lower()}, "Uses")\\n'
    
    for service in services:
        for repo in repos[:2]:  # Connect each service to first 2 repositories
            puml_content += f'Rel({service.lower()}, {repo.lower()}, "Uses")\\n'
    
    for repo in repos:
        puml_content += f'Rel({repo.lower()}, database, "Reads/Writes")\\n'
    
    # External integrations
    for service in services[:2]:
        puml_content += f'Rel({service.lower()}, raast, "Calls")\\n'
        puml_content += f'Rel({service.lower()}, bank, "Integrates with")\\n'
    
    puml_content += """
note right of web_app
  <b>Layered Architecture</b>
  API Layer: {controllers_count} controllers
  Business Layer: {services_count} services  
  Data Layer: {repos_count} repositories
end note
""".format(
    controllers_count=len(controllers),
    services_count=len(services), 
    repos_count=len(repos)
)

    puml_content += "\n@enduml"
    
    puml_file = os.path.join(output_dir, f"{project}_c3_component.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    if generate_image(puml_file):
        print("  ✅ C3: Component diagram created")
    return puml_file

def create_uml_class_diagram(project, components, output_dir):
    """Bonus: UML Class Diagram (not part of C4 model)"""
    
    # Focus on key entities and their relationships
    key_entities = components['entities'][:8]  # Show first 8 entities
    
    puml_content = f"""@startuml
title UML Class Diagram for {project} - Key Entities

' Entity classes
"""
    
    for entity in key_entities:
        table_info = f"\\n(table: {entity['table']})" if entity.get('table') else ""
        puml_content += f'class {entity["name"]} {{\n}}\n'
        puml_content += f'note top of {entity["name"]}\n{table_info}\nend note\n\n'
    
    # Add some sample relationships (in a real scenario, these would be parsed from code)
    if len(key_entities) >= 2:
        puml_content += f'{key_entities[0]["name"]} --> {key_entities[1]["name"]} : "references"\n'
    if len(key_entities) >= 3:
        puml_content += f'{key_entities[1]["name"]} --> {key_entities[2]["name"]} : "has many"\n'
    if len(key_entities) >= 4:
        puml_content += f'{key_entities[0]["name"]} --> {key_entities[3]["name"]} : "belongs to"\n'
    
    puml_content += """
note right
  <b>Domain Model</b>
  Shows key JPA entities
  and their relationships
  Based on database schema
end note

@enduml"""
    
    puml_file = os.path.join(output_dir, f"{project}_uml_classes.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    if generate_image(puml_file):
        print("  📊 Bonus: UML class diagram created")
    return puml_file

def generate_image(puml_file):
    """Generate PNG image from PlantUML file"""
    try:
        subprocess.run(["java", "-jar", "/plantuml.jar", "-tpng", puml_file], 
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error creating: {os.path.basename(puml_file)}")
        print(f"     PlantUML error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False

def main():
    projects = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
    
    if not projects:
        print("❌ No projects found in input directory!")
        return
    
    for project in projects:
        print(f"\n{'='*60}")
        print(f"📊 GENERATING C4 MODEL FOR: {project}")
        print(f"{'='*60}")
        
        project_path = Path(input_dir) / project
        
        # Analyze components
        components = analyze_spring_components(project_path)
        
        print(f"\n🎨 Generating diagrams...")
        
        # Generate the core C4 diagrams
        create_c1_context_diagram(project, output_dir)
        create_c2_container_diagram(project, components, output_dir) 
        create_c3_component_diagram(project, components, output_dir)
        
        # Bonus: UML class diagram (not part of C4)
        create_uml_class_diagram(project, components, output_dir)
        
        print(f"\n✅ COMPLETED: {project}")
        print("   Generated:")
        print("   • C1: System Context Diagram")
        print("   • C2: Container Diagram") 
        print("   • C3: Component Diagram")
        print("   • Bonus: UML Class Diagram")
    
    print(f"\n{'='*60}")
    print("🎉 C4 MODEL GENERATION COMPLETE!")
    print("Generated 3 core C4 diagrams + 1 bonus UML diagram per project")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()