import logging
import requests
from typing import Optional
from langchain.tools import Tool

logger = logging.getLogger(__name__)


class LyricsFinder:
    """
    Buscador de letras de canciones usando API gratuita
    API: lyrics.ovh (gratuita, sin key necesaria)
    """
    
    def __init__(self):
        # API gratuita sin autenticación
        self.base_url = "https://api.lyrics.ovh/v1"
        
        logger.info("✅ LyricsFinder inicializado")
    
    
    def search_lyrics(self, artist: str, song: str) -> dict:
        """
        Busca la letra de una canción
        
        Args:
            artist: Nombre del artista
            song: Nombre de la canción
            
        Returns:
            Diccionario con letra o error
        """
        try:
            # Limpiar y preparar nombres
            artist = artist.strip()
            song = song.strip()
            
            if not artist or not song:
                return {'error': 'Debe proporcionar artista y canción'}
            
            logger.info(f"🎵 Buscando: '{song}' de {artist}")
            
            # Hacer request a la API
            url = f"{self.base_url}/{artist}/{song}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 404:
                return {
                    'error': f'No se encontró la letra de "{song}" de {artist}. Verifica el nombre.'
                }
            
            response.raise_for_status()
            data = response.json()
            
            # Extraer letra
            if 'lyrics' in data and data['lyrics']:
                lyrics = data['lyrics'].strip()
                
                result = {
                    'artist': artist,
                    'song': song,
                    'lyrics': lyrics,
                    'length': len(lyrics),
                    'lines': len(lyrics.split('\n'))
                }
                
                logger.info(f"✅ Letra encontrada: {result['lines']} líneas")
                return result
            else:
                return {'error': 'La letra no está disponible en este momento'}
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Error HTTP: {e}")
            return {'error': f'Error al buscar letra: {response.status_code}'}
            
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout en API de letras")
            return {'error': 'Tiempo de espera agotado. Intenta de nuevo.'}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de conexión: {e}")
            return {'error': 'Error de conexión con el servicio'}
            
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return {'error': f'Error al buscar letra: {str(e)}'}
    
    
    def format_result(self, result: dict, max_lines: int = 30) -> str:
        """
        Formatea el resultado de búsqueda de letra
        
        Args:
            result: Diccionario con datos de la letra
            max_lines: Máximo de líneas a mostrar (para Telegram)
            
        Returns:
            Mensaje formateado
        """
        if 'error' in result:
            return f"❌ {result['error']}"
        
        # Limitar letra si es muy larga
        lyrics = result['lyrics']
        lines = lyrics.split('\n')
        
        if len(lines) > max_lines:
            # Mostrar primeras líneas + indicador
            lyrics_preview = '\n'.join(lines[:max_lines])
            lyrics_preview += f"\n\n... ({len(lines) - max_lines} líneas más)"
        else:
            lyrics_preview = lyrics
        
        message = f"""
🎵 **{result['song'].upper()}**
🎤 **Artista:** {result['artist']}

📝 **Letra:**

{lyrics_preview}

---
📊 **Info:** {result['lines']} líneas | {result['length']} caracteres
💡 _Si la letra está incompleta, búscala completa en Genius o LyricFind_
        """
        
        return message.strip()
    
    
    def get_sample_searches(self) -> str:
        """
        Retorna ejemplos de búsquedas populares
        """
        samples = """
🎵 **EJEMPLOS DE BÚSQUEDA**

**Éxitos Latinos:**
• Bad Bunny - Tití Me Preguntó
• Shakira - Hips Don't Lie
• J Balvin - Mi Gente

**Pop Internacional:**
• The Weeknd - Blinding Lights
• Ed Sheeran - Shape of You
• Taylor Swift - Anti-Hero

**Rock Clásico:**
• Queen - Bohemian Rhapsody
• The Beatles - Hey Jude
• Nirvana - Smells Like Teen Spirit

**Reggaeton:**
• Daddy Yankee - Gasolina
• Ozuna - Taki Taki
• Karol G - Bichota

💡 **Formato:** Escribe artista y canción
        """
        return samples.strip()


