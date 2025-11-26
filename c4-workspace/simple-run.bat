@echo off
echo ========================================
echo Spring Boot C4 Generator (Docker)
echo ========================================

mkdir input 2>nul
mkdir output 2>nul

echo.
echo If you have Spring Boot projects, copy them to the 'input' folder.
echo Press any key to generate diagrams...
pause

echo.
echo Creating diagrams...

docker run --rm -v "%CD%\input:/input" -v "%CD%\output:/output" eclipse-temurin:17-jre-jammy /bin/bash -c "
apt-get update && apt-get install -y wget graphviz &&
wget -O /plantuml.jar https://github.com/plantuml/plantuml/releases/download/v1.2023.12/plantuml-1.2023.12.jar &&
cd /input &&
if [ -z \"\$(ls -A)\" ]; then
    echo 'No projects found, creating sample diagram...'
    cat > /output/sample_architecture.puml << 'EOF'
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Sample Spring Boot Microservice

Person(user, \"User\", \"Uses the application\")
Container(webapp, \"Web Application\", \"Spring Boot\", \"Provides REST API\")
ContainerDb(database, \"Database\", \"MySQL\", \"Stores application data\")

Rel(user, webapp, \"Uses\", \"HTTPS/REST\")
Rel(webapp, database, \"Reads/Writes\", \"JDBC\")
@enduml
EOF
    java -jar /plantuml.jar /output/sample_architecture.puml
    echo 'Created sample diagram'
else
    for project in */; do
        if [ -d \"\$project\" ]; then
            echo \"Creating diagram for: \$project\"
            cat > /output/\${project%/}_architecture.puml << EOF
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Spring Boot Microservice: \${project%/}

Person(user, \"User\", \"Uses the application\")
Container(webapp, \"Web Application\", \"Spring Boot\", \"Provides REST API\")
ContainerDb(database, \"Database\", \"MySQL\", \"Stores application data\")

Rel(user, webapp, \"Uses\", \"HTTPS/REST\")
Rel(webapp, database, \"Reads/Writes\", \"JDBC\")

note right of webapp
  **Project:** \${project%/}
  **Framework:** Spring Boot
  **Architecture:** Microservice
end note
@enduml
EOF
            java -jar /plantuml.jar /output/\${project%/}_architecture.puml
            echo \"Created diagram for: \$project\"
        fi
    done
fi
echo 'All diagrams generated!'
"

echo.
echo Check the 'output' folder for your C4 diagrams!
pause