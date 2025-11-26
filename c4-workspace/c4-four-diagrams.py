import os
import subprocess
import json
import re
from pathlib import Path

print("=== C4 Model Generator - All 4 Levels ===")

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
    
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            class_name = java_file.stem
            
            if '@RestController' in content:
                components['rest_controllers'].append({'name': class_name})
            elif '@Service' in content:
                components['services'].append({'name': class_name})
            elif '@Repository' in content:
                components['repositories'].append({'name': class_name})
            elif 'JpaRepository' in content:
                components['jpa_repositories'].append({'name': class_name})
            elif '@Entity' in content:
                table_name = extract_table_name(content)
                components['entities'].append({'name': class_name, 'table': table_name})
            elif '@Configuration' in content:
                components['configs'].append({'name': class_name})
            elif '@Component' in content:
                components['components'].append({'name': class_name})
                
        except:
            pass
    
    return components

def extract_table_name(content):
    """Extract database table name from entity"""
    table_match = re.search(r'@Table\s*\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
    return table_match.group(1) if table_match else None

def create_c1_system_context(project, output_dir):
    """C1: System Context Diagram - Highest level"""
    
    puml_content = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

title System Context Diagram for {project}

Person(customer, "Customer", "A customer of the banking system")
Person(merchant, "Merchant", "A merchant accepting payments")
Person(admin, "Administrator", "Manages the system")

System({project.lower()}, "{project}", "Spring Boot microservice for payment processing")

System_Ext(raast, "Raast System", "National payment infrastructure")
System_Ext(bank, "Banking System", "Financial institution backend")
System_Ext(sms_gateway, "SMS Gateway", "Sends notification messages")

Rel(customer, {project.lower()}, "Makes payments", "HTTPS/REST")
Rel(merchant, {project.lower()}, "Receives payments", "HTTPS/REST")
Rel(admin, {project.lower()}, "Manages configuration", "Web UI")

Rel({project.lower()}, raast, "Processes payments", "ISO8583/API")
Rel({project.lower()}, bank, "Bank transactions", "SOAP/REST")
Rel({project.lower()}, sms_gateway, "Sends notifications", "HTTP")

note right of {project.lower()}
  <b>Payment Processing System</b>
  Processes financial transactions
  Integrates with national payment systems
  Provides merchant services
end note

@enduml"""
    
    puml_file = os.path.join(output_dir, f"{project}_c1_system_context.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    generate_image(puml_file)
    return puml_file

def create_c2_container_diagram(project, components, output_dir):
    """C2: Container Diagram - Applications and databases"""
    
    puml_content = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Container Diagram for {project}

Person(customer, "Customer", "Uses mobile banking app")

System_Boundary({project.lower()}, "{project} System") {{
    Container(web_app, "Web Application", "Spring Boot", "Provides REST APIs and web interface")
    ContainerDb(database, "Database", "MySQL", "Stores transactions, merchants, and configuration")
    Container(file_system, "File System", "Local Storage", "Stores reports and logs")
}}

System_Ext(raast, "Raast System", "National payment infrastructure")
System_Ext(bank_api, "Bank API", "Financial services")
System_Ext(sms_provider, "SMS Provider", "Notification service")

Rel(customer, web_app, "Makes payments", "HTTPS")

Rel(web_app, database, "Reads from and writes to", "JDBC")
Rel(web_app, file_system, "Stores reports", "File I/O")

Rel(web_app, raast, "Processes payments", "ISO8583")
Rel(web_app, bank_api, "Bank transactions", "SOAP/REST")
Rel(web_app, sms_provider, "Sends notifications", "HTTP")

note left of web_app
  <b>Spring Boot Application</b>
  REST API Controllers: {len(components['rest_controllers'])}
  Business Services: {len(components['services'])}
  Data Repositories: {len(components['repositories']) + len(components['jpa_repositories'])}
end note

note right of database
  <b>Database Schema</b>
  Total Entities: {len(components['entities'])}
  Key Tables:
  - Merchant data
  - Transaction records
  - Notification logs
  - System configuration
end note

@enduml"""
    
    puml_file = os.path.join(output_dir, f"{project}_c2_container_diagram.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    generate_image(puml_file)
    return puml_file

def create_c3_component_diagram(project, components, output_dir):
    """C3: Component Diagram - Components within web application"""
    
    # Sample components for demonstration
    controllers_sample = [c['name'] for c in components['rest_controllers'][:3]] or ["PaymentController", "MerchantController"]
    services_sample = [s['name'] for s in components['services'][:4]] or ["PaymentService", "NotificationService", "ValidationService"]
    entities_sample = [e['name'] for e in components['entities'][:5]] or ["Transaction", "Merchant", "User"]
    
    puml_content = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Component Diagram for {project} - Web Application

Container_Boundary(web_app, "Web Application") {{
    
    Component_Boundary(api_layer, "API Layer") {{
"""
    
    # Add controllers
    for controller in controllers_sample:
        puml_content += f'        Component({controller.lower()}, "{controller}", "Spring REST Controller")\n'
    
    puml_content += """    }
    
    Component_Boundary(business_layer, "Business Layer") {
"""
    
    # Add services
    for service in services_sample:
        puml_content += f'        Component({service.lower()}, "{service}", "Spring Service")\n'
    
    puml_content += """    }
    
    Component_Boundary(data_layer, "Data Layer") {
"""
    
    # Add repositories if available, otherwise show data access components
    if components['repositories'] or components['jpa_repositories']:
        repos = [r['name'] for r in (components['repositories'] + components['jpa_repositories'])[:3]]
        for repo in repos:
            puml_content += f'        Component({repo.lower()}, "{repo}", "Spring Repository")\n'
    else:
        puml_content += '        Component(repository, "Data Access", "Spring Data", "Handles database operations")\n'
    
    puml_content += """    }
    
    Component_Boundary(security_layer, "Security Layer") {
        Component(security, "Security Config", "Spring Security", "Authentication & Authorization")
        Component(jwt, "JWT Service", "JWT", "Token management")
    }
}}

ContainerDb(database, "Database", "MySQL", "Stores application data")

' API Layer relationships
Rel(customer, api_layer, "Uses", "HTTPS/REST")

' Internal relationships
"""
    
    # Connect controllers to services
    for i, controller in enumerate(controllers_sample):
        if i < len(services_sample):
            puml_content += f'Rel({controller.lower()}, {services_sample[i].lower()}, "Calls")\n'
    
    # Connect services to data layer
    for i, service in enumerate(services_sample):
        if components['repositories'] or components['jpa_repositories']:
            if i < len(components['repositories'] + components['jpa_repositories']):
                repos = [r['name'] for r in (components['repositories'] + components['jpa_repositories'])]
                puml_content += f'Rel({service.lower()}, {repos[i % len(repos)].lower()}, "Uses")\n'
        else:
            puml_content += f'Rel({service.lower()}, repository, "Data access")\n'
    
    # Connect data layer to database
    if components['repositories'] or components['jpa_repositories']:
        repos = [r['name'] for r in (components['repositories'] + components['jpa_repositories'])[:2]]
        for repo in repos:
            puml_content += f'Rel({repo.lower()}, database, "Reads/Writes")\n'
    else:
        puml_content += 'Rel(repository, database, "JDBC")\n'
    
    # Security relationships
    puml_content += """
Rel(security, api_layer, "Protects")
Rel(jwt, security, "Provides tokens")

note right of web_app
  <b>Application Architecture</b>
  Layered Spring Boot Application
  REST API with Business Logic
  Database Persistence
  Security Integration
end note

@enduml"""
    
    puml_file = os.path.join(output_dir, f"{project}_c3_component_diagram.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    generate_image(puml_file)
    return puml_file

def create_c4_code_diagram(project, components, output_dir):
    """C4: Code Diagram - Classes within a component"""
    
    # Focus on one key component - PaymentService and related classes
    puml_content = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Code Diagram for {project} - Payment Processing Component

Container_Boundary(payment_component, "Payment Processing Component") {{
    
    Component_Boundary(payment_service, "PaymentService") {{
        Component(process_payment, "processPayment()", "Method", "Main payment processing logic")
        Component(validate_transaction, "validateTransaction()", "Method", "Transaction validation")
        Component(update_balances, "updateBalances()", "Method", "Balance updates")
        Component(log_transaction, "logTransaction()", "Method", "Audit logging")
    }}
    
    Component_Boundary(entities, "Domain Entities") {{
"""
    
    # Add key entities
    key_entities = [e for e in components['entities'] if any(term in e['name'].lower() for term in ['payment', 'transaction', 'merchant', 'account'])]
    if not key_entities:
        key_entities = components['entities'][:4] if components['entities'] else [{'name': 'Payment', 'table': 'payments'}, {'name': 'Transaction', 'table': 'transactions'}]
    
    for entity in key_entities[:4]:
        table_info = f"\\nTable: {entity['table']}" if entity.get('table') else ""
        puml_content += f'        Component({entity["name"].lower()}_ent, "{entity["name"]}{table_info}", "JPA Entity")\n'
    
    puml_content += """    }
    
    Component_Boundary(repositories, "Data Access") {
"""
    
    # Add repositories
    if components['repositories'] or components['jpa_repositories']:
        repos = [r['name'] for r in (components['repositories'] + components['jpa_repositories'])[:2]]
        for repo in repos:
            puml_content += f'        Component({repo.lower()}_repo, "{repo}", "Repository Interface")\n'
    else:
        puml_content += '        Component(payment_repo, "PaymentRepository", "Repository", "Data access methods")\n'
        puml_content += '        Component(merchant_repo, "MerchantRepository", "Repository", "Merchant data access")\n'
    
    puml_content += """    }
    
    Component_Boundary(external_apis, "External Integrations") {
        Component(raast_client, "RaastClient", "REST Client", "Raast system integration")
        Component(bank_client, "BankClient", "SOAP Client", "Bank API integration")
        Component(notification_client, "NotificationClient", "HTTP Client", "SMS/Email service")
    }
}}

' Internal relationships
Rel(process_payment, validate_transaction, "Calls")
Rel(process_payment, update_balances, "Calls") 
Rel(process_payment, log_transaction, "Calls")

Rel(process_payment, payment_repo, "Saves data")
Rel(process_payment, merchant_repo, "Updates merchant")

Rel(payment_repo, payment_ent, "Manages")
Rel(merchant_repo, merchant_ent, "Manages")

Rel(process_payment, raast_client, "Process payment")
Rel(process_payment, bank_client, "Bank transaction")
Rel(process_payment, notification_client, "Send notification")

note right of payment_component
  <b>Payment Processing Flow</b>
  1. Validate transaction details
  2. Process via Raast system
  3. Update bank balances
  4. Send notifications
  5. Log for audit
end note

@enduml"""
    
    puml_file = os.path.join(output_dir, f"{project}_c4_code_diagram.puml")
    with open(puml_file, "w") as f:
        f.write(puml_content)
    
    generate_image(puml_file)
    return puml_file

def generate_image(puml_file):
    """Generate PNG image from PlantUML file"""
    try:
        subprocess.run(["java", "-jar", "/plantuml.jar", "-tpng", puml_file], check=True)
        print(f"✅ Created: {os.path.basename(puml_file).replace('.puml', '.png')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating image for {puml_file}: {e}")
        return False

def print_c4_summary(project):
    """Print summary of all C4 diagrams created"""
    print(f"\n{'='*80}")
    print(f"C4 MODEL GENERATED FOR: {project}")
    print(f"{'='*80}")
    print("📊 FOUR ARCHITECTURE DIAGRAMS CREATED:")
    print("")
    print("1. 🎯 C1: SYSTEM CONTEXT DIAGRAM")
    print("   - High-level system overview")
    print("   - External actors and systems")
    print("   - System boundaries and relationships")
    print("   File: {project}_c1_system_context.png")
    print("")
    print("2. 🏗️  C2: CONTAINER DIAGRAM") 
    print("   - Applications, databases, and infrastructure")
    print("   - Technology choices and interactions")
    print("   - Deployment context")
    print("   File: {project}_c2_container_diagram.png")
    print("")
    print("3. ⚙️  C3: COMPONENT DIAGRAM")
    print("   - Internal components of main application")
    print("   - Component relationships and responsibilities")
    print("   - Architectural layers and patterns")
    print("   File: {project}_c3_component_diagram.png")
    print("")
    print("4. 🔧 C4: CODE DIAGRAM")
    print("   - Detailed class-level view")
    print("   - Method interactions and data flow")
    print("   - Implementation details for key components")
    print("   File: {project}_c4_code_diagram.png")
    print("")
    print("💡 Each diagram provides different level of detail for different audiences:")
    print("   - C1: Stakeholders & Business")
    print("   - C2: DevOps & Architects") 
    print("   - C3: Developers & Tech Leads")
    print("   - C4: Development Teams")
    print(f"{'='*80}")

# MAIN EXECUTION
def main():
    projects = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
    
    if not projects:
        print("❌ No projects found in input directory!")
        print("💡 Please copy your Spring Boot projects to the 'input' folder")
        return
    
    for project in projects:
        print(f"\n{'='*80}")
        print(f"GENERATING C4 MODEL FOR: {project}")
        print(f"{'='*80}")
        
        project_path = Path(input_dir) / project
        
        # Analyze Spring components
        print("🔍 Analyzing project structure...")
        components = analyze_spring_components(project_path)
        
        # Generate all 4 C4 diagrams
        print("\n📈 Generating C4 diagrams...")
        
        # C1: System Context
        print("  🎯 Creating C1: System Context Diagram...")
        create_c1_system_context(project, output_dir)
        
        # C2: Container Diagram  
        print("  🏗️  Creating C2: Container Diagram...")
        create_c2_container_diagram(project, components, output_dir)
        
        # C3: Component Diagram
        print("  ⚙️  Creating C3: Component Diagram...")
        create_c3_component_diagram(project, components, output_dir)
        
        # C4: Code Diagram
        print("  🔧 Creating C4: Code Diagram...")
        create_c4_code_diagram(project, components, output_dir)
        
        # Print summary
        print_c4_summary(project)
    
    print(f"\n{'='*80}")
    print("🎉 C4 MODEL GENERATION COMPLETE!")
    print("All 4 architecture diagrams have been generated:")
    print("  ✅ C1: System Context - High-level overview")
    print("  ✅ C2: Container - Applications & infrastructure") 
    print("  ✅ C3: Component - Internal structure")
    print("  ✅ C4: Code - Implementation details")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()