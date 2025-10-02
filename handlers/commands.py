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


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /help - Lista de comandos disponibles
    """
    help_text = """
📋 **COMANDOS DISPONIBLES:**

**Comandos básicos:**
🔹 /start - Iniciar el bot
🔹 /help - Ver esta ayuda
🔹 /fecha - Fecha y hora actual
🔹 /clima [ciudad] - Clima de una ciudad
   _Ejemplos:_
   • `/clima San Salvador`
   • `/clima Madrid`
   • `/clima Tokyo`

**Conversaciones con IA:**
💬 Simplemente escribe cualquier pregunta o mensaje y te responderé usando Gemini AI

**Ejemplos de preguntas:**
- ¿Qué es la inteligencia artificial?
- Explícame sobre Python
- Dame consejos para programar mejor
- Cuéntame un chiste
- ¿Cómo funciona el clima?

⚡ **Powered by Google Gemini AI & WeatherAPI**
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