import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración del Bot de Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configuración de Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configuración de Weather API
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# Validar que las variables existan
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN no encontrado en .env")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY no encontrado en .env")

if not WEATHER_API_KEY:
    raise ValueError("❌ WEATHER_API_KEY no encontrado en .env")

print("✅ Configuración cargada correctamente")