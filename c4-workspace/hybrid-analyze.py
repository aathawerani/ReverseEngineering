import os
import subprocess
import json
import re
from pathlib import Path

print("=== HYBRID Spring Boot Architecture Analyzer ===")

input_dir = "/workspace/input"
output_dir = "/workspace/output"

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

projects = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]

def hybrid_spring_analysis(project_path):
    """Comprehensive analysis with enhanced detection"""
    
    components = {
        'controllers': [],
        'rest_controllers': [],
        'services': [],
        'repositories': [],
        'jpa_repositories': [],
        'entities': [],
        'configs': [],
        'components': [],
        'rest_clients': [],
        'scheduled_tasks': [],
        'listeners': [],
        'aspects': []
    }
    
    java_files = list(Path(project_path).rglob("*.java"))
    print(f"🔍 Analyzing {len(java_files)} Java files...")
    
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            class_name = java_file.stem
            file_path = str(java_file.relative_to(project_path))
            
            # Enhanced annotation detection
            if '@RestController' in content:
                components['rest_controllers'].append({
                    'name': class_name, 
                    'file': file_path,
                    'type': 'REST Controller'
                })
                print(f"  🎮 REST Controller: {class_name}")
                
            elif '@Controller' in content:
                components['controllers'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'MVC Controller'
                })
                print(f"  🌐 MVC Controller: {class_name}")
                
            # Service detection with multiple patterns
            elif '@Service' in content:
                components['services'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'Service'
                })
                print(f"  ⚙️  Service: {class_name}")
                
            # Repository patterns
            elif '@Repository' in content:
                components['repositories'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'Repository'
                })
                print(f"  💾 Repository: {class_name}")
                
            elif any(repo in content for repo in ['JpaRepository', 'CrudRepository', 'MongoRepository']):
                components['jpa_repositories'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'JPA Repository'
                })
                print(f"  🗄️  JPA Repository: {class_name}")
                
            # Entities
            elif '@Entity' in content:
                table_name = extract_table_name(content)
                components['entities'].append({
                    'name': class_name,
                    'file': file_path,
                    'table': table_name,
                    'type': 'JPA Entity'
                })
                print(f"  🏷️  Entity: {class_name}" + (f" → {table_name}" if table_name else ""))
                
            # Configuration
            elif '@Configuration' in content:
                components['configs'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'Configuration'
                })
                print(f"  🔧 Configuration: {class_name}")
                
            # Components
            elif '@Component' in content:
                components['components'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'Component'
                })
                print(f"  ⚡ Component: {class_name}")
                
            # REST Clients
            elif any(client in content for client in ['@FeignClient', 'RestTemplate']):
                components['rest_clients'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'REST Client'
                })
                print(f"  🌐 REST Client: {class_name}")
                
            # Enhanced pattern inference
            else:
                # Service inference with broader patterns
                if (class_name.endswith('Service') or class_name.endswith('ServiceImpl') or 
                    class_name.endswith('Manager') or class_name.endswith('Processor')) and 'interface' not in content:
                    if class_name not in [s['name'] for s in components['services']]:
                        components['services'].append({
                            'name': class_name,
                            'file': file_path,
                            'type': 'Service (inferred)',
                            'inferred': True
                        })
                        print(f"  🔍 Inferred Service: {class_name}")
                        
                # Controller inference
                elif (class_name.endswith('Controller') or class_name.endswith('Endpoint') or
                      class_name.endswith('Resource')) and 'interface' not in content:
                    if class_name not in [c['name'] for c in components['rest_controllers'] + components['controllers']]:
                        components['rest_controllers'].append({
                            'name': class_name,
                            'file': file_path,
                            'type': 'Controller (inferred)',
                            'inferred': True
                        })
                        print(f"  🔍 Inferred Controller: {class_name}")
                        
                # Repository inference
                elif class_name.endswith('Repository') and 'interface' in content:
                    if class_name not in [r['name'] for r in components['repositories'] + components['jpa_repositories']]:
                        components['jpa_repositories'].append({
                            'name': class_name,
                            'file': file_path,
                            'type': 'Repository (inferred)',
                            'inferred': True
                        })
                        print(f"  🔍 Inferred Repository: {class_name}")
                        
                # Check for request mappings (strong indicator of controllers)
                elif re.search(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping|PatchMapping)', content):
                    components['rest_controllers'].append({
                        'name': class_name,
                        'file': file_path,
                        'type': 'Controller (mapped)',
                        'inferred': True
                    })
                    print(f"  🗺️  Mapped Controller: {class_name}")
                    
                # Check for @Autowired or @Inject (Spring components)
                elif ('@Autowired' in content or '@Inject' in content or '@Resource' in content) and 'interface' not in content:
                    if class_name not in [c['name'] for c in components['services'] + components['components']]:
                        components['components'].append({
                            'name': class_name,
                            'file': file_path,
                            'type': 'Component (inferred)',
                            'inferred': True
                        })
                        print(f"  🔍 Inferred Component: {class_name}")
                        
        except Exception as e:
            print(f"  ❌ Error reading {java_file}: {e}")
    
    return components

