import os
import subprocess
import json
import re
from pathlib import Path

print("=== DEEP Spring Boot Architecture Analyzer ===")

input_dir = "/workspace/input"
output_dir = "/workspace/output"

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

projects = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]

def deep_spring_analysis(project_path):
    """Perform deep analysis of Spring Boot application structure"""
    
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
        'aspects': [],
        'mvc_controllers': [],
        'feign_clients': [],
        'kafka_listeners': [],
        'rabbit_listeners': [],
        'web_services': [],
        'jms_listeners': []
    }
    
    java_files = list(Path(project_path).rglob("*.java"))
    print(f"🔍 Analyzing {len(java_files)} Java files...")
    
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            class_name = java_file.stem
            package_path = str(java_file.relative_to(project_path))
            
            # Deep annotation analysis
            annotations = re.findall(r'@\w+', content)
            
            # REST Controllers and Web Controllers
            if '@RestController' in content:
                components['rest_controllers'].append({
                    'name': class_name, 
                    'file': package_path,
                    'methods': extract_rest_methods(content)
                })
                print(f"  🎮 REST Controller: {class_name}")
                
            elif '@Controller' in content:
                components['mvc_controllers'].append({
                    'name': class_name,
                    'file': package_path
                })
                print(f"  🌐 MVC Controller: {class_name}")
                
            # Services with different patterns
            elif '@Service' in content:
                components['services'].append({
                    'name': class_name,
                    'file': package_path
                })
                print(f"  ⚙️  Service: {class_name}")
                
            # Repository patterns
            elif '@Repository' in content:
                components['repositories'].append({
                    'name': class_name,
                    'file': package_path
                })
                print(f"  💾 Repository: {class_name}")
                
            elif any(repo in content for repo in ['JpaRepository', 'CrudRepository', 'MongoRepository', 'PagingAndSortingRepository']):
                components['jpa_repositories'].append({
                    'name': class_name,
                    'file': package_path,
                    'type': extract_repository_type(content)
                })
                print(f"  🗄️  JPA Repository: {class_name}")
                
            # Entities
            elif '@Entity' in content:
                components['entities'].append({
                    'name': class_name,
                    'file': package_path,
                    'table': extract_table_name(content)
                })
                print(f"  🏷️  Entity: {class_name}")
                
            # Configuration
            elif '@Configuration' in content:
                components['configs'].append({
                    'name': class_name,
                    'file': package_path,
                    'beans': extract_bean_methods(content)
                })
                print(f"  🔧 Configuration: {class_name}")
                
            # Components
            elif '@Component' in content:
                components['components'].append({
                    'name': class_name,
                    'file': package_path
                })
                print(f"  ⚡ Component: {class_name}")
                
            # REST Clients
            elif any(client in content for client in ['@FeignClient', '@RestClient', 'RestTemplate']):
                components['rest_clients'].append({
                    'name': class_name,
                    'file': package_path
                })
                print(f"  🌐 REST Client: {class_name}")
                
            # Scheduled tasks
            elif '@Scheduled' in content:
                components['scheduled_tasks'].append({
                    'name': class_name,
                    'file': package_path
                })
                print(f"  ⏰ Scheduled: {class_name}")
                
            # Event listeners
            elif any(listener in content for listener in ['@EventListener', '@KafkaListener', '@RabbitListener', '@JmsListener']):
                if '@KafkaListener' in content:
                    components['kafka_listeners'].append({
                        'name': class_name,
                        'file': package_path
                    })
                    print(f"  📨 Kafka Listener: {class_name}")
                elif '@RabbitListener' in content:
                    components['rabbit_listeners'].append({
                        'name': class_name,
                        'file': package_path
                    })
                    print(f"  🐇 RabbitMQ Listener: {class_name}")
                elif '@JmsListener' in content:
                    components['jms_listeners'].append({
                        'name': class_name,
                        'file': package_path
                    })
                    print(f"  📬 JMS Listener: {class_name}")
                else:
                    components['listeners'].append({
                        'name': class_name,
                        'file': package_path
                    })
                    print(f"  👂 Event Listener: {class_name}")
                
            # Web Services
            elif any(ws in content for ws in ['@WebService', '@Endpoint', '@SOAP']):
                components['web_services'].append({
                    'name': class_name,
                    'file': package_path
                })
                print(f"  🔗 Web Service: {class_name}")
                
            # AOP Aspects
            elif '@Aspect' in content:
                components['aspects'].append({
                    'name': class_name,
                    'file': package_path
                })
                print(f"  ✂️  Aspect: {class_name}")
                
            # Pattern-based inference (fallback)
            else:
                # Infer by naming convention
                if class_name.endswith('Service') and 'interface' not in content:
                    if class_name not in [s['name'] for s in components['services']]:
                        components['services'].append({
                            'name': class_name,
                            'file': package_path,
                            'inferred': True
                        })
                        print(f"  🔍 Inferred Service: {class_name}")
                        
                elif class_name.endswith('Controller') and 'interface' not in content:
                    if class_name not in [c['name'] for c in components['rest_controllers'] + components['mvc_controllers']]:
                        components['rest_controllers'].append({
                            'name': class_name,
                            'file': package_path,
                            'inferred': True
                        })
                        print(f"  🔍 Inferred Controller: {class_name}")
                        
                elif class_name.endswith('Repository') and 'interface' in content:
                    if class_name not in [r['name'] for r in components['repositories'] + components['jpa_repositories']]:
                        components['jpa_repositories'].append({
                            'name': class_name,
                            'file': package_path,
                            'inferred': True
                        })
                        print(f"  🔍 Inferred Repository: {class_name}")
                        
                # Check for common Spring patterns
                elif re.search(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)', content):
                    components['rest_controllers'].append({
                        'name': class_name,
                        'file': package_path,
                        'inferred': True,
                        'mappings': extract_request_mappings(content)
                    })
                    print(f"  🗺️  Mapped Controller: {class_name}")
                    
        except Exception as e:
            print(f"  ❌ Error reading {java_file}: {e}")
    
    return components

