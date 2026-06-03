@echo off
REM Double-cliquez sur ce fichier pour lancer le contrôleur JavaFX.
REM Recherche automatique du dossier IntelliJ IDEA
for /d %%i in ("C:\Program Files\JetBrains\IntelliJ IDEA*") do set "IDEA_DIR=%%i"
set "JAVA_HOME=%IDEA_DIR%\jbr"
set "MVN=%IDEA_DIR%\plugins\maven\lib\maven3\bin\mvn.cmd"
if not exist "%MVN%" set "MVN=mvn"
cd /d "%~dp0"
call "%MVN%" -f pom.xml javafx:run
echo.
echo (Fenetre fermee. Appuyez sur une touche pour quitter.)
pause >nul