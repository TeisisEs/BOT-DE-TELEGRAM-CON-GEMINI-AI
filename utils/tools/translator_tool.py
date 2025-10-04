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
            
            # Si es auto, intentar detectar idioma con heurística más amplia
            if source_lang == 'auto':
                source_lang = self.detect_language(text)
            
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

            # Verificar respuesta de MyMemory
            if data.get('responseStatus') == 200 and 'responseData' in data:
                translated_text = data['responseData']['translatedText']

                # Si MyMemory devuelve exactamente el mismo texto, intentar fallback
                if translated_text.strip().lower() == text.strip().lower():
                    logger.info("ℹ️ MyMemory devolvió mismo texto; intentando fallback LibreTranslate")
                    fb = self.translate_libre(text, source_lang, target_lang)
                    if 'error' not in fb:
                        fb['used_fallback'] = 'libretranslate'
                        return fb
                    # Intentar googletrans como último recurso
                    gb = self.translate_google(text, source_lang, target_lang)
                    if 'error' not in gb:
                        gb['used_fallback'] = 'googletrans'
                        return gb
                    else:
                        return {'error': 'No se pudo traducir con MyMemory, LibreTranslate ni googletrans.'}

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
                logger.info("⚠️ MyMemory no pudo traducir correctamente; intentando LibreTranslate")
                fb = self.translate_libre(text, source_lang, target_lang)
                if 'error' not in fb:
                    fb['used_fallback'] = 'libretranslate'
                    return fb
                # Intentar googletrans
                gb = self.translate_google(text, source_lang, target_lang)
                if 'error' not in gb:
                    gb['used_fallback'] = 'googletrans'
                    return gb
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


    def detect_language(self, text: str) -> str:
        """
        Heurística simple para detectar idioma de entrada cuando se pide 'auto'.
        No es perfecta pero mejora la detección para varios idiomas comunes.
        """
        t = text.lower()

        # Revisar scripts no-latinos primero
        if any(ord(c) >= 0x0400 and ord(c) <= 0x04FF for c in t):
            return 'ru'  # cirílico -> ruso u otros
        if any('\u4e00' <= c <= '\u9fff' for c in t):
            return 'zh'  # caracteres chinos
        if any('\u3040' <= c <= '\u30ff' for c in t):
            return 'ja'  # japonés
        if any('\u0600' <= c <= '\u06ff' for c in t):
            return 'ar'  # árabe

        # Caracteres y palabras típicas por idioma
        if any(c in t for c in ['ä', 'ö', 'ü', 'ß']):
            return 'de'

        # Palabras comunes por idioma
        german_words = ['ich', 'bin', 'und', 'nicht', 'sie', 'ist', 'der', 'die', 'das', 'ein', 'hallo']
        french_words = ['bonjour', 'merci', 'vous', 'que', 'le', 'la', 'est']
        portuguese_words = ['obrigado', 'por favor', 'bom', 'boa', 'que', 'está']
        italian_words = ['ciao', 'grazie', 'sono', 'mia', 'tu']
        spanish_words = ['hola', 'buenos', 'gracias', 'por', 'favor', 'qué', 'como', '¿', '¡', 'ñ']
        english_words = ['the', 'and', 'is', 'you', 'hello', 'how', 'are']

        # Contar coincidencias
        scores = {
            'de': sum(1 for w in german_words if w in t),
            'fr': sum(1 for w in french_words if w in t),
            'pt': sum(1 for w in portuguese_words if w in t),
            'it': sum(1 for w in italian_words if w in t),
            'es': sum(1 for w in spanish_words if w in t),
            'en': sum(1 for w in english_words if w in t),
        }

        # Elegir el mayor
        best = max(scores.items(), key=lambda x: x[1])
        if best[1] > 0:
            return best[0]

        # Fallback: si contiene tildes o ñ, preferir español
        if any(c in t for c in ['á', 'é', 'í', 'ó', 'ú', 'ñ']):
            return 'es'

        # Por defecto, inglés
        return 'en'

    def translate_libre(self, text: str, source: str, target: str) -> dict:
        """
        Intentar traducir usando LibreTranslate public instance como fallback.
        Nota: puede estar rate-limited. No requiere API key en instancias públicas, pero
        es opcional y se usa sólo si MyMemory falla.
        """
        endpoints = [
            'https://libretranslate.de/translate',
            'https://translate.argosopentech.com/translate',
            'https://libretranslate.com/translate'
        ]
        payload = {
            'q': text,
            'source': source if source != 'auto' else 'auto',
            'target': target,
            'format': 'text'
        }
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        last_err = None
        for url in endpoints:
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=15)
                resp.raise_for_status()
                try:
                    j = resp.json()
                except ValueError:
                    last_err = f'No JSON from {url}: {resp.text[:200]}'
                    logger.warning(last_err)
                    continue

                # LibreTranslate returns { translatedText: '...' }
                translated = j.get('translatedText') or j.get('translation') or j.get('translated')
                if not translated:
                    last_err = f'No translated field in response from {url}'
                    logger.warning(last_err)
                    continue

                result = {
                    'original': text,
                    'translated': translated,
                    'source_lang': source,
                    'target_lang': target,
                    'source_name': self.languages.get(source, source),
                    'target_name': self.languages.get(target, target),
                    'source_flag': self.flags.get(source, '🌐'),
                    'target_flag': self.flags.get(target, '🌐')
                }
                logger.info(f'✅ Traducción exitosa (LibreTranslate via {url})')
                return result

            except requests.exceptions.RequestException as e:
                last_err = f'Error contacting {url}: {e}'
                logger.warning(last_err)
                continue

        return {'error': f'Fallback LibreTranslate falló. Último error: {last_err}'}

    def translate_google(self, text: str, source: str, target: str) -> dict:
        """
        Último recurso: usar googletrans (offline client) como fallback.
        """
        try:
            from googletrans import Translator as GT
        except Exception as e:
            logger.warning(f'googletrans no disponible: {e}')
            return {'error': 'googletrans no está disponible'}

        try:
            gt = GT()
            # googletrans auto-detecta si source='auto'
            src = None if source == 'auto' else source
            res = gt.translate(text, src=src, dest=target)
            translated = res.text
            result = {
                'original': text,
                'translated': translated,
                'source_lang': res.src or source,
                'target_lang': target,
                'source_name': self.languages.get(res.src, res.src),
                'target_name': self.languages.get(target, target),
                'source_flag': self.flags.get(res.src, '🌐'),
                'target_flag': self.flags.get(target, '🌐')
            }
            logger.info('✅ Traducción exitosa (googletrans)')
            return result
        except Exception as e:
            logger.warning(f'googletrans fallback falló: {e}')
            return {'error': 'googletrans fallback falló'}
    
    
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

    # Mapeo de nombres de idiomas a códigos
    lang_map = {
        'ESPAÑOL': 'es', 'ES': 'es', 'SPANISH': 'es', 'ESPANOL': 'es',
        'INGLÉS': 'en', 'INGLES': 'en', 'ENGLISH': 'en', 'EN': 'en',
        'FRANCÉS': 'fr', 'FRANCES': 'fr', 'FRENCH': 'fr', 'FR': 'fr',
        'ALEMÁN': 'de', 'ALEMAN': 'de', 'GERMAN': 'de', 'DE': 'de', 'GER': 'de',
        'ITALIANO': 'it', 'ITALIAN': 'it', 'IT': 'it',
        'PORTUGUÉS': 'pt', 'PORTUGUES': 'pt', 'PORTUGUESE': 'pt', 'PT': 'pt',
        'RUSO': 'ru', 'RUS': 'ru', 'RUSSIAN': 'ru', 'ZH': 'zh', 'CHINO': 'zh', 'CHINESE': 'zh',
        'JAPONES': 'ja', 'JAPONÉS': 'ja', 'JP': 'ja', 'ARABE': 'ar', 'AR': 'ar',
        'HINDI': 'hi', 'HI': 'hi', 'COREANO': 'ko', 'KO': 'ko', 'TURCO': 'tr', 'TR': 'tr'
    }

    import re

    try:
        q = query.strip()
        q_lower = q.lower()

        # Intentar extraer texto entre comillas primero
        text_to_translate = None
        if "'" in q or '"' in q:
            parts_single = re.findall(r"'([^']+)'", q)
            parts_double = re.findall(r'"([^\"]+)"', q)
            if parts_single:
                text_to_translate = parts_single[0]
            elif parts_double:
                text_to_translate = parts_double[0]

        # Si no hay comillas, buscar patrones 'traducir X al Y' o 'translate X to Y'
        if not text_to_translate:
            # patrones comunes (incluye 'traducir' y 'traduce', y 'a'/'al')
            m = re.search(r"(?:traducir|traduce)\s+(.+?)\s+(?:al|a)\s+([a-zA-ZñÑáéíóúÁÉÍÓÚ]+)", q_lower)
            if not m:
                m = re.search(r"translate\s+(.+?)\s+to\s+([a-zA-Z]+)", q_lower)
            if not m:
                # patrón 'X en español' o 'X en ingles' al final
                m = re.search(r"(.+?)\s+en\s+([a-zA-ZñÑáéíóúÁÉÍÓÚ]+)$", q_lower)
            if m:
                text_to_translate = m.group(1).strip()
                target_word = m.group(2).strip().upper()
                target_lang = lang_map.get(target_word, None)
            else:
                # como fallback, intentar quitar la palabra de idioma final si existe
                # separar en tokens y comprobar si el último token es un idioma conocido
                tokens = q.split()
                last = tokens[-1].strip().upper() if tokens else ''
                candidate = re.sub(r"[^A-ZÑÁÉÍÓÚ]", '', last.upper())
                if candidate and candidate in lang_map:
                    # quitar el último token y usarlo como target
                    text_to_translate = ' '.join(tokens[:-1]).strip()
                    target_lang = lang_map.get(candidate)
                else:
                    # último recurso, quitar palabras clave comunes
                    keywords = ['translate', 'traducir', 'traduce', 'to', 'al', 'a', 'en', 'in',
                                'english', 'spanish', 'español', 'inglés', 'french', 'francés']
                    temp = q
                    for kw in keywords:
                        temp = re.sub(rf"\b{kw}\b", '', temp, flags=re.IGNORECASE)
                    text_to_translate = temp.strip()

        # Si aún no definimos target_lang, intentar extraer de la query con más patrones
        if 'target_lang' not in locals() or not locals().get('target_lang'):
            target_lang = None
            # patrones como 'al español', 'a alemán', 'to english', 'in french', 'en francés'
            patterns = [r"al\s+([a-zA-ZñÑáéíóúÁÉÍÓÚ]+)", r"a\s+([a-zA-ZñÑáéíóúÁÉÍÓÚ]+)",
                        r"to\s+([a-zA-Z]+)", r"in\s+([a-zA-Z]+)", r"en\s+([a-zA-ZñÑáéíóúÁÉÍÓÚ]+)"]
            m2 = None
            for pat in patterns:
                m2 = re.search(pat, q_lower)
                if m2:
                    break
            if m2:
                target_word = m2.group(1).strip().upper()
                target_lang = lang_map.get(target_word)

        # Default si no se detecta
        if not target_lang:
            # si el texto parece español, traducir a inglés; si parece inglés, traducir a español
            # heurística simple
            sample = text_to_translate or q
            tiene_espanol = any(c in sample.lower() for c in ['á', 'é', 'í', 'ó', 'ú', 'ñ', '¿', '¡'])
            palabras_espanol = ['hola', 'buenos', 'gracias', 'por', 'favor', 'que', 'como']
            es_espanol = tiene_espanol or any(p in sample.lower() for p in palabras_espanol)
            target_lang = 'en' if es_espanol else 'es'

        if not text_to_translate or len(text_to_translate) < 1:
            return "❌ No se encontró texto para traducir. Ejemplo: 'translate \"hello\" to spanish'"

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
        "También entiende frases en lenguaje natural como: 'traduce \"how are you\" al español', "
        "o 'how to say \"buenos días\" in english'. Detecta automáticamente el idioma origen. Máximo 1000 caracteres."
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