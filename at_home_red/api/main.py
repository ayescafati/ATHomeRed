from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query

from .data import InMemoryDataStore, get_data_store
from .schemas import (
    EspecialidadSchema,
    ProfesionalSchema,
    PublicacionSchema,
    ResponsableSchema,
)

app = FastAPI(
    title="AT Home Red API",
    version="0.1.0",
    description="API basica en FastAPI para explorar el dominio modelado en at_home_red.",
)


@app.get("/", tags=["meta"])
def read_root() -> dict:
    return {"message": "AT Home Red API en FastAPI", "version": "0.1.0"}


@app.get("/health", tags=["meta"])
def healthcheck() -> dict:
    return {"status": "ok"}


@app.get(
    "/profesionales",
    response_model=List[ProfesionalSchema],
    tags=["profesionales"],
)
def listar_profesionales(
    especialidad: Optional[str] = Query(
        default=None,
        description="Filtra por nombre exacto de especialidad (ej.: 'Enfermeria Domiciliaria').",
    ),
    ciudad: Optional[str] = Query(
        default=None,
        description="Filtra por ciudad de residencia del profesional.",
    ),
    data_store: InMemoryDataStore = Depends(get_data_store),
) -> List[ProfesionalSchema]:
    profesionales = data_store.list_profesionales(
        especialidad=especialidad, ciudad=ciudad
    )
    return [
        ProfesionalSchema.from_domain(
            profesional,
            disponibilidades=data_store.get_disponibilidades(profesional.id),
            publicaciones=data_store.get_publicaciones_de_profesional(
                profesional.id
            ),
        )
        for profesional in profesionales
    ]


@app.get(
    "/profesionales/{profesional_id}",
    response_model=ProfesionalSchema,
    tags=["profesionales"],
)
def obtener_profesional(
    profesional_id: UUID,
    data_store: InMemoryDataStore = Depends(get_data_store),
) -> ProfesionalSchema:
    profesional = data_store.get_profesional(profesional_id)
    if not profesional:
        raise HTTPException(
            status_code=404, detail="Profesional no encontrado"
        )
    return ProfesionalSchema.from_domain(
        profesional,
        disponibilidades=data_store.get_disponibilidades(profesional.id),
        publicaciones=data_store.get_publicaciones_de_profesional(
            profesional.id
        ),
    )


@app.get(
    "/especialidades",
    response_model=List[EspecialidadSchema],
    tags=["catalogo"],
)
def listar_especialidades(
    data_store: InMemoryDataStore = Depends(get_data_store),
) -> List[EspecialidadSchema]:
    return [
        EspecialidadSchema.from_domain(e)
        for e in data_store.list_especialidades()
    ]


@app.get(
    "/publicaciones", response_model=List[PublicacionSchema], tags=["catalogo"]
)
def listar_publicaciones(
    especialidad: Optional[str] = Query(
        default=None,
        description="Filtra publicaciones por especialidad.",
    ),
    ciudad: Optional[str] = Query(
        default=None,
        description="Filtra publicaciones por ciudad del profesional.",
    ),
    data_store: InMemoryDataStore = Depends(get_data_store),
) -> List[PublicacionSchema]:
    publicaciones = data_store.list_publicaciones(
        especialidad=especialidad, ciudad=ciudad
    )
    return [
        PublicacionSchema.from_domain(pub, include_profesional=True)
        for pub in publicaciones
    ]


@app.get(
    "/responsables",
    response_model=List[ResponsableSchema],
    tags=["responsables"],
)
def listar_responsables(
    data_store: InMemoryDataStore = Depends(get_data_store),
) -> List[ResponsableSchema]:
    return [
        ResponsableSchema.from_domain(r)
        for r in data_store.list_responsables()
    ]


@app.get(
    "/responsables/{responsable_id}",
    response_model=ResponsableSchema,
    tags=["responsables"],
)
def obtener_responsable(
    responsable_id: UUID,
    data_store: InMemoryDataStore = Depends(get_data_store),
) -> ResponsableSchema:
    responsable = data_store.get_responsable(responsable_id)
    if not responsable:
        raise HTTPException(
            status_code=404, detail="Responsable no encontrado"
        )
    return ResponsableSchema.from_domain(responsable)
