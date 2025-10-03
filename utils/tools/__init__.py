"""
LangChain Tools Module
======================

Este módulo contiene las herramientas personalizadas (Tools) para usar con LangChain.

Tools disponibles:
- CurrencyConverter: Conversión de monedas en tiempo real
- TextTranslator: Traducción de textos entre idiomas
- LyricsFinder: Búsqueda de letras de canciones

Uso básico:
-----------
from utils.tools import currency_tool, translator_tool, lyrics_tool

# Lista de todas las tools
all_tools = [currency_tool, translator_tool, lyrics_tool]
"""

from .currency_tool import currency_tool, currency_converter
from .translator_tool import translator_tool, translator
from .lyrics_tool import lyrics_tool, lyrics_finder

# Exportar todas las tools como lista para fácil uso
all_tools = [currency_tool, translator_tool, lyrics_tool]

# Exportar instancias individuales
__all__ = [
    'currency_tool',
    'translator_tool', 
    'lyrics_tool',
    'all_tools',
    'currency_converter',
    'translator',
    'lyrics_finder'
]