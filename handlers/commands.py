import logging
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import pytz
from utils.weather_api import weather_api

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
💡 **Respuestas a tus dudas** - Cualquier tema

📝 Escribe /help para ver todos mis comandos.

💬 **¡Simplemente escribe tu pregunta y te responderé!**
    """
    
    await update.message.reply_text(welcome_message)
    logger.info(f"Usuario {user_name} inició el bot")


#--------------------------------------------------------------------------------
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
   _Ejemplos:_
   • `/clima San Salvador`
   • `/chiste programacion`

**Conversaciones con IA:**
💬 Simplemente escribe cualquier pregunta y te responderé usando Gemini AI

El bot ahora **recuerda** nuestra conversación anterior (hasta 30 minutos).
Usa /reset si quieres empezar de cero.

⚡ **Powered by Google Gemini AI & OpenWeatherMap**
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

#__________________________________________________________________________
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
🌍 Zona horaria: El Salvador (GMT-6)

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
    
    # Obtener nombre de la ciudad (puede ser más de una palabra)
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
        
#__________________________________________________________________

from utils.gemini_client import gemini_client

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /reset - Limpia el historial de conversación y muestra info útil
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
• /chiste [categoría] - Generar chiste

💬 **¿En qué puedo ayudarte ahora?**
Puedes preguntarme cualquier cosa o usar algún comando.
    """
    
    await update.message.reply_text(reset_message, parse_mode='Markdown')
    logger.info(f"Historial reiniciado para usuario {user_name} ({user_id})")


async def chiste_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /chiste - Genera chistes usando Gemini AI
    Uso: /chiste [categoría opcional]
    
    Categorías disponibles:
    - programacion
    - ciencia
    - general
    - papa (dad jokes)
    """
    chat_id = update.effective_chat.id
    
    # Obtener categoría si se especificó
    categoria = " ".join(context.args) if context.args else "general"
    
    # Verificar que el cliente de Gemini esté disponible
    if not gemini_client:
        await update.message.reply_text(
            "❌ Lo siento, el servicio de IA no está disponible."
        )
        return
    
    try:
        # Mostrar indicador de "escribiendo..."
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        logger.info(f"🎭 Generando chiste de categoría: {categoria}")
        
        # Agregar timestamp para forzar respuestas diferentes
        import time
        timestamp = int(time.time())
        
        # Crear prompt específico para generar chistes
        categoria_lower = categoria.lower()
        
        if categoria_lower == "programacion":
            prompt = f"""
            Genera UN SOLO chiste original y gracioso sobre programación o desarrollo de software.
            Debe ser diferente, ingenioso y que los programadores disfruten.
            IMPORTANTE: Sé creativo, evita chistes comunes o repetitivos.
            Formato: Solo el chiste con un emoji al inicio. Nada más.
            ID único: {timestamp}
            """
        elif categoria_lower == "ciencia":
            prompt = f"""
            Genera UN SOLO chiste original sobre ciencia (física, química, biología, matemáticas).
            Debe ser inteligente, educativo y gracioso.
            IMPORTANTE: Crea algo único, no uses chistes conocidos.
            Formato: Solo el chiste con un emoji al inicio. Nada más.
            ID único: {timestamp}
            """
        elif categoria_lower in ["papa", "papá"]:
            prompt = f"""
            Genera UN SOLO "dad joke" (chiste de papá) original en español.
            Debe ser un juego de palabras simple, predecible pero gracioso.
            IMPORTANTE: Inventa uno nuevo, no repitas chistes clásicos.
            Formato: Solo el chiste con un emoji al inicio. Nada más.
            ID único: {timestamp}
            """
        else:
            # Para cualquier otra categoría (incluyendo perros, gatos, etc.)
            prompt = f"""
            Genera UN SOLO chiste corto, original y gracioso sobre: {categoria}
            Debe ser apropiado, divertido y relacionado específicamente con "{categoria}".
            IMPORTANTE: Sé muy creativo. Evita chistes genéricos como el del semáforo.
            Crea algo único basado en la temática solicitada.
            Formato: Solo el chiste con un emoji al inicio. Nada más.
            ID único: {timestamp}
            """
        
        # Obtener chiste de Gemini
        chiste = gemini_client.get_simple_response(prompt)
        
        # Formatear respuesta
        respuesta = f"""
🎭 **CHISTE DE {categoria.upper()}**

{chiste}

---
💡 _Prueba otras categorías:_
• `/chiste programacion`
• `/chiste ciencia`
• `/chiste papa`
• `/chiste` (general)
        """
        
        await update.message.reply_text(respuesta, parse_mode='Markdown')
        logger.info(f"✅ Chiste enviado (categoría: {categoria})")
        
    except Exception as e:
        logger.error(f"❌ Error en comando /chiste: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error al generar el chiste. Por favor intenta de nuevo."
        )