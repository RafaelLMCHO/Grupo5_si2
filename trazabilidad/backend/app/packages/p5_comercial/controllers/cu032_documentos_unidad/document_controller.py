"""CU-032 - T049: carga y asociación de documentos a unidades.

Permite adjuntar (factura, certificado de importación, comprobante de garantía,
certificado de autenticidad, informe técnico) a una unidad, listarlos, consultarlos,
verificar la integridad de su hash y eliminarlos. El archivo vive en un storage
externo (URL); aquí se guarda su hash SHA-256 para asegurar la integridad.
"""

import hashlib
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.cu002_usuarios.user import User
from app.models.cu005_bitacora.bitacora import Bitacora
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu032_documentos_unidad.documento_unidad import (
    TIPO_DOCUMENTO_ENUM,
    DocumentoUnidad,
)
from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.controllers.shared import (
    get_bolivia_now,
    get_client_ip,
    get_idusuariotenant,
    require_roles,
    resolve_tenant_id,
)
from app.views.cu032_documentos_unidad.document_views import (
    CreateDocumentoRequest,
    DocumentoListResponse,
    DocumentoResponse,
    VerifyDocumentoRequest,
    VerifyDocumentoResponse,
)

router = APIRouter(prefix="/documents", tags=["Documentos de Unidad (CU-032)"])

ROLES_DOCUMENTOS = ("SuperAdministrador", "AdministradorEmpresa", "GestorVentasPostventa")
requires_documentos = require_roles(*ROLES_DOCUMENTOS)

_TIPOS_VALIDOS = set(TIPO_DOCUMENTO_ENUM.enums)


def _sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


class DocumentoController:

    @staticmethod
    def _get_unidad(db: Session, tenant_id: int, idunidad: int) -> UnidadProducto:
        unidad = db.execute(
            select(UnidadProducto).where(
                UnidadProducto.idunidad == idunidad,
                UnidadProducto.idtenant == tenant_id,
            )
        ).scalar_one_or_none()
        if not unidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La unidad con ID {idunidad} no existe en su empresa.",
            )
        return unidad

    @staticmethod
    def _get_documento(db: Session, tenant_id: int, iddocumento: int) -> DocumentoUnidad:
        documento = db.execute(
            select(DocumentoUnidad)
            .join(UnidadProducto, UnidadProducto.idunidad == DocumentoUnidad.idunidad)
            .where(
                DocumentoUnidad.iddocumento == iddocumento,
                UnidadProducto.idtenant == tenant_id,
            )
        ).scalar_one_or_none()
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El documento con ID {iddocumento} no encontrado.",
            )
        return documento

    @staticmethod
    def _to_response(documento: DocumentoUnidad, unidad: Optional[UnidadProducto] = None) -> DocumentoResponse:
        vencido = None
        hoy = get_bolivia_now().date()
        if documento.fechavencimiento is not None:
            vencido = documento.fechavencimiento < hoy
        return DocumentoResponse(
            iddocumento=documento.iddocumento,
            idunidad=documento.idunidad,
            nombre=documento.nombre,
            urlarchivo=documento.urlarchivo,
            hasharchivo=documento.hasharchivo,
            fechaemision=documento.fechaemision,
            fechavencimiento=documento.fechavencimiento,
            tipodocumento=str(documento.tipodocumento),
            numeroserie=unidad.numeroserie if unidad else None,
            uuidpublico=unidad.uuidpublico if unidad else None,
            vencido=vencido,
        )

    @staticmethod
    def _registrar_bitacora(
        db: Session, user: User, accion: str, identidad: int, ip: str
    ) -> None:
        idut = get_idusuariotenant(db, user)
        db.add(
            Bitacora(
                idusuariotenant=idut,
                accion=accion,
                entidad="DocumentoUnidad",
                identidad=identidad,
                ip=ip,
                fechahora=get_bolivia_now(),
            )
        )

    @staticmethod
    def _resolver_hash(body: CreateDocumentoRequest) -> str:
        if body.contenido is not None:
            return _sha256(body.contenido)
        if body.hasharchivo:
            return body.hasharchivo.strip()
        # Sin contenido ni hash explícito: huella determinística de la metadata.
        return _sha256(f"{body.nombre}|{body.urlarchivo}|{body.tipodocumento}")

    @staticmethod
    def attach_document(
        db: Session, user: User, request: Request, idunidad: int, body: CreateDocumentoRequest
    ) -> DocumentoResponse:
        tenant_id = resolve_tenant_id(db, user)
        unidad = DocumentoController._get_unidad(db, tenant_id, idunidad)

        if body.tipodocumento not in _TIPOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de documento inválido. Valores permitidos: {sorted(_TIPOS_VALIDOS)}.",
            )

        fechaemision = body.fechaemision or get_bolivia_now().date()
        if body.fechavencimiento and body.fechavencimiento < fechaemision:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de vencimiento no puede ser anterior a la fecha de emisión.",
            )

        documento = DocumentoUnidad(
            idunidad=unidad.idunidad,
            nombre=body.nombre.strip(),
            urlarchivo=body.urlarchivo.strip(),
            hasharchivo=DocumentoController._resolver_hash(body),
            fechaemision=fechaemision,
            fechavencimiento=body.fechavencimiento,
            tipodocumento=body.tipodocumento,
        )
        db.add(documento)
        db.flush()

        DocumentoController._registrar_bitacora(
            db, user, "ADJUNTAR_DOCUMENTO", documento.iddocumento, get_client_ip(request)
        )
        db.commit()
        db.refresh(documento)
        return DocumentoController._to_response(documento, unidad)

    @staticmethod
    def list_by_unidad(
        db: Session, user: User, idunidad: int
    ) -> DocumentoListResponse:
        tenant_id = resolve_tenant_id(db, user)
        unidad = DocumentoController._get_unidad(db, tenant_id, idunidad)

        documentos = db.execute(
            select(DocumentoUnidad)
            .where(DocumentoUnidad.idunidad == unidad.idunidad)
            .order_by(DocumentoUnidad.iddocumento.desc())
        ).scalars().all()

        return DocumentoListResponse(
            total=len(documentos),
            items=[DocumentoController._to_response(d, unidad) for d in documentos],
        )

    @staticmethod
    def list_documents(
        db: Session,
        user: User,
        tipodocumento: Optional[str] = None,
        idunidad: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> DocumentoListResponse:
        tenant_id = resolve_tenant_id(db, user)

        query = (
            select(DocumentoUnidad)
            .join(UnidadProducto, UnidadProducto.idunidad == DocumentoUnidad.idunidad)
            .where(UnidadProducto.idtenant == tenant_id)
        )
        if tipodocumento:
            if tipodocumento not in _TIPOS_VALIDOS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de documento inválido: {tipodocumento}.",
                )
            query = query.where(DocumentoUnidad.tipodocumento == tipodocumento)
        if idunidad:
            query = query.where(DocumentoUnidad.idunidad == idunidad)

        total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
        documentos = db.execute(
            query.order_by(DocumentoUnidad.iddocumento.desc()).offset(skip).limit(limit)
        ).scalars().all()

        return DocumentoListResponse(
            total=total,
            items=[DocumentoController._to_response(d) for d in documentos],
        )

    @staticmethod
    def get_document(db: Session, user: User, iddocumento: int) -> DocumentoResponse:
        tenant_id = resolve_tenant_id(db, user)
        documento = DocumentoController._get_documento(db, tenant_id, iddocumento)
        unidad = db.execute(
            select(UnidadProducto).where(UnidadProducto.idunidad == documento.idunidad)
        ).scalar_one_or_none()
        return DocumentoController._to_response(documento, unidad)

    @staticmethod
    def verify_document(
        db: Session, user: User, iddocumento: int, body: VerifyDocumentoRequest
    ) -> VerifyDocumentoResponse:
        tenant_id = resolve_tenant_id(db, user)
        documento = DocumentoController._get_documento(db, tenant_id, iddocumento)

        if body.contenido is not None:
            calculado = _sha256(body.contenido)
        elif body.hasharchivo:
            calculado = body.hasharchivo.strip()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe enviar 'hasharchivo' o 'contenido' para verificar la integridad.",
            )

        coincide = calculado.lower() == documento.hasharchivo.lower()
        return VerifyDocumentoResponse(
            iddocumento=documento.iddocumento,
            hasharchivo=documento.hasharchivo,
            hashcalculado=calculado,
            coincide=coincide,
            mensaje=(
                "El documento es íntegro y no ha sido alterado."
                if coincide
                else "El hash no coincide: el documento pudo haber sido alterado."
            ),
        )

    @staticmethod
    def delete_document(db: Session, user: User, request: Request, iddocumento: int) -> None:
        tenant_id = resolve_tenant_id(db, user)
        documento = DocumentoController._get_documento(db, tenant_id, iddocumento)

        DocumentoController._registrar_bitacora(
            db, user, "ELIMINAR_DOCUMENTO", documento.iddocumento, get_client_ip(request)
        )
        db.delete(documento)
        db.commit()


