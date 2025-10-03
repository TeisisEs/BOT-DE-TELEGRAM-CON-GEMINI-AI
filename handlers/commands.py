import logging
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import pytz
from utils.weather_api import weather_api
from utils.gemini_client import gemini_client

# Importar las nuevas Tools
from utils.tools import currency_converter, translator, lyrics_finder

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /start - Mensaje de bienvenida
    """
    user_name = update.effective_user.first_name
    
    welcome_message = f"""
🤖 ¡Hola {user_name}! Bienvenido a tu Bot Inteligente

Soy un asistente potenciado por **Google Gemini AI** que puede ayudarte con:

✨ **Conversaciones inteligentes** - Pregúntame lo que quieras
🌤️ **Información del clima** - /clima [ciudad]
📅 **Fecha y hora actual** - /fecha
💱 **Conversión de monedas** - /convertir [cantidad] [moneda1] [moneda2]
🌍 **Traducción de textos** - /traducir [texto] [idioma]
🎵 **Letras de canciones** - /letra [artista] - [canción]
😂 **Chistes con IA** - /chiste

📋 Escribe /help para ver todos mis comandos.

💬 **¡Simplemente escribe tu pregunta y te responderé!**
    """
    
    await update.message.reply_text(welcome_message)
    logger.info(f"Usuario {user_name} inició el bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📋 **COMANDOS DISPONIBLES:**

**Comandos básicos:**
🔹 /start - Iniciar el bot
🔹 /help - Ver esta ayuda
🔹 /fecha - Fecha y hora actual
🔹 /clima [ciudad] - Clima de una ciudad
🔹 /chiste [categoría] - Chiste con IA
🔹 /reset - Reiniciar conversación

**🆕 Nuevas herramientas:**
💱 /convertir [cantidad] [de] [a] - Convertir monedas
   _Ejemplos:_
   • `/convertir 100 USD EUR`
   • `/convertir 50 MXN USD`

🌍 /traducir [texto] - Traducir texto
   _Ejemplos:_
   • `/traducir hello world`
   • `/traducir buenos días`

🎵 /letra [artista] - [canción] - Buscar letra
   _Ejemplos:_
   • `/letra Bad Bunny - Tití Me Preguntó`
   • `/letra The Beatles - Hey Jude`

**Conversaciones con IA:**
💬 Simplemente escribe cualquier pregunta y te responderé usando Gemini AI

El bot ahora **recuerda** nuestra conversación anterior (hasta 30 minutos).
Usa /reset si quieres empezar de cero.

⚡ **Powered by Google Gemini AI, OpenWeatherMap & LangChain Tools**
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def fecha_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /fecha - Muestra fecha y hora actual
    """
    # Zona horaria de El Salvador
    timezone = pytz.timezone('America/El_Salvador')
    now = datetime.now(timezone)
    
    # Formatear fecha en español
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    
    dia_semana = dias[now.weekday()]
    mes = meses[now.month - 1]
    
    fecha_formateada = f"""
📅 **FECHA Y HORA ACTUAL**

🗓️ {dia_semana}, {now.day} de {mes} de {now.year}
🕐 Hora: {now.strftime('%I:%M:%S %p')}
🌎 Zona horaria: El Salvador (GMT-6)

_Información actualizada en tiempo real_
    """
    
    await update.message.reply_text(fecha_formateada, parse_mode='Markdown')
    logger.info("Comando /fecha ejecutado")


