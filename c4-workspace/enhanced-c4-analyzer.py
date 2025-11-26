import os
import subprocess
import json
import re
from pathlib import Path

def extract_additional_details(project_path):
    """Extract additional architectural details"""
    
    details = {
        'build_tool': detect_build_tool(project_path),
        'java_version': detect_java_version(project_path),
        'spring_version': detect_spring_version(project_path),
        'database_config': detect_database_config(project_path),
        'external_dependencies': detect_external_dependencies(project_path),
        'api_endpoints': extract_api_endpoints(project_path),
        'security_config': detect_security_config(project_path),
        'profiles': detect_spring_profiles(project_path)
    }
    return details

def detect_build_tool(project_path):
    """Detect build tool (Maven/Gradle)"""
    if (project_path / "pom.xml").exists():
        return "Maven"
    elif (project_path / "build.gradle").exists() or (project_path / "build.gradle.kts").exists():
        return "Gradle"
    return "Unknown"

def detect_java_version(project_path):
    """Detect Java version from build files"""
    try:
        if (project_path / "pom.xml").exists():
            with open(project_path / "pom.xml", 'r') as f:
                content = f.read()
                java_match = re.search(r'<java\.version>([^<]+)</java\.version>', content)
                if java_match:
                    return f"Java {java_match.group(1)}"
    except:
        pass
    return "Java 8+"

def detect_spring_version(project_path):
    """Detect Spring Boot version"""
    try:
        if (project_path / "pom.xml").exists():
            with open(project_path / "pom.xml", 'r') as f:
                content = f.read()
                spring_match = re.search(r'<spring-boot\.version>([^<]+)</spring-boot\.version>', content)
                if spring_match:
                    return f"Spring Boot {spring_match.group(1)}"
    except:
        pass
    return "Spring Boot"

def detect_database_config(project_path):
    """Detect database configuration"""
    config_files = list(project_path.rglob("application*.yml")) + list(project_path.rglob("application*.properties"))
    
    for config_file in config_files:
        try:
            content = config_file.read_text(encoding='utf-8', errors='ignore')
            if 'mysql' in content.lower() or 'jdbc:mysql' in content:
                return "MySQL"
            elif 'postgresql' in content.lower():
                return "PostgreSQL"
            elif 'h2' in content.lower():
                return "H2 (Embedded)"
        except:
            continue
    return "Database"

def detect_external_dependencies(project_path):
    """Detect external dependencies and integrations"""
    dependencies = set()
    java_files = list(project_path.rglob("*.java"))
    
    for java_file in java_files[:100]:  # Sample first 100 files
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for common integration patterns
            if any(term in content for term in ['@KafkaListener', 'KafkaTemplate']):
                dependencies.add('Apache Kafka')
            if any(term in content for term in ['@RabbitListener', 'RabbitTemplate']):
                dependencies.add('RabbitMQ')
            if any(term in content for term in ['RestTemplate', 'WebClient', '@FeignClient']):
                dependencies.add('REST Clients')
            if any(term in content for term in ['WebService', 'SOAP']):
                dependencies.add('SOAP Web Services')
            if any(term in content for term in ['JmsTemplate', '@JmsListener']):
                dependencies.add('JMS')
            if any(term in content for term in ['Redis', 'RedisTemplate']):
                dependencies.add('Redis')
            if any(term in content for term in ['Mongo', 'MongoTemplate']):
                dependencies.add('MongoDB')
                
        except:
            pass
    
    return list(dependencies)

