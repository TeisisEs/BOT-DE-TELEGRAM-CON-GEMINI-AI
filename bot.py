import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Importar configuración
from config import TELEGRAM_TOKEN

# Importar handlers
from handlers.messages import handle_message, handle_voice, handle_photo

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# COMANDOS DEL BOT
# ============================================

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
   Ejemplo: _/clima San Salvador_

**Conversaciones con IA:**
💬 Simplemente escribe cualquier pregunta o mensaje y te responderé usando Gemini AI

**Ejemplos de preguntas:**
- ¿Qué es la inteligencia artificial?
- Explícame sobre Python
- Dame consejos para programar mejor
- Cuéntame un chiste
- ¿Cómo está el clima en París?

⚡ **Powered by Google Gemini AI**
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def fecha_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /fecha - Muestra fecha y hora actual
    """
    from datetime import datetime
    import pytz
    
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


# ============================================
# MANEJADOR DE ERRORES
# ============================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja errores que ocurran durante la ejecución
    """
    logger.error(f"Error: {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "❌ Ocurrió un error procesando tu solicitud. Por favor intenta de nuevo."
        )


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """
    Función principal que inicia el bot
    """
    print("🚀 Iniciando bot...")
    print("🤖 Conectando con Gemini AI...")
    
    # Crear aplicación del bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fecha", fecha_command))
    
    # Registrar manejadores de mensajes
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Registrar manejador de errores
    application.add_error_handler(error_handler)
    
    # Iniciar el bot
    print("✅ Bot iniciado correctamente")
    print("🧠 Gemini AI está listo")
    print("👋 Abre Telegram y prueba tu bot")
    print("⏹️  Presiona Ctrl+C para detener\n")
    
    # Polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()