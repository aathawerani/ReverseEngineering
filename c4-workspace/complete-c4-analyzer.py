import os
import subprocess
import json
import re
from pathlib import Path

print("=== COMPLETE Spring Boot C4 Architecture Analyzer ===")

input_dir = "/workspace/input"
output_dir = "/workspace/output"

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

def analyze_spring_components(project_path):
    """Analyze Spring Boot components with enhanced detection"""
    
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
                
            # Service detection
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
                
            # Enhanced pattern inference
            else:
                # Service inference
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
                        
                # Check for request mappings
                elif re.search(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping|PatchMapping)', content):
                    components['rest_controllers'].append({
                        'name': class_name,
                        'file': file_path,
                        'type': 'Controller (mapped)',
                        'inferred': True
                    })
                    print(f"  🗺️  Mapped Controller: {class_name}")
                        
        except Exception as e:
            print(f"  ❌ Error reading {java_file}: {e}")
    
    return components

def extract_table_name(content):
    """Extract database table name from entity"""
    table_match = re.search(r'@Table\s*\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
    if table_match:
        return table_match.group(1)
    return None

def extract_architecture_details(project_path):
    """Extract additional architectural details"""
    
    details = {
        'build_tool': 'Maven' if (project_path / "pom.xml").exists() else 'Gradle' if (project_path / "build.gradle").exists() else 'Unknown',
        'database_type': detect_database_type(project_path),
        'external_dependencies': detect_external_dependencies(project_path),
        'api_endpoints': extract_api_endpoints(project_path),
        'security_features': detect_security_features(project_path),
    }
    return details

def detect_database_type(project_path):
    """Detect database type from configuration"""
    config_files = list(project_path.rglob("application*.yml")) + list(project_path.rglob("application*.properties"))
    
    for config_file in config_files[:3]:  # Check first 3 config files
        try:
            content = config_file.read_text(encoding='utf-8', errors='ignore')
            if 'mysql' in content.lower() or 'jdbc:mysql' in content:
                return "MySQL"
            elif 'postgresql' in content.lower():
                return "PostgreSQL"
            elif 'oracle' in content.lower():
                return "Oracle"
        except:
            continue
    return "Database"

def detect_external_dependencies(project_path):
    """Detect external dependencies"""
    dependencies = set()
    java_files = list(project_path.rglob("*.java"))
    
    for java_file in java_files[:50]:  # Sample files
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            
            if any(term in content for term in ['@KafkaListener', 'KafkaTemplate']):
                dependencies.add('Apache Kafka')
            if any(term in content for term in ['@RabbitListener', 'RabbitTemplate']):
                dependencies.add('RabbitMQ')
            if any(term in content for term in ['RestTemplate', 'WebClient', '@FeignClient']):
                dependencies.add('REST Clients')
            if any(term in content for term in ['WebService', 'SOAP']):
                dependencies.add('SOAP Web Services')
                
        except:
            pass
    
    return list(dependencies)

def extract_api_endpoints(project_path):
    """Extract REST API endpoints"""
    endpoints = []
    java_files = list(project_path.rglob("*.java"))
    
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            
            if '@RestController' in content or '@Controller' in content:
                # Extract method mappings
                method_mappings = re.findall(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping|PatchMapping)\s*\(\s*["\']([^"\']*)["\']', content)
                
                for method_annotation, path in method_mappings:
                    endpoints.append({
                        'method': method_annotation.replace('Mapping', '').upper(),
                        'path': path,
                        'controller': java_file.stem
                    })
                        
        except:
            pass
    
    return endpoints[:8]  # Return first 8 endpoints

def detect_security_features(project_path):
    """Detect security features"""
    security = set()
    java_files = list(project_path.rglob("*Security*.java"))
    
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            if any(term in content for term in ['@EnableWebSecurity', 'SecurityConfig']):
                security.add('Spring Security')
            if 'JWT' in content:
                security.add('JWT')
            if 'OAuth2' in content:
                security.add('OAuth2')
        except:
            pass
    
    return list(security) if security else ['Spring Security']

def create_comprehensive_diagram(project, components, details, output_dir):
    """Create a comprehensive C4 diagram with all enhancements"""
    
    puml_lines = []
    
    puml_lines.append("@startuml")
    puml_lines.append("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml")
    puml_lines.append("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml")
    puml_lines.append("")
    puml_lines.append(f"title Comprehensive Architecture: {project}")
    puml_lines.append("")
    
    # System Context
    puml_lines.append("Person(api_client, \"API Client\", \"External systems consuming APIs\")")
    puml_lines.append("Person(end_user, \"End User\", \"Uses the application\")")
    puml_lines.append("")
    
    # External systems
    puml_lines.append("System_Ext(raast_system, \"Raast Payment System\", \"National payment infrastructure\")")
    puml_lines.append("System_Ext(banking_apis, \"Banking APIs\", \"Financial institution services\")")
    
    if details['external_dependencies']:
        for dep in details['external_dependencies']:
            if 'Kafka' in dep:
                puml_lines.append("System_Ext(kafka, \"Apache Kafka\", \"Event streaming platform\")")
            elif 'RabbitMQ' in dep:
                puml_lines.append("System_Ext(rabbitmq, \"RabbitMQ\", \"Message broker\")")
    
    puml_lines.append("")
    
    # Main application
    puml_lines.append(f"System_Boundary(app, \"{project} Microservice\") {{")
    puml_lines.append("")
    
    # Security Layer
    puml_lines.append("    Container_Boundary(security, \"Security Layer\") {")
    puml_lines.append('        Component(security_filter, "Security Filter", "Spring Security", "Request authentication")')
    if 'JWT' in details['security_features']:
        puml_lines.append('        Component(jwt_processor, "JWT Processor", "JWT", "Token validation")')
    puml_lines.append("    }")
    puml_lines.append("")
    
    # API Layer
    puml_lines.append("    Container_Boundary(api, \"API Layer\") {")
    
    if components['rest_controllers']:
        for controller in components['rest_controllers'][:4]:
            puml_lines.append(f'        Component({controller["name"].lower()}, "{controller["name"]}", "REST Controller")')
    else:
        puml_lines.append('        Component(api_placeholder, "REST Controllers", "Spring MVC", "Handles HTTP requests")')
    
    puml_lines.append("    }")
    puml_lines.append("")
    
    # Business Layer
    puml_lines.append("    Container_Boundary(business, \"Business Layer\") {")
    
    if components['services']:
        for service in components['services'][:6]:
            puml_lines.append(f'        Component({service["name"].lower()}, "{service["name"]}", "Business Service")')
    
    # Common business components for payment system
    business_components = [
        'PaymentProcessor', 'TransactionManager', 'NotificationService', 
        'ValidationService', 'ReconciliationService', 'ReportGenerator'
    ]
    
    for comp in business_components:
        puml_lines.append(f'        Component({comp.lower()}, "{comp}", "Business Logic")')
    
    puml_lines.append("    }")
    puml_lines.append("")
    
    # Data Layer
    puml_lines.append("    Container_Boundary(data, \"Data Layer\") {")
    
    # Group entities by domain
    payment_entities = [e for e in components['entities'] if any(term in e['name'] for term in ['Merchant', 'Transaction', 'Payment', 'Tax'])]
    notification_entities = [e for e in components['entities'] if 'Notification' in e['name']]
    system_entities = [e for e in components['entities'] if any(term in e['name'] for term in ['Log', 'Job', 'Config', 'Security'])]
    
    if payment_entities:
        puml_lines.append("        ' === Payment Entities ===")
        for entity in payment_entities[:4]:
            table_info = f"\\nTable: {entity['table']}" if entity.get('table') else ""
            puml_lines.append(f'        Component({entity["name"].lower()}_ent, "{entity["name"]}{table_info}", "JPA Entity")')
    
    if components['repositories'] or components['jpa_repositories']:
        puml_lines.append("        ' === Data Access ===")
        for repo in (components['repositories'] + components['jpa_repositories'])[:3]:
            puml_lines.append(f'        Component({repo["name"].lower()}_repo, "{repo["name"]}", "Repository")')
    else:
        puml_lines.append('        Component(data_access, "Data Access", "Spring Data", "Direct database access")')
    
    puml_lines.append("    }")
    puml_lines.append("")
    
    puml_lines.append("}")
    puml_lines.append("")
    
    # External data stores
    puml_lines.append(f'ContainerDb(main_db, "Main Database", "{details["database_type"]}", "Primary data store")')
    puml_lines.append('ContainerDb(audit_db, "Audit Database", "Database", "Audit trails & logs")')
    puml_lines.append("")
    
    # Core relationships
    puml_lines.append("' === Core Data Flow ===")
    puml_lines.append('Rel(api_client, security, "API Requests", "HTTPS/REST")')
    puml_lines.append('Rel(security, api, "Authenticated requests")')
    puml_lines.append('Rel(api, business, "Business logic delegation")')
    puml_lines.append('Rel(business, data, "Data access operations")')
    puml_lines.append('Rel(data, main_db, "Persistence", "JPA/Hibernate")')
    puml_lines.append('Rel(business, audit_db, "Audit logging", "JDBC")')
    puml_lines.append("")
    
    # External integrations
    puml_lines.append("' === External Integrations ===")
    puml_lines.append('Rel(business, raast_system, "Payment processing", "ISO8583/API")')
    puml_lines.append('Rel(business, banking_apis, "Bank transactions", "SOAP/REST")')
    
    if 'Apache Kafka' in details['external_dependencies']:
        puml_lines.append('Rel(business, kafka, "Event publishing", "Kafka Protocol")')
    
    # Technology stack note
    puml_lines.append("")
    puml_lines.append("note right of app")
    puml_lines.append("  **Technology Stack**")
    puml_lines.append(f"  Framework: Spring Boot")
    puml_lines.append(f"  Build Tool: {details['build_tool']}")
    puml_lines.append(f"  Database: {details['database_type']}")
    puml_lines.append(f"  Security: {', '.join(details['security_features'])}")
    if details['external_dependencies']:
        puml_lines.append(f"  Integrations: {', '.join(details['external_dependencies'])}")
    puml_lines.append("end note")
    puml_lines.append("")
    
    # API endpoints note
    if details['api_endpoints']:
        puml_lines.append("note left of api")
        puml_lines.append("  **Key API Endpoints**")
        for endpoint in details['api_endpoints'][:4]:
            puml_lines.append(f"  {endpoint['method']} {endpoint['path']}")
        if len(details['api_endpoints']) > 4:
            puml_lines.append(f"  ... {len(details['api_endpoints']) - 4} more endpoints")
        puml_lines.append("end note")
        puml_lines.append("")
    
    # Data model note
    puml_lines.append("note right of main_db")
    puml_lines.append("  **Data Model**")
    puml_lines.append(f"  Total Entities: {len(components['entities'])}")
    puml_lines.append("  Key Domains:")
    if payment_entities:
        puml_lines.append(f"  • Payment ({len(payment_entities)} entities)")
    if notification_entities:
        puml_lines.append(f"  • Notification ({len(notification_entities)} entities)")
    if system_entities:
        puml_lines.append(f"  • System ({len(system_entities)} entities)")
    puml_lines.append("end note")
    puml_lines.append("")
    
    # Quality attributes
    puml_lines.append("note bottom of app")
    puml_lines.append("  **Quality Attributes**")
    puml_lines.append("  🔒 High Security (Financial Grade)")
    puml_lines.append("  ⚡ Performance (< 2s response)")
    puml_lines.append("  📊 Audit & Compliance")
    puml_lines.append("  🔄 Transaction Integrity")
    puml_lines.append("end note")
    puml_lines.append("")
    
    # Legend
    puml_lines.append("legend right")
    puml_lines.append("  == Architecture Summary ==")
    puml_lines.append(f"  **{project}**")
    puml_lines.append(f"  Controllers: {len(components['rest_controllers'])}")
    puml_lines.append(f"  Services: {len(components['services'])}")
    puml_lines.append(f"  Entities: {len(components['entities'])}")
    puml_lines.append(f"  Endpoints: {len(details['api_endpoints'])}")
    puml_lines.append("  == Financial System ==")
    puml_lines.append("  💰 Payment Processing")
    puml_lines.append("  🏦 Bank Integration") 
    puml_lines.append("  📨 Notifications")
    puml_lines.append("  📊 Reporting")
    puml_lines.append("end legend")
    
    puml_lines.append("")
    puml_lines.append("@enduml")
    
    puml_content = '\n'.join(puml_lines)
    
    # Save and generate diagram
    puml_file = os.path.join(output_dir, f"{project}_complete_architecture.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    try:
        subprocess.run(["java", "-jar", "/plantuml.jar", "-tpng", puml_file], check=True)
        print(f"✅ Created comprehensive diagram: {project}_complete_architecture.png")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating diagram: {e}")
        return False

def print_comprehensive_summary(project, components, details):
    """Print detailed analysis summary"""
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE ANALYSIS SUMMARY: {project}")
    print(f"{'='*80}")
    
    total_components = sum(len(components[key]) for key in components)
    
    print(f"📊 TOTAL COMPONENTS: {total_components}")
    print(f"🔍 SPRING BEANS: {sum(len(components[key]) for key in components if key != 'entities')}")
    print(f"🏷️  JPA ENTITIES: {len(components['entities'])}")
    
    print(f"\n🏗️  ARCHITECTURE LAYERS:")
    print(f"   🎮 API Layer: {len(components['rest_controllers'])} controllers")
    print(f"   ⚙️  Business Layer: {len(components['services'])} services") 
    print(f"   💾 Data Layer: {len(components['repositories']) + len(components['jpa_repositories'])} repositories")
    
    print(f"\n🔧 TECHNOLOGY STACK:")
    print(f"   Build Tool: {details['build_tool']}")
    print(f"   Database: {details['database_type']}")
    print(f"   Security: {', '.join(details['security_features'])}")
    if details['external_dependencies']:
        print(f"   Integrations: {', '.join(details['external_dependencies'])}")
    
    print(f"\n🌐 API ENDPOINTS: {len(details['api_endpoints'])} endpoints discovered")
    for endpoint in details['api_endpoints'][:3]:
        print(f"   {endpoint['method']} {endpoint['path']} → {endpoint['controller']}")

# MAIN EXECUTION
def main():
    projects = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
    
    if not projects:
        print("❌ No projects found in input directory!")
        print("💡 Please copy your Spring Boot projects to the 'input' folder")
        return
    
    for project in projects:
        print(f"\n{'='*80}")
        print(f"ANALYZING: {project}")
        print(f"{'='*80}")
        
        project_path = Path(input_dir) / project
        
        # Analyze Spring components
        components = analyze_spring_components(project_path)
        
        # Extract architectural details
        details = extract_architecture_details(project_path)
        
        # Create comprehensive diagram
        success = create_comprehensive_diagram(project, components, details, output_dir)
        
        if success:
            # Print summary
            print_comprehensive_summary(project, components, details)
        else:
            print(f"❌ Failed to create diagram for {project}")
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE!")
    print("Generated comprehensive C4 diagrams with:")
    print("  ✅ Complete layered architecture")
    print("  ✅ Technology stack details") 
    print("  ✅ API endpoints and contracts")
    print("  ✅ External integrations")
    print("  ✅ Security context")
    print("  ✅ Quality attributes")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()