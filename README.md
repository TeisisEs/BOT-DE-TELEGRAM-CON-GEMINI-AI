# 🤖 Bot de Telegram con Gemini AI y LangChain

Bot inteligente de Telegram que integra **Google Gemini AI**, **LangChain Framework** y **herramientas personalizadas** para ofrecer conversaciones naturales, información del clima, conversión de monedas, traducción y búsqueda de letras de canciones.

---

##  **Características Principales**

### ** Inteligencia Artificial**
- ✅ Conversaciones naturales con **Google Gemini AI**
- ✅ **LangChain Agent** que decide automáticamente qué herramienta usar
- ✅ Memoria conversacional por usuario (30 minutos)

### **🛠️ LangChain Tools Personalizadas**
1. **💱 CurrencyConverter** - Conversión de monedas en tiempo real
2. **🌐 TextTranslator** - Traducción automática entre idiomas
3. **🎵 LyricsFinder** - Búsqueda de letras de canciones

### ** Funcionalidades**
- 📅 Fecha y hora actual
- 🌤️ Información meteorológica (OpenWeatherMap)
- 😂 Generación de chistes con IA
- 💬 Conversaciones inteligentes con contexto
- 🔄 Detección automática de necesidad de herramientas

---

##  **Requisitos**

- Python 3.10+
- Cuenta de Telegram
- API Keys:
  - [Telegram Bot Token](https://t.me/BotFather)
  - [Google Gemini API](https://aistudio.google.com/app/apikey)
  - [OpenWeatherMap API](https://openweathermap.org/api)

---

##  **Instalación**

### **1. Clonar repositorio**
```bash
git clone https://github.com/tu-usuario/telegram-bot-gemini.git
cd telegram-bot-gemini
```

### **2. Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### **3. Instalar dependencias**
```bash
pip install -r requirements.txt
```

### **4. Configurar variables de entorno**
Copia `.env.example` a `.env` y agrega tus API keys:

```bash
cp .env.example .env
```

Edita el archivo `.env`:
```properties
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
GEMINI_API_KEY=tu_api_key_de_gemini
WEATHER_API_KEY=tu_api_key_de_openweather
```

### **5. Ejecutar el bot**
```bash
python bot.py
```

✅ El bot estará corriendo y verás:
```
 INICIANDO BOT DE TELEGRAM CON LANGCHAIN AGENT
============================================================
✅ BOT INICIADO CORRECTAMENTE
```

---

##  **Comandos Disponibles**

### **Comandos Básicos**
```
/start      - Mensaje de bienvenida
/help       - Ver ayuda completa
/fecha      - Fecha y hora actual
/clima      - Información del clima
/chiste     - Generar chiste con IA
/reset      - Reiniciar conversación
```

### **LangChain Tools (Nuevos)**
```
/convertir  - 💱 Convertir monedas
  Ejemplo: /convertir 100 USD EUR

/traducir   - 🌐 Traducir textos
  Ejemplo: /traducir hello world

/letra      - 🎵 Buscar letras de canciones
  Ejemplo: /letra The Beatles - Hey Jude
```

### **Conversación Natural**
También puedes hacer preguntas naturales sin usar comandos:
- "convierte 50 dólares a euros"
- "traduce 'good morning' al español"
- "quiero la letra de Bohemian Rhapsody"

El **LangChain Agent** detectará automáticamente qué herramienta usar.

---

##  **Arquitectura del Proyecto**

```
telegram_bot_proyecto/
│
├── 📄 bot.py                    # Archivo principal
├── 📄 config.py                 # Configuración
├── 📄 requirements.txt          # Dependencias
│
├── 📁 handlers/
│   ├── commands.py              # Comandos del bot
│   └── messages.py              # Manejo de mensajes
│
└── 📁 utils/
    ├── gemini_client.py         # Cliente Gemini AI
    ├── weather_api.py           # API del clima
    ├── conversation_manager.py  # Gestión de conversaciones
    ├── agent_handler.py         #  LangChain Agent
    │
    └── 📁 tools/                # LangChain Tools
        ├── currency_tool.py     # Conversor de monedas
        ├── translator_tool.py   # Traductor
        └── lyrics_tool.py       # Buscador de letras
```

---

##  **Testing**

### **Probar el Agent**
```bash
python -m utils.agent_handler
```

### **Probar Tools individuales**
```bash
# Currency Tool
python -m utils.tools.currency_tool

# Translator Tool
python -m utils.tools.translator_tool

# Lyrics Tool
python -m utils.tools.lyrics_tool
```

---

##  **Tecnologías Utilizadas**

| Tecnología | Uso |
|------------|-----|
| **Python 3.10+** | Lenguaje principal |
| **python-telegram-bot** | Framework del bot |
| **LangChain** | Orquestación de IA |
| **Google Gemini AI** | Modelo de lenguaje |
| **OpenWeatherMap API** | Datos meteorológicos |
| **LibreTranslate API** | Traducción de textos |
| **Lyrics.ovh API** | Letras de canciones |
| **ExchangeRate API** | Conversión de monedas |

---

##  **Proyecto Académico**

Este proyecto fue desarrollado como parte del **Bootcamp KODIGO** - Módulo de Despliegue de Proyectos de IA.

### **Cumplimiento de Requisitos**
- ✅ Bot funcional en Telegram 
- ✅ Integración LangChain + Gemini 
- ✅ Funcionalidades básicas 
- ✅ Bot local funcionando 
- ✅ **2+ LangChain Tools** personalizadas 
- ✅ **LangChain Agent** implementado 



---

##  **Autores**

- **Angel Escobar** - [@TeisisEs](https://github.com/TeisisEs)

---

##  **Licencia**

Este proyecto es de código abierto y está disponible bajo la [MIT License](LICENSE).

---

##  **Contribuciones**

Las contribuciones son bienvenidas. Para cambios importantes:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

**⭐ Si te gustó este proyecto, dale una estrella en GitHub!**