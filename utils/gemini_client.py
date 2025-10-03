import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from typing import List, Dict

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Cliente mejorado para interactuar con Google Gemini AI
    Incluye manejo de contexto y prevención de respuestas repetitivas
    """
    
    def __init__(self):
        """
        Inicializa el cliente de Gemini AI con configuración optimizada
        """
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=GEMINI_API_KEY,
                temperature=0.8,  # Mayor creatividad para evitar repeticiones
                top_p=0.95,  # Diversidad en las respuestas
                top_k=40,  # Mayor variedad de tokens
                convert_system_message_to_human=True
            )
            logger.info("✅ Cliente Gemini AI inicializado con configuración optimizada")
        except Exception as e:
            logger.error(f"❌ Error al inicializar Gemini AI: {e}")
            raise
    
    
    def get_response_with_context(
        self, 
        user_message: str, 
        conversation_history: List[dict] = None,
        user_name: str = "Usuario"
    ) -> str:
        """
        Obtiene respuesta considerando el historial de conversación
        
        Args:
            user_message: Mensaje actual del usuario
            conversation_history: Lista de mensajes previos [{'role': 'user'/'assistant', 'content': '...'}]
            user_name: Nombre del usuario para personalización
        
        Returns:
            Respuesta generada por Gemini AI
        """
        try:
            messages = []
            
            # Sistema: Personalidad del bot (mejorada)
            system_prompt = f"""
Eres un asistente inteligente y versátil en un bot de Telegram.

PERSONALIDAD:
- Amigable pero profesional
- Respuestas claras y estructuradas
- Evitas ser repetitivo o predecible
- Adaptas tu tono según el contexto
- Usas emojis con moderación (1-2 por respuesta)
- Respuestas concisas: máximo 3-4 párrafos

ESTILO DE COMUNICACIÓN:
- Si el usuario hace preguntas similares, ofreces perspectivas diferentes
- Evitas frases clichés como "¡Claro!" o "¡Por supuesto!" al inicio
- Vas directo al punto sin introducciones innecesarias
- Usas formato Markdown cuando ayuda a la claridad
- Si no sabes algo, lo admites honestamente

CONTEXTO:
- Usuario: {user_name}
- Plataforma: Telegram
- Idioma: Español

Mantén el contexto de la conversación pero no repitas información ya mencionada.
"""
            
            messages.append(SystemMessage(content=system_prompt))
            
            # Agregar historial de conversación (últimos mensajes)
            if conversation_history:
                # Limitar a los últimos 6 mensajes para no sobrecargar el contexto
                recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
                
                for msg in recent_history:
                    if msg['role'] == 'user':
                        messages.append(HumanMessage(content=msg['content']))
                    elif msg['role'] == 'assistant':
                        messages.append(AIMessage(content=msg['content']))
            
            # Agregar mensaje actual
            messages.append(HumanMessage(content=user_message))
            
            # Obtener respuesta
            logger.info(f"📤 Enviando a Gemini con {len(messages)} mensajes de contexto")
            response = self.llm.invoke(messages)
            
            response_text = response.content.strip()
            logger.info(f"📥 Respuesta: {response_text[:80]}...")
            
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error al obtener respuesta: {e}")
            return self._get_error_response()
    
    
    def get_response(self, user_message: str, context: str = None) -> str:
        """
        Método simple para compatibilidad con código existente
        """
        return self.get_response_with_context(user_message, None, context or "Usuario")
    
    
    def get_simple_response(self, prompt: str) -> str:
        """
        Respuesta simple sin contexto (para comandos específicos)
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"❌ Error en respuesta simple: {e}")
            return self._get_error_response()
    
    
    def _get_error_response(self) -> str:
        """
        Genera respuesta de error amigable
        """
        error_responses = [
            "Disculpa, tuve un problema al procesar tu mensaje. ¿Podrías intentarlo de nuevo?",
            "Lo siento, hubo un error temporal. Por favor intenta nuevamente.",
            "Ups, algo no salió bien. ¿Podrías reformular tu pregunta?",
        ]
        
        import random
        return random.choice(error_responses)


# Crear instancia global
try:
    gemini_client = GeminiClient()
    logger.info("🎯 Cliente Gemini listo con manejo de contexto")
except Exception as e:
    logger.error(f"❌ No se pudo inicializar Gemini: {e}")
    gemini_client = None