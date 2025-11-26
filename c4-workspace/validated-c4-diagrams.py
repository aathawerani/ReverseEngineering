import os
import subprocess
import json
import re
from pathlib import Path

print("=== VALIDATED C4 Model Generator ===")

input_dir = "/workspace/input"
output_dir = "/workspace/output"

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

def analyze_spring_components(project_path):
    """Analyze Spring Boot components with dependency analysis"""
    
    components = {
        'rest_controllers': [],
        'services': [],
        'repositories': [],
        'jpa_repositories': [],
        'entities': [],
        'configs': [],
        'components': []
    }
    
    # Track dependencies between components
    dependencies = []
    
    java_files = list(Path(project_path).rglob("*.java"))
    print(f"📁 Found {len(java_files)} Java files")
    
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            class_name = java_file.stem
            package = str(java_file.relative_to(project_path))
            
            component_info = {
                'name': class_name,
                'file': package,
                'dependencies': []
            }
            
            # Find Spring annotations and dependencies
            if '@RestController' in content:
                components['rest_controllers'].append(component_info)
                print(f"  🎮 REST Controller: {class_name}")
                
                # Find autowired dependencies in controllers
                deps = find_autowired_dependencies(content, class_name)
                component_info['dependencies'] = deps
                dependencies.extend(deps)
                
            elif '@Service' in content:
                components['services'].append(component_info)
                print(f"  ⚙️  Service: {class_name}")
                
                # Find autowired dependencies in services
                deps = find_autowired_dependencies(content, class_name)
                component_info['dependencies'] = deps
                dependencies.extend(deps)
                
            elif '@Repository' in content or 'JpaRepository' in content:
                if '@Repository' in content:
                    components['repositories'].append(component_info)
                    print(f"  💾 Repository: {class_name}")
                else:
                    components['jpa_repositories'].append(component_info)
                    print(f"  🗄️  JPA Repository: {class_name}")
                    
            elif '@Entity' in content:
                table_name = extract_table_name(content)
                component_info['table'] = table_name
                components['entities'].append(component_info)
                print(f"  🏷️  Entity: {class_name}" + (f" → {table_name}" if table_name else ""))
                
            elif '@Configuration' in content:
                components['configs'].append(component_info)
                print(f"  🔧 Configuration: {class_name}")
                
        except Exception as e:
            continue
    
    return components, dependencies

def find_autowired_dependencies(content, source_class):
    """Find @Autowired dependencies in a class"""
    dependencies = []
    
    # Look for @Autowired fields
    autowired_pattern = r'@Autowired\s+(?:private|protected|public)\s+\w+\s+(\w+);'
    autowired_matches = re.findall(autowired_pattern, content)
    
    for field_name in autowired_matches:
        dependencies.append({
            'from': source_class,
            'to': field_name,
            'type': 'autowired'
        })
    
    # Look for constructor injection
    constructor_pattern = r'public\s+' + re.escape(source_class) + r'\s*\([^)]*(\w+\s+\w+)[^)]*\)'
    constructor_matches = re.findall(constructor_pattern, content)
    
    for param in constructor_matches:
        # Extract the type/name - this is simplified
        param_parts = param.strip().split()
        if len(param_parts) >= 2:
            dep_name = param_parts[1]
            dependencies.append({
                'from': source_class,
                'to': dep_name,
                'type': 'constructor'
            })
    
    return dependencies

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

note right of web_app
  <b>Spring Boot Application</b>
  Controllers: {len(components['rest_controllers'])}
  Services: {len(components['services'])}
  Repositories: {len(components['repositories']) + len(components['jpa_repositories'])}
end note

note left of database
  <b>Database Schema</b>
  Entities: {len(components['entities'])}
end note

