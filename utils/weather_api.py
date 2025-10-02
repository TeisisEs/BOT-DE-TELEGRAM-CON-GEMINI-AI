import logging
import requests
from config import WEATHER_API_KEY

logger = logging.getLogger(__name__)

class WeatherAPI:
    """
    Cliente para obtener información del clima usando OpenWeatherMap API
    """
    
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    
    def get_current_weather(self, city: str) -> dict:
        """
        Obtiene el clima actual de una ciudad usando OpenWeatherMap
        
        Args:
            city: Nombre de la ciudad
            
        Returns:
            Diccionario con información del clima o None si hay error
        """
        try:
            # Construir URL de la API de OpenWeatherMap
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",  # Celsius
                "lang": "es"  # Respuestas en español
            }
            
            logger.info(f"Consultando clima para: {city}")
            
            # Hacer petición a la API
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extraer información relevante de OpenWeatherMap
            weather_info = {
                "ciudad": data["name"],
                "pais": data["sys"]["country"],
                "temperatura": round(data["main"]["temp"], 1),
                "sensacion": round(data["main"]["feels_like"], 1),
                "condicion": data["weather"][0]["description"].capitalize(),
                "icono": data["weather"][0]["icon"],
                "humedad": data["main"]["humidity"],
                "viento_kph": round(data["wind"]["speed"] * 3.6, 1),  # m/s a km/h
                "viento_dir": self._get_wind_direction(data["wind"].get("deg", 0)),
                "presion_mb": data["main"]["pressure"],
                "visibilidad_km": round(data.get("visibility", 0) / 1000, 1),
                "temp_min": round(data["main"]["temp_min"], 1),
                "temp_max": round(data["main"]["temp_max"], 1),
                "nubosidad": data["clouds"]["all"]
            }
            
            logger.info(f"Clima obtenido: {weather_info['ciudad']}, {weather_info['temperatura']}°C")
            return weather_info
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                logger.warning(f"Ciudad no encontrada: {city}")
                return {"error": "Ciudad no encontrada"}
            elif response.status_code == 401:
                logger.error("API Key inválida")
                return {"error": "Error de autenticación - Verifica tu API Key"}
            else:
                logger.error(f"Error HTTP: {e}")
                return {"error": "Error al consultar la API"}
                
        except requests.exceptions.Timeout:
            logger.error("Timeout al consultar OpenWeatherMap")
            return {"error": "Tiempo de espera agotado"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {e}")
            return {"error": "Error de conexión"}
            
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return {"error": "Error inesperado"}
    
    
    def _get_wind_direction(self, degrees: int) -> str:
        """
        Convierte grados a dirección cardinal
        """
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
        index = round(degrees / 45) % 8
        return directions[index]
    
    
    def format_weather_message(self, weather_data: dict) -> str:
        """
        Formatea la información del clima en un mensaje legible
        
        Args:
            weather_data: Diccionario con datos del clima
            
        Returns:
            Mensaje formateado
        """
        if "error" in weather_data:
            if weather_data["error"] == "Ciudad no encontrada":
                return "No pude encontrar esa ciudad. Verifica el nombre e intenta de nuevo."
            else:
                return f"{weather_data['error']}. Por favor intenta más tarde."
        
        # Determinar emoji según la condición
        condicion_lower = weather_data["condicion"].lower()
        if "despejado" in condicion_lower or "claro" in condicion_lower:
            emoji = "☀️"
        elif "nube" in condicion_lower:
            emoji = "☁️"
        elif "lluvia" in condicion_lower or "llovizna" in condicion_lower:
            emoji = "🌧️"
        elif "tormenta" in condicion_lower:
            emoji = "⛈️"
        elif "nieve" in condicion_lower:
            emoji = "❄️"
        elif "niebla" in condicion_lower or "neblina" in condicion_lower:
            emoji = "🌫️"
        else:
            emoji = "🌤️"
        
        message = f"""
{emoji} **CLIMA EN {weather_data['ciudad'].upper()}, {weather_data['pais']}**

🌡️ **Temperatura:** {weather_data['temperatura']}°C
🤔 **Sensación térmica:** {weather_data['sensacion']}°C
☁️ **Condición:** {weather_data['condicion']}
📊 **Min/Max:** {weather_data['temp_min']}°C / {weather_data['temp_max']}°C

💧 **Humedad:** {weather_data['humedad']}%
💨 **Viento:** {weather_data['viento_kph']} km/h ({weather_data['viento_dir']})
👁️ **Visibilidad:** {weather_data['visibilidad_km']} km
📊 **Presión:** {weather_data['presion_mb']} mb
☁️ **Nubosidad:** {weather_data['nubosidad']}%

_Powered by OpenWeatherMap_
        """
        
        return message.strip()


# Crear instancia global
weather_api = WeatherAPI()