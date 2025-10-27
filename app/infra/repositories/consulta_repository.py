from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date

from domain.entities.agenda import Consulta, EstadoConsulta
from domain.value_objects.objetos_valor import Ubicacion
from domain.eventos import Event
from infra.persistence.models import ConsultaORM, EventoORM, UbicacionORM

class ConsultaRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def _to_domain(self, orm: ConsultaORM) -> Consulta:
        """ORM → Dominio"""
        return Consulta(
            id=UUID(orm.id),
            id_paciente=UUID(orm.paciente_id),
            id_profesional=orm.profesional_id,
            fecha=orm.fecha,
            hora_inicio=orm.hora_inicio,
            hora_fin=orm.hora_fin,
            ubicacion=Ubicacion(
                provincia=orm.ubicacion_servicio.provincia,
                departamento=orm.ubicacion_servicio.departamento,
                barrio=orm.ubicacion_servicio.barrio,
                calle=orm.ubicacion_servicio.calle,
                numero=orm.ubicacion_servicio.numero
            ) if orm.ubicacion_servicio else None,
            estado=EstadoConsulta(orm.estado)
        )
    
    def obtener_por_id(self, id: UUID) -> Optional[Consulta]:
        orm = self.session.query(ConsultaORM).filter(
            ConsultaORM.id == str(id)
        ).first()
        return self._to_domain(orm) if orm else None
    
    def listar_por_profesional(self, id_profesional: UUID, desde: date = None) -> List[Consulta]:
        query = self.session.query(ConsultaORM).filter(
            ConsultaORM.profesional_id == str(id_profesional)
        )
        if desde:
            query = query.filter(ConsultaORM.fecha >= desde)
        
        return [self._to_domain(orm) for orm in query.all()]
    
    def crear(self, consulta: Consulta) -> Consulta:
        """Dominio → ORM"""
        # Ubicación
        ub_orm = None
        if consulta.ubicacion:
            ub_orm = UbicacionORM(
                calle=consulta.ubicacion.calle,
                numero=consulta.ubicacion.numero,
                barrio=consulta.ubicacion.barrio,
                departamento=consulta.ubicacion.departamento,
                provincia=consulta.ubicacion.provincia
            )
            self.session.add(ub_orm)
            self.session.flush()
        
        orm = ConsultaORM(
            id=str(consulta.id),
            paciente_id=str(consulta.id_paciente),
            profesional_id=str(consulta.id_profesional),
            ubicacion_servicio_id=ub_orm.id if ub_orm else None,
            fecha=consulta.fecha,
            hora_inicio=consulta.hora_inicio,
            hora_fin=consulta.hora_fin,
            estado=consulta.estado.value,
            notas=""
        )
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        
        return self._to_domain(orm)
    
    def actualizar(self, consulta: Consulta) -> Consulta:
        orm = self.session.query(ConsultaORM).filter(
            ConsultaORM.id == str(consulta.id)
        ).first()
        
        if orm:
            orm.estado = consulta.estado.value
            orm.fecha = consulta.fecha
            orm.hora_inicio = consulta.hora_inicio
            orm.hora_fin = consulta.hora_fin
            self.session.commit()
            self.session.refresh(orm)
            return self._to_domain(orm)
        return None
    
    def guardar_evento(self, evento: Event) -> None:
        """Persiste eventos del Observer"""
        evento_orm = EventoORM(
            consulta_id=str(evento.cita_id),
            tipo=evento.tipo,
            datos=evento.datos
        )
        self.session.add(evento_orm)
        self.session.commit()