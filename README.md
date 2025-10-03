# 🤖 Bot de Telegram con Gemini AI y LangChain Tools

Bot inteligente de Telegram potenciado por **Google Gemini AI** con **LangChain Tools** personalizadas para conversión de monedas, traducción de textos y búsqueda de letras de canciones.

---

## ✨ Características

### 🧠 Inteligencia Artificial
- **Conversaciones naturales** con Google Gemini AI
- **Memoria conversacional** (30 minutos de contexto)
- **Respuestas no repetitivas** y contextuales
- Sistema anti-repetición inteligente

### 🛠️ LangChain Tools (Nivel Intermedio - 85 pts)
- 💱 **CurrencyConverter**: Conversión de monedas en tiempo real
- 🌍 **TextTranslator**: Traducción entre 25+ idiomas
- 🎵 **LyricsFinder**: Búsqueda de letras de canciones

### 📋 Funcionalidades Básicas
- 🌤️ **Información del clima** (OpenWeatherMap API)
- 📅 **Fecha y hora actual** (zona horaria configurable)
- 😂 **Generación de chistes** con IA
- 🔄 **Reset de conversación**

### 🎯 Características Técnicas
- ✅ Manejo robusto de errores
- ✅ Logging completo (consola + archivo)
- ✅ Indicadores de "escribiendo..."
- ✅ Soporte para mensajes largos (división automática)
- ✅ Formato Markdown en respuestas

---

## 📦 Instalación

### 1️⃣ Prerrequisitos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

### 2️⃣ Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/telegram-bot-gemini.git
cd telegram-bot-gemini
```

### 3️⃣ Crear Entorno Virtual

**Linux/Mac:**
```bash
python3 -m venv bot_env
source bot_env/bin/activate
```

**Windows:**
```bash
python -m venv bot_env
bot_env\Scripts\activate
```

### 4️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## 🔑 Configuración

### 1️⃣ Obtener API Keys

#### **Telegram Bot Token:**
1. Abrir Telegram y buscar `@BotFather`
2. Enviar `/newbot` y seguir instrucciones
3. Copiar el token proporcionado

#### **Gemini API Key:**
1. Ir a [Google AI Studio](https://ai.google.dev/)
2. Crear un proyecto o usar existente
3. Generar API Key (gratuita)

#### **OpenWeatherMap API Key:**
1. Registrarse en [OpenWeatherMap](https://openweathermap.org/api)
2. Obtener API Key (plan gratuito)

### 2️⃣ Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
TELEGRAM_BOT_TOKEN=tu_token_de_telegram_aqui
GEMINI_API_KEY=tu_api_key_de_gemini_aqui
WEATHER_API_KEY=tu_api_key_de_openweather_aqui
```

**⚠️ IMPORTANTE:** Nunca subir el archivo `.env` a GitHub

---

## 🚀 Uso

### Iniciar el Bot

```bash
python bot.py
```

Deberías ver:

```
==================================================
🚀 INICIANDO BOT DE TELEGRAM
==================================================

📋 Cargando módulos...
   ✅ Configuración cargada
   ✅ Gemini AI inicializado
   ✅ Weather API conectada
   ✅ LangChain Tools cargadas:
      • 💱 CurrencyConverter
      • 🌍 TextTranslator
      • 🎵 LyricsFinder

✅ BOT INICIADO CORRECTAMENTE
```

---

## 📋 Comandos Disponibles

### 🔹 Comandos Básicos

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Iniciar el bot | `/start` |
| `/help` | Ver ayuda completa | `/help` |
| `/fecha` | Fecha y hora actual | `/fecha` |
| `/clima [ciudad]` | Consultar clima | `/clima San Salvador` |
| `/chiste [categoría]` | Generar chiste | `/chiste programacion` |
| `/reset` | Reiniciar conversación | `/reset` |

### 🆕 Comandos con LangChain Tools

#### 💱 Convertir Monedas

```
/convertir [cantidad] [moneda_origen] [moneda_destino]
```

**Ejemplos:**
```
/convertir 100 USD EUR
/convertir 50 MXN USD
/convertir 1000 JPY GBP
```

**Monedas soportadas:** USD, EUR, GBP, JPY, CNY, MXN, CAD, AUD, BRL, INR, KRW, CHF, y más

#### 🌍 Traducir Textos

```
/traducir [texto]
```

**Ejemplos:**
```
/traducir hello world
/traducir buenos días
/traducir how are you doing today
```

**Idiomas soportados:** Español, Inglés, Francés, Alemán, Italiano, Portugués, Ruso, Chino, Japonés, Coreano, Árabe, Hindi, y más (25+ idiomas)

**Nota:** Detecta automáticamente el idioma origen y traduce inteligentemente:
- Español → Inglés
- Inglés → Español

#### 🎵 Buscar Letras de Canciones

```
/letra [Artista] - [Canción]
```

**Ejemplos:**
```
/letra Bad Bunny - Tití Me Preguntó
/letra The Beatles - Hey Jude
/letra Shakira - Waka Waka
/letra Queen - Bohemian Rhapsody
```

**Nota:** Usa el guion ( - ) para separar artista y canción

---

## 💬 Conversación con IA

Simplemente escribe cualquier mensaje y el bot responderá usando **Google Gemini AI**:

```
Usuario: ¿Qué es la inteligencia artificial?
Bot: La inteligencia artificial (IA) es...

Usuario: Dame un ejemplo práctico
Bot: [Responde con contexto de la conversación anterior]
```

