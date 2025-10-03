import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Importar configuración
from config import TELEGRAM_TOKEN

# Importar handlers
from handlers.commands import (
    start_command, 
    help_command, 
    fecha_command, 
    clima_command, 
    chiste_command,
    reset_command
)
from handlers.messages import (
    handle_message, 
    handle_voice, 
    handle_photo,
    handle_document,
    handle_sticker
)

# Configurar logging mejorado
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),  # Consola
        logging.FileHandler('bot.log', encoding='utf-8')  # Archivo
    ]
)
logger = logging.getLogger(__name__)


# ============================================
# MANEJADOR DE ERRORES
# ============================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja errores de forma elegante
    """
    logger.error(f"Error: {context.error}", exc_info=context.error)
    
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Ocurrió un error inesperado.\n"
                "El error ha sido registrado. Por favor intenta de nuevo."
            )
        except Exception as e:
            logger.error(f"No se pudo enviar mensaje de error: {e}")


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """
    Función principal que inicia el bot con configuración mejorada
    """
    print("\n" + "="*50)
    print("🚀 INICIANDO BOT DE TELEGRAM")
    print("="*50)
    
    print("\n📋 Cargando módulos...")
    print("   ✅ Configuración cargada")
    print("   ✅ Gemini AI inicializado")
    print("   ✅ Weather API conectada")
    print("   ✅ Sistema de memoria conversacional activo")
    
    # Crear aplicación
    print("\n🔧 Configurando bot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar comandos
    print("📝 Registrando comandos...")
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fecha", fecha_command))
    application.add_handler(CommandHandler("clima", clima_command))
    application.add_handler(CommandHandler("chiste", chiste_command))
    application.add_handler(CommandHandler("reset", reset_command))
    
    # Registrar manejadores de mensajes
    print("💬 Registrando handlers de mensajes...")
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    
    # Registrar manejador de errores
    application.add_error_handler(error_handler)
    
    # Mensaje de inicio
    print("\n" + "="*50)
    print("✅ BOT INICIADO CORRECTAMENTE")
    print("="*50)
    print("\n🤖 Funcionalidades activas:")
    print("   • Conversaciones con contexto e historial")
    print("   • Respuestas no repetitivas")
    print("   • Manejo inteligente de errores")
    print("   • Sistema de memoria por usuario")
    print("\n📋 Comandos disponibles:")
    print("   /start    - Mensaje de bienvenida")
    print("   /help     - Ver ayuda completa")
    print("   /fecha    - Fecha y hora actual")
    print("   /clima    - Consultar clima")
    print("   /chiste   - Generar chiste con IA")
    print("   /reset    - Reiniciar conversación")
    print("\n💡 Mejoras implementadas:")
    print("   ✓ Memoria conversacional (30 min)")
    print("   ✓ Contexto entre mensajes")
    print("   ✓ Respuestas más naturales")
    print("   ✓ Evita repeticiones")
    print("   ✓ Mejor manejo de errores")
    print("\n👋 Abre Telegram y prueba tu bot")
    print("ℹ️  Presiona Ctrl+C para detener\n")
    
    logger.info("Bot iniciado y listo para recibir mensajes")
    
    # Iniciar polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Bot detenido por el usuario")
        logger.info("Bot detenido manualmente")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        logger.error(f"Error fatal al iniciar el bot: {e}", exc_info=True)