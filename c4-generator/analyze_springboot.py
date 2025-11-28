#!/usr/bin/env python3
"""
Spring Boot Microservices C4 Diagram Generator
Analyzes Spring Boot code without building and generates C4 diagrams
"""

import os
import re
import yaml
import json
from pathlib import Path
from collections import defaultdict

class SpringBootAnalyzer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.services = {}
        self.relationships = []
        
    def find_microservices(self):
        """Find all microservice projects by looking for pom.xml or build.gradle"""
        services = []
        for root, dirs, files in os.walk(self.base_path):
            if 'pom.xml' in files or 'build.gradle' in files:
                services.append(Path(root))
        return services
    
    def extract_service_name(self, service_path):
        """Extract service name from pom.xml or build.gradle"""
        pom_file = service_path / 'pom.xml'
        gradle_file = service_path / 'build.gradle'
        
        if pom_file.exists():
            with open(pom_file, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'<artifactId>(.*?)</artifactId>', content)
                if match:
                    return match.group(1)
        
        if gradle_file.exists():
            return service_path.name
            
        return service_path.name
    
    def find_application_properties(self, service_path):
        """Find and parse application.properties, application.yml, or config.properties"""
        props = {}
        
        # Check for config.properties (legacy Spring apps)
        config_files = list(service_path.rglob('config.properties'))
        for prop_file in config_files:
            if 'target' not in str(prop_file):  # Skip compiled files
                try:
                    with open(prop_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and not line.startswith('!'):
                                if '=' in line:
                                    key, value = line.split('=', 1)
                                    props[key.strip()] = value.strip()
                except:
                    pass
        
        # Check for application.yml
        yml_files = list(service_path.rglob('application*.yml')) + list(service_path.rglob('application*.yaml'))
        for yml_file in yml_files:
            if 'target' not in str(yml_file):
                try:
                    with open(yml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data:
                            props.update(self._flatten_dict(data))
                except:
                    pass
        
        # Check for application.properties
        prop_files = list(service_path.rglob('application*.properties'))
        for prop_file in prop_files:
            if 'target' not in str(prop_file):
                try:
                    with open(prop_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if '=' in line:
                                    key, value = line.split('=', 1)
                                    props[key.strip()] = value.strip()
                except:
                    pass
        
        return props
    
    def _flatten_dict(self, d, parent_key='', sep='.'):
        """Flatten nested dictionary for YAML properties"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def extract_service_components(self, service_path):
        """Extract service layer components (for non-REST apps)"""
        services = []
        daos = []
        entities = []
        
        java_files = list(service_path.rglob('*.java'))
        
        for java_file in java_files:
            if 'target' in str(java_file):
                continue
                
            try:
                with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for Service classes
                    if '@Service' in content or java_file.name.endswith('Service.java'):
                        services.append(java_file.name)
                    
                    # Check for DAO/Repository classes
                    if '@Repository' in content or java_file.name.endswith('DAO.java') or java_file.name.endswith('Repository.java'):
                        daos.append(java_file.name)
                    
                    # Check for Entity classes
                    if '@Entity' in content or '@Table' in content:
                        entities.append(java_file.name)
                        
            except:
                pass
        
        return services, daos, entities
        """Extract REST endpoints from all Java files with REST annotations"""
        endpoints = []
        controllers = []
        java_files = list(service_path.rglob('*.java'))
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check if file has REST annotations
                    if any(anno in content for anno in ['@RestController', '@Controller', '@RequestMapping', 
                                                         '@GetMapping', '@PostMapping', '@PutMapping', 
                                                         '@DeleteMapping', '@PatchMapping']):
                        controllers.append(java_file.name)
                        
                        # Find class-level RequestMapping
                        class_mapping = re.search(r'@RequestMapping\(["\']([^"\']+)["\']', content)
                        base_path = class_mapping.group(1) if class_mapping else ""
                        
                        # Also check for value parameter
                        if not base_path:
                            class_mapping = re.search(r'@RequestMapping\([^)]*value\s*=\s*["\']([^"\']+)["\']', content)
                            base_path = class_mapping.group(1) if class_mapping else ""
                        
                        # Find method mappings with various formats
                        method_patterns = [
                            r'@(?:Get|Post|Put|Delete|Patch)Mapping\(["\']([^"\']+)["\']',
                            r'@(?:Get|Post|Put|Delete|Patch)Mapping\([^)]*value\s*=\s*["\']([^"\']+)["\']',
                            r'@RequestMapping\([^)]*value\s*=\s*["\']([^"\']+)["\'][^)]*method\s*=\s*RequestMethod\.(\w+)'
                        ]
                        
                        for pattern in method_patterns:
                            methods = re.findall(pattern, content)
                            for method in methods:
                                if isinstance(method, tuple):
                                    path = method[0]
                                else:
                                    path = method
                                full_path = base_path + path
                                endpoints.append(full_path)
                        
            except Exception as e:
                pass
        
        return endpoints, controllers
    
    def extract_feign_clients(self, service_path):
        """Extract Feign client dependencies and other HTTP clients"""
        feign_clients = []
        http_clients = []
        java_files = service_path.rglob('*.java')
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Find @FeignClient annotations
                    clients = re.findall(r'@FeignClient\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
                    feign_clients.extend(clients)
                    
                    # Also check for value parameter
                    clients = re.findall(r'@FeignClient\(["\']([^"\']+)["\']', content)
                    feign_clients.extend(clients)
                    
                    # Look for WebClient or RestTemplate usage with service names
                    if 'WebClient' in content or 'RestTemplate' in content:
                        http_clients.append(java_file.name)
                    
            except:
                pass
        
        return list(set(feign_clients)), http_clients
    
    def extract_rest_template_calls(self, service_path):
        """Extract RestTemplate calls to other services"""
        external_calls = []
        java_files = service_path.rglob('*.java')
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Find RestTemplate URLs
                    urls = re.findall(r'restTemplate\.[a-zA-Z]+\(["\']([^"\']+)["\']', content)
                    external_calls.extend(urls)
                    
            except:
                pass
        
        return external_calls
    
    def extract_database_info(self, props):
        """Extract database information from properties"""
        db_info = {}
        
        # Check various datasource property formats
        ds_url_keys = [
            'spring.datasource.url', 'spring.r2dbc.url', 'datasource.url',
            'jdbc.url', 'db.url', 'database.url', 'hibernate.connection.url'
        ]
        for key in ds_url_keys:
            if key in props:
                db_url = props[key]
                if 'postgresql' in db_url.lower():
                    db_info['type'] = 'PostgreSQL'
                elif 'mysql' in db_url.lower():
                    db_info['type'] = 'MySQL'
                elif 'oracle' in db_url.lower():
                    db_info['type'] = 'Oracle'
                elif 'sqlserver' in db_url.lower():
                    db_info['type'] = 'SQL Server'
                elif 'h2' in db_url.lower():
                    db_info['type'] = 'H2'
                elif 'mongodb' in db_url.lower():
                    db_info['type'] = 'MongoDB'
                else:
                    db_info['type'] = 'Database'
                db_info['url'] = db_url
                break
        
        # Check driver class
        driver_keys = ['jdbc.driverClassName', 'db.driver', 'hibernate.connection.driver_class']
        for key in driver_keys:
            if key in props:
                driver = props[key]
                if not db_info and 'postgresql' in driver.lower():
                    db_info['type'] = 'PostgreSQL'
                elif not db_info and 'mysql' in driver.lower():
                    db_info['type'] = 'MySQL'
                elif not db_info and 'oracle' in driver.lower():
                    db_info['type'] = 'Oracle'
        
        # Check for JPA/Hibernate
        if 'spring.jpa.database-platform' in props or 'spring.jpa.hibernate.ddl-auto' in props or 'hibernate.dialect' in props:
            if not db_info:
                db_info['type'] = 'JPA/Hibernate Database'
        
        # Check for MongoDB
        if 'spring.data.mongodb.uri' in props or 'spring.data.mongodb.host' in props or 'mongodb.uri' in props:
            db_info['type'] = 'MongoDB'
        
        return db_info
    
    def analyze(self):
        """Analyze all microservices"""
        service_paths = self.find_microservices()
        
        for service_path in service_paths:
            service_name = self.extract_service_name(service_path)
            props = self.find_application_properties(service_path)
            
            endpoints, controllers = self.extract_rest_endpoints(service_path)
            feign_clients, http_clients = self.extract_feign_clients(service_path)
            services, daos, entities = self.extract_service_components(service_path)
            
            # Determine port from various property keys
            port = 'unknown'
            port_keys = ['server.port', 'port', 'http.port', 'tomcat.port', 'jetty.port']
            for key in port_keys:
                if key in props:
                    port = props[key]
                    break
            
            self.services[service_name] = {
                'path': str(service_path),
                'endpoints': endpoints,
                'controllers': controllers,
                'services': services,
                'daos': daos,
                'entities': entities,
                'feign_clients': feign_clients,
                'http_clients': http_clients,
                'rest_calls': self.extract_rest_template_calls(service_path),
                'database': self.extract_database_info(props),
                'port': port,
                'properties': props,
                'is_rest_api': len(controllers) > 0
            }
            
            # Create relationships
            for client in self.services[service_name]['feign_clients']:
                self.relationships.append({
                    'from': service_name,
                    'to': client,
                    'type': 'uses',
                    'technology': 'Feign Client'
                })
    
    def generate_structurizr_dsl(self, output_file):
        """Generate Structurizr DSL for C4 diagrams"""
        dsl = []
        dsl.append("workspace {")
        dsl.append("    model {")
        dsl.append('        user = person "User" {')
        dsl.append('            description "System User"')
        dsl.append("        }")
        dsl.append("")
        
        # Add microservices
        service_ids = []
        for service_name, service_data in self.services.items():
            service_id = self.sanitize_id(service_name)
            service_ids.append(service_id)
            dsl.append(f'        {service_id} = softwareSystem "{service_name}" {{')
            dsl.append(f'            description "Spring Boot Microservice"')
            dsl.append(f'            tags "Microservice"')
            dsl.append("        }")
            
            # Add database if exists
            if service_data['database']:
                db_id = f"{service_id}_db"
                db_type = service_data['database'].get('type', 'Database')
                dsl.append(f'        {db_id} = softwareSystem "{service_name} {db_type}" {{')
                dsl.append(f'            description "{db_type} Database"')
                dsl.append(f'            tags "Database"')
                dsl.append("        }")
                dsl.append(f"        {service_id} -> {db_id} \"Reads/Writes\"")
        
        # Add relationships
        for rel in self.relationships:
            from_id = self.sanitize_id(rel['from'])
            to_id = self.sanitize_id(rel['to'])
            tech = rel.get('technology', '')
            dsl.append(f'        {from_id} -> {to_id} "Uses" "{tech}"')
        
        dsl.append("    }")
        dsl.append("")
        dsl.append("    views {")
        dsl.append("        systemLandscape \"SystemLandscape\" {")
        dsl.append("            include *")
        dsl.append("            autolayout lr")
        dsl.append("        }")
        dsl.append("")
        
        # Add system context views for each service
        for service_id in service_ids:
            dsl.append(f'        systemContext {service_id} "SystemContext_{service_id}" {{')
            dsl.append("            include *")
            dsl.append("            autolayout lr")
            dsl.append("        }")
            dsl.append("")
        
        dsl.append("        styles {")
        dsl.append("            element \"Microservice\" {")
        dsl.append("                background #1168bd")
        dsl.append("                color #ffffff")
        dsl.append("            }")
        dsl.append("            element \"Database\" {")
        dsl.append("                shape Cylinder")
        dsl.append("                background #438dd5")
        dsl.append("                color #ffffff")
        dsl.append("            }")
        dsl.append("        }")
        dsl.append("    }")
        dsl.append("}")
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(dsl))
    
    def sanitize_id(self, name):
        """Convert name to valid identifier"""
        return re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    def generate_report(self, output_file):
        """Generate analysis report"""
        report = []
        report.append("# Spring Application Analysis Report\n")
        report.append(f"Total Services Found: {len(self.services)}\n")
        
        for service_name, service_data in self.services.items():
            report.append(f"\n## {service_name}")
            report.append(f"- **Path**: {service_data['path']}")
            report.append(f"- **Type**: {'REST API' if service_data.get('is_rest_api') else 'Legacy Spring Application'}")
            report.append(f"- **Port**: {service_data['port']}")
            
            # REST Controllers (if any)
            if service_data.get('controllers'):
                report.append(f"- **REST Controllers Found**: {len(service_data['controllers'])}")
                report.append(f"  - {', '.join(service_data['controllers'][:10])}")
            
            if service_data['endpoints']:
                report.append(f"- **REST Endpoints Found**: {len(service_data['endpoints'])}")
                for endpoint in service_data['endpoints'][:10]:
                    report.append(f"  - {endpoint}")
                if len(service_data['endpoints']) > 10:
                    report.append(f"  - ... and {len(service_data['endpoints']) - 10} more")
            
            # Service Layer Components
            if service_data.get('services'):
                report.append(f"- **Service Classes**: {len(service_data['services'])}")
                if service_data['services'][:5]:
                    report.append(f"  - {', '.join(service_data['services'][:5])}")
            
            if service_data.get('daos'):
                report.append(f"- **DAO/Repository Classes**: {len(service_data['daos'])}")
                if service_data['daos'][:5]:
                    report.append(f"  - {', '.join(service_data['daos'][:5])}")
            
            if service_data.get('entities'):
                report.append(f"- **Entity Classes**: {len(service_data['entities'])}")
                if service_data['entities'][:5]:
                    report.append(f"  - {', '.join(service_data['entities'][:5])}")
            
            # External Dependencies
            if service_data.get('feign_clients'):
                report.append(f"- **Feign Clients**: {', '.join(service_data['feign_clients'])}")
            
            if service_data.get('http_clients'):
                report.append(f"- **HTTP Client Files**: {len(service_data['http_clients'])} files")
            
            # Database
            if service_data['database']:
                report.append(f"- **Database**: {service_data['database'].get('type', 'Unknown')}")
                if 'url' in service_data['database']:
                    report.append(f"  - URL: {service_data['database']['url']}")
            
            # Configuration
            if service_data.get('properties'):
                report.append(f"- **Configuration Properties**: {len(service_data['properties'])} found")
                # Show some interesting properties
                interesting_keys = [k for k in service_data['properties'].keys() 
                                   if any(x in k.lower() for x in ['url', 'host', 'port', 'endpoint', 'api'])]
                if interesting_keys[:5]:
                    report.append("  - Key properties:")
                    for key in interesting_keys[:5]:
                        report.append(f"    - {key}")
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))

if __name__ == '__main__':
    import sys
    
    code_path = sys.argv[1] if len(sys.argv) > 1 else '/workspace'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/output'
    
    print(f"Analyzing Spring Boot code in: {code_path}")
    
    analyzer = SpringBootAnalyzer(code_path)
    analyzer.analyze()
    
    print(f"Found {len(analyzer.services)} microservices")
    
    # Generate outputs
    dsl_file = os.path.join(output_path, 'architecture.dsl')
    report_file = os.path.join(output_path, 'analysis_report.md')
    json_file = os.path.join(output_path, 'services.json')
    
    analyzer.generate_structurizr_dsl(dsl_file)
    analyzer.generate_report(report_file)
    
    # Save JSON for further processing
    with open(json_file, 'w') as f:
        json.dump(analyzer.services, f, indent=2)
    
    print(f"\nOutputs generated:")
    print(f"  - {dsl_file}")
    print(f"  - {report_file}")
    print(f"  - {json_file}")
    print("\nRun 'structurizr.sh export -workspace architecture.dsl -format plantuml' to generate diagrams")