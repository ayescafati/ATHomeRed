from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from domain.entities.usuarios import Profesional
from domain.entities.catalogo import Especialidad
from domain.value_objects.objetos_valor import Ubicacion, Disponibilidad, Matricula
from domain.enumeraciones import DiaSemana
from infra.persistence.models import ProfesionalORM, EspecialidadORM, UbicacionORM

class ProfesionalRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def _to_domain(self, orm: ProfesionalORM) -> Profesional:
        """ORM → Dominio"""
        return Profesional(
            id=UUID(orm.id),
            nombre=orm.nombre,
            apellido=orm.apellido,
            email=orm.email,
            celular=orm.celular,
            ubicacion=Ubicacion(
                provincia=orm.ubicacion.provincia,
                departamento=orm.ubicacion.departamento,
                barrio=orm.ubicacion.barrio,
                calle=orm.ubicacion.calle,
                numero=orm.ubicacion.numero
            ) if orm.ubicacion else None,
            activo=orm.activo,
            verificado=orm.verificado,
            especialidades=[
                Especialidad(id=e.id_especialidad, nombre=e.nombre)
                for e in (orm.especialidades or [])
            ],
            disponibilidades=[
                Disponibilidad(
                    dias_semana=[DiaSemana(int(d)) for d in disp.dias_semana if d.isdigit()],
                    hora_inicio=disp.hora_inicio,
                    hora_fin=disp.hora_fin
                )
                for disp in (orm.disponibilidades or [])
            ],
            matriculas=[
                Matricula(
                    numero=m.numero,
                    provincia=m.provincia,
                    vigente_desde=m.vigente_desde,
                    vigente_hasta=m.vigente_hasta
                )
                for m in (orm.matriculas or [])
            ]
        )
    
    def obtener_por_id(self, id: UUID) -> Optional[Profesional]:
        orm = self.session.query(ProfesionalORM).filter(
            ProfesionalORM.id == str(id)
        ).first()
        return self._to_domain(orm) if orm else None
    
    def listar_activos(self) -> List[Profesional]:
        """Para Strategy de búsqueda"""
        orms = self.session.query(ProfesionalORM).filter(
            ProfesionalORM.activo == True
        ).all()
        return [self._to_domain(orm) for orm in orms]
    
    def crear(self, profesional: Profesional) -> Profesional:
        """Guarda nuevo profesional (dominio → ORM)"""
        # 1. Crear ubicación
        ub_orm = UbicacionORM(
            calle=profesional.ubicacion.calle,
            numero=profesional.ubicacion.numero,
            barrio=profesional.ubicacion.barrio,
            departamento=profesional.ubicacion.departamento,
            provincia=profesional.ubicacion.provincia
        )
        self.session.add(ub_orm)
        self.session.flush()
        
        # 2. Crear profesional
        orm = ProfesionalORM(
            id=str(profesional.id),
            nombre=profesional.nombre,
            apellido=profesional.apellido,
            email=profesional.email,
            celular=profesional.celular,
            ubicacion_id=ub_orm.id,
            activo=profesional.activo,
            verificado=profesional.verificado,
            matricula=""
        )
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        
        return self._to_domain(orm)