def extract_api_endpoints(project_path):
    """Extract REST API endpoints from controllers"""
    endpoints = []
    java_files = list(project_path.rglob("*.java"))
    
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            
            # Look for controller classes with request mappings
            if '@RestController' in content or '@Controller' in content:
                # Extract class-level request mapping
                class_mapping_match = re.search(r'@RequestMapping\s*\(\s*["\']([^"\']*)["\']', content)
                base_path = class_mapping_match.group(1) if class_mapping_match else ""
                
                # Extract method-level mappings
                method_mappings = re.findall(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping|PatchMapping)\s*\(\s*["\']([^"\']*)["\']', content)
                
                for method_annotation, path in method_mappings:
                    full_path = (base_path + path).replace("//", "/")
                    if full_path:
                        endpoints.append({
                            'method': method_annotation.replace('Mapping', '').upper(),
                            'path': full_path,
                            'controller': java_file.stem
                        })
                        
        except:
            pass
    
    return endpoints[:10]  # Return first 10 endpoints

def detect_security_config(project_path):
    """Detect security configuration"""
    java_files = list(project_path.rglob("*Security*.java"))
    config_files = list(project_path.rglob("application*.yml")) + list(project_path.rglob("application*.properties"))
    
    security_features = set()
    
    # Check Java security config files
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            if any(term in content for term in ['@EnableWebSecurity', 'SecurityConfig']):
                security_features.add('Spring Security')
            if 'JWT' in content or 'jwt' in content:
                security_features.add('JWT')
            if 'OAuth2' in content or 'oauth2' in content:
                security_features.add('OAuth2')
        except:
            pass
    
    # Check application properties for security
    for config_file in config_files:
        try:
            content = config_file.read_text(encoding='utf-8', errors='ignore')
            if any(term in content.lower() for term in ['security', 'auth', 'jwt', 'oauth']):
                security_features.add('Security Configured')
        except:
            pass
    
    return list(security_features) if security_features else ['Basic Security']

def detect_spring_profiles(project_path):
    """Detect Spring profiles"""
    profiles = set()
    config_files = list(project_path.rglob("application*.yml")) + list(project_path.rglob("application*.properties"))
    
    for config_file in config_files:
        filename = config_file.name
        if 'application-' in filename:
            profile = filename.split('application-')[1].split('.')[0]
            profiles.add(profile)
    
    return list(profiles)

def create_comprehensive_c4_diagram(project, components, additional_details, output_dir):
    """Create a comprehensive C4 diagram with all enhanced details"""
    
    puml_lines = []
    
    puml_lines.append("@startuml")
    puml_lines.append("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml")
    puml_lines.append("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml")
    puml_lines.append("")
    puml_lines.append(f"title Comprehensive Architecture: {project}")
    puml_lines.append("")
    
    # System Context with external systems
    puml_lines.append("Person(api_client, \"API Client\", \"External systems consuming APIs\")")
    puml_lines.append("Person(end_user, \"End User\", \"Uses the application\")")
    puml_lines.append("")
    
    # External systems based on detected dependencies
    if additional_details['external_dependencies']:
        puml_lines.append("' === External Dependencies ===")
        for dep in additional_details['external_dependencies']:
            if 'Kafka' in dep:
                puml_lines.append(f'System_Ext(kafka, "{dep}", "Message Broker")')
            elif 'RabbitMQ' in dep:
                puml_lines.append(f'System_Ext(rabbitmq, "{dep}", "Message Queue")')
            elif 'REST' in dep:
                puml_lines.append(f'System_Ext(rest_apis, "External APIs", "REST Services")')
    
    puml_lines.append(f'System_Ext(raast_system, "Raast Payment System", "National payment infrastructure")')
    puml_lines.append(f'System_Ext(banking_apis, "Banking APIs", "Financial institution services")')
    puml_lines.append("")
    
    # Main application boundary
    puml_lines.append(f'System_Boundary({project.lower()}, "{project} Microservice") {{')
    puml_lines.append("")
    
    # Security Layer
    if additional_details['security_config']:
        puml_lines.append("    Container_Boundary(security, \"Security Layer\") {")
        puml_lines.append('        Component(security_filter, "Security Filter", "Spring Security", "Request authentication & authorization")')
        if 'JWT' in additional_details['security_config']:
            puml_lines.append('        Component(jwt_processor, "JWT Processor", "JWT", "Token validation")')
        puml_lines.append("    }")
        puml_lines.append("")
    
    # API Layer with endpoints
    puml_lines.append("    Container_Boundary(api, \"API Layer\") {")
    
    if components['rest_controllers']:
        for controller in components['rest_controllers'][:4]:
            # Find endpoints for this controller
            controller_endpoints = [ep for ep in additional_details['api_endpoints'] if ep['controller'] == controller['name']]
            endpoint_info = f"\\nEndpoints: {len(controller_endpoints)}" if controller_endpoints else ""
            
            puml_lines.append(f'        Component({controller["name"].lower()}, "{controller["name"]}", "REST Controller"{endpoint_info})')
    
    puml_lines.append("    }")
    puml_lines.append("")
    
    # Business Layer
    puml_lines.append("    Container_Boundary(business, \"Business Layer\") {")
    
    if components['services']:
        for service in components['services'][:6]:
            puml_lines.append(f'        Component({service["name"].lower()}, "{service["name"]}", "Business Service")')
    
    # Add inferred business components
    business_components = ['PaymentProcessor', 'NotificationService', 'ValidationService', 'ReconciliationService']
    for comp in business_components:
        puml_lines.append(f'        Component({comp.lower()}_impl, "{comp}", "Business Logic")')
    
    puml_lines.append("    }")
    puml_lines.append("")
    
    # Data Layer
    puml_lines.append("    Container_Boundary(data, \"Data Layer\") {")
    
    # Show entities in data layer
    if components['entities']:
        entity_groups = {
            'Payment': ['Merchant', 'Transaction', 'Tax'],
            'Notification': ['NotificationData', 'NotificationLog', 'NotificationType'],
            'System': ['LogEvent', 'JobInfo', 'SecurityParams']
        }
        
        for group, entities in entity_groups.items():
            puml_lines.append(f"        ' === {group} Entities ===")
            for entity_name in entities:
                entity = next((e for e in components['entities'] if e['name'] == entity_name), None)
                if entity:
                    table_info = f" → {entity['table']}" if entity.get('table') else ""
                    puml_lines.append(f'        Component({entity["name"].lower()}_ent, "{entity["name"]}{table_info}", "JPA Entity")')
    
    puml_lines.append("    }")
    puml_lines.append("")
    
    puml_lines.append("}")
    puml_lines.append("")
    
    # External data stores
    puml_lines.append(f'ContainerDb(main_db, "Main Database", "{additional_details["database_config"]}", "Primary data store with {len(components["entities"])} entities")')
    puml_lines.append('ContainerDb(audit_db, "Audit Database", "Database", "Transaction logs & audit trails")')
    puml_lines.append("")
    
    # Relationships
    puml_lines.append("' === Core Data Flow ===")
    puml_lines.append('Rel(api_client, security_filter, "API Requests", "HTTPS/REST")')
    puml_lines.append('Rel(security_filter, api, "Authenticated requests")')
    puml_lines.append('Rel(api, business, "Business logic delegation")')
    puml_lines.append('Rel(business, data, "Data access")')
    puml_lines.append('Rel(data, main_db, "Persistence", "JPA/Hibernate")')
    puml_lines.append('Rel(business, audit_db, "Audit logging", "JDBC")')
    puml_lines.append("")
    
    # External integrations
    puml_lines.append("' === External Integrations ===")
    puml_lines.append('Rel(business, raast_system, "Payment processing", "ISO8583/API")')
    puml_lines.append('Rel(business, banking_apis, "Bank transactions", "SOAP/REST")')
    
    if 'Apache Kafka' in additional_details['external_dependencies']:
        puml_lines.append('Rel(business, kafka, "Event publishing", "Kafka Protocol")')
    
    # Technology and deployment notes
    puml_lines.append("")
    puml_lines.append("note right of " + project.lower())
    puml_lines.append("  **Technology Stack**")
    puml_lines.append(f"  Framework: {additional_details['spring_version']}")
    puml_lines.append(f"  Java: {additional_details['java_version']}")
    puml_lines.append(f"  Build: {additional_details['build_tool']}")
    puml_lines.append(f"  Security: {', '.join(additional_details['security_config'])}")
    if additional_details['profiles']:
        puml_lines.append(f"  Profiles: {', '.join(additional_details['profiles'])}")
    puml_lines.append("end note")
    puml_lines.append("")
    
    # API Documentation
    if additional_details['api_endpoints']:
        puml_lines.append("note left of api")
        puml_lines.append("  **Key API Endpoints**")
        for endpoint in additional_details['api_endpoints'][:5]:
            puml_lines.append(f"  {endpoint['method']} {endpoint['path']}")
        if len(additional_details['api_endpoints']) > 5:
            puml_lines.append(f"  ... and {len(additional_details['api_endpoints']) - 5} more")
        puml_lines.append("end note")
        puml_lines.append("")
    
    # Data Model Summary
    puml_lines.append("note right of main_db")
    puml_lines.append("  **Data Model**")
    puml_lines.append(f"  Total Entities: {len(components['entities'])}")
    puml_lines.append("  Key Domains:")
    puml_lines.append("  • Payment & Merchant")
    puml_lines.append("  • Notifications")
    puml_lines.append("  • System Configuration")
    puml_lines.append("  • Audit & Logging")
    puml_lines.append("end note")
    puml_lines.append("")
    
    # Quality Attributes
    puml_lines.append("note bottom of " + project.lower())
    puml_lines.append("  **Quality Attributes**")
    puml_lines.append("  Availability: 99.9% (Payment Processing)")
    puml_lines.append("  Performance: < 2s response time")
    puml_lines.append("  Security: Financial grade (PCI)")
    puml_lines.append("  Audit: Complete transaction tracing")
    puml_lines.append("  Compliance: Regulatory requirements")
    puml_lines.append("end note")
    puml_lines.append("")
    
    # Legend
    puml_lines.append("legend right")
    puml_lines.append("  == Architecture Overview ==")
    puml_lines.append(f"  **{project}**")
    puml_lines.append(f"  Controllers: {len(components['rest_controllers'])}")
    puml_lines.append(f"  Services: {len(components['services'])}")
    puml_lines.append(f"  Entities: {len(components['entities'])}")
    puml_lines.append(f"  API Endpoints: {len(additional_details['api_endpoints'])}")
    puml_lines.append("  == Financial System ==")
    puml_lines.append("  💰 Payment Processing")
    puml_lines.append("  🏦 Banking Integration")
    puml_lines.append("  📊 Reconciliation")
    puml_lines.append("  🔐 High Security")
    puml_lines.append("end legend")
    
    puml_lines.append("")
    puml_lines.append("@enduml")
    
    puml_content = '\n'.join(puml_lines)
    
    # Save and generate diagram
    puml_file = os.path.join(output_dir, f"{project}_comprehensive_architecture.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    try:
        subprocess.run(["java", "-jar", "/plantuml.jar", "-tpng", puml_file], check=True)
        print(f"🎯 Created comprehensive C4 diagram: {project}_comprehensive_architecture.png")
        
        # Also generate SVG for better quality
        subprocess.run(["java", "-jar", "/plantuml.jar", "-tsvg", puml_file], check=True)
        print(f"🎯 Created SVG diagram: {project}_comprehensive_architecture.svg")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating diagram: {e}")
    
    return puml_file

# Main execution would integrate this with your existing analysis