async def clima_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /clima - Obtiene información del clima de una ciudad
    Uso: /clima [nombre de ciudad]
    """
    chat_id = update.effective_chat.id
    
    # Verificar que se proporcionó una ciudad
    if not context.args:
        await update.message.reply_text(
            "❌ Por favor especifica una ciudad.\n\n"
            "**Uso correcto:**\n"
            "`/clima San Salvador`\n"
            "`/clima Madrid`\n"
            "`/clima Tokyo`",
            parse_mode='Markdown'
        )
        return
    
    # Obtener nombre de la ciudad
    ciudad = " ".join(context.args)
    
    try:
        # Mostrar indicador de "escribiendo..."
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        logger.info(f"🌤️ Consultando clima para: {ciudad}")
        
        # Obtener datos del clima
        weather_data = weather_api.get_current_weather(ciudad)
        
        # Formatear y enviar mensaje
        message = weather_api.format_weather_message(weather_data)
        await update.message.reply_text(message, parse_mode='Markdown')
        
        logger.info(f"✅ Clima enviado para: {ciudad}")
        
    except Exception as e:
        logger.error(f"❌ Error en comando /clima: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error al obtener el clima. Por favor intenta de nuevo."
        )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /reset - Limpia el historial de conversación
    """
    from utils.conversation_manager import conversation_manager
    
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Limpiar historial
    conversation_manager.clear_history(user_id)
    
    reset_message = f"""
🔄 **Conversación reiniciada**

¡Hola de nuevo, {user_name}! 👋

He limpiado nuestro historial de conversación.
Ahora empezamos desde cero con memoria fresca.

📋 **Comandos rápidos:**
• /help - Ver ayuda completa
• /fecha - Fecha y hora actual
• /clima [ciudad] - Consultar clima
• /convertir - Convertir monedas
• /traducir - Traducir textos
• /letra - Buscar letras

💬 **¿En qué puedo ayudarte ahora?**
    """
    
    await update.message.reply_text(reset_message, parse_mode='Markdown')
    logger.info(f"Historial reiniciado para usuario {user_name} ({user_id})")


async def chiste_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /chiste - Genera chistes usando Gemini AI
    """
    chat_id = update.effective_chat.id
    categoria = " ".join(context.args) if context.args else "general"
    
    if not gemini_client:
        await update.message.reply_text("❌ El servicio de IA no está disponible.")
        return
    
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        import time
        timestamp = int(time.time())
        
        prompt = f"""
        Genera UN SOLO chiste corto y original sobre: {categoria}
        Debe ser apropiado, divertido y creativo.
        Formato: Solo el chiste con un emoji al inicio.
        ID único: {timestamp}
        """
        
        chiste = gemini_client.get_simple_response(prompt)
        
        respuesta = f"""
🎭 **CHISTE DE {categoria.upper()}**

{chiste}

---
💡 _Prueba: /chiste programacion, /chiste ciencia_
        """
        
        await update.message.reply_text(respuesta, parse_mode='Markdown')
        logger.info(f"✅ Chiste enviado (categoría: {categoria})")
        
    except Exception as e:
        logger.error(f"❌ Error en /chiste: {e}")
        await update.message.reply_text("❌ Error al generar chiste.")


# ============================================
# 🆕 NUEVOS COMANDOS CON LANGCHAIN TOOLS
# ============================================

async def convertir_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /convertir - Convierte monedas usando CurrencyTool
    Uso: /convertir [cantidad] [moneda_origen] [moneda_destino]
    Ejemplos: /convertir 100 USD EUR
    """
    chat_id = update.effective_chat.id
    
    # Verificar argumentos
    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ Formato incorrecto.\n\n"
            "**Uso correcto:**\n"
            "`/convertir [cantidad] [de] [a]`\n\n"
            "**Ejemplos:**\n"
            "• `/convertir 100 USD EUR`\n"
            "• `/convertir 50 MXN USD`\n"
            "• `/convertir 1000 JPY GBP`\n\n"
            "💡 Usa códigos de moneda: USD, EUR, GBP, JPY, MXN, CAD, etc.",
            parse_mode='Markdown'
        )
        return
    
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Extraer parámetros
        cantidad = float(context.args[0])
        moneda_origen = context.args[1].upper()
        moneda_destino = context.args[2].upper()
        
        logger.info(f"💱 Convirtiendo {cantidad} {moneda_origen} → {moneda_destino}")
        
        # Usar CurrencyConverter
        result = currency_converter.convert(cantidad, moneda_origen, moneda_destino)
        message = currency_converter.format_result(result)
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"✅ Conversión enviada")
        
    except ValueError:
        await update.message.reply_text(
            "❌ Cantidad inválida. Debe ser un número.\n"
            "Ejemplo: `/convertir 100 USD EUR`",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"❌ Error en /convertir: {e}")
        await update.message.reply_text("❌ Error al convertir monedas.")