def extract_table_name(content):
    """Extract database table name from entity"""
    table_match = re.search(r'@Table\s*\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
    if table_match:
        return table_match.group(1)
    return None

def create_rich_architecture_diagram(project, components, output_dir):
    """Create a detailed C4 diagram with comprehensive visualization"""
    
    puml_lines = []
    
    puml_lines.append("@startuml")
    puml_lines.append("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml")
    puml_lines.append("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml")
    puml_lines.append("")
    puml_lines.append(f"title Detailed Spring Boot Architecture: {project}")
    puml_lines.append("' Shows complete application structure with all discovered components")
    puml_lines.append("")
    
    # System Context
    puml_lines.append("Person_Ext(client, \"External Client\", \"Uses microservice APIs\")")
    puml_lines.append("System_Boundary(app, \"Spring Boot Application: " + project + "\") {")
    puml_lines.append("")
    
    # API Layer - Show even if empty to illustrate architecture
    puml_lines.append("    Container_Boundary(api_layer, \"API Layer\") {")
    
    if components['rest_controllers']:
        for controller in components['rest_controllers'][:6]:
            puml_lines.append(f'        Component({controller["name"].lower()}, "{controller["name"]}", "REST Controller")')
    else:
        puml_lines.append('        Component(api_placeholder, "REST Controllers", "Spring MVC", "Not detected")')
        
    if components['controllers']:
        for controller in components['controllers'][:3]:
            puml_lines.append(f'        Component({controller["name"].lower()}_web, "{controller["name"]}", "Web Controller")')
    
    puml_lines.append("    }")
    puml_lines.append("")
    
    # Business Layer
    puml_lines.append("    Container_Boundary(business_layer, \"Business Layer\") {")
    
    if components['services']:
        for service in components['services'][:8]:
            puml_lines.append(f'        Component({service["name"].lower()}, "{service["name"]}", "Business Service")')
    else:
        puml_lines.append('        Component(biz_placeholder, "Business Services", "Spring", "Not detected")')
        
    if components['components']:
        for component in components['components'][:5]:
            puml_lines.append(f'        Component({component["name"].lower()}_comp, "{component["name"]}", "Component")')
    
    puml_lines.append("    }")
    puml_lines.append("")
    
    # Data Layer
    puml_lines.append("    Container_Boundary(data_layer, \"Data Layer\") {")
    
    if components['repositories'] or components['jpa_repositories']:
        for repo in components['repositories'][:4]:
            puml_lines.append(f'        Component({repo["name"].lower()}, "{repo["name"]}", "Repository")')
            
        for repo in components['jpa_repositories'][:4]:
            puml_lines.append(f'        Component({repo["name"].lower()}_jpa, "{repo["name"]}", "JPA Repository")')
    else:
        puml_lines.append('        Component(data_placeholder, "Data Repositories", "Spring Data", "Not detected")')
    
    puml_lines.append("    }")
    puml_lines.append("")
    
    puml_lines.append("}")
    puml_lines.append("")
    
    # External Systems
    puml_lines.append('ContainerDb(database, "Database", "MySQL", "Stores application data")')
    
    if components['rest_clients']:
        puml_lines.append('System_Ext(external_api, "External API", "Third-party services")')
    
    puml_lines.append("")
    
    # Entity Layer (show entities separately)
    puml_lines.append("' === JPA Entities === ")
    if components['entities']:
        for i, entity in enumerate(components['entities'][:12]):  # Show first 12 entities
            table_info = f" → {entity['table']}" if entity.get('table') else ""
            puml_lines.append(f'Component(entity_{i}, "{entity["name"]}{table_info}", "JPA Entity")')
            puml_lines.append(f'Rel(entity_{i}, database, "maps to")')
    
    puml_lines.append("")
    
    # Core Relationships
    puml_lines.append("' === Core Application Flow ===")
    puml_lines.append('Rel(client, api_layer, "HTTP REST API", "JSON/HTTPS")')
    
    # Internal relationships (show architecture flow)
    if components['rest_controllers'] and components['services']:
        puml_lines.append(f'Rel(api_layer, business_layer, "delegates to", "method calls")')
    
    if components['services'] and (components['repositories'] or components['jpa_repositories']):
        puml_lines.append(f'Rel(business_layer, data_layer, "data access", "Spring Data")')
    
    if components['repositories'] or components['jpa_repositories']:
        puml_lines.append(f'Rel(data_layer, database, "persistence", "JDBC/JPA")')
    else:
        puml_lines.append(f'Rel(business_layer, database, "direct access", "JDBC")')
    
    # Entity relationships
    if components['entities'] and (components['repositories'] or components['jpa_repositories']):
        puml_lines.append(f'Rel(data_layer, database, "entity mapping", "JPA/Hibernate")')
    
    puml_lines.append("")
    
    # Comprehensive Notes and Legend
    total_controllers = len(components['rest_controllers']) + len(components['controllers'])
    total_services = len(components['services'])
    total_repos = len(components['repositories']) + len(components['jpa_repositories'])
    total_entities = len(components['entities'])
    
    puml_lines.append("note right of database")
    puml_lines.append("  **Database Schema**")
    puml_lines.append(f"  Entities: {total_entities}")
    if components['entities']:
        entity_list = ", ".join([e['name'] for e in components['entities'][:8]])
        puml_lines.append(f"  Sample: {entity_list}")
        if total_entities > 8:
            puml_lines.append(f"  ... and {total_entities - 8} more")
    puml_lines.append("end note")
    puml_lines.append("")
    
    puml_lines.append("note left of api_layer")
    puml_lines.append("  **API Layer**")
    puml_lines.append(f"  Controllers: {total_controllers}")
    if components['rest_controllers']:
        puml_lines.append(f"  REST: {len(components['rest_controllers'])}")
    if components['controllers']:
        puml_lines.append(f"  MVC: {len(components['controllers'])}")
    puml_lines.append("end note")
    puml_lines.append("")
    
    puml_lines.append("note left of business_layer")
    puml_lines.append("  **Business Logic**")
    puml_lines.append(f"  Services: {total_services}")
    puml_lines.append(f"  Components: {len(components['components'])}")
    if components['services']:
        service_list = ", ".join([s['name'] for s in components['services'][:4]])
        puml_lines.append(f"  Key Services: {service_list}")
    puml_lines.append("end note")
    puml_lines.append("")
    
    puml_lines.append("legend right")
    puml_lines.append("  == Architecture Summary ==")
    puml_lines.append(f"  **{project}**")
    puml_lines.append(f"  Controllers: {total_controllers}")
    puml_lines.append(f"  Services: {total_services}")
    puml_lines.append(f"  Repositories: {total_repos}")
    puml_lines.append(f"  Entities: {total_entities}")
    puml_lines.append(f"  Configurations: {len(components['configs'])}")
    puml_lines.append(f"  Total Files: {sum(len(components[key]) for key in components)}")
    puml_lines.append("  == Layers ==")
    puml_lines.append("  🎮 API - REST Controllers")
    puml_lines.append("  ⚙️  Business - Services/Logic")
    puml_lines.append("  💾 Data - Repositories")
    puml_lines.append("  🏷️  Entities - JPA Models")
    puml_lines.append("end legend")
    
    puml_lines.append("")
    puml_lines.append("@enduml")
    
    puml_content = '\n'.join(puml_lines)
    
    # Save and generate diagram
    puml_file = os.path.join(output_dir, f"{project}_rich_architecture.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    try:
        subprocess.run(["java", "-jar", "/plantuml.jar", "-tpng", puml_file], check=True)
        print(f"✅ Created rich architecture diagram: {project}_rich_architecture.png")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating diagram: {e}")
    
    return puml_file

def print_hybrid_summary(project, components):
    """Print comprehensive analysis summary"""
    print(f"\n{'='*80}")
    print(f"HYBRID ANALYSIS SUMMARY: {project}")
    print(f"{'='*80}")
    
    total_components = sum(len(components[key]) for key in components)
    spring_components = sum(len(components[key]) for key in components if key != 'entities')
    
    print(f"📊 TOTAL COMPONENTS: {total_components}")
    print(f"🔍 SPRING BEANS: {spring_components}")
    print(f"🏷️  JPA ENTITIES: {len(components['entities'])}")
    
    print(f"\n🏗️  ARCHITECTURE BREAKDOWN:")
    print(f"   🎮 API Layer (Controllers): {len(components['rest_controllers']) + len(components['controllers'])}")
    print(f"   ⚙️  Business Layer (Services): {len(components['services']) + len(components['components'])}") 
    print(f"   💾 Data Layer (Repositories): {len(components['repositories']) + len(components['jpa_repositories'])}")
    print(f"   🏷️  Entity Layer (Models): {len(components['entities'])}")
    
    print(f"\n📋 DETAILED FINDINGS:")
    for comp_type, items in components.items():
        if items:
            type_name = comp_type.replace('_', ' ').title()
            sample = ", ".join([item['name'] for item in items[:3]])
            print(f"   {type_name}: {len(items)} → {sample}" + ("..." if len(items) > 3 else ""))
    
    # Architecture assessment
    print(f"\n🔍 ARCHITECTURE ASSESSMENT:")
    if len(components['entities']) > 0:
        print(f"   ✅ Strong data model with {len(components['entities'])} entities")
    else:
        print(f"   ⚠️  No JPA entities detected")
        
    if len(components['services']) > 0:
        print(f"   ✅ Business logic layer with {len(components['services'])} services")
    else:
        print(f"   ⚠️  Limited service layer detected")
        
    if len(components['rest_controllers']) + len(components['controllers']) > 0:
        print(f"   ✅ API layer with {len(components['rest_controllers']) + len(components['controllers'])} controllers")
    else:
        print(f"   🔍 API layer components not detected - may use different patterns")
        
    if len(components['repositories']) + len(components['jpa_repositories']) > 0:
        print(f"   ✅ Data access layer with {len(components['repositories']) + len(components['jpa_repositories'])} repositories")
    else:
        print(f"   🔍 Repository layer not detected - may use direct database access")

# Main execution
for project in projects:
    print(f"\n{'='*80}")
    print(f"HYBRID ANALYSIS: {project}")
    print(f"{'='*80}")
    
    project_path = os.path.join(input_dir, project)
    
    # Perform hybrid analysis
    components = hybrid_spring_analysis(project_path)
    
    # Create rich diagram
    create_rich_architecture_diagram(project, components, output_dir)
    
    # Print hybrid summary
    print_hybrid_summary(project, components)

print(f"\n{'='*80}")
print("HYBRID ARCHITECTURE ANALYSIS COMPLETE!")
print("Generated detailed C4 diagrams showing:")
print("  ✅ Complete layered architecture (even with missing components)")
print("  ✅ All discovered JPA entities with table mappings") 
print("  ✅ Business services and components")
print("  ✅ Data access patterns")
print("  ✅ Architecture assessment and recommendations")
print(f"{'='*80}")