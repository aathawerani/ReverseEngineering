@echo off
echo ========================================
echo Spring Boot C4 Model Generator (Docker)
echo ========================================

REM Build the Docker image
echo Building Docker image...
docker build -t c4-generator .

REM Run the analysis
echo Running analysis...
docker run --rm -v "%CD%\input:/workspace/input" -v "%CD%\output:/workspace/output" c4-generator

echo.
echo Analysis complete!
echo Check the 'output' folder for your diagrams.
pause