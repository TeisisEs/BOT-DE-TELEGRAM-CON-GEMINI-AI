import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Importar configuración
from config import TELEGRAM_TOKEN

# Importar handlers
from handlers.commands import start_command, help_command, fecha_command, clima_command
from handlers.messages import handle_message, handle_voice, handle_photo

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


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
    print("🌤️ Conectando con Weather API...")
    
    # Crear aplicación del bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fecha", fecha_command))
    application.add_handler(CommandHandler("clima", clima_command))
    
    # Registrar manejadores de mensajes
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Registrar manejador de errores
    application.add_error_handler(error_handler)
    
    # Iniciar el bot
    print("✅ Bot iniciado correctamente")
    print("🧠 Gemini AI está listo")
    print("🌍 Weather API está lista")
    print("👋 Abre Telegram y prueba tu bot")
    print("\n📝 Comandos disponibles:")
    print("   /start - Iniciar bot")
    print("   /help - Ver ayuda")
    print("   /fecha - Fecha y hora")
    print("   /clima [ciudad] - Consultar clima")
    print("\n⏹️  Presiona Ctrl+C para detener\n")
    
    # Polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()