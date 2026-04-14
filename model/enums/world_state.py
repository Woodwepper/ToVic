from enum import Enum

class WorldState(Enum):
    """Estados posibles del mundo durante su ciclo de vida"""
    DRAFT = "draft"              # Siendo configurado en web (editable)
    READY = "ready"              # Validado, listo para iniciar (editables definiciones solo)
    RUNNING = "running"          # Gameloop activo (NO ediciones, congelado)
    PAUSED = "paused"            # Pausado temporalmente (NO ediciones, puede resumir)
    FINISHED = "finished"        # Juego terminó (histórico, solo lectura)
    ARCHIVED = "archived"        # Archivo permanente (histórico)
    
    def is_editable(self) -> bool:
        """Verifica si el mundo está en estado editable"""
        return self == WorldState.DRAFT
    
    def is_playable(self) -> bool:
        """Verifica si el mundo está en estado de juego"""
        return self in (WorldState.RUNNING, WorldState.PAUSED)
    
    def is_active(self) -> bool:
        """Verifica si el mundo tiene gameplay activo"""
        return self == WorldState.RUNNING
    
    def is_historical(self) -> bool:
        """Verifica si el mundo es solo para lectura (terminado/archivado)"""
        return self in (WorldState.FINISHED, WorldState.ARCHIVED)