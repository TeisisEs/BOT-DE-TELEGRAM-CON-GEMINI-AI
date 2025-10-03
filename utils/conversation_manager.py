import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Gestiona el historial de conversaciones por usuario
    Mantiene contexto y evita respuestas repetitivas
    """
    
    def __init__(self, max_history: int = 10, timeout_minutes: int = 30):
        """
        Inicializa el gestor de conversaciones
        
        Args:
            max_history: Número máximo de mensajes a recordar por usuario
            timeout_minutes: Minutos antes de limpiar conversación inactiva
        """
        self.conversations: Dict[int, List[dict]] = defaultdict(list)
        self.last_activity: Dict[int, datetime] = {}
        self.max_history = max_history
        self.timeout = timedelta(minutes=timeout_minutes)
        
        logger.info(f"✅ ConversationManager inicializado (historial: {max_history}, timeout: {timeout_minutes}min)")
    
    
    def add_message(self, user_id: int, role: str, content: str):
        """
        Agrega un mensaje al historial del usuario
        
        Args:
            user_id: ID del usuario
            role: 'user' o 'assistant'
            content: Contenido del mensaje
        """
        # Limpiar conversaciones antiguas
        self._cleanup_old_conversations()
        
        # Agregar mensaje
        self.conversations[user_id].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        })
        
        # Limitar tamaño del historial
        if len(self.conversations[user_id]) > self.max_history * 2:
            # Mantener solo los últimos max_history pares (user + assistant)
            self.conversations[user_id] = self.conversations[user_id][-(self.max_history * 2):]
        
        # Actualizar última actividad
        self.last_activity[user_id] = datetime.now()
        
        logger.debug(f"Mensaje agregado para usuario {user_id} (total: {len(self.conversations[user_id])})")
    
    
    def get_history(self, user_id: int, limit: int = None) -> List[dict]:
        """
        Obtiene el historial de conversación del usuario
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de mensajes a devolver (None = todos)
        
        Returns:
            Lista de mensajes del historial
        """
        history = self.conversations.get(user_id, [])
        
        if limit:
            return history[-limit:]
        return history
    
    
    def get_context_summary(self, user_id: int, last_n: int = 4) -> str:
        """
        Genera un resumen del contexto reciente de la conversación
        
        Args:
            user_id: ID del usuario
            last_n: Número de mensajes recientes a incluir
        
        Returns:
            Resumen del contexto como string
        """
        history = self.get_history(user_id, limit=last_n)
        
        if not history:
            return ""
        
        # Crear resumen compacto
        context_parts = []
        for msg in history:
            role = "Usuario" if msg['role'] == 'user' else "Asistente"
            content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            context_parts.append(f"{role}: {content_preview}")
        
        return "\n".join(context_parts)
    
    
    def clear_history(self, user_id: int):
        """
        Limpia el historial de un usuario específico
        
        Args:
            user_id: ID del usuario
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"Historial limpiado para usuario {user_id}")
    
    
    def has_recent_activity(self, user_id: int) -> bool:
        """
        Verifica si el usuario tiene actividad reciente
        
        Args:
            user_id: ID del usuario
        
        Returns:
            True si hay actividad reciente, False si no
        """
        if user_id not in self.last_activity:
            return False
        
        time_since_last = datetime.now() - self.last_activity[user_id]
        return time_since_last < self.timeout
    
    
    def _cleanup_old_conversations(self):
        """
        Limpia conversaciones inactivas para liberar memoria
        """
        current_time = datetime.now()
        users_to_remove = []
        
        for user_id, last_time in self.last_activity.items():
            if current_time - last_time > self.timeout:
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            self.clear_history(user_id)
            del self.last_activity[user_id]
            logger.info(f"Conversación expirada limpiada para usuario {user_id}")
    
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas del gestor de conversaciones
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'active_users': len(self.conversations),
            'total_messages': sum(len(conv) for conv in self.conversations.values()),
            'average_messages_per_user': (
                sum(len(conv) for conv in self.conversations.values()) / len(self.conversations)
                if self.conversations else 0
            )
        }


# Crear instancia global
conversation_manager = ConversationManager(
    max_history=10,  # Recordar últimos 10 intercambios
    timeout_minutes=30  # Limpiar después de 30 minutos de inactividad
)