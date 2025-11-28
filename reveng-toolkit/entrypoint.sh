#!/usr/bin/env bash
set -e

echo "Reverse Engineering Toolkit - interactive container"
echo ""
echo "Mounted workspace: /workspace"
echo ""
echo "Usage examples (run from inside container or call via docker run):"
echo "  /tools/analyzer.py --src /workspace/path-to-your-project --out /workspace/rev-output"
echo "  java -jar /tools/structurizr/structurizr-cli.jar export -w /workspace/rev-output/workspace.dsl -o /workspace/rev-output/export -f plantuml"
echo ""
echo "Common commands (examples):"
echo "  analyzer: /tools/analyzer.py --src /workspace --out /workspace/rev-output"
echo "  plantuml: java -jar /tools/plantuml/plantuml.jar /workspace/rev-output/*.puml"
echo "  mermaid: mmdc -i /workspace/rev-output/diagrams.mmd -o /workspace/rev-output/diagram.png"
echo ""
# If there are args, run them (useful for one-shot runs)
if [ "$#" -gt 0 ]; then
  exec "$@"
fi

# otherwise, open bash
/bin/bash
