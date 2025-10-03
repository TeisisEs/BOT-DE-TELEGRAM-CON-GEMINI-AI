"""
LangChain Agent Handler - VERSIÓN CORREGIDA
===========================================
Agente inteligente que decide automáticamente qué tool usar
"""

import logging
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
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
            
            # Obtener prompt de ReAct desde hub
            try:
                prompt = hub.pull("hwchase17/react")
            except Exception as e:
                logger.warning(f"No se pudo cargar prompt del hub: {e}")
                # Crear prompt simple manualmente
                from langchain.prompts import PromptTemplate
                
                template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

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
            
            # Crear AgentExecutor
            self.agent = AgentExecutor(
                agent=agent,
                tools=all_tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=3,
                early_stopping_method="generate"
            )
            
            logger.info("✅ Agente LangChain inicializado con 3 tools")
            
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
            
            logger.info(f"✅ Agente respondió: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Error en agente: {e}")
            return (
                "Disculpa, tuve un problema al procesar tu solicitud. "
                "¿Podrías reformular tu pregunta?"
            )


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
        
        # Translator
        'traducir', 'traducción', 'traductor', 'translate', 'translation',
        'en ingles', 'en español', 'al ingles', 'al español', 'en frances',
        'cómo se dice', 'como se dice', 'traduce',
        
        # Lyrics
        'letra', 'letras', 'cancion', 'canción', 'song', 'lyrics', 'lyric',
        'musica', 'música', 'artista', 'banda', 'busca letra', 'quiero letra'
    ]
    
    return any(keyword in query_lower for keyword in agent_keywords)


# Crear instancia global
try:
    intelligent_agent = IntelligentAgent()
    logger.info("🎯 Agente inteligente listo")
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
        print("\n📝 Test 1: Conversión de monedas")
        response = intelligent_agent.run("convierte 100 dólares a euros")
        print(f"Respuesta: {response[:200]}...\n")
        
        print("=" * 60)
        print("✅ Testing completado")
        print("=" * 60)