import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.gemini_client import gemini_client

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja todos los mensajes de texto que no son comandos
    Usa Gemini AI para generar respuestas inteligentes
    """
    user_message = update.message.text
    user_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    
    logger.info(f"💬 Mensaje de {user_name}: {user_message}")
    
    # Verificar que el cliente de Gemini esté disponible
    if not gemini_client:
        await update.message.reply_text(
            "❌ Lo siento, el servicio de IA no está disponible en este momento."
        )
        return
    
    try:
        # Mostrar indicador de "escribiendo..."
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Obtener respuesta de Gemini AI
        response = gemini_client.get_response(user_message)
        
        # Enviar respuesta al usuario
        await update.message.reply_text(response)
        
        logger.info(f"✅ Respuesta enviada a {user_name}")
        
    except Exception as e:
        logger.error(f"❌ Error al manejar mensaje: {e}")
        await update.message.reply_text(
            "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo."
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja mensajes de voz (opcional - para futuras mejoras)
    """
    await update.message.reply_text(
        "🎤 Por ahora solo puedo procesar mensajes de texto. ¡Pronto podré escuchar audios!"
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja fotos enviadas (opcional - para futuras mejoras)
    """
    await update.message.reply_text(
        "📸 Recibí tu imagen. Por ahora solo puedo procesar texto, pero pronto podré analizar imágenes."
    )