**Características:**
- ✅ Recuerda la conversación (30 minutos)
- ✅ Respuestas contextuales
- ✅ No repite información
- ✅ Tono natural y amigable

---

## 🏗️ Estructura del Proyecto

```
telegram_bot_proyecto/
├── .env                          # Variables de entorno (NO subir a Git)
├── .gitignore                    # Archivos ignorados por Git
├── bot.py                        # Archivo principal
├── config.py                     # Configuración y validación
├── requirements.txt              # Dependencias del proyecto
├── bot.log                       # Archivo de logs
├── README.md                     # Este archivo
│
├── handlers/                     # Manejadores del bot
│   ├── __init__.py
│   ├── commands.py               # Comandos del bot
│   └── messages.py               # Manejo de mensajes
│
├── utils/                        # Utilidades
│   ├── __init__.py
│   ├── gemini_client.py          # Cliente de Gemini AI
│   ├── weather_api.py            # Cliente de OpenWeatherMap
│   ├── conversation_manager.py   # Gestor de conversaciones
│   │
│   └── tools/                    # 🆕 LangChain Tools
│       ├── __init__.py
│       ├── currency_tool.py      # 💱 Conversor de monedas
│       ├── translator_tool.py    # 🌍 Traductor de textos
│       └── lyrics_tool.py        # 🎵 Buscador de letras
```

---

## 🧪 Testing Local

### Probar las LangChain Tools individualmente:

```bash
# Probar Currency Tool
python utils/tools/currency_tool.py

# Probar Translator Tool
python utils/tools/translator_tool.py

# Probar Lyrics Tool
python utils/tools/lyrics_tool.py
```

---

## 🎯 Nivel de Implementación

### ✅ Nivel Básico (70 puntos)
- ✅ Bot funcional en Telegram
- ✅ Integración con LangChain + Gemini AI
- ✅ Comandos básicos (/start, /help, /fecha, /clima, /chiste)
- ✅ Bot funcionando localmente

### ✅ Nivel Intermedio (85 puntos)
- ✅ **3 LangChain Tools personalizadas:**
  - 💱 CurrencyConverter
  - 🌍 TextTranslator
  - 🎵 LyricsFinder
- ✅ Tools encapsuladas con `Tool` class de LangChain
- ✅ Funcionalidades originales y útiles

### 🔜 Nivel Avanzado (100 puntos)
- ⏳ Implementar LangChain Agent
- ⏳ El agente decide automáticamente qué tool usar
- ⏳ Memoria conversacional integrada con el agente

---

## 🐛 Troubleshooting

### Error: "TELEGRAM_BOT_TOKEN no encontrado"
- Verificar que el archivo `.env` existe
- Verificar que las variables están correctamente escritas
- Reiniciar el bot después de modificar `.env`

### Error: "ModuleNotFoundError"
- Activar el entorno virtual: `source bot_env/bin/activate`
- Reinstalar dependencias: `pip install -r requirements.txt`

### Bot no responde en Telegram
- Verificar que el bot está ejecutándose (consola debe mostrar logs)
- Verificar token con @BotFather: `/token`
- Revisar logs en `bot.log`

### Error en traducción/conversión/letras
- Verificar conexión a internet
- Algunas APIs gratuitas tienen límites de uso
- Revisar logs para más detalles

---

## 📊 APIs Utilizadas

| Servicio | Propósito | Límite Gratuito |
|----------|-----------|-----------------|
| **Google Gemini AI** | Conversaciones IA | 15 requests/min |
| **OpenWeatherMap** | Información del clima | 1,000 calls/día |
| **ExchangeRate API** | Conversión de monedas | 1,500 requests/mes |
| **LibreTranslate** | Traducción de textos | Ilimitado |
| **Lyrics.ovh** | Letras de canciones | Ilimitado |

---

## 🚀 Deployment (Opcional - Puntos Bonus)

### Opción 1: Render.com (Recomendado)

1. Crear cuenta en [Render.com](https://render.com)
2. Conectar repositorio GitHub
3. Crear Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
4. Configurar variables de entorno en dashboard
5. Deploy! 🎉

### Opción 2: Railway.app

1. Crear cuenta en [Railway.app](https://railway.app)
2. Nuevo proyecto desde GitHub
3. Configurar variables de entorno
4. Railway detecta automáticamente Python y deploy

---

## 🎓 Tecnologías Utilizadas

- **Python 3.9+**
- **python-telegram-bot 20.7** - Framework para bots de Telegram
- **LangChain** - Framework para aplicaciones con LLMs
- **Google Gemini AI** - Modelo de IA conversacional
- **OpenWeatherMap API** - Datos meteorológicos
- **ExchangeRate API** - Tasas de cambio de monedas
- **LibreTranslate** - Traducción automática
- **Lyrics.ovh** - Base de datos de letras

---

## 👨‍💻 Autor

**Nombre:** [Tu Nombre]  
**Bootcamp:** KODIGO  
**Proyecto:** Tarea - Bot de Telegram con Gemini AI  
**Fecha:** [Fecha actual]

---

## 📝 Licencia

Este proyecto fue creado con fines educativos para el Bootcamp KODIGO.

---

## 🙏 Agradecimientos

- Google AI por Gemini API
- Anthropic por la documentación de LangChain
- Comunidad de python-telegram-bot
- Bootcamp KODIGO

---

## 📞 Contacto

Si tienes preguntas o sugerencias:
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Telegram: @tu_usuario
- Email: tu@email.com

---

**⭐ Si te gustó el proyecto, dale una estrella en GitHub!**