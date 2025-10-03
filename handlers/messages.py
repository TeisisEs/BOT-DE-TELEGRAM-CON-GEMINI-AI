import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.gemini_client import gemini_client
from utils.conversation_manager import conversation_manager

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja mensajes de texto con contexto conversacional mejorado
    Evita respuestas repetitivas y mantiene flujo natural
    """
    user = update.effective_user
    user_message = update.message.text
    user_id = user.id
    user_name = user.first_name
    chat_id = update.effective_chat.id
    
    logger.info(f"💬 [{user_name}] {user_message[:100]}")
    
    # Verificar cliente de Gemini
    if not gemini_client:
        await update.message.reply_text(
            "❌ El servicio de IA no está disponible. Intenta más tarde."
        )
        return
    
    try:
        # Mostrar indicador "escribiendo..."
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Obtener historial de conversación
        conversation_history = conversation_manager.get_history(user_id)
        
        # Log de contexto
        if conversation_history:
            logger.info(f"📚 Usuario {user_name} tiene {len(conversation_history)} mensajes en historial")
        
        # Obtener respuesta con contexto
        response = gemini_client.get_response_with_context(
            user_message=user_message,
            conversation_history=conversation_history,
            user_name=user_name
        )
        
        # Guardar mensaje del usuario en historial
        conversation_manager.add_message(user_id, 'user', user_message)
        
        # Guardar respuesta del asistente en historial
        conversation_manager.add_message(user_id, 'assistant', response)
        
        # Dividir respuesta si es muy larga
        if len(response) > 4096:
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for i, chunk in enumerate(chunks):
                await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
                if i < len(chunks) - 1:
                    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        else:
            # Intentar enviar con Markdown, si falla enviar sin formato
            try:
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            except Exception:
                # Si hay error de formato Markdown, enviar texto plano
                await update.message.reply_text(response)
        
        logger.info(f"✅ Respuesta enviada a {user_name}")
        
    except Exception as e:
        logger.error(f"❌ Error al procesar mensaje: {e}", exc_info=True)
        await update.message.reply_text(
            "Disculpa, hubo un problema al procesar tu mensaje. "
            "¿Podrías intentarlo de nuevo?"
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja notas de voz (funcionalidad futura)
    """
    user_name = update.effective_user.first_name
    logger.info(f"🎙️ Nota de voz recibida de {user_name}")
    
    await update.message.reply_text(
        "🎙️ **Nota de voz recibida**\n\n"
        "La transcripción de audio estará disponible próximamente.\n"
        "Por ahora, envía tu mensaje como texto. 📝",
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja imágenes (funcionalidad futura con Gemini Vision)
    """
    user_name = update.effective_user.first_name
    logger.info(f"📸 Imagen recibida de {user_name}")
    
    await update.message.reply_text(
        "📸 **Imagen recibida**\n\n"
        "El análisis de imágenes con Gemini Vision estará disponible próximamente.\n"
        "Por ahora, describe lo que necesitas en texto. ✍️",
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja documentos enviados
    """
    user_name = update.effective_user.first_name
    document = update.message.document
    logger.info(f"📄 Documento recibido de {user_name}: {document.file_name}")
    
    await update.message.reply_text(
        f"📄 **Documento recibido:** {document.file_name}\n\n"
        f"Tamaño: {document.file_size / 1024:.1f} KB\n\n"
        "El procesamiento de documentos estará disponible próximamente. 📋",
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja stickers con respuestas contextuales
    """
    user_name = update.effective_user.first_name
    sticker = update.message.sticker
    emoji = sticker.emoji or "🎯"
    
    logger.info(f"🎨 Sticker recibido de {user_name}: {emoji}")
    
    # Respuestas contextuales según el emoji
    emoji_responses = {
        '👍': 'Genial! 😊',
        '❤️': 'Gracias! ❤️',
        '😂': 'Jaja! 😄',
        '🤔': '¿En qué estás pensando?',
        '👋': 'Hola! 👋',
        '🎉': 'A celebrar! 🎊',
        '😢': '¿Todo bien?',
        '🔥': 'Increíble! 🔥',
        '💯': 'Perfecto! 💯',
        '🤝': 'De acuerdo! 🤝',
    }
    
    response = emoji_responses.get(emoji, f"{emoji} ¿En qué puedo ayudarte?")
    await update.message.reply_text(response)