# ============================================
# CREAR LANGCHAIN TOOL
# ============================================

def find_lyrics_function(query: str) -> str:
    """
    Función wrapper para usar con LangChain Tool
    
    Formatos aceptados:
    - "lyrics of Imagine Dragons - Radioactive"
    - "letra de Bad Bunny Tití Me Preguntó"
    - "find Shape of You by Ed Sheeran"
    - "Bohemian Rhapsody Queen"
    
    Args:
        query: String con artista y canción
        
    Returns:
        Resultado formateado como string
    """
    finder = LyricsFinder()
    
    try:
        # Limpiar query
        query = query.replace('lyrics of', '').replace('letra de', '').replace('find', '').strip()
        
        # Intentar parsear diferentes formatos
        artist = None
        song = None
        
        # Formato: "Artist - Song"
        if ' - ' in query:
            parts = query.split(' - ')
            artist = parts[0].strip()
            song = parts[1].strip()
        
        # Formato: "Song by Artist"
        elif ' by ' in query.lower():
            parts = query.lower().split(' by ')
            song = query[:len(parts[0])].strip()
            artist = query[len(parts[0]) + 4:].strip()
        
        # Formato: "Artist Song" (últimas 2-4 palabras como canción)
        else:
            words = query.split()
            if len(words) >= 2:
                # Asumir: primeras palabras = artista, últimas = canción
                # Si hay muchas palabras, dividir a la mitad
                mid = len(words) // 2
                artist = ' '.join(words[:mid])
                song = ' '.join(words[mid:])
            else:
                return "❌ Formato incorrecto. Usa: 'Artista - Canción' o 'Canción by Artista'"
        
        if not artist or not song:
            return "❌ No se pudo identificar artista y canción. Usa formato: 'Artista - Canción'"
        
        # Buscar letra
        result = finder.search_lyrics(artist, song)
        return finder.format_result(result)
        
    except Exception as e:
        logger.error(f"Error en find_lyrics_function: {e}")
        return f"❌ Error al buscar letra: {str(e)}"


# Crear la Tool de LangChain
lyrics_tool = Tool(
    name="LyricsFinder",
    description=(
        "Busca y muestra la letra completa de canciones. "
        "Formato: 'Artista - Canción' o 'Canción by Artista'. "
        "Funciona con artistas y canciones en español e inglés. "
        "Ejemplos: 'Bad Bunny - Tití Me Preguntó', 'Shape of You by Ed Sheeran', "
        "'Queen - Bohemian Rhapsody'. "
        "Útil para encontrar letras de canciones populares y clásicas."
    ),
    func=find_lyrics_function
)


# Instancia global para uso directo
lyrics_finder = LyricsFinder()


if __name__ == "__main__":
    # Testing
    finder = LyricsFinder()
    
    # Prueba 1: Canción en inglés
    print("Prueba 1: The Beatles - Hey Jude")
    result = finder.search_lyrics("The Beatles", "Hey Jude")
    print(finder.format_result(result, max_lines=20))
    print("\n" + "="*50 + "\n")
    
    # Prueba 2: Canción latina
    print("Prueba 2: Shakira - Waka Waka")
    result = finder.search_lyrics("Shakira", "Waka Waka")
    print(finder.format_result(result, max_lines=20))
    print("\n" + "="*50 + "\n")
    
    # Prueba 3: Usando la tool
    print("Testing LangChain Tool:")
    print(find_lyrics_function("Imagine Dragons - Radioactive"))
    print("\n" + "="*50 + "\n")
    
    # Prueba 4: Formato alternativo
    print("Testing formato alternativo:")
    print(find_lyrics_function("Blinding Lights by The Weeknd"))