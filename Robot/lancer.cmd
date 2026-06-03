@echo off
REM Double-cliquez sur ce fichier pour lancer le simulateur de robots.
set "JAVA_HOME=C:\Program Files\Java\jdk-21"
set "MVN=C:\Program Files\JetBrains\IntelliJ IDEA 2025.2.2\plugins\maven\lib\maven3\bin\mvn.cmd"
if not exist "%MVN%" set "MVN=mvn"
cd /d "%~dp0"
call "%MVN%" -f pom.xml javafx:run
echo.
echo (Fenetre fermee. Appuyez sur une touche pour quitter.)
pause >nul
