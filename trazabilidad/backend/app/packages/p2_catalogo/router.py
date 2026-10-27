from fastapi import APIRouter
from app.packages.p2_catalogo.controllers.cu009_categorias.category_controller import router as category_router
from app.packages.p2_catalogo.controllers.cu006_productos_variantes.product_controller import router as product_router
from app.packages.p2_catalogo.controllers.cu007_certificaciones.certification_controller import router as certification_router
from app.packages.p2_catalogo.controllers.cu008_catalogo_empresa.tenant_catalog_controller import router as tenant_catalog_router
from app.packages.p2_catalogo.controllers.cu010_ordenes_compra.purchase_controller import router as purchase_router
from app.packages.p2_catalogo.controllers.cu011_compras.purchase_approval_controller import router as purchase_approval_router
from app.packages.p2_catalogo.controllers.cu012_recepciones.reception_controller import router as reception_router

router = APIRouter()

# Registro de routers de P2: Catálogo y Abastecimiento
router.include_router(category_router)
router.include_router(product_router)
router.include_router(certification_router)
router.include_router(tenant_catalog_router)
router.include_router(purchase_router)
router.include_router(purchase_approval_router)
router.include_router(reception_router)
