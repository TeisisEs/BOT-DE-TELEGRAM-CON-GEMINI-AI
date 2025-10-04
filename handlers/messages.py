import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.gemini_client import gemini_client
from utils.conversation_manager import conversation_manager

# IMPORTAR AGENTE LANGCHAIN
from utils.agent_handler import intelligent_agent, should_use_agent
from utils.tools import currency_tool, translator_tool

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja mensajes de texto con:
    - Agente LangChain (si detecta necesidad de tools)
    - Gemini con contexto (para conversación general)
    
    VERSIÓN MEJORADA con mejor logging y manejo de errores
    """
    user = update.effective_user
    user_message = update.message.text
    user_id = user.id
    user_name = user.first_name
    chat_id = update.effective_chat.id
    
    logger.info(f"💬 [{user_name}] {user_message}")
    
    # Verificar servicios disponibles
    if not gemini_client and not intelligent_agent:
        await update.message.reply_text(
            "❌ Los servicios de IA no están disponibles. Intenta más tarde."
        )
        return
    
    try:
        # Mostrar indicador "escribiendo..."
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # DECISIÓN MEJORADA: ¿Usar agente o Gemini directo?
        use_agent = should_use_agent(user_message)

        # Heurística rápida: si la consulta claramente pide conversión o traducción,
        # invocar directamente la tool correspondiente para mayor confiabilidad.
        import re
        lower = user_message.lower()

        # Detectar conversiones: número + palabra de moneda o código
        number_present = bool(re.search(r"\b[0-9]+(?:[\.,][0-9]+)?\b", user_message))
        currency_words = ['dolar', 'dólar', 'dolares', 'dólares', 'euro', 'euros', 'peso', 'pesos', 'yen', 'yene', 'libra',
                          'usd', 'eur', 'mxn', 'jpy', 'gbp', 'cad', 'aud', 'brl', 'inr']
        has_currency_word = any(w in lower for w in currency_words)

        # Detectar traducciones: palabras clave típicas
        translation_words = ['traducir', 'traduce', 'translate', 'cómo se dice', 'how to say', 'en español', 'al español', 'to english', 'al inglés', 'en ingles']
        has_translation = any(w in lower for w in translation_words)

        # Si detectamos conversión de monedas de forma explícita, usar la tool directamente
        if number_present and has_currency_word:
            try:
                logger.info(f"🔧 Llamando directamente a CurrencyTool para: {user_message}")
                tool_result = currency_tool.func(user_message)
                # Guardar en historial
                conversation_manager.add_message(user_id, 'user', user_message)
                conversation_manager.add_message(user_id, 'assistant', tool_result)
                response = tool_result
                # Enviar respuesta y saltar el flujo del agente
                try:
                    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
                except Exception:
                    await update.message.reply_text(response)
                logger.info("✅ CurrencyTool respondió directamente")
                return
            except Exception as e:
                logger.error(f"❌ Error al usar CurrencyTool directamente: {e}")

        # Si detectamos una petición de traducción explícita, usar la tool directamente
        if has_translation:
            try:
                logger.info(f"🔧 Llamando directamente a TranslatorTool para: {user_message}")
                tool_result = translator_tool.func(user_message)
                conversation_manager.add_message(user_id, 'user', user_message)
                conversation_manager.add_message(user_id, 'assistant', tool_result)
                response = tool_result
                try:
                    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
                except Exception:
                    await update.message.reply_text(response)
                logger.info("✅ TranslatorTool respondió directamente")
                return
            except Exception as e:
                logger.error(f"❌ Error al usar TranslatorTool directamente: {e}")

        if use_agent and intelligent_agent:
            # ================================
            # USAR AGENTE LANGCHAIN
            # ================================
            logger.info(f"🤖 USANDO AGENTE para: {user_message[:50]}")
            
            try:
                response = intelligent_agent.run(user_message)
                
                # Verificar si la respuesta es válida
                if not response or len(response.strip()) < 10:
                    logger.warning("⚠️ Respuesta del agente muy corta, usando Gemini como fallback")
                    raise Exception("Respuesta del agente inválida")
                
                # Guardar en historial
                conversation_manager.add_message(user_id, 'user', user_message)
                conversation_manager.add_message(user_id, 'assistant', response)
                
                logger.info(f"✅ Agente respondió exitosamente")
                
            except Exception as agent_error:
                # Fallback a Gemini si el agente falla
                logger.error(f"❌ Error en agente, usando Gemini: {agent_error}")
                
                # Usar Gemini como respaldo
                conversation_history = conversation_manager.get_history(user_id)
                response = gemini_client.get_response_with_context(
                    user_message=user_message,
                    conversation_history=conversation_history,
                    user_name=user_name
                )
                
                conversation_manager.add_message(user_id, 'user', user_message)
                conversation_manager.add_message(user_id, 'assistant', response)
                
                # Añadir nota explicativa
                response += "\n\n_💡 Nota: Respondí con IA general. Para usar herramientas específicas, intenta con comandos como /convertir, /traducir o /letra_"
            
        else:
            # ================================
            # USAR GEMINI CON CONTEXTO
            # ================================
            logger.info(f"💭 USANDO GEMINI para: {user_message[:50]}")
            
            # Obtener historial de conversación
            conversation_history = conversation_manager.get_history(user_id)
            
            if conversation_history:
                logger.info(f"📚 Historial: {len(conversation_history)} mensajes")
            
            # Obtener respuesta con contexto
            response = gemini_client.get_response_with_context(
                user_message=user_message,
                conversation_history=conversation_history,
                user_name=user_name
            )
            
            # Guardar en historial
            conversation_manager.add_message(user_id, 'user', user_message)
            conversation_manager.add_message(user_id, 'assistant', response)
        
        # ================================
        # ENVIAR RESPUESTA
        # ================================
        
        # Dividir si es muy largo
        if len(response) > 4096:
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for i, chunk in enumerate(chunks):
                try:
                    await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
                except Exception:
                    # Fallback sin Markdown
                    await update.message.reply_text(chunk)
                    
                if i < len(chunks) - 1:
                    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        else:
            # Intentar con Markdown, fallback a texto plano
            try:
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logger.warning(f"⚠️ Error con Markdown, enviando texto plano: {e}")
                await update.message.reply_text(response)
        
        logger.info(f"✅ Respuesta enviada a {user_name}")
        
    except Exception as e:
        logger.error(f"❌ Error al procesar mensaje: {e}", exc_info=True)
        await update.message.reply_text(
            "Disculpa, hubo un problema al procesar tu mensaje. "
            "¿Podrías intentarlo de nuevo? Si el problema persiste, "
            "intenta usar los comandos directos como /convertir, /traducir o /letra"
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