"""
LangChain Agent Handler - VERSIÓN MEJORADA
===========================================
Agente inteligente que decide automáticamente qué tool usar
"""

import logging
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain import hub

from config import GEMINI_API_KEY
from utils.tools import all_tools

logger = logging.getLogger(__name__)


class IntelligentAgent:
    """
    Agente LangChain que usa Tools automáticamente
    """
    
    def __init__(self):
        """
        Inicializa el agente con Gemini AI y todas las tools
        """
        try:
            # Modelo Gemini para el agente
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=GEMINI_API_KEY,
                temperature=0.7,
                convert_system_message_to_human=True
            )
            
            # Crear prompt personalizado más robusto
            template = """Eres un asistente útil que tiene acceso a las siguientes herramientas:

{tools}

Usa el siguiente formato:

Question: la pregunta que debes responder
Thought: siempre debes pensar qué hacer
Action: la acción a tomar, debe ser una de [{tool_names}]
Action Input: la entrada para la acción
Observation: el resultado de la acción
... (este proceso Thought/Action/Action Input/Observation puede repetirse N veces)
Thought: ahora sé la respuesta final
Final Answer: la respuesta final a la pregunta original

IMPORTANTE:
- Si la pregunta requiere convertir monedas, usa CurrencyConverter
- Si requiere traducción, usa TextTranslator
- Si requiere letra de canción, usa LyricsFinder
- Responde en español de forma clara y amigable
- Si no necesitas herramientas, responde directamente

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
            
            prompt = PromptTemplate(
                input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
                template=template
            )
            
            # Crear agente con create_react_agent
            agent = create_react_agent(
                llm=self.llm,
                tools=all_tools,
                prompt=prompt
            )
            
            # Crear AgentExecutor con configuración optimizada
            self.agent = AgentExecutor(
                agent=agent,
                tools=all_tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,  # Aumentado para mayor flexibilidad
                early_stopping_method="generate",
                return_intermediate_steps=False  # Para respuestas más limpias
            )
            
            logger.info("✅ Agente LangChain inicializado correctamente con 3 tools")
            
        except Exception as e:
            logger.error(f"❌ Error al inicializar agente: {e}")
            raise
    
    
    def run(self, query: str) -> str:
        """
        Ejecuta el agente con una consulta
        
        Args:
            query: Consulta del usuario
            
        Returns:
            Respuesta del agente
        """
        try:
            logger.info(f"🤖 Agente procesando: {query[:100]}")
            
            # Ejecutar agente
            response = self.agent.invoke({"input": query})
            
            # Extraer respuesta
            if isinstance(response, dict):
                answer = response.get("output", str(response))
            else:
                answer = str(response)
            
            # Limpiar respuesta de artefactos del agente
            answer = self._clean_response(answer)
            
            logger.info(f"✅ Agente respondió: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Error en agente: {e}")
            return (
                "Disculpa, tuve un problema al procesar tu solicitud. "
                "¿Podrías reformular tu pregunta?"
            )
    
    
    def _clean_response(self, response: str) -> str:
        """
        Limpia la respuesta del agente de artefactos internos
        """
        # Remover posibles artefactos del proceso ReAct
        artifacts = ["Thought:", "Action:", "Action Input:", "Observation:", "Final Answer:"]
        
        for artifact in artifacts:
            if artifact in response:
                # Tomar solo la parte después del último artifact
                response = response.split(artifact)[-1].strip()
        
        return response


# ==================================================
# FUNCIÓN PARA DETECTAR SI USAR AGENTE O GEMINI
# ==================================================

def should_use_agent(query: str) -> bool:
    """
    Decide si usar el agente o respuesta simple de Gemini
    
    Args:
        query: Consulta del usuario
        
    Returns:
        True si debe usar el agente, False para respuesta simple
    """
    query_lower = query.lower()
    
    # Palabras clave que indican uso de tools
    agent_keywords = [
        # Currency
        'convertir', 'conversion', 'conversor', 'moneda', 'dolar', 'euro', 'peso',
        'usd', 'eur', 'gbp', 'mxn', 'currency', 'convert', 'cuanto es', 'cuánto es',
        'cambio', 'divisa', 'cotizacion', 'cotización',
        
        # Translator
        'traducir', 'traducción', 'traductor', 'translate', 'translation',
        'en ingles', 'en español', 'al ingles', 'al español', 'en frances',
        'cómo se dice', 'como se dice', 'traduce', 'en inglés',
        
        # Lyrics
        'letra', 'letras', 'cancion', 'canción', 'song', 'lyrics', 'lyric',
        'musica', 'música', 'artista', 'banda', 'busca letra', 'quiero letra',
        'tema de', 'tema musical'
    ]
    
    return any(keyword in query_lower for keyword in agent_keywords)


# Crear instancia global
try:
    intelligent_agent = IntelligentAgent()
    logger.info("🎯 Agente inteligente listo para usar")
except Exception as e:
    logger.error(f"❌ No se pudo inicializar el agente: {e}")
    intelligent_agent = None


if __name__ == "__main__":
    # Testing del agente
    if intelligent_agent:
        print("=" * 60)
        print("🧪 TESTING LANGCHAIN AGENT")
        print("=" * 60)
        
        # Test 1: Currency conversion
        print("\n📊 Test 1: Conversión de monedas")
        response = intelligent_agent.run("convierte 100 dólares a euros")
        print(f"Respuesta: {response}\n")
        
        # Test 2: Translation
        print("📊 Test 2: Traducción")
        response = intelligent_agent.run("traduce 'hello world' al español")
        print(f"Respuesta: {response}\n")
        
        # Test 3: Lyrics (si la API responde)
        print("📊 Test 3: Letra de canción")
        response = intelligent_agent.run("letra de Hey Jude de The Beatles")
        print(f"Respuesta: {response[:200]}...\n")
        
        print("=" * 60)
        print("✅ Testing completado")
        print("=" * 60)