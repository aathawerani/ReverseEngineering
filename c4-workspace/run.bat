@echo off
echo ========================================
echo Proper C4 Model Generator
echo ========================================

echo Building Docker image...
docker build -t c4-generator .

echo.
echo Generating C4 model diagrams...
docker run --rm -v "%CD%\input:/workspace/input" -v "%CD%\output:/workspace/output" c4-generator

echo.
echo COMPLETE! Generated proper C4 model:
echo   C1 - System Context Diagram
echo   C2 - Container Diagram  
echo   C3 - Component Diagram
echo   Bonus - UML Class Diagram
echo.
echo Check the 'output' folder for your diagrams.
pause