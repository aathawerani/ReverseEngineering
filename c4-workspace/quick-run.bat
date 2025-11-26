@echo off
echo Spring Boot C4 Diagram Generator
echo.

mkdir input 2>nul
mkdir output 2>nul

echo If you have Spring Boot projects, copy them to the 'input' folder.
echo Press any key to continue...
pause

echo Generating diagrams...
docker run --rm -v "%CD%\input:/input" -v "%CD%\output:/output" maven:3.8.5-openjdk-17 /bin/bash -c "
cd /input
if [ -z \"\$(ls -A)\" ]; then
    echo 'No projects found. Creating sample diagram...'
    cat > /output/sample.puml << 'EOF'
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
title Spring Boot Microservice
Container(app, 'Spring Boot App', 'Java', 'Microservice')
ContainerDb(db, 'Database', 'MySQL', 'Data Storage')
Rel(app, db, 'Uses', 'JDBC')
@enduml
EOF
    echo 'Sample diagram created'
else
    for project in */; do
        echo \"Processing \$project\"
        cat > /output/\${project%/}.puml << EOF
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
title \$project
Container(app, 'Spring Boot App', 'Java', 'Microservice')
ContainerDb(db, 'Database', 'MySQL', 'Data Storage')
Rel(app, db, 'Uses', 'JDBC')
@enduml
EOF
    done
    echo 'All diagrams created'
fi
"

echo.
echo Diagrams created in the 'output' folder!
echo Note: These are basic diagrams. For advanced analysis, use Method 2.
pause