import logging
import os
import threading
from flask import Flask
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
    reset_command,
    convertir_command,
    traducir_command,
    letra_command
)
from handlers.messages import (
    handle_message, 
    handle_voice, 
    handle_photo,
    handle_document,
    handle_sticker
)

# Detectar si estamos en producción (Render) o desarrollo
IS_PRODUCTION = os.getenv('RENDER') is not None

# Configurar logging mejorado
if IS_PRODUCTION:
    # En producción: solo consola (Render captura estos logs)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[logging.StreamHandler()]
    )
else:
    # En desarrollo: consola + archivo
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log', encoding='utf-8')
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
    env_status = "🌐 PRODUCCIÓN (Render)" if IS_PRODUCTION else "💻 DESARROLLO (Local)"
    
    print("\n" + "="*60)
    print("🚀 INICIANDO BOT DE TELEGRAM CON LANGCHAIN AGENT")
    print(f"   Entorno: {env_status}")
    print("="*60)
    
    print("\n📋 Cargando módulos...")
    print("   ✅ Configuración cargada")
    print("   ✅ Gemini AI inicializado")
    print("   ✅ Weather API conectada")
    print("   ✅ Sistema de memoria conversacional activo")
    
    print("\n🔧 Cargando LangChain Tools...")
    print("      • 💱 CurrencyConverter")
    print("      • 🌐 TextTranslator")
    print("      • 🎵 LyricsFinder")
    
    print("\n🤖 Inicializando LangChain Agent...")
    print("      • AgentType: CONVERSATIONAL_REACT_DESCRIPTION")
    print("      • Memory: ConversationBufferMemory")
    print("      • Tools: 3 herramientas especializadas")
    print("      ✅ Agente listo para decisiones automáticas")
    
    # Crear aplicación
    print("\n🔧 Configurando bot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar comandos básicos
    print("📝 Registrando comandos básicos...")
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fecha", fecha_command))
    application.add_handler(CommandHandler("clima", clima_command))
    application.add_handler(CommandHandler("chiste", chiste_command))
    application.add_handler(CommandHandler("reset", reset_command))
    
    # Registrar comandos con Tools
    print("🆕 Registrando comandos con LangChain Tools...")
    application.add_handler(CommandHandler("convertir", convertir_command))
    application.add_handler(CommandHandler("traducir", traducir_command))
    application.add_handler(CommandHandler("letra", letra_command))
    
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
    print("\n" + "="*60)
    print("✅ BOT INICIADO CORRECTAMENTE")
    print("="*60)
    
    print("\n🤖 Funcionalidades activas:")
    print("   • Conversaciones con contexto e historial")
    print("   • 🆕 Agente LangChain inteligente")
    print("   • Decisión automática de herramientas")
    print("   • Respuestas no repetitivas")
    print("   • Sistema de memoria por usuario")
    
    print("\n📋 Comandos disponibles:")
    print("   /start       - Mensaje de bienvenida")
    print("   /help        - Ver ayuda completa")
    print("   /fecha       - Fecha y hora actual")
    print("   /clima       - Consultar clima")
    print("   /chiste      - Generar chiste con IA")
    print("   /reset       - Reiniciar conversación")
    
    print("\n🆕 Comandos con LangChain Tools:")
    print("   /convertir   - 💱 Convertir monedas")
    print("   /traducir    - 🌐 Traducir textos")
    print("   /letra       - 🎵 Buscar letras de canciones")
    
    print("\n🤖 Características del Agente:")
    print("   ✓ Detecta automáticamente necesidad de tools")
    print("   ✓ Decide qué herramienta usar")
    print("   ✓ Conversación natural sin comandos")
    print("   ✓ Ejemplos:")
    print("     • 'convierte 100 dólares a euros'")
    print("     • 'traduce hello world al español'")
    print("     • 'letra de Bohemian Rhapsody'")
    
    print("\n💡 Tecnologías implementadas:")
    print("   ✓ LangChain Framework")
    print("   ✓ Google Gemini AI (gemini-2.0-flash-exp)")
    print("   ✓ LangChain Tools (3 personalizadas)")
    print("   ✓ LangChain Agent (CONVERSATIONAL_REACT)")
    print("   ✓ Memoria conversacional (30 min)")
    print("   ✓ Sistema de decisión inteligente")
    
    if IS_PRODUCTION:
        print("\n🌐 Bot desplegado en Render - Funcionando 24/7")
        logger.info("Bot ejecutándose en producción (Render)")
    else:
        print("\n👋 Abre Telegram y prueba tu bot")
        print("💡 Prueba tanto comandos como preguntas naturales")
        print("ℹ️  Presiona Ctrl+C para detener\n")
    
    logger.info("Bot con LangChain Agent iniciado correctamente")
    
    # Iniciar polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


# ==============================
# SERVIDOR FLASK PARA RENDER
# ==============================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot de Telegram con LangChain está corriendo en Render (plan Free)."

# ==============================
if __name__ == '__main__':
    try:
        # Hilo para ejecutar el bot en paralelo
        bot_thread = threading.Thread(target=main, daemon=True)
        bot_thread.start()

        # Flask mantiene el servicio “vivo” para Render
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)

    except KeyboardInterrupt:
        print("\n\n🛑 Bot detenido por el usuario")
        logger.info("Bot detenido manualmente")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        logger.error(f"Error fatal al iniciar el bot: {e}", exc_info=True)
