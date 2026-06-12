@echo off
REM Double-cliquez pour lancer le serveur FastAPI et voir les requetes EN DIRECT.
REM Ctrl+C dans la fenetre pour l'arreter.
cd /d "%~dp0"
echo Serveur FastAPI sur http://0.0.0.0:8000  (Swagger : http://127.0.0.1:8000/docs)
echo Les requetes s'affichent ci-dessous en direct :
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000
echo.
echo (Serveur arrete. Appuyez sur une touche pour quitter.)
pause >nul
