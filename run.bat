@echo off
echo Starting GNN Molecular Property Prediction API...
"C:\Users\pc\my_env\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause


