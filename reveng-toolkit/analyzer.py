import os
import argparse

def scan_project(src_path):
    """
    Scan the project directory and detect systems, containers, and components.
    For simplicity, each top-level folder = container, each file = component.
    """
    containers = []
    for root, dirs, files in os.walk(src_path):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if root == src_path:
            # Top-level directories = containers
            for d in dirs:
                container = {
                    "name": d,
                    "desc": "Auto-detected package container",
                    "tech": "Java",  # You can make this dynamic based on file type
                    "components": []
                }
                # Scan components inside container
                container_path = os.path.join(root, d)
                for f in os.listdir(container_path):
                    if f.endswith(".java") or f.endswith(".py"):  # adjust as needed
                        container["components"].append({
                            "name": os.path.splitext(f)[0],
                            "desc": "Auto-detected class/file",
                            "tech": "Java" if f.endswith(".java") else "Python"
                        })
                containers.append(container)
    return containers

def generate_dsl(containers, output_file):
    with open(output_file, "w") as f:
        f.write("workspace {\n")
        f.write("    model {\n")
        f.write('        softwareSystem "Auto-detected System" {\n')

        if not containers:
            f.write('            container "Placeholder" "Auto-generated container" "Java"\n')
        else:
            for c in containers:
                name = c.get("name", "Unnamed")
                description = c.get("description", "Auto-detected package container")
                technology = c.get("technology", "Java")
                f.write(f'            container "{name}" "{description}" "{technology}"\n')

        f.write("        }\n")  # end softwareSystem
        f.write("    }\n")      # end model

        f.write("    views {\n")
        f.write('        systemContext "Auto-detected System" {\n')
        f.write("            include *\n")
        f.write("            autolayout lr\n")
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

if __name__ == "__main__":
    main()
