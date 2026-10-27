from fastapi import APIRouter
from app.packages.p3_actores.controllers.cu013_actores_cadena.actor_controller import router as actor_router
from app.packages.p3_actores.controllers.cu014_ubicaciones.location_controller import router as location_router

router = APIRouter()

# Registro de routers de P3: Actores de la Cadena y Ubicaciones
router.include_router(actor_router)
router.include_router(location_router)