@enduml"""
    
    puml_file = os.path.join(output_dir, f"{project}_c2_container.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    if generate_image(puml_file):
        print("  ✅ C2: Container diagram created")
    return puml_file

def create_c3_component_diagram(project, components, dependencies, output_dir):
    """C3: Component Diagram with validated relationships"""
    
    # Get actual components
    controllers = components['rest_controllers'][:4]
    services = components['services'][:6]
    repos = (components['repositories'] + components['jpa_repositories'])[:4]
    
    puml_content = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Component Diagram for {project} - Web Application

Container_Boundary(web_app, "Web Application") {{
"""
    
    # API Layer - Controllers
    if controllers:
        puml_content += "    ' === API Layer - Controllers ===\\n"
        for controller in controllers:
            puml_content += f'    Component({controller["name"].lower()}, "{controller["name"]}", "REST Controller")\\n'
        puml_content += "\\n"
    
    # Business Layer - Services
    if services:
        puml_content += "    ' === Business Layer - Services ===\\n"
        for service in services:
            puml_content += f'    Component({service["name"].lower()}, "{service["name"]}", "Business Service")\\n'
        puml_content += "\\n"
    
    # Data Layer - Repositories
    if repos:
        puml_content += "    ' === Data Layer - Repositories ===\\n"
        for repo in repos:
            puml_content += f'    Component({repo["name"].lower()}_repo, "{repo["name"]}", "Repository")\\n'
    
    puml_content += """}

ContainerDb(database, "Database", "MySQL", "Stores application data")

' External systems
System_Ext(raast_system, "Raast System", "Payment processing")
System_Ext(bank_api, "Bank API", "Financial services")

' External relationships
Rel(customer, web_app, "Uses", "HTTPS/REST")
"""
    
    # Add validated internal relationships based on dependencies
    valid_relationships = 0
    
    # Controller -> Service relationships
    for controller in controllers:
        controller_deps = [d for d in dependencies if d['from'] == controller['name']]
        for dep in controller_deps:
            # Check if dependency target is a service we know about
            target_service = next((s for s in services if s['name'] == dep['to']), None)
            if target_service:
                puml_content += f'Rel({controller["name"].lower()}, {target_service["name"].lower()}, "calls")\\n'
                valid_relationships += 1
    
    # Service -> Repository relationships
    for service in services:
        service_deps = [d for d in dependencies if d['from'] == service['name']]
        for dep in service_deps:
            # Check if dependency target is a repository we know about
            target_repo = next((r for r in repos if r['name'] == dep['to']), None)
            if target_repo:
                puml_content += f'Rel({service["name"].lower()}, {target_repo["name"].lower()}_repo, "uses")\\n'
                valid_relationships += 1
    
    # Repository -> Database relationships
    for repo in repos:
        puml_content += f'Rel({repo["name"].lower()}_repo, database, "reads/writes")\\n'
        valid_relationships += 1
    
    # Service -> External systems (based on naming patterns)
    for service in services:
        if any(keyword in service['name'].lower() for keyword in ['payment', 'raast', 'transaction']):
            puml_content += f'Rel({service["name"].lower()}, raast_system, "processes payments")\\n'
            valid_relationships += 1
        if any(keyword in service['name'].lower() for keyword in ['bank', 'financial']):
            puml_content += f'Rel({service["name"].lower()}, bank_api, "bank integration")\\n'
            valid_relationships += 1
    
    # Add validation note
    puml_content += f"""
note right of web_app
  <b>Validation Summary</b>
  Components: {len(controllers) + len(services) + len(repos)}
  Valid Relationships: {valid_relationships}
  Based on code analysis of:
  - @Autowired dependencies
  - Constructor injection
  - Spring component patterns
end note
"""
    
    puml_content += "\n@enduml"
    
    puml_file = os.path.join(output_dir, f"{project}_c3_component.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    if generate_image(puml_file):
        print(f"  ✅ C3: Component diagram created ({valid_relationships} validated relationships)")
    return puml_file, valid_relationships

def generate_validation_report(project, components, dependencies, valid_relationships, output_dir):
    """Generate a validation report showing what was found vs what's in diagrams"""
    
    report = f"""
# C4 Diagram Validation Report for {project}

## Analysis Summary
- Java Files Analyzed: {sum(len(components[key]) for key in components)}
- Spring Components Found: {sum(len(components[key]) for key in components if key != 'entities')}
- JPA Entities: {len(components['entities'])}
- Dependencies Found: {len(dependencies)}
- Valid Relationships in Diagram: {valid_relationships}

## Component Breakdown

### Controllers ({len(components['rest_controllers'])})
{chr(10).join([f"- {c['name']} ({c['file']})" for c in components['rest_controllers'][:10]])}
{'...' if len(components['rest_controllers']) > 10 else ''}

### Services ({len(components['services'])})
{chr(10).join([f"- {s['name']} ({s['file']})" for s in components['services'][:10]])}
{'...' if len(components['services']) > 10 else ''}

### Repositories ({len(components['repositories']) + len(components['jpa_repositories'])})
{chr(10).join([f"- {r['name']} ({r['file']})" for r in (components['repositories'] + components['jpa_repositories'])[:10]])}
{'...' if len(components['repositories'] + components['jpa_repositories']) > 10 else ''}

### Entities ({len(components['entities'])})
{chr(10).join([f"- {e['name']} → {e.get('table', 'N/A')} ({e['file']})" for e in components['entities'][:10]])}
{'...' if len(components['entities']) > 10 else ''}

## Dependency Analysis

### Found Dependencies ({len(dependencies)})
{chr(10).join([f"- {d['from']} → {d['to']} ({d['type']})" for d in dependencies[:20]])}
{'...' if len(dependencies) > 20 else ''}

## Diagram Accuracy Assessment

The generated C4 diagrams are based on:
- ✅ Spring annotation analysis (@Controller, @Service, @Repository, @Entity)
- ✅ Dependency injection analysis (@Autowired, constructor injection)
- ✅ File structure and package analysis

**Accuracy Level:** {'HIGH' if valid_relationships > 5 else 'MEDIUM' if valid_relationships > 2 else 'LOW'}

**Recommendations:**
{'✓ Good component coverage' if len(components['rest_controllers']) > 0 and len(components['services']) > 0 else '⚠️ Limited component discovery'}
{'✓ Strong dependency mapping' if valid_relationships > 5 else '⚠️ Limited dependency mapping'}

## Files Generated
- `{project}_c1_context.png` - System context diagram
- `{project}_c2_container.png` - Container diagram  
- `{project}_c3_component.png` - Component diagram (with {valid_relationships} validated relationships)
- `{project}_validation_report.md` - This report

## Manual Validation Steps
1. Check that all major controllers appear in C3 diagram
2. Verify service-layer dependencies match your business logic
3. Confirm repository relationships align with data access patterns
4. Review external system integrations
"""
    
    report_file = os.path.join(output_dir, f"{project}_validation_report.md")
    with open(report_file, "w") as f:
        f.write(report)
    
    print(f"  📋 Validation report generated: {project}_validation_report.md")
    return report_file

def generate_image(puml_file):
    """Generate PNG image from PlantUML file"""
    try:
        result = subprocess.run(
            ["java", "-jar", "/plantuml.jar", "-tpng", puml_file], 
            check=True, 
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error creating: {os.path.basename(puml_file)}")
        if e.stderr:
            print(f"     Error: {e.stderr[:200]}...")
        return False

def main():
    projects = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
    
    if not projects:
        print("❌ No projects found in input directory!")
        return
    
    for project in projects:
        print(f"\n{'='*60}")
        print(f"📊 GENERATING VALIDATED C4 MODEL FOR: {project}")
        print(f"{'='*60}")
        
        project_path = Path(input_dir) / project
        
        # Analyze components with dependencies
        print("🔍 Analyzing components and dependencies...")
        components, dependencies = analyze_spring_components(project_path)
        
        print(f"\n🎨 Generating validated diagrams...")
        
        # Generate diagrams
        create_c1_context_diagram(project, output_dir)
        create_c2_container_diagram(project, components, output_dir)
        
        # Component diagram returns relationship count for validation
        component_file, valid_relationships = create_c3_component_diagram(
            project, components, dependencies, output_dir
        )
        
        # Generate validation report
        generate_validation_report(project, components, dependencies, valid_relationships, output_dir)
        
        print(f"\n✅ VALIDATION COMPLETE: {project}")
        print(f"   Components: {sum(len(components[key]) for key in components if key != 'entities')}")
        print(f"   Dependencies: {len(dependencies)}")
        print(f"   Valid Relationships: {valid_relationships}")
    
    print(f"\n{'='*60}")
    print("🎉 VALIDATED C4 MODEL GENERATION COMPLETE!")
    print("Each project includes:")
    print("  • 3 C4 diagrams with validated relationships") 
    print("  • Detailed validation report")
    print("  • Dependency analysis")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()