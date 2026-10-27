from fastapi import APIRouter
from app.packages.p5_comercial.controllers.cu032_documentos_unidad.document_controller import router as document_router

router = APIRouter()

# Registro de routers de P5: Comercialización y Post-Venta
router.include_router(document_router)
