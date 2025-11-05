from fastapi import FastAPI
from app.api.routers import auth, busqueda, consultas, pacientes, profesionales, valoraciones

app = FastAPI(
    title="ATHomeRed API",
    version="0.1",
    description="API para la gestion de profesionales de la salud, pacientes y consultas"
)

app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(busqueda.router, prefix="/busqueda", tags=["Búsqueda"])
app.include_router(consultas.router, prefix="/consultas", tags=["Consultas"])
app.include_router(pacientes.router, prefix="/pacientes", tags=["Pacientes"])
app.include_router(profesionales.router, prefix="/profesionales", tags=["Profesionales"])
app.include_router(valoraciones.router, prefix="/valoraciones", tags=["Valoraciones"])  

@app.get("/health")
def health_check():
    return {"status": "ok"}