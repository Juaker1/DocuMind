# DocuMind Backend - Guía de Setup de Base de Datos

## Opción 1: Usando Docker (Recomendado)

1. **Asegúrate de que Docker Desktop esté corriendo**

2. **Inicia PostgreSQL con pgvector:**
```powershell
cd c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind
docker-compose up -d
```

3. **Verifica que esté corriendo:**
```powershell
docker ps
```

Deberías ver un contenedor llamado `documind_db`.

4. **Crea las tablas:**
```powershell
$env:PYTHONPATH = "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"
conda activate documind
cd backend
python init_db.py
```

## Opción 2: PostgreSQL Local

Si prefieres usar PostgreSQL instalado localmente:

1. **Instala pgvector en tu base de datos local**

2. **Crea una base de datos llamada `documind`:**
```sql
CREATE DATABASE documind;
\c documind
CREATE EXTENSION vector;
```

3. **Actualiza el .env con tu configuración:**
```env
DATABASE_URL=postgresql+asyncpg://tu_usuario:tu_password@localhost:5432/documind
```

4. **Crea las tablas:**
```powershell
$env:PYTHONPATH = "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"
conda activate documind
cd backend
python init_db.py
```

## Verificar la Instalación

Una vez creadas las tablas, verifica conectándote a la base de datos:

```sql
\dt  -- Lista las tablas
```

Deberías ver:
- `documents`
- `document_chunks`
- `conversations`
- `messages`

## Iniciar el Servidor

```powershell
.\backend\start_server.ps1
```

O manualmente:

```powershell
$env:PYTHONPATH = "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"
conda activate documind
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Probar la API

1. Abre http://localhost:8000/docs en tu navegador
2. Prueba el endpoint `/health` para verificar que todo funciona
3. Prueba subir un PDF en `/api/documents/upload`

## Troubleshooting

### Error: "No module named 'src'"
```powershell
$env:PYTHONPATH = "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"
```

### Error: "Connection refused" to database
- Verifica que PostgreSQL/Docker esté corriendo
- Verifica la variable `DATABASE_URL` en `.env`

### Error: "Ollama not available"
- Verifica que Ollama esté corriendo: `ollama list`
- Inicia Ollama si es necesario
