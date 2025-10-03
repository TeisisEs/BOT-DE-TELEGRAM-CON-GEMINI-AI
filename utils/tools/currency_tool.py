import logging
import requests
from typing import Optional
from langchain.tools import Tool

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """
    Conversor de monedas usando API gratuita
    API: exchangerate-api.com (1500 requests/mes gratis)
    """
    
    def __init__(self):
        # API gratuita sin necesidad de key
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        
        # Monedas más comunes con símbolos
        self.currency_symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
            'CNY': '¥', 'MXN': '$', 'CAD': 'C$', 'AUD': 'A$',
            'BRL': 'R$', 'INR': '₹', 'KRW': '₩', 'CHF': 'Fr'
        }
        
        logger.info("✅ CurrencyConverter inicializado")
    
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> dict:
        """
        Convierte una cantidad de una moneda a otra
        
        Args:
            amount: Cantidad a convertir
            from_currency: Moneda origen (ej: USD)
            to_currency: Moneda destino (ej: EUR)
            
        Returns:
            Diccionario con resultado o error
        """
        try:
            # Normalizar códigos de moneda
            from_currency = from_currency.upper().strip()
            to_currency = to_currency.upper().strip()
            
            logger.info(f"💱 Convirtiendo {amount} {from_currency} → {to_currency}")
            
            # Obtener tasas de cambio
            response = requests.get(
                f"{self.base_url}/{from_currency}",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Verificar que la moneda destino existe
            if to_currency not in data['rates']:
                return {
                    'error': f"Moneda '{to_currency}' no encontrada. Usa códigos como USD, EUR, GBP, etc."
                }
            
            # Calcular conversión
            rate = data['rates'][to_currency]
            converted_amount = amount * rate
            
            # Formatear resultado
            result = {
                'amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'rate': round(rate, 4),
                'converted_amount': round(converted_amount, 2),
                'from_symbol': self.currency_symbols.get(from_currency, ''),
                'to_symbol': self.currency_symbols.get(to_currency, ''),
                'date': data.get('date', 'N/A')
            }
            
            logger.info(f"✅ Conversión exitosa: {amount} {from_currency} = {converted_amount} {to_currency}")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Error HTTP en conversión: {e}")
            return {'error': f"Moneda '{from_currency}' no válida o no encontrada"}
            
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout en API de monedas")
            return {'error': "Tiempo de espera agotado. Intenta de nuevo."}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de conexión: {e}")
            return {'error': "Error de conexión con el servicio de monedas"}
            
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return {'error': f"Error al convertir monedas: {str(e)}"}
    
    
    def format_result(self, result: dict) -> str:
        """
        Formatea el resultado de conversión en mensaje legible
        
        Args:
            result: Diccionario con datos de conversión
            
        Returns:
            Mensaje formateado
        """
        if 'error' in result:
            return f"❌ {result['error']}"
        
        from_symbol = result['from_symbol']
        to_symbol = result['to_symbol']
        
        message = f"""
💱 **CONVERSIÓN DE MONEDAS**

**Cantidad original:**
{from_symbol}{result['amount']:,.2f} {result['from_currency']}

**Resultado:**
{to_symbol}{result['converted_amount']:,.2f} {result['to_currency']}

📊 **Tasa de cambio:** 1 {result['from_currency']} = {result['rate']} {result['to_currency']}
📅 **Fecha:** {result['date']}

_Tasas actualizadas en tiempo real_
        """
        
        return message.strip()
    
    
    def get_popular_currencies(self) -> str:
        """
        Retorna lista de monedas más populares
        """
        currencies = """
💱 **Monedas Más Comunes:**

🇺🇸 USD - Dólar estadounidense
🇪🇺 EUR - Euro
🇬🇧 GBP - Libra esterlina
🇯🇵 JPY - Yen japonés
🇨🇳 CNY - Yuan chino
🇲🇽 MXN - Peso mexicano
🇨🇦 CAD - Dólar canadiense
🇦🇺 AUD - Dólar australiano
🇧🇷 BRL - Real brasileño
🇮🇳 INR - Rupia india
🇰🇷 KRW - Won surcoreano
🇨🇭 CHF - Franco suizo
        """
        return currencies.strip()


# ============================================
# CREAR LANGCHAIN TOOL
# ============================================

def convert_currency_function(query: str) -> str:
    """
    Función wrapper para usar con LangChain Tool
    
    Formatos aceptados:
    - "100 USD to EUR"
    - "50 MXN EUR"
    - "convert 200 GBP to JPY"
    
    Args:
        query: String con la consulta de conversión
        
    Returns:
        Resultado formateado como string
    """
    converter = CurrencyConverter()
    
    try:
        # Parsear query (formatos flexibles)
        query = query.upper().replace('TO', '').replace('CONVERT', '').strip()
        parts = query.split()
        
        # Intentar extraer: amount from_currency to_currency
        if len(parts) < 3:
            return "❌ Formato incorrecto. Usa: '100 USD EUR' o '100 USD to EUR'"
        
        amount = float(parts[0])
        from_currency = parts[1]
        to_currency = parts[2] if len(parts) > 2 else parts[-1]
        
        # Realizar conversión
        result = converter.convert(amount, from_currency, to_currency)
        return converter.format_result(result)
        
    except ValueError:
        return "❌ Cantidad inválida. Debe ser un número. Ejemplo: '100 USD EUR'"
    except Exception as e:
        logger.error(f"Error en convert_currency_function: {e}")
        return f"❌ Error al procesar conversión: {str(e)}"


# Crear la Tool de LangChain
currency_tool = Tool(
    name="CurrencyConverter",
    description=(
        "Convierte cantidades entre diferentes monedas usando tasas actualizadas en tiempo real. "
        "Formato de entrada: 'CANTIDAD MONEDA_ORIGEN MONEDA_DESTINO' (ej: '100 USD EUR'). "
        "Soporta códigos de moneda como USD, EUR, GBP, JPY, MXN, CAD, AUD, BRL, INR, etc. "
        "Útil para conversiones de dinero y tasas de cambio actuales."
    ),
    func=convert_currency_function
)


# Instancia global para uso directo
currency_converter = CurrencyConverter()


if __name__ == "__main__":
    # Testing
    converter = CurrencyConverter()
    
    # Prueba 1
    result = converter.convert(100, "USD", "EUR")
    print(converter.format_result(result))
    print("\n" + "="*50 + "\n")
    
    # Prueba 2
    result = converter.convert(50, "MXN", "USD")
    print(converter.format_result(result))
    print("\n" + "="*50 + "\n")
    
    # Prueba 3 - usando la tool
    print("Testing LangChain Tool:")
    print(convert_currency_function("100 USD EUR"))