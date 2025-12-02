import os
import argparse
import glob

def scan_project(src_path):
    """
    Scan the project directory and detect systems, containers, and components.
    Optimized for Spring Boot projects.
    """
    containers = []
    
    # Common Spring Boot source patterns
    source_dirs = ['src/main/java', 'src', 'main/java']
    
    # Look for Spring Boot specific files
    spring_files = glob.glob(os.path.join(src_path, "**/*Application.java"), recursive=True)
    pom_exists = os.path.exists(os.path.join(src_path, "pom.xml"))
    gradle_exists = os.path.exists(os.path.join(src_path, "build.gradle")) or os.path.exists(os.path.join(src_path, "build.gradle.kts"))
    
    # If it's a Spring Boot project
    if spring_files or pom_exists or gradle_exists:
        print("Detected Spring Boot project")
        
        # Main application container
        main_container = {
            "name": "SpringBootApp",
            "desc": "Spring Boot Application",
            "tech": "Java/Spring Boot",
            "components": []
        }
        
        # Find Java source files
        java_files = glob.glob(os.path.join(src_path, "**/*.java"), recursive=True)
        for java_file in java_files:
            rel_path = os.path.relpath(java_file, src_path)
            file_name = os.path.basename(java_file)
            class_name = os.path.splitext(file_name)[0]
            
            # Classify components based on naming conventions
            if file_name.endswith("Application.java"):
                comp_type = "Spring Boot Application"
            elif "Controller" in file_name:
                comp_type = "REST Controller"
            elif "Service" in file_name:
                comp_type = "Business Service"
            elif "Repository" in file_name or "DAO" in file_name:
                comp_type = "Data Repository"
            elif "Config" in file_name:
                comp_type = "Configuration"
            elif "Entity" in file_name or "Model" in file_name:
                comp_type = "Data Model"
            else:
                comp_type = "Java Component"
            
            main_container["components"].append({
                "name": f"{class_name}",
                "desc": f"{comp_type}: {rel_path}",
                "tech": "Java"
            })
        
        containers.append(main_container)
        
        # Look for additional modules
        for item in os.listdir(src_path):
            item_path = os.path.join(src_path, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                # Check if it's a module with its own source
                module_java_files = glob.glob(os.path.join(item_path, "**/*.java"), recursive=True)
                if module_java_files:
                    module_container = {
                        "name": f"Module_{item}",
                        "desc": f"Module: {item}",
                        "tech": "Java",
                        "components": []
                    }
                    containers.append(module_container)
    
    else:
        # Fallback to generic scanning
        print("Using generic project scanning")
        for root, dirs, files in os.walk(src_path):
            # Skip hidden dirs and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ['target', 'build', 'node_modules', '.git', '.idea']]
            
            if root == src_path:
                for d in dirs:
                    container = {
                        "name": d,
                        "desc": f"Module: {d}",
                        "tech": detect_technology(os.path.join(root, d)),
                        "components": []
                    }
                    containers.append(container)
    
    # If no containers found, create a default one
    if not containers:
        containers.append({
            "name": "MainApplication",
            "desc": "Detected Application",
            "tech": "Unknown",
            "components": [{"name": "Main", "desc": "Main component", "tech": "Unknown"}]
        })
    
    return containers

def detect_technology(path):
    """Detect technology based on files in directory"""
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == "pom.xml":
                return "Java/Spring"
            elif file == "build.gradle":
                return "Java/Spring"
            elif file == "package.json":
                return "Node.js"
            elif file.endswith(".py"):
                return "Python"
            elif file.endswith(".go"):
                return "Go"
    return "Java"

def generate_dsl(containers, output_file):
    """Generate Structurizr DSL"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w") as f:
        f.write("workspace {\n")
        f.write("    model {\n")
        f.write('        enterprise "MyEnterprise" {\n')
        f.write('            softwareSystem "Application" {\n')
        f.write('                description "Auto-detected System"\n')

        for c in containers:
            name = c.get("name", "Unnamed")
            description = c.get("desc", "Auto-detected container")
            technology = c.get("tech", "Java")
            f.write(f'                container "{name}" "{description}" "{technology}" {{\n')
            
            # Add components
            for comp in c.get("components", []):
                comp_name = comp.get("name", "UnnamedComponent")
                comp_desc = comp.get("desc", "Auto-detected component")
                comp_tech = comp.get("tech", "Unknown")
                f.write(f'                    component "{comp_name}" "{comp_desc}" "{comp_tech}"\n')
            
            f.write("                }\n")

        f.write("            }\n")  # end softwareSystem
        f.write("        }\n")      # end enterprise
        f.write("    }\n")          # end model

        f.write("    views {\n")
        f.write('        systemContext "Application" "SystemContext" {\n')
        f.write("            include *\n")
        f.write("            autolayout\n")
        f.write("        }\n")
        
        f.write('        container "Application" "Containers" {\n')
        f.write("            include *\n")
        f.write("            autolayout\n")
        f.write("        }\n")
        
        f.write("    }\n")
        f.write("}\n")

def main():
    parser = argparse.ArgumentParser(description="Reverse Engineer Project to Structurizr DSL")
    parser.add_argument("--src", required=True, help="Path to project source")
    parser.add_argument("--out", required=True, help="Output DSL file path")
    args = parser.parse_args()

    containers = scan_project(args.src)
    generate_dsl(containers, args.out)
    print(f"Structurizr DSL generated at: {args.out}")
    print(f"Found {len(containers)} containers with {sum(len(c.get('components', [])) for c in containers)} components")

if __name__ == "__main__":
    main()