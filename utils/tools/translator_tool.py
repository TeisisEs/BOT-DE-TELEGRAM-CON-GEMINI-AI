import logging
import requests
from typing import Optional
from langchain.tools import Tool

logger = logging.getLogger(__name__)


class Translator:
    """
    Traductor usando MyMemory Translation API
    API: mymemory.translated.net (gratuita, sin key necesaria)
    Límite: 1000 caracteres por request, 5000 requests/día
    """
    
    def __init__(self):
        # API pública gratuita más estable
        self.base_url = "https://api.mymemory.translated.net/get"
        
        # Códigos de idiomas soportados
        self.languages = {
            'es': 'Español',
            'en': 'English',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어',
            'ar': 'العربية',
            'hi': 'हिन्दी',
            'nl': 'Nederlands',
            'pl': 'Polski',
            'tr': 'Türkçe',
            'sv': 'Svenska',
            'da': 'Dansk',
            'fi': 'Suomi',
            'no': 'Norsk',
            'cs': 'Čeština',
        }
        
        # Emojis de banderas por idioma
        self.flags = {
            'es': '🇪🇸', 'en': '🇺🇸', 'fr': '🇫🇷', 'de': '🇩🇪',
            'it': '🇮🇹', 'pt': '🇵🇹', 'ru': '🇷🇺', 'zh': '🇨🇳',
            'ja': '🇯🇵', 'ko': '🇰🇷', 'ar': '🇸🇦', 'hi': '🇮🇳',
            'nl': '🇳🇱', 'pl': '🇵🇱', 'tr': '🇹🇷'
        }
        
        logger.info("✅ Translator inicializado (MyMemory API)")
    
    
    def translate(self, text: str, source_lang: str = 'auto', target_lang: str = 'es') -> dict:
        """
        Traduce texto de un idioma a otro
        
        Args:
            text: Texto a traducir
            source_lang: Código de idioma origen ('auto' para detectar)
            target_lang: Código de idioma destino (ej: 'es', 'en')
            
        Returns:
            Diccionario con resultado o error
        """
        try:
            # Normalizar códigos
            source_lang = source_lang.lower().strip()
            target_lang = target_lang.lower().strip()
            
            # Validar longitud del texto
            if len(text) > 1000:
                return {'error': 'Texto demasiado largo. Máximo 1000 caracteres.'}
            
            if not text.strip():
                return {'error': 'El texto está vacío.'}
            
            # Si es auto, intentar detectar idioma básico
            if source_lang == 'auto':
                # Detección simple: si tiene caracteres latinos españoles, es español
                tiene_espanol = any(c in text.lower() for c in ['á', 'é', 'í', 'ó', 'ú', 'ñ', '¿', '¡'])
                palabras_espanol = ['hola', 'buenos', 'gracias', 'por', 'favor', 'que', 'como']
                es_espanol = tiene_espanol or any(palabra in text.lower() for palabra in palabras_espanol)
                
                source_lang = 'es' if es_espanol else 'en'
            
            logger.info(f"🌐 Traduciendo de '{source_lang}' a '{target_lang}'")
            
            # Preparar parámetros para MyMemory API
            params = {
                'q': text,
                'langpair': f"{source_lang}|{target_lang}"
            }
            
            # Hacer request a la API
            response = requests.get(
                self.base_url,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Verificar respuesta
            if data.get('responseStatus') == 200 or 'responseData' in data:
                translated_text = data['responseData']['translatedText']
                
                # Verificar que no sea el mismo texto (traducción fallida)
                if translated_text.lower() == text.lower():
                    return {'error': 'No se pudo traducir. Verifica los idiomas.'}
                
                result = {
                    'original': text,
                    'translated': translated_text,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'source_name': self.languages.get(source_lang, source_lang),
                    'target_name': self.languages.get(target_lang, target_lang),
                    'source_flag': self.flags.get(source_lang, '🌐'),
                    'target_flag': self.flags.get(target_lang, '🌐')
                }
                
                logger.info(f"✅ Traducción exitosa: {len(text)} → {len(translated_text)} caracteres")
                return result
            else:
                error_msg = data.get('responseDetails', 'Error desconocido')
                return {'error': f'Error de traducción: {error_msg}'}
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Error HTTP en traducción: {e}")
            return {'error': f'Error del servidor: {response.status_code}'}
            
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout en API de traducción")
            return {'error': 'Tiempo de espera agotado. Intenta con texto más corto.'}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de conexión: {e}")
            return {'error': 'Error de conexión con el servicio de traducción'}
            
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return {'error': f'Error al traducir: {str(e)}'}
    
    
    def format_result(self, result: dict) -> str:
        """
        Formatea el resultado de traducción
        
        Args:
            result: Diccionario con datos de traducción
            
        Returns:
            Mensaje formateado
        """
        if 'error' in result:
            return f"❌ {result['error']}"
        
        # Limitar preview de texto original si es muy largo
        original_preview = result['original']
        if len(original_preview) > 200:
            original_preview = original_preview[:200] + '...'
        
        message = f"""
🌐 **TRADUCCIÓN**

{result['source_flag']} **{result['source_name']}:**
_{original_preview}_

{result['target_flag']} **{result['target_name']}:**
**{result['translated']}**

_Traducción automática - MyMemory_
        """
        
        return message.strip()
    
    
    def get_supported_languages(self) -> str:
        """
        Retorna lista de idiomas soportados
        """
        langs_list = "\n".join([
            f"{self.flags.get(code, '🌐')} **{code.upper()}** - {name}"
            for code, name in sorted(self.languages.items(), key=lambda x: x[1])
        ])
        
        message = f"""
🌐 **IDIOMAS SOPORTADOS**

{langs_list}

**Uso:** Usa los códigos (ej: 'en', 'es', 'fr')
**Límite:** 1000 caracteres por traducción
        """
        
        return message.strip()


# ============================================
# CREAR LANGCHAIN TOOL
# ============================================

def translate_text_function(query: str) -> str:
    """
    Función wrapper para usar con LangChain Tool
    
    Formatos aceptados:
    - "translate 'hello' to spanish"
    - "traducir 'how are you' al español"
    - "hello world en español"
    
    Args:
        query: String con la consulta de traducción
        
    Returns:
        Resultado formateado como string
    """
    translator = Translator()
    
    try:
        # Parsear query de manera flexible
        query_lower = query.lower()
        
        # Detectar idioma destino
        target_lang = 'es'  # Default español
        if 'to english' in query_lower or 'al inglés' in query_lower or 'in english' in query_lower:
            target_lang = 'en'
        elif 'to spanish' in query_lower or 'al español' in query_lower or 'en español' in query_lower:
            target_lang = 'es'
        elif 'to french' in query_lower or 'al francés' in query_lower or 'en francés' in query_lower:
            target_lang = 'fr'
        elif 'to german' in query_lower or 'al alemán' in query_lower or 'en alemán' in query_lower:
            target_lang = 'de'
        elif 'to portuguese' in query_lower or 'al portugués' in query_lower:
            target_lang = 'pt'
        elif 'to italian' in query_lower or 'al italiano' in query_lower:
            target_lang = 'it'
        
        # Extraer el texto a traducir
        text_to_translate = query
        
        # Intentar extraer texto entre comillas
        if "'" in query:
            parts = query.split("'")
            if len(parts) >= 2:
                text_to_translate = parts[1]
        elif '"' in query:
            parts = query.split('"')
            if len(parts) >= 2:
                text_to_translate = parts[1]
        else:
            # Remover palabras clave comunes
            keywords = ['translate', 'traducir', 'traduce', 'to', 'al', 'en', 'in', 
                       'english', 'spanish', 'español', 'inglés', 'french', 'francés']
            text_to_translate = query
            for keyword in keywords:
                text_to_translate = text_to_translate.replace(keyword, '')
            text_to_translate = text_to_translate.strip()
        
        if not text_to_translate or len(text_to_translate) < 2:
            return "❌ No se encontró texto para traducir. Ejemplo: 'translate \"hello\" to spanish'"
        
        # Realizar traducción
        result = translator.translate(text_to_translate, 'auto', target_lang)
        return translator.format_result(result)
        
    except Exception as e:
        logger.error(f"Error en translate_text_function: {e}")
        return f"❌ Error al procesar traducción: {str(e)}"


# Crear la Tool de LangChain
translator_tool = Tool(
    name="TextTranslator",
    description=(
        "Traduce texto entre diferentes idiomas usando detección automática. "
        "Formato: 'translate \"texto\" to [language]' o 'texto en [idioma]'. "
        "Idiomas soportados: español (es), inglés (en), francés (fr), alemán (de), "
        "italiano (it), portugués (pt), y más. "
        "Detecta automáticamente el idioma origen. Máximo 1000 caracteres. "
        "Útil para comunicación multilingüe y comprensión de textos en otros idiomas."
    ),
    func=translate_text_function
)


# Instancia global para uso directo
translator = Translator()


if __name__ == "__main__":
    # Testing
    trans = Translator()
    
    # Prueba 1: Inglés a Español
    print("Prueba 1: Inglés → Español")
    result = trans.translate("Hello, how are you?", "en", "es")
    print(trans.format_result(result))
    print("\n" + "="*50 + "\n")
    
    # Prueba 2: Español a Inglés
    print("Prueba 2: Español → Inglés")
    result = trans.translate("¿Cómo está el clima hoy?", "es", "en")
    print(trans.format_result(result))
    print("\n" + "="*50 + "\n")
    
    # Prueba 3: Auto-detectar
    print("Prueba 3: Auto-detectar → Francés")
    result = trans.translate("I love programming", "auto", "fr")
    print(trans.format_result(result))
    print("\n" + "="*50 + "\n")
    
    # Prueba 4: Usando la tool
    print("Testing LangChain Tool:")
    print(translate_text_function("translate 'good morning' to spanish"))