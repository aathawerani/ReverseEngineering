import os
import re
import json
from pathlib import Path

def analyze_spring_boot_project(project_path):
    print(f"Analyzing project at: {project_path}")
    
    results = {
        'microservice_name': os.path.basename(project_path.rstrip('/')),
        'controllers': [],
        'services': [],
        'repositories': [],
        'entities': [],
        'configurations': []
    }
    
    # Look for Java files
    for java_file in Path(project_path).rglob('*.java'):
        try:
            with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            class_name = java_file.stem
            file_path = str(java_file)
            
            # Check for Spring annotations
            if '@RestController' in content or '@Controller' in content:
                results['controllers'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'Controller'
                })
                print(f"✓ Found Controller: {class_name}")
                
            elif '@Service' in content:
                results['services'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'Service'
                })
                print(f"✓ Found Service: {class_name}")
                
            elif '@Repository' in content or 'extends JpaRepository' in content:
                results['repositories'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'Repository'
                })
                print(f"✓ Found Repository: {class_name}")
                
            elif '@Entity' in content:
                results['entities'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'Entity'
                })
                print(f"✓ Found Entity: {class_name}")
                
            elif '@Configuration' in content or '@Bean' in content:
                results['configurations'].append({
                    'name': class_name,
                    'file': file_path,
                    'type': 'Configuration'
                })
                print(f"✓ Found Configuration: {class_name}")
                
        except Exception as e:
            print(f"Error reading {java_file}: {e}")
    
    return results

def generate_c4_diagram(analysis_results, output_dir):
    ms_name = analysis_results['microservice_name'].replace(' ', '_')
    filename = f"{ms_name}_architecture.puml"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        # Write PlantUML header with C4 includes
        f.write("@startuml\n")
        f.write("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n")
        f.write("!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml\n\n")
        
        f.write(f"title Container Diagram for {analysis_results['microservice_name']}\n\n")
        
        # Define containers
        f.write('Container(webapp, "Web Application", "Spring Boot", "Provides REST API")\n')
        f.write('ContainerDb(database, "Database", "MySQL", "Stores application data")\n\n')
        
        # Add components found in analysis
        if analysis_results['controllers']:
            f.write("' === Controllers ===\n")
            for controller in analysis_results['controllers']:
                f.write(f'Component({controller["name"].lower()}, "{controller["name"]}", "Spring Controller")\n')
            f.write("\n")
        
        if analysis_results['services']:
            f.write("' === Services ===\n")
            for service in analysis_results['services']:
                f.write(f'Component({service["name"].lower()}, "{service["name"]}", "Spring Service")\n')
            f.write("\n")
        
        if analysis_results['repositories']:
            f.write("' === Repositories ===\n")
            for repo in analysis_results['repositories']:
                f.write(f'Component({repo["name"].lower()}, "{repo["name"]}", "Spring Repository")\n')
            f.write("\n")
        
        # Add relationships
        f.write("' === Relationships ===\n")
        f.write("Rel(webapp, database, \"Reads/Writes\", \"JDBC\")\n")
        
        # Connect controllers to services
        for controller in analysis_results['controllers']:
            for service in analysis_results['services']:
                f.write(f'Rel({controller["name"].lower()}, {service["name"].lower()}, "Uses")\n')
        
        # Connect services to repositories
        for service in analysis_results['services']:
            for repo in analysis_results['repositories']:
                f.write(f'Rel({service["name"].lower()}, {repo["name"].lower()}, "Uses")\n')
        
        # Connect repositories to database
        for repo in analysis_results['repositories']:
            f.write(f'Rel({repo["name"].lower()}, database, "Reads/Writes")\n')
        
        f.write("\n@enduml")
    
    print(f"Generated C4 diagram: {filepath}")
    return filepath

def generate_diagram_image(puml_file):
    """Generate PNG from PlantUML file"""
    try:
        os.system(f"java -jar /opt/plantuml.jar -tpng {puml_file}")
        png_file = puml_file.replace('.puml', '.png')
        if os.path.exists(png_file):
            print(f"Generated diagram image: {png_file}")
        return png_file
    except Exception as e:
        print(f"Error generating diagram: {e}")
        return None

def main():
    print("=== Spring Boot C4 Model Generator (Docker) ===\n")
    
    # Set paths for Docker environment
    input_dir = "/workspace/input"
    output_dir = "/workspace/output"
    
    # Check if input directory exists and has projects
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist!")
        return
    
    projects = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
    
    if not projects:
        print("No projects found in input directory!")
        print("Please copy your Spring Boot projects to the 'input' folder")
        return
    
    print(f"Found projects: {', '.join(projects)}\n")
    
    for project in projects:
        project_path = os.path.join(input_dir, project)
        print(f"Analyzing: {project}")
        
        # Analyze project
        results = analyze_spring_boot_project(project_path)
        
        # Generate diagram
        diagram_file = generate_c4_diagram(results, output_dir)
        
        # Generate PNG image
        generate_diagram_image(diagram_file)
        
        # Save analysis results
        report_file = os.path.join(output_dir, f"{results['microservice_name'].replace(' ', '_')}_analysis.json")
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Completed: {results['microservice_name']}")
        print(f"  - Controllers: {len(results['controllers'])}")
        print(f"  - Services: {len(results['services'])}")
        print(f"  - Repositories: {len(results['repositories'])}")
        print(f"  - Output files saved to /workspace/output/")
        print()

if __name__ == "__main__":
    main()