import os
import subprocess
import json
import re
from pathlib import Path

print("=== Comprehensive Spring Boot C4 Model Generator ===")

input_dir = "/workspace/input"
output_dir = "/workspace/output"

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

projects = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]

def create_comprehensive_diagram(project, components, output_dir):
    """Create a detailed C4 diagram showing all discovered components"""
    
    # Build the PlantUML content step by step to avoid f-string issues
    puml_lines = []
    
    puml_lines.append("@startuml")
    puml_lines.append("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml")
    puml_lines.append("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml")
    puml_lines.append("")
    puml_lines.append(f"title Spring Boot Microservice: {project}")
    puml_lines.append("' Comprehensive Architecture Diagram")
    puml_lines.append("")
    puml_lines.append('Person(user, "External System", "Uses REST API")')
    puml_lines.append('Container(api, "API Layer", "Spring Boot", "REST Controllers")')
    puml_lines.append('Container(service, "Service Layer", "Spring", "Business Logic")')
    puml_lines.append('Container(repository, "Repository Layer", "Spring Data JPA", "Data Access")')
    puml_lines.append('ContainerDb(database, "Database", "MySQL", "Stores Entities")')
    puml_lines.append("")
    
    # API Layer Components
    puml_lines.append("' API Layer Components")
    puml_lines.append("Container_Boundary(api, \"API Layer\") {")
    
    # Add REST Controllers
    if components['rest_controllers']:
        for controller in components['rest_controllers'][:8]:
            puml_lines.append(f'    Component({controller["name"].lower()}, "{controller["name"]}", "REST Controller")')
    
    puml_lines.append("}")
    puml_lines.append("")
    
    # Service Layer Components
    puml_lines.append("Container_Boundary(service, \"Service Layer\") {")
    
    if components['services']:
        for service in components['services'][:8]:
            puml_lines.append(f'    Component({service["name"].lower()}, "{service["name"]}", "Service")')
    
    if components['components']:
        for component in components['components'][:5]:
            puml_lines.append(f'    Component({component["name"].lower()}_comp, "{component["name"]}", "Component")')
    
    puml_lines.append("}")
    puml_lines.append("")
    
    # Repository Layer Components
    puml_lines.append("Container_Boundary(repository, \"Repository Layer\") {")
    
    if components['repositories']:
        for repo in components['repositories'][:6]:
            puml_lines.append(f'    Component({repo["name"].lower()}, "{repo["name"]}", "Repository")')
    
    if components['jpa_repositories']:
        for repo in components['jpa_repositories'][:6]:
            puml_lines.append(f'    Component({repo["name"].lower()}_jpa, "{repo["name"]}", "JPA Repository")')
    
    puml_lines.append("}")
    puml_lines.append("")
    
    # Entity Layer
    puml_lines.append("' Entity Layer (outside containers)")
    
    if components['entities']:
        for entity in components['entities'][:10]:
            puml_lines.append(f'Component({entity["name"].lower()}_ent, "{entity["name"]}", "JPA Entity")')
    
    puml_lines.append("")
    
    # Main relationships
    puml_lines.append("' Main relationships")
    puml_lines.append('Rel(user, api, "HTTP Requests", "REST/JSON")')
    puml_lines.append('Rel(api, service, "Calls", "Java")')
    puml_lines.append('Rel(service, repository, "Uses", "Spring Data")')
    puml_lines.append('Rel(repository, database, "Reads/Writes", "JDBC")')
    puml_lines.append("")
    
    # Entity relationships
    puml_lines.append("' Entity relationships")
    
    # Connect entities to database
    for entity in components['entities'][:5]:
        puml_lines.append(f'Rel({entity["name"].lower()}_ent, database, "Maps to", "JPA")')
    
    # Internal component relationships (simplified)
    if components['rest_controllers'] and components['services']:
        puml_lines.append(f'Rel({components["rest_controllers"][0]["name"].lower()}, {components["services"][0]["name"].lower()}, "delegates to")')
    
    if components['services'] and (components['repositories'] or components['jpa_repositories']):
        if components['repositories']:
            repo_target = components['repositories'][0]["name"].lower()
        else:
            repo_target = components['jpa_repositories'][0]["name"].lower() + '_jpa'
        puml_lines.append(f'Rel({components["services"][0]["name"].lower()}, {repo_target}, "data access")')
    
    puml_lines.append("")
    
    # Add comprehensive notes
    entity_names = [e['name'] for e in components['entities'][:15]]
    entity_list = ', '.join(entity_names)
    if len(components['entities']) > 15:
        entity_list += '...'
    
    puml_lines.append('note right of database')
    puml_lines.append('  **Database Entities:**')
    puml_lines.append(f'  {entity_list}')
    puml_lines.append('end note')
    puml_lines.append("")
    
    puml_lines.append('note left of api')
    puml_lines.append('  **API Layer:**')
    puml_lines.append(f'  REST Controllers: {len(components["rest_controllers"])}')
    puml_lines.append(f'  Web Controllers: {len(components["web_controllers"])}')
    puml_lines.append('end note')
    puml_lines.append("")
    
    puml_lines.append('note left of service')
    puml_lines.append('  **Business Logic:**')
    puml_lines.append(f'  Services: {len(components["services"])}')
    puml_lines.append(f'  Components: {len(components["components"])}')
    puml_lines.append(f'  Scheduled Tasks: {len(components["scheduled_tasks"])}')
    puml_lines.append('end note')
    puml_lines.append("")
    
    puml_lines.append('note right of repository')
    puml_lines.append('  **Data Access:**')
    puml_lines.append(f'  Repositories: {len(components["repositories"])}')
    puml_lines.append(f'  JPA Repositories: {len(components["jpa_repositories"])}')
    puml_lines.append('end note')
    puml_lines.append("")
    
    total_components = sum(len(components[key]) for key in components if key != 'entities')
    
    puml_lines.append('legend right')
    puml_lines.append('  **Project Summary**')
    puml_lines.append(f'  Total Java Files: {sum(len(components[key]) for key in components)}')
    puml_lines.append(f'  Spring Components Found: {total_components}')
    puml_lines.append(f'  JPA Entities: {len(components["entities"])}')
    puml_lines.append('end legend')
    puml_lines.append("")
    
    puml_lines.append("@enduml")
    
    puml_content = '\n'.join(puml_lines)
    
    # Save and generate diagram
    puml_file = os.path.join(output_dir, f"{project}_comprehensive_architecture.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    try:
        subprocess.run(["java", "-jar", "/plantuml.jar", "-tpng", puml_file], check=True)
        print(f"✅ Created comprehensive diagram: {project}_comprehensive_architecture.png")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating diagram: {e}")
    
    return puml_file

def print_summary(project, components):
    """Print detailed analysis summary"""
    print(f"\n{'='*60}")
    print(f"COMPREHENSIVE ANALYSIS SUMMARY: {project}")
    print(f"{'='*60}")
    
    total_components = sum(len(components[key]) for key in components)
    print(f"📊 Total Spring Components Found: {total_components}")
    
    print(f"\n🔍 Detailed Breakdown:")
    print(f"   🎮 REST Controllers: {len(components['rest_controllers'])}")
    print(f"   🌐 Web Controllers: {len(components['web_controllers'])}") 
    print(f"   ⚙️  Services: {len(components['services'])}")
    print(f"   💾 Repositories: {len(components['repositories'])}")
    print(f"   🗄️  JPA Repositories: {len(components['jpa_repositories'])}")
    print(f"   🏷️  Entities: {len(components['entities'])}")
    print(f"   ⚡ Components: {len(components['components'])}")
    print(f"   🔧 Configurations: {len(components['configs'])}")
    print(f"   ⏰ Scheduled Tasks: {len(components['scheduled_tasks'])}")
    print(f"   👂 Listeners: {len(components['listeners'])}")
    print(f"   ✂️  Aspects: {len(components['aspects'])}")
    
    # Show some examples
    if components['entities']:
        print(f"\n🏷️  Sample Entities: {', '.join([e['name'] for e in components['entities'][:5]])}")
    
    if components['rest_controllers']:
        print(f"🎮 REST Controllers: {', '.join([c['name'] for c in components['rest_controllers'][:3]])}")
    
    if components['services']:
        print(f"⚙️  Services: {', '.join([s['name'] for s in components['services'][:3]])}")

# Main analysis loop
for project in projects:
    print(f"\n--- Comprehensive Analysis: {project} ---")
    project_path = os.path.join(input_dir, project)
    
    # Comprehensive component detection
    components = {
        'web_controllers': [],
        'rest_controllers': [],
        'services': [],
        'repositories': [],
        'jpa_repositories': [],
        'entities': [],
        'configs': [],
        'components': [],
        'beans': [],
        'scheduled_tasks': [],
        'listeners': [],
        'aspects': []
    }
    
    java_files = list(Path(project_path).rglob("*.java"))
    print(f"Found {len(java_files)} Java files")
    
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            class_name = java_file.stem
            file_path = str(java_file)
            
            # Comprehensive Spring annotation detection
            if '@RestController' in content:
                components['rest_controllers'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ REST Controller: {class_name}")
                
            elif '@Controller' in content:
                components['web_controllers'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ Web Controller: {class_name}")
                
            elif '@Service' in content:
                components['services'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ Service: {class_name}")
                
            elif '@Repository' in content:
                components['repositories'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ Repository: {class_name}")
                
            elif 'extends JpaRepository' in content or 'extends CrudRepository' in content:
                components['jpa_repositories'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ JPA Repository: {class_name}")
                
            elif '@Entity' in content:
                components['entities'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ Entity: {class_name}")
                
            elif '@Configuration' in content:
                components['configs'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ Configuration: {class_name}")
                
            elif '@Component' in content:
                components['components'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ Component: {class_name}")
                
            elif '@Bean' in content and '@Configuration' not in content:
                components['beans'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ Bean: {class_name}")
                
            elif '@Scheduled' in content:
                components['scheduled_tasks'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ Scheduled Task: {class_name}")
                
            elif '@Aspect' in content:
                components['aspects'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ Aspect: {class_name}")
                
            elif '@EventListener' in content or 'ApplicationListener' in content:
                components['listeners'].append({'name': class_name, 'file': file_path})
                print(f"  ✅ Listener: {class_name}")
                
            # Look for common patterns without annotations
            elif re.search(r'class\s+\w+Service\b', content) and 'interface' not in content:
                if class_name.endswith('Service') and class_name not in [s['name'] for s in components['services']]:
                    components['services'].append({'name': class_name, 'file': file_path, 'inferred': True})
                    print(f"  🔍 Inferred Service: {class_name}")
                    
            elif re.search(r'class\s+\w+Controller\b', content) and 'interface' not in content:
                if class_name.endswith('Controller') and class_name not in [c['name'] for c in components['rest_controllers'] + components['web_controllers']]:
                    components['rest_controllers'].append({'name': class_name, 'file': file_path, 'inferred': True})
                    print(f"  🔍 Inferred Controller: {class_name}")
                    
            elif re.search(r'interface\s+\w+Repository\b', content):
                if class_name.endswith('Repository') and class_name not in [r['name'] for r in components['repositories'] + components['jpa_repositories']]:
                    components['jpa_repositories'].append({'name': class_name, 'file': file_path, 'inferred': True})
                    print(f"  🔍 Inferred Repository: {class_name}")
                
        except Exception as e:
            print(f"  ❌ Error reading {java_file}: {e}")
    
    # Create comprehensive C4 diagram
    create_comprehensive_diagram(project, components, output_dir)
    
    # Print detailed summary
    print_summary(project, components)

print("\n" + "="*70)
print("COMPREHENSIVE ANALYSIS COMPLETE!")
print("Check the 'output' folder for detailed architecture diagrams")
print("="*70)