# Endpoints API REST

@router.post(
    "/units/{idunidad}",
    response_model=DocumentoResponse,
    status_code=status.HTTP_201_CREATED,
)
def attach_document_route(
    idunidad: int,
    body: CreateDocumentoRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_documentos),
):
    """T049 - Adjuntar un documento a una unidad (CU-032)."""
    return DocumentoController.attach_document(db, current_user, request, idunidad, body)


@router.get("/units/{idunidad}", response_model=DocumentoListResponse)
def list_by_unidad_route(
    idunidad: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar los documentos de una unidad (CU-032)."""
    return DocumentoController.list_by_unidad(db, current_user, idunidad)


@router.get("", response_model=DocumentoListResponse)
def list_documents_route(
    tipodocumento: Optional[str] = Query(None, description="Filtrar por tipo de documento"),
    idunidad: Optional[int] = Query(None, description="Filtrar por unidad"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar documentos de la empresa (CU-032)."""
    return DocumentoController.list_documents(db, current_user, tipodocumento, idunidad, skip, limit)


@router.get("/{iddocumento}", response_model=DocumentoResponse)
def get_document_route(
    iddocumento: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detalle de un documento (CU-032)."""
    return DocumentoController.get_document(db, current_user, iddocumento)


@router.post("/{iddocumento}/verify", response_model=VerifyDocumentoResponse)
def verify_document_route(
    iddocumento: int,
    body: VerifyDocumentoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verificar la integridad de un documento por su hash (CU-032)."""
    return DocumentoController.verify_document(db, current_user, iddocumento, body)


@router.delete("/{iddocumento}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_route(
    iddocumento: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_documentos),
):
    """Eliminar un documento de una unidad (CU-032)."""
    DocumentoController.delete_document(db, current_user, request, iddocumento)
