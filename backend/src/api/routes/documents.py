from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from typing import List
from src.application.use_cases.upload_document import UploadDocumentUseCase
from src.application.use_cases.process_document import ProcessDocumentUseCase
from src.application.dtos.document_dto import DocumentUploadResponse, DocumentListItem, DocumentDetail
from src.api.dependencies import get_document_repository
from src.infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from src.infrastructure.database.repositories.document_chunk_repository_impl import DocumentChunkRepositoryImpl
from src.infrastructure.database.connection import AsyncSessionLocal


router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Sube un documento PDF para ser procesado.
    Usa su propia sesión de BD con commit explícito antes de programar el background task,
    para evitar race conditions con el procesamiento en background.
    """
    # Validar tipo de archivo
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    if not file.content_type or 'pdf' not in file.content_type.lower():
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido")
    
    # Obtener tamaño del archivo
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    try:
        # Usar sesión propia con commit explícito e inmediato
        async with AsyncSessionLocal() as session:
            try:
                document_repo = DocumentRepositoryImpl(session)
                chunk_repo = DocumentChunkRepositoryImpl(session)
                upload_use_case = UploadDocumentUseCase(document_repo, chunk_repo)
                
                document = await upload_use_case.execute(
                    file=file.file,
                    filename=file.filename,
                    file_size=file_size
                )
                
                # Commit inmediato — garantiza que el documento está en BD
                # antes de que el background task intente encontrarlo
                await session.commit()
                print(f"💾 Documento {document.id} guardado y commiteado en BD")
                
            except Exception:
                await session.rollback()
                raise
        
        # Programar procesamiento en background DESPUÉS del commit
        background_tasks.add_task(
            process_document_background,
            document.id
        )
        
        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            file_size=document.file_size,
            total_pages=document.total_pages,
            upload_date=document.upload_date,
            processed=document.processed
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir documento: {str(e)}")


async def process_document_background(document_id: int):
    """
    Procesa el documento en background con su PROPIA sesión de BD.
    Espera brevemente para garantizar que el commit del request original ya ocurrió.
    """
    import asyncio
    import traceback

    # Pequeña espera removida: el upload ya hace commit antes de programar este task
    print(f"🔄 Iniciando procesamiento en background para documento {document_id}")
    async with AsyncSessionLocal() as session:
        try:
            document_repo = DocumentRepositoryImpl(session)
            chunk_repo = DocumentChunkRepositoryImpl(session)
            use_case = ProcessDocumentUseCase(document_repo, chunk_repo)
            chunks = await use_case.execute(document_id)
            await session.commit()
            print(f"✅ Background: documento {document_id} procesado con {len(chunks)} chunks guardados")
        except ValueError as e:
            await session.rollback()
            print(f"⚠️ Background: error de validación en documento {document_id}: {str(e)}")
        except Exception as e:
            await session.rollback()
            print(f"❌ Background: error procesando documento {document_id}: {str(e)}")
            traceback.print_exc()

@router.get("/", response_model=List[DocumentListItem])
async def list_documents(
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository)
):
    """
    Lista todos los documentos subidos.
    Incluye `has_conversation` para cada documento.
    """
    from sqlalchemy import select, exists
    from src.infrastructure.database.models import DocumentModel, ConversationModel

    try:
        # Subquery: ¿existe al menos una conversación para este documento?
        conv_exists = (
            select(ConversationModel.id)
            .where(ConversationModel.document_id == DocumentModel.id)
            .correlate(DocumentModel)
            .exists()
        )

        stmt = select(DocumentModel, conv_exists.label("has_conversation"))
        result = await document_repo.session.execute(stmt)
        rows = result.all()

        return [
            DocumentListItem(
                id=doc.id,
                filename=doc.filename,
                file_size=doc.file_size,
                total_pages=doc.total_pages,
                upload_date=doc.upload_date,
                processed=doc.processed,
                has_conversation=bool(has_conv),
            )
            for doc, has_conv in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar documentos: {str(e)}")


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: int,
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository)
):
    """
    Obtiene los detalles de un documento específico
    
    - **document_id**: ID del documento
    """
    try:
        document = await document_repo.find_by_id(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        return DocumentDetail(
            id=document.id,
            filename=document.filename,
            file_size=document.file_size,
            total_pages=document.total_pages,
            upload_date=document.upload_date,
            processed=document.processed,
            conversation_count=0  # TODO: Implementar conteo real
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener documento: {str(e)}")

@router.post("/{document_id}/process")
async def process_document(
    document_id: int,
):
    """
    Procesa manualmente un documento (genera embeddings)
    
    - **document_id**: ID del documento a procesar
    
    Útil si el procesamiento automático falló o si se quiere reprocesar.
    """
    try:
        async with AsyncSessionLocal() as session:
            try:
                document_repo = DocumentRepositoryImpl(session)
                chunk_repo = DocumentChunkRepositoryImpl(session)
                use_case = ProcessDocumentUseCase(document_repo, chunk_repo)
                chunks = await use_case.execute(document_id)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        
        return {
            "message": "Documento procesado exitosamente",
            "document_id": document_id,
            "chunks_created": len(chunks)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar documento: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository)
):
    """
    Elimina un documento y todos sus chunks y conversaciones
    
    - **document_id**: ID del documento a eliminar
    """
    try:
        # Verificar que existe
        document = await document_repo.find_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        # Eliminar (CASCADE eliminará chunks y conversaciones)
        success = await document_repo.delete(document_id)
        
        if success:
            return {"message": "Documento eliminado exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar documento")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar documento: {str(e)}")
