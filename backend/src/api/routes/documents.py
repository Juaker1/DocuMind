from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from typing import List
from src.application.use_cases.upload_document import UploadDocumentUseCase
from src.application.use_cases.process_document import ProcessDocumentUseCase
from src.application.dtos.document_dto import DocumentUploadResponse, DocumentListItem, DocumentDetail
from src.api.dependencies import get_document_repository, get_current_user
from src.infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from src.infrastructure.database.repositories.document_chunk_repository_impl import DocumentChunkRepositoryImpl
from src.infrastructure.database.connection import AsyncSessionLocal
from src.domain.entities.user import User


router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Sube un documento PDF para ser procesado.
    El documento queda ligado al usuario actual (anónimo o registrado).
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    if not file.content_type or 'pdf' not in file.content_type.lower():
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido")

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    try:
        async with AsyncSessionLocal() as session:
            try:
                document_repo = DocumentRepositoryImpl(session)
                chunk_repo = DocumentChunkRepositoryImpl(session)
                upload_use_case = UploadDocumentUseCase(document_repo, chunk_repo)

                document = await upload_use_case.execute(
                    file=file.file,
                    filename=file.filename,
                    file_size=file_size,
                    user_id=current_user.id,  # Tag with owner
                )

                await session.commit()
                print(f"💾 Documento {document.id} guardado para usuario {current_user.id}")

            except Exception:
                await session.rollback()
                raise

        background_tasks.add_task(process_document_background, document.id)

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
    """Procesa el documento en background con su PROPIA sesión de BD."""
    import traceback

    print(f"🔄 Iniciando procesamiento en background para documento {document_id}")
    async with AsyncSessionLocal() as session:
        try:
            document_repo = DocumentRepositoryImpl(session)
            chunk_repo = DocumentChunkRepositoryImpl(session)
            use_case = ProcessDocumentUseCase(document_repo, chunk_repo)
            chunks = await use_case.execute(document_id)
            await session.commit()
            print(f"✅ Background: documento {document_id} procesado con {len(chunks)} chunks")
        except ValueError as e:
            await session.rollback()
            print(f"⚠️ Background: error de validación en documento {document_id}: {str(e)}")
        except Exception as e:
            await session.rollback()
            print(f"❌ Background: error procesando documento {document_id}: {str(e)}")
            traceback.print_exc()


@router.get("/", response_model=List[DocumentListItem])
async def list_documents(
    current_user: User = Depends(get_current_user),
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository),
):
    """Lista los documentos del usuario actual (filtrado por user_id)."""
    from sqlalchemy import select, exists
    from src.infrastructure.database.models import DocumentModel, ConversationModel

    try:
        conv_exists = (
            select(ConversationModel.id)
            .where(ConversationModel.document_id == DocumentModel.id)
            .correlate(DocumentModel)
            .exists()
        )

        stmt = (
            select(DocumentModel, conv_exists.label("has_conversation"))
            .where(DocumentModel.user_id == current_user.id)
        )
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
    current_user: User = Depends(get_current_user),
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository),
):
    """Obtiene los detalles de un documento (solo si pertenece al usuario actual)."""
    try:
        document = await document_repo.find_by_id(document_id)

        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")

        if document.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Acceso denegado")

        return DocumentDetail(
            id=document.id,
            filename=document.filename,
            file_size=document.file_size,
            total_pages=document.total_pages,
            upload_date=document.upload_date,
            processed=document.processed,
            conversation_count=0
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener documento: {str(e)}")


@router.post("/{document_id}/process")
async def process_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository),
):
    """Procesa manualmente un documento (genera embeddings). Solo el dueño puede hacerlo."""
    try:
        document = await document_repo.find_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        if document.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Acceso denegado")

        async with AsyncSessionLocal() as session:
            try:
                doc_repo2 = DocumentRepositoryImpl(session)
                chunk_repo = DocumentChunkRepositoryImpl(session)
                use_case = ProcessDocumentUseCase(doc_repo2, chunk_repo)
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
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar documento: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository),
):
    """Elimina un documento. Solo el dueño puede eliminarlo."""
    try:
        document = await document_repo.find_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")

        if document.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Acceso denegado")

        success = await document_repo.delete(document_id)

        if success:
            return {"message": "Documento eliminado exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar documento")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar documento: {str(e)}")
