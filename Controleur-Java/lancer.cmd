@echo off
REM Double-cliquez sur ce fichier pour lancer le contrôleur JavaFX.
cd /d "%~dp0"
call mvn -f pom.xml javafx:run
echo.
echo (Fenetre fermee. Appuyez sur une touche pour quitter.)
pause >nul