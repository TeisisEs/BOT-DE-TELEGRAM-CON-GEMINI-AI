import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from config import GEMINI_API_KEY

# Configurar logging
logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Cliente para interactuar con Google Gemini AI usando LangChain
    """
    
    def __init__(self):
        """
        Inicializa el cliente de Gemini AI
        """
        try:
            # Crear instancia de ChatGoogleGenerativeAI con LangChain
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",  # Modelo Gemini
                google_api_key=GEMINI_API_KEY,
                temperature=0.7,  # Creatividad (0 = conservador, 1 = muy creativo)
                convert_system_message_to_human=True  # Compatibilidad con Gemini
            )
            logger.info("✅ Cliente Gemini AI inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error al inicializar Gemini AI: {e}")
            raise
    
    
    def get_response(self, user_message: str, context: str = None) -> str:
        """
        Obtiene una respuesta de Gemini AI para el mensaje del usuario
        
        Args:
            user_message: Mensaje del usuario
            context: Contexto adicional (opcional)
        
        Returns:
            Respuesta generada por Gemini AI
        """
        try:
            # Crear mensajes para LangChain
            messages = []
            
            # Mensaje del sistema (personalidad del bot)
            system_prompt = """
            Eres un asistente inteligente y amigable de un bot de Telegram.
            
            Características:
            - Respondes de manera clara y concisa
            - Eres educado y profesional
            - Si no sabes algo, lo admites honestamente
            - Usas emojis ocasionalmente para ser más amigable
            - Mantienes respuestas de máximo 3-4 párrafos
            - Hablas en español
            
            Tu objetivo es ayudar al usuario de la mejor manera posible.
            """
            
            messages.append(SystemMessage(content=system_prompt))
            
            # Agregar contexto si existe
            if context:
                messages.append(HumanMessage(content=f"Contexto: {context}"))
            
            # Agregar mensaje del usuario
            messages.append(HumanMessage(content=user_message))
            
            # Obtener respuesta de Gemini
            logger.info(f"📤 Enviando mensaje a Gemini: {user_message[:50]}...")
            response = self.llm.invoke(messages)
            
            # Extraer contenido de la respuesta
            response_text = response.content
            logger.info(f"📥 Respuesta recibida de Gemini: {response_text[:50]}...")
            
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error al obtener respuesta de Gemini: {e}")
            return "Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo."
    
    
    def get_simple_response(self, prompt: str) -> str:
        """
        Obtiene una respuesta simple sin contexto adicional
        
        Args:
            prompt: Pregunta o prompt para Gemini
        
        Returns:
            Respuesta de Gemini
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"❌ Error en respuesta simple: {e}")
            return "Error al procesar la solicitud."


# Crear instancia global del cliente
try:
    gemini_client = GeminiClient()
except Exception as e:
    logger.error(f"❌ No se pudo inicializar el cliente de Gemini: {e}")
    gemini_client = None