def extract_rest_methods(content):
    """Extract REST mapping methods from controller"""
    mappings = re.findall(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)\s*\([^)]*\)', content)
    return list(set(mappings))

def extract_repository_type(content):
    """Extract repository interface type"""
    if 'JpaRepository' in content:
        return 'JPA'
    elif 'CrudRepository' in content:
        return 'CRUD'
    elif 'MongoRepository' in content:
        return 'MongoDB'
    elif 'PagingAndSortingRepository' in content:
        return 'Paging'
    return 'Unknown'

def extract_table_name(content):
    """Extract database table name from entity"""
    table_match = re.search(r'@Table\s*\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
    if table_match:
        return table_match.group(1)
    return None

def extract_bean_methods(content):
    """Extract @Bean methods from configuration class"""
    bean_methods = re.findall(r'@Bean\s*\n\s*public\s+(\w+)', content)
    return bean_methods

def extract_request_mappings(content):
    """Extract request mapping paths"""
    mappings = re.findall(r'@\w+Mapping\s*\(\s*["\']([^"\']+)["\']', content)
    return mappings

def create_detailed_architecture_diagram(project, components, output_dir):
    """Create a comprehensive C4 diagram with all discovered components"""
    
    puml_lines = []
    
    puml_lines.append("@startuml")
    puml_lines.append("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml")
    puml_lines.append("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml")
    puml_lines.append("")
    puml_lines.append(f"title Detailed Architecture: {project}")
    puml_lines.append("")
    
    # System Context
    puml_lines.append("Person_Ext(user, \"External System\", \"Uses APIs\")")
    puml_lines.append("System_Boundary(microservice, \"Spring Boot Microservice\") {")
    puml_lines.append("")
    
    # API Layer
    if components['rest_controllers'] or components['mvc_controllers']:
        puml_lines.append("    Container_Boundary(api, \"API Layer\") {")
        
        for controller in components['rest_controllers'][:6]:
            puml_lines.append(f'        Component({controller["name"].lower()}, "{controller["name"]}", "REST Controller")')
            
        for controller in components['mvc_controllers'][:3]:
            puml_lines.append(f'        Component({controller["name"].lower()}_mvc, "{controller["name"]}", "MVC Controller")')
            
        puml_lines.append("    }")
        puml_lines.append("")
    
    # Business Layer
    if components['services'] or components['components']:
        puml_lines.append("    Container_Boundary(business, \"Business Layer\") {")
        
        for service in components['services'][:8]:
            puml_lines.append(f'        Component({service["name"].lower()}, "{service["name"]}", "Service")')
            
        for component in components['components'][:5]:
            puml_lines.append(f'        Component({component["name"].lower()}_comp, "{component["name"]}", "Component")')
            
        puml_lines.append("    }")
        puml_lines.append("")
    
    # Data Layer
    if components['repositories'] or components['jpa_repositories']:
        puml_lines.append("    Container_Boundary(data, \"Data Layer\") {")
        
        for repo in components['repositories'][:5]:
            puml_lines.append(f'        Component({repo["name"].lower()}, "{repo["name"]}", "Repository")')
            
        for repo in components['jpa_repositories'][:5]:
            puml_lines.append(f'        Component({repo["name"].lower()}_jpa, "{repo["name"]}", "JPA Repository")')
            
        puml_lines.append("    }")
        puml_lines.append("")
    
    puml_lines.append("}")
    puml_lines.append("")
    
    # External systems
    puml_lines.append('ContainerDb(database, "Database", "MySQL", "Stores application data")')
    
    if components['rest_clients']:
        puml_lines.append('System_Ext(external_api, "External API", "Third-party service")')
    
    if components['kafka_listeners']:
        puml_lines.append('System_Ext(kafka, "Kafka", "Message Broker")')
    
    if components['rabbit_listeners']:
        puml_lines.append('System_Ext(rabbitmq, "RabbitMQ", "Message Broker")')
    
    puml_lines.append("")
    
    # Relationships
    puml_lines.append('Rel(user, api, "HTTP Requests", "REST/JSON")')
    
    if components['rest_controllers'] and components['services']:
        puml_lines.append(f'Rel({components["rest_controllers"][0]["name"].lower()}, {components["services"][0]["name"].lower()}, "calls")')
    
    if components['services'] and (components['repositories'] or components['jpa_repositories']):
        if components['repositories']:
            repo_name = components['repositories'][0]["name"].lower()
        else:
            repo_name = components['jpa_repositories'][0]["name"].lower() + '_jpa'
        puml_lines.append(f'Rel({components["services"][0]["name"].lower()}, {repo_name}, "data access")')
    
    if components['repositories'] or components['jpa_repositories']:
        puml_lines.append('Rel(data, database, "Reads/Writes", "JDBC")')
    
    # Add comprehensive legend
    total_spring_components = sum(len(components[key]) for key in components if key != 'entities')
    
    puml_lines.append("")
    puml_lines.append("legend right")
    puml_lines.append("  == Spring Components Found ==")
    puml_lines.append(f"  Controllers: {len(components['rest_controllers']) + len(components['mvc_controllers'])}")
    puml_lines.append(f"  Services: {len(components['services'])}")
    puml_lines.append(f"  Repositories: {len(components['repositories']) + len(components['jpa_repositories'])}")
    puml_lines.append(f"  Entities: {len(components['entities'])}")
    puml_lines.append(f"  Configurations: {len(components['configs'])}")
    puml_lines.append(f"  Total Components: {total_spring_components}")
    puml_lines.append("end legend")
    puml_lines.append("")
    
    puml_lines.append("@enduml")
    
    puml_content = '\n'.join(puml_lines)
    
    # Save and generate diagram
    puml_file = os.path.join(output_dir, f"{project}_deep_architecture.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    try:
        subprocess.run(["java", "-jar", "/plantuml.jar", "-tpng", puml_file], check=True)
        print(f"✅ Created deep architecture diagram: {project}_deep_architecture.png")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating diagram: {e}")
    
    return puml_file

def print_detailed_summary(project, components):
    """Print comprehensive analysis summary"""
    print(f"\n{'='*70}")
    print(f"DEEP ANALYSIS SUMMARY: {project}")
    print(f"{'='*70}")
    
    total_components = sum(len(components[key]) for key in components)
    
    print(f"📊 TOTAL COMPONENTS FOUND: {total_components}")
    print(f"🔍 SPRING COMPONENTS: {sum(len(components[key]) for key in components if key != 'entities')}")
    print(f"🏷️  JPA ENTITIES: {len(components['entities'])}")
    
    print(f"\n🏗️  ARCHITECTURE LAYERS:")
    print(f"   🎮 API Layer: {len(components['rest_controllers']) + len(components['mvc_controllers'])} components")
    print(f"   ⚙️  Business Layer: {len(components['services']) + len(components['components'])} components") 
    print(f"   💾 Data Layer: {len(components['repositories']) + len(components['jpa_repositories'])} components")
    
    print(f"\n🔧 SPRING COMPONENT TYPES:")
    for comp_type, items in components.items():
        if items and comp_type != 'entities':
            type_name = comp_type.replace('_', ' ').title()
            print(f"   {type_name}: {len(items)}")
    
    # Show key findings
    if components['entities']:
        print(f"\n🗃️  KEY ENTITIES: {', '.join([e['name'] for e in components['entities'][:8]])}")
    
    if components['services']:
        print(f"⚙️  SERVICES: {', '.join([s['name'] for s in components['services'][:5]])}")
    
    if components['rest_controllers']:
        print(f"🎮 REST CONTROLLERS: {', '.join([c['name'] for c in components['rest_controllers'][:3]])}")

# Main execution
for project in projects:
    print(f"\n{'='*80}")
    print(f"DEEP ANALYSIS: {project}")
    print(f"{'='*80}")
    
    project_path = os.path.join(input_dir, project)
    
    # Perform deep analysis
    components = deep_spring_analysis(project_path)
    
    # Create detailed diagram
    create_detailed_architecture_diagram(project, components, output_dir)
    
    # Print comprehensive summary
    print_detailed_summary(project, components)

print(f"\n{'='*80}")
print("DEEP ARCHITECTURE ANALYSIS COMPLETE!")
print("Generated comprehensive C4 diagrams showing:")
print("  - API Layer with REST/MVC Controllers")
print("  - Business Layer with Services & Components") 
print("  - Data Layer with Repositories")
print("  - External integrations (Kafka, RabbitMQ, REST Clients)")
print("  - Complete component relationships")
print(f"{'='*80}")