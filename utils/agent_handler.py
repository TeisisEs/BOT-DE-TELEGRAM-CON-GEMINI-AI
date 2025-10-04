"""
LangChain Agent Handler - VERSIÓN MEJORADA Y ROBUSTA
====================================================
Agente inteligente que decide automáticamente qué tool usar
"""

import logging
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

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
            # Modelo Gemini para el agente con configuración optimizada
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=GEMINI_API_KEY,
                temperature=0.3,  # Más bajo para decisiones más consistentes
                convert_system_message_to_human=True
            )
            
            # Prompt mejorado y más específico
            template = """Eres un asistente útil que puede usar herramientas especializadas cuando sea necesario.

Tienes acceso a las siguientes herramientas:

{tools}

REGLAS IMPORTANTES:
1. Si el usuario pide convertir monedas o menciona dinero/divisas, DEBES usar CurrencyConverter
2. Si el usuario pide traducir o menciona idiomas, DEBES usar TextTranslator  
3. Si el usuario pide letras de canciones o menciona artistas/música, DEBES usar LyricsFinder
4. Si no necesitas herramientas, responde directamente
5. SIEMPRE responde en español de forma clara

EJEMPLOS DE CUÁNDO USAR HERRAMIENTAS:
- "convierte 100 dólares a euros" → Usa CurrencyConverter
- "cuánto es 50 USD en MXN" → Usa CurrencyConverter
- "traduce hello al español" → Usa TextTranslator
- "cómo se dice good morning en español" → Usa TextTranslator
- "letra de Bohemian Rhapsody" → Usa LyricsFinder
- "busca la letra de Hey Jude" → Usa LyricsFinder

TRIGGERS DE LENGUAJE NATURAL (usa las tools cuando detectes cualquiera de estos ejemplos):
- Frases de conversión en español: "¿Cuánto son 100 dólares en euros?", "a cuantos dolares equivale 10000 yenes", "cuantos dolares son 5000 pesos mexicanos"
- Frases de conversión en inglés: "how much is 100 USD in EUR", "convert 50 GBP to MXN"
- Frases de traducción en español: "traduce 'how are you' al español", "cómo se dice 'buenos días' en inglés"
- Frases de traducción en inglés: "translate 'buenos días' to english", "how to say 'gracias' in english"

Usa EXACTAMENTE este formato:

Question: la pregunta del usuario
Thought: Pienso en qué hacer. ¿Necesito una herramienta? ¿Cuál?
Action: [nombre de la herramienta: {tool_names}]
Action Input: [entrada para la herramienta]
Observation: [resultado de la herramienta]
... (repite Thought/Action/Action Input/Observation si es necesario)
Thought: Ya tengo la respuesta final
Final Answer: [respuesta completa al usuario]

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
            
            prompt = PromptTemplate(
                input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
                template=template
            )
            
            # Crear agente
            agent = create_react_agent(
                llm=self.llm,
                tools=all_tools,
                prompt=prompt
            )
            
            # Crear AgentExecutor con mejor configuración
            self.agent = AgentExecutor(
                agent=agent,
                tools=all_tools,
                verbose=True,  # Para debugging
                handle_parsing_errors=True,
                max_iterations=4,
                early_stopping_method="generate",
                return_intermediate_steps=False
            )
            
            logger.info("✅ Agente LangChain inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error al inicializar agente: {e}")
            raise
    
    
    def run(self, query: str) -> str:
        """
        Ejecuta el agente con una consulta
        """
        try:
            logger.info(f"🤖 Agente procesando: {query}")
            
            # Ejecutar agente
            response = self.agent.invoke({"input": query})
            
            # Extraer respuesta
            if isinstance(response, dict):
                answer = response.get("output", str(response))
            else:
                answer = str(response)
            
            # Limpiar respuesta
            answer = self._clean_response(answer)
            
            logger.info(f"✅ Respuesta del agente: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Error en agente: {e}", exc_info=True)
            return (
                "Disculpa, tuve un problema al procesar tu solicitud con las herramientas. "
                "¿Podrías reformular tu pregunta o usar el comando directo?"
            )
    
    
    def _clean_response(self, response: str) -> str:
        """
        Limpia la respuesta del agente de artefactos internos
        """
        # Remover artefactos del proceso ReAct
        artifacts = [
            "Thought:", "Action:", "Action Input:", "Observation:", 
            "Final Answer:", "Question:"
        ]
        
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Saltar líneas que son solo artefactos
            if any(line.strip().startswith(artifact) for artifact in artifacts):
                # Si es "Final Answer:", tomar el contenido después
                if line.strip().startswith("Final Answer:"):
                    content = line.replace("Final Answer:", "").strip()
                    if content:
                        cleaned_lines.append(content)
                continue
            cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines).strip()
        
        # Si quedó vacío, usar la respuesta original
        return result if result else response


def should_use_agent(query: str) -> bool:
    """
    Decide si usar el agente o respuesta simple de Gemini
    VERSIÓN MEJORADA con mejor detección
    """
    query_lower = query.lower()
    
    # Palabras clave expandidas y más flexibles
    agent_triggers = {
        # Currency - EXPANDIDO
        'currency': [
            'convertir', 'conversion', 'conversor', 'convierte', 'cuanto',
            'moneda', 'divisa', 'cambio', 'cotizacion', 'dolar', 'euro', 
            'peso', 'libra', 'yen', 'usd', 'eur', 'gbp', 'mxn', 'jpy',
            'currency', 'exchange', 'vale', 'equivale', 'dolares', 'euros'
        ],
        
        # Translation - EXPANDIDO  
        'translation': [
            'traducir', 'traductor', 'traduce', 'traduccion',
            'translate', 'como se dice', 'que significa', 'en ingles',
            'en español', 'al ingles', 'al español', 'en frances',
            'en aleman', 'how to say', 'what does', 'mean in'
        ],
        
        # Lyrics - EXPANDIDO
        'lyrics': [
            'letra', 'letras', 'cancion', 'song', 'lyrics', 'musica',
            'artista', 'tema', 'busca letra', 'encuentra letra',
            'banda', 'cantante', 'interpreta', 'canta', 'album'
        ]
    }
    
    # Verificar si alguna categoría tiene coincidencias
    for category, keywords in agent_triggers.items():
        matches = sum(1 for keyword in keywords if keyword in query_lower)
        if matches > 0:
            logger.info(f"🎯 Detectado: {category} (matches: {matches})")
            return True
    
    # Patrones adicionales (regex-like)
    patterns = [
        ('cuánto es', 'en'),  # "cuánto es X en Y"
        ('cuanto vale', ''),
        ('precio de', 'en'),
        ('how much', 'in'),
        ('what is', 'in'),
    ]
    
    for pattern in patterns:
        if all(p in query_lower for p in pattern if p):
            logger.info(f"🎯 Detectado patrón: {pattern}")
            return True
    
    logger.info("💭 No se detectó necesidad de tools - usando Gemini directo")
    return False


# Crear instancia global
try:
    intelligent_agent = IntelligentAgent()
    logger.info("🎯 Agente inteligente listo para usar")
except Exception as e:
    logger.error(f"❌ No se pudo inicializar el agente: {e}")
    intelligent_agent = None


if __name__ == "__main__":
    # Testing mejorado
    if intelligent_agent:
        print("=" * 60)
        print("🧪 TESTING LANGCHAIN AGENT - VERSIÓN MEJORADA")
        print("=" * 60)
        
        tests = [
            "convierte 100 dólares a euros",
            "cuánto es 50 USD en pesos mexicanos",
            "traduce 'hello world' al español",
            "cómo se dice 'buenos días' en inglés",
            "letra de Hey Jude de The Beatles",
        ]
        
        for i, test_query in enumerate(tests, 1):
            print(f"\n📊 Test {i}: {test_query}")
            print(f"Usar agente: {should_use_agent(test_query)}")
            try:
                response = intelligent_agent.run(test_query)
                print(f"Respuesta: {response[:200]}...")
            except Exception as e:
                print(f"Error: {e}")
            print("-" * 60)
        
        print("\n✅ Testing completado")