async def traducir_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /traducir - Traduce texto usando TranslatorTool
    Uso: /traducir [texto]
    Detecta automáticamente el idioma y traduce (inglés ↔ español por defecto)
    """
    chat_id = update.effective_chat.id
    
    # Verificar que hay texto
    if not context.args:
        await update.message.reply_text(
            "❌ Por favor proporciona un texto para traducir.\n\n"
            "**Uso correcto:**\n"
            "`/traducir hello world`\n"
            "`/traducir buenos días`\n"
            "`/traducir how are you doing`\n\n"
            "💡 El bot detecta el idioma automáticamente:\n"
            "• Inglés → Español\n"
            "• Español → Inglés",
            parse_mode='Markdown'
        )
        return
    
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Obtener texto completo
        texto = " ".join(context.args)
        
        logger.info(f"🌍 Traduciendo: {texto[:50]}...")
        
        # Detectar idioma básico y traducir
        # Si tiene caracteres latinos/español, traducir a inglés
        # Si es inglés, traducir a español
        tiene_espanol = any(c in texto.lower() for c in ['á', 'é', 'í', 'ó', 'ú', 'ñ', '¿', '¡'])
        palabras_espanol = ['hola', 'buenos', 'días', 'cómo', 'qué', 'gracias', 'por', 'favor']
        es_espanol = tiene_espanol or any(palabra in texto.lower() for palabra in palabras_espanol)
        
        target_lang = 'en' if es_espanol else 'es'
        
        # Usar Translator
        result = translator.translate(texto, 'auto', target_lang)
        message = translator.format_result(result)
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"✅ Traducción enviada")
        
    except Exception as e:
        logger.error(f"❌ Error en /traducir: {e}")
        await update.message.reply_text("❌ Error al traducir texto.")


async def letra_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /letra - Busca letra de canción usando LyricsTool
    Uso: /letra [Artista] - [Canción]
    Ejemplos: /letra Bad Bunny - Tití Me Preguntó
    """
    chat_id = update.effective_chat.id
    
    # Verificar que hay query
    if not context.args:
        await update.message.reply_text(
            "❌ Por favor especifica artista y canción.\n\n"
            "**Uso correcto:**\n"
            "`/letra [Artista] - [Canción]`\n\n"
            "**Ejemplos:**\n"
            "• `/letra Bad Bunny - Tití Me Preguntó`\n"
            "• `/letra The Beatles - Hey Jude`\n"
            "• `/letra Shakira - Waka Waka`\n"
            "• `/letra Queen - Bohemian Rhapsody`\n\n"
            "💡 Usa el guion ( - ) para separar artista y canción",
            parse_mode='Markdown'
        )
        return
    
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Obtener query completa
        query = " ".join(context.args)
        
        logger.info(f"🎵 Buscando letra: {query}")
        
        # Parsear artista y canción
        if ' - ' not in query:
            await update.message.reply_text(
                "❌ Formato incorrecto. Usa: `/letra Artista - Canción`\n"
                "Ejemplo: `/letra The Beatles - Hey Jude`",
                parse_mode='Markdown'
            )
            return
        
        parts = query.split(' - ')
        artista = parts[0].strip()
        cancion = parts[1].strip()
        
        # Usar LyricsFinder
        result = lyrics_finder.search_lyrics(artista, cancion)
        
        # Formatear resultado (limitar a 30 líneas para Telegram)
        message = lyrics_finder.format_result(result, max_lines=25)
        
        # Si el mensaje es muy largo, dividirlo
        if len(message) > 4000:
            # Enviar en partes
            parts = [message[i:i+3800] for i in range(0, len(message), 3800)]
            for part in parts:
                await update.message.reply_text(part, parse_mode='Markdown')
                await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        else:
            await update.message.reply_text(message, parse_mode='Markdown')
        
        logger.info(f"✅ Letra enviada: {artista} - {cancion}")
        
    except Exception as e:
        logger.error(f"❌ Error en /letra: {e}")
        await update.message.reply_text("❌ Error al buscar letra de canción.")