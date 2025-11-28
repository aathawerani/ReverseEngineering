import os
import json

def write_structurizr_dsl(system_name, containers, out_file):
    """
    Write a Structurizr DSL workspace from detected system and containers.
    :param system_name: Name of the software system
    :param containers: List of dicts with 'name', 'description', 'technology'
    :param out_file: Path to output DSL file
    """
    with open(out_file, 'w') as f:
        f.write("workspace {\n\n")
        f.write("    model {\n")
        f.write(f"        softwareSystem \"{system_name}\" \"Auto-detected package container\" {{\n")
        for c in containers:
            f.write(f"            container \"{c['name']}\" \"{c.get('description','')}\" \"{c.get('technology','Java')}\"\n")
        f.write("        }\n")
        f.write("    }\n\n")

        f.write("    views {\n")
        f.write(f"        systemContext \"{system_name}\" {{\n")
        f.write("            include *\n")
        f.write("            autolayout lr\n")
        f.write("        }\n\n")

        f.write(f"        container \"{system_name}\" {{\n")
        f.write("            include *\n")
        f.write("            autolayout lr\n")
        f.write("        }\n")
        f.write("    }\n")
        f.write("}\n")

# Example usage
detected_containers = [
    {"name": "vaulsys", "description": "Main container", "technology": "Java"},
    {"name": "auth", "description": "Authentication module", "technology": "Java"}
]

write_structurizr_dsl("VaulSys", detected_containers, "/workspace/rev-output/workspace.dsl")
