from fastapi import APIRouter
from app.packages.p6_blockchain.controllers.cu033_blockchain.blockchain_controller import router as blockchain_router
from app.packages.p6_blockchain.controllers.cu034_certificados.certificate_controller import router as certificate_router

router = APIRouter()

# Registro de routers de P6: Blockchain y Notarización
router.include_router(blockchain_router)
router.include_router(certificate_router)
