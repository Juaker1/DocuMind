# Establecer PYTHONPATH para que src sea accesible
$env:PYTHONPATH = "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"

# Activar conda environment
conda activate documind

# Ir al directorio backend
Set-Location "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"

# Iniciar el servidor con uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
