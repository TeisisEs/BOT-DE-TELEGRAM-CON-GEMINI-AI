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

    # Mapeos simples de nombres a códigos de moneda para lenguaje natural
    name_to_code = {
        'DOLAR': 'USD', 'DOLARES': 'USD', 'DÓLAR': 'USD', 'DÓLARES': 'USD', 'DOLLAR': 'USD', 'DOLLARS': 'USD',
        'EURO': 'EUR', 'EUROS': 'EUR',
        'LIBRA': 'GBP', 'LIBRAS': 'GBP', 'POUND': 'GBP', 'POUNDS': 'GBP',
        'YEN': 'JPY', 'YENS': 'JPY',
        'PESO': 'MXN', 'PESOS': 'MXN', 'PESO MEXICANO': 'MXN', 'PESOS MEXICANOS': 'MXN',
        'CNY': 'CNY', 'YUAN': 'CNY', 'RENMINBI': 'CNY',
        'CAD': 'CAD', 'AUD': 'AUD', 'BRL': 'BRL', 'INR': 'INR', 'KRW': 'KRW', 'CHF': 'CHF'
    }

    import re

    try:
        q = query.strip()

        # Buscar cantidad: números con punto o coma, puede venir con símbolo $
        amount_match = re.search(r"([0-9]+(?:[\.,][0-9]+)?)", q)
        if not amount_match:
            return "❌ No pude encontrar una cantidad en la consulta. Ejemplo: '100 USD a EUR'"
        amount_str = amount_match.group(1).replace(',', '.')
        amount = float(amount_str)

        # Normalizar texto para buscar monedas
        q_upper = q.upper()

        # Buscar códigos de 3 letras primero (USD, EUR, MXN, etc.)
        code_matches = re.findall(r"\b([A-Z]{3})\b", q_upper)
        from_currency = None
        to_currency = None

        if len(code_matches) >= 2:
            from_currency, to_currency = code_matches[0], code_matches[1]
        elif len(code_matches) == 1:
            # Intentar inferir dirección por palabras clave 'A', 'TO', 'EN'
            if re.search(r"\bA\b|\bTO\b|\bEN\b", q_upper):
                # Si aparece 'A' o 'TO', tomar primer código como origen y el resto buscar nombre destino
                from_currency = code_matches[0]
        
        # Si no hay códigos, buscar nombres de moneda en español/inglés
        if not from_currency or not to_currency:
            # Buscar patrones 'X a Y' o 'from X to Y' donde X/Y son palabras
            # Extraer palabras que puedan ser nombres de moneda
            words = re.findall(r"\b[\wñóáéíú'-]+\b", q_upper)
            # Intentar localizar la palabra que sigue a la cantidad como posible moneda origen
            idx = None
            for i, w in enumerate(words):
                if amount_match and w == amount_str.upper().replace('.', ','):
                    idx = i
                    break
            # Fallback: buscar primera palabra no numérica cerca del número
            if idx is None:
                # encontrar el índice aproximado del número en words
                for i, w in enumerate(words):
                    if re.search(r"[0-9]", w):
                        idx = i
                        break

            cand_from = None
            cand_to = None
            if idx is not None:
                # palabra siguiente
                if idx + 1 < len(words):
                    cand_from = words[idx + 1]
                # intentar palabra después de 'A' o 'TO'
                for j in range(idx + 1, min(idx + 6, len(words))):
                    if words[j] in ('A', 'TO', 'EN') and j + 1 < len(words):
                        cand_to = words[j + 1]
                        break

            # Si no encontramos cand_to, intentar tomar la última palabra del query
            if not cand_to and len(words) >= 1:
                cand_to = words[-1]

            # Mapear candidatos por nombre
            def map_name(w):
                if not w:
                    return None
                w = w.upper().strip()
                # remover puntuación
                w = re.sub(r"[^A-ZÀ-ÿ]", '', w)
                return name_to_code.get(w)

            if cand_from:
                mapped = map_name(cand_from)
                if mapped:
                    from_currency = mapped
            if cand_to:
                mapped = map_name(cand_to)
                if mapped:
                    to_currency = mapped

        # Si aún no hay moneda destino/origen, intentar heurística: buscar dos nombres propios en el texto
        if not from_currency or not to_currency:
            # buscar nombres conocidos en el texto
            for name, code in name_to_code.items():
                if name in q_upper:
                    if not from_currency:
                        from_currency = code
                    elif not to_currency and code != from_currency:
                        to_currency = code

        if not from_currency or not to_currency:
            return "❌ No pude determinar las monedas origen/destino. Usa: '100 USD a EUR' o '/convertir 100 USD EUR'"

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
        "También acepta consultas en lenguaje natural en español o inglés, por ejemplo: "
        "'¿Cuánto son 100 dólares en euros?', 'a cuantos dolares equivale 10000 yenes', 'convert 50 GBP to MXN'. "
        "Si el usuario indica una cantidad y menciona monedas, utiliza esta herramienta."
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