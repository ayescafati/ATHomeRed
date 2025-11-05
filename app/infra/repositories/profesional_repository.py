from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.domain.entities.usuarios import Profesional
from app.domain.entities.catalogo import Especialidad
from app.domain.value_objects.objetos_valor import Ubicacion, Disponibilidad, Matricula
from app.domain.enumeraciones import DiaSemana
from app.infra.persistence.perfiles import ProfesionalORM
from app.infra.persistence.usuarios import UsuarioORM
from app.infra.persistence.servicios import EspecialidadORM
from app.infra.persistence.ubicacion import DireccionORM, BarrioORM, DepartamentoORM, ProvinciaORM
from app.infra.repositories.direccion_repository import DireccionRepository

class ProfesionalRepository:
    def __init__(self, session: Session):
        self.session = session
        self.direccion_repo = DireccionRepository(session)
    
    def _to_domain(self, orm: ProfesionalORM) -> Profesional:
        """ORM → Dominio"""
        # Convertir direccion ORM a Ubicacion value object
        ubicacion = None
        if orm.direccion:
            # Acceder a la jerarquía: direccion → barrio → departamento → provincia
            ubicacion = Ubicacion(
                provincia=orm.direccion.barrio.departamento.provincia.nombre,
                departamento=orm.direccion.barrio.departamento.nombre,
                barrio=orm.direccion.barrio.nombre,
                calle=orm.direccion.calle,
                numero=str(orm.direccion.numero),
                latitud=orm.direccion.latitud,
                longitud=orm.direccion.longitud
            )
        
        # Si no hay dirección, crear una ubicación vacía
        if ubicacion is None:
            ubicacion = Ubicacion(
                provincia="", departamento="", barrio="", calle="", numero=""
            )
        
        return Profesional(
            id=orm.id,
            nombre=orm.usuario.nombre,        # ✅ Acceso correcto vía usuario
            apellido=orm.usuario.apellido,    # ✅
            email=orm.usuario.email,          # ✅
            celular=orm.usuario.celular or "", # ✅
            ubicacion=ubicacion,
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
    
    def listar_todos(self) -> List[Profesional]:
        orms = self.session.query(ProfesionalORM).all()
        return [self._to_domain(orm) for orm in orms]
    
    def crear(self, profesional: Profesional, usuario_id: Optional[UUID] = None, direccion_id: Optional[UUID] = None) -> Profesional:
        """
        Guarda nuevo profesional (dominio → ORM)
        
        Args:
            profesional: Entidad de dominio Profesional
            usuario_id: (Opcional) ID de usuario existente. 
                       Si no se proporciona, se crea un nuevo UsuarioORM.
            direccion_id: (Opcional) ID de dirección existente. 
                         Si no se proporciona y el profesional tiene ubicación,
                         se crea automáticamente usando DireccionRepository.
        
        Returns:
            Profesional creado con ID asignado
            
        Example:
            # Opción 1: Con usuario y dirección existentes
            prof_repo.crear(profesional, usuario_id=uuid_usuario, direccion_id=uuid_dir)
            
            # Opción 2: Crear todo automáticamente
            profesional.ubicacion = Ubicacion(...)
            prof_repo.crear(profesional)  # Crea usuario y dirección
        """
        # Paso 1: Crear o usar UsuarioORM
        if usuario_id is None:
            # Crear nuevo usuario
            usuario_orm = UsuarioORM(
                nombre=profesional.nombre,
                apellido=profesional.apellido,
                email=profesional.email,
                celular=profesional.celular,
                es_profesional=True,
                es_solicitante=False,
                activo=profesional.activo,
                verificado=profesional.verificado
            )
            self.session.add(usuario_orm)
            self.session.flush()  # Para obtener el ID
            usuario_id = usuario_orm.id
        
        # Paso 2: Crear o usar DireccionORM
        if direccion_id is None and profesional.ubicacion:
            direccion_orm = self.direccion_repo.crear_con_jerarquia(profesional.ubicacion)
            direccion_id = direccion_orm.id
        
        # Paso 3: Crear ProfesionalORM
        orm = ProfesionalORM(
            usuario_id=usuario_id,
            direccion_id=direccion_id,
            activo=profesional.activo,
            verificado=profesional.verificado,
            matricula=""  # Campo legacy
        )
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        
        return self._to_domain(orm)
    
    def actualizar(self, profesional: Profesional, direccion_id: Optional[UUID] = None) -> Profesional:
        """
        Actualiza un profesional existente
        
        Args:
            profesional: Entidad de dominio con los nuevos datos
            direccion_id: (Opcional) Nueva dirección existente. 
                         Si no se proporciona pero profesional.ubicacion cambió,
                         se crea automáticamente.
        
        Example:
            # Opción 1: Mantener dirección actual
            profesional.email = "nuevo@email.com"
            prof_repo.actualizar(profesional)
            
            # Opción 2: Cambiar a dirección existente
            prof_repo.actualizar(profesional, direccion_id=nueva_direccion_id)
            
            # Opción 3: Cambiar ubicación (crea dirección automáticamente)
            profesional.ubicacion = Ubicacion(...)
            prof_repo.actualizar(profesional)  # Crea nueva dirección
        """
        # Obtener el ORM existente
        orm = self.session.query(ProfesionalORM).filter(
            ProfesionalORM.id == profesional.id
        ).first()
        
        if not orm:
            raise ValueError(f"Profesional con id {profesional.id} no encontrado")
        
        # Actualizar campos del usuario
        orm.usuario.nombre = profesional.nombre
        orm.usuario.apellido = profesional.apellido
        orm.usuario.email = profesional.email
        orm.usuario.celular = profesional.celular
        orm.usuario.activo = profesional.activo
        
        # Actualizar campos del profesional
        orm.activo = profesional.activo
        orm.verificado = profesional.verificado
        
        # Manejar actualización de dirección
        if direccion_id:
            # Dirección explícita proporcionada
            orm.direccion_id = direccion_id
        elif profesional.ubicacion:
            # Verificar si la ubicación cambió
            ubicacion_actual = self.direccion_repo._to_domain(orm.direccion) if orm.direccion else None
            
            if ubicacion_actual != profesional.ubicacion:
                # La ubicación cambió, crear nueva dirección
                nueva_direccion = self.direccion_repo.crear_con_jerarquia(profesional.ubicacion)
                orm.direccion_id = nueva_direccion.id
        
        self.session.commit()
        self.session.refresh(orm)
        
        return self._to_domain(orm)
    
    def eliminar(self, id: UUID) -> bool:
        """Elimina físicamente un profesional (NO RECOMENDADO)"""
        orm = self.session.query(ProfesionalORM).filter(
            ProfesionalORM.id == str(id)
        ).first()
        
        if not orm:
            return False
        
        self.session.delete(orm)
        self.session.commit()
        
        return True
    
    def desactivar(self, id: UUID) -> Optional[Profesional]:
        """Desactivación lógica (RECOMENDADO)"""
        orm = self.session.query(ProfesionalORM).filter(
            ProfesionalORM.id == str(id)
        ).first()
        
        if not orm:
            return None
        
        orm.activo = False
        self.session.commit()
        self.session.refresh(orm)
        
        return self._to_domain(orm)
    
    def buscar_por_especialidad(self, especialidad_nombre: str) -> List[Profesional]:
        """Busca profesionales por nombre de especialidad"""
        orms = self.session.query(ProfesionalORM).join(
            ProfesionalORM.especialidades
        ).filter(
            EspecialidadORM.nombre.ilike(f"%{especialidad_nombre}%"),
            ProfesionalORM.activo == True
        ).all()
        
        return [self._to_domain(orm) for orm in orms]
    
    def buscar_por_ubicacion(
        self, 
        provincia: Optional[str] = None,
        departamento: Optional[str] = None,
        barrio: Optional[str] = None
    ) -> List[Profesional]:
        """
        Busca profesionales por ubicación (provincia, departamento, barrio)
        
        Usa la jerarquía: Direccion → Barrio → Departamento → Provincia
        """
        query = self.session.query(ProfesionalORM).join(
            ProfesionalORM.direccion
        ).filter(
            ProfesionalORM.activo == True
        )
        
        # Aplicar filtros según la jerarquía
        if provincia:
            query = query.join(DireccionORM.barrio).join(BarrioORM.departamento).join(DepartamentoORM.provincia).filter(
                ProvinciaORM.nombre.ilike(f"%{provincia}%")
            )
        if departamento:
            query = query.filter(DepartamentoORM.nombre.ilike(f"%{departamento}%"))
        if barrio:
            query = query.filter(BarrioORM.nombre.ilike(f"%{barrio}%"))
        
        orms = query.all()
        return [self._to_domain(orm) for orm in orms]
    
    def buscar_combinado(
        self,
        especialidad_nombre: Optional[str] = None,
        provincia: Optional[str] = None,
        departamento: Optional[str] = None,
        barrio: Optional[str] = None
    ) -> List[Profesional]:
        """
        Busca profesionales por ubicación y/o especialidad
        Mantiene la misma firma y estilo que los otros métodos
        """
        query = self.session.query(ProfesionalORM).join(
            ProfesionalORM.direccion
        ).outerjoin(
            ProfesionalORM.especialidades
        ).filter(
            ProfesionalORM.activo == True
        )

        # Ubicación
        if provincia:
            query = query.join(DireccionORM.barrio).join(BarrioORM.departamento).join(DepartamentoORM.provincia).filter(
                ProvinciaORM.nombre.ilike(f"%{provincia}%")
            )
        if departamento:
            query = query.join(DireccionORM.barrio).join(BarrioORM.departamento).filter(
                DepartamentoORM.nombre.ilike(f"%{departamento}%")
            )
        if barrio:
            query = query.join(DireccionORM.barrio).filter(
                BarrioORM.nombre.ilike(f"%{barrio}%")
            )

        # Especialidad
        if especialidad_nombre:
            query = query.filter(EspecialidadORM.nombre.ilike(f"%{especialidad_nombre}%"))

        orms = query.all()
        return [self._to_domain(orm) for orm in orms]

    
    def verificar(self, id: UUID) -> Optional[Profesional]:
        """Marca un profesional como verificado"""
        orm = self.session.query(ProfesionalORM).filter(
            ProfesionalORM.id == str(id)
        ).first()
        
        if not orm:
            return None
        
        orm.verificado = True
        self.session.commit()
        self.session.refresh(orm)
        
        return self._to_domain(orm)
    
    def contar_profesionales(
        self, 
        solo_activos: bool = False,
        solo_verificados: bool = False
    ) -> int:
        """Cuenta profesionales con filtros opcionales"""
        query = self.session.query(ProfesionalORM)
        
        if solo_activos:
            query = query.filter(ProfesionalORM.activo == True)
        if solo_verificados:
            query = query.filter(ProfesionalORM.verificado == True)
        
        return query.count()