"""
Script de Testing para LangChain Agent
=======================================
Verifica que todas las tools y el agente funcionen correctamente
"""

import sys
import os

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.agent_handler import intelligent_agent, should_use_agent
from utils.tools import currency_converter, translator, lyrics_finder


def test_currency_tool():
    """Test de Currency Converter Tool"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Currency Converter Tool")
    print("="*60)
    
    result = currency_converter.convert(100, "USD", "EUR")
    if "error" not in result:
        print("✅ PASSED - Conversión exitosa")
        print(f"   100 USD = {result['converted_amount']} EUR")
    else:
        print(f"❌ FAILED - {result['error']}")
    
    return "error" not in result


def test_translator_tool():
    """Test de Text Translator Tool"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Text Translator Tool")
    print("="*60)
    
    result = translator.translate("hello world", "auto", "es")
    if "error" not in result:
        print("✅ PASSED - Traducción exitosa")
        print(f"   'hello world' → '{result['translated']}'")
    else:
        print(f"❌ FAILED - {result['error']}")
    
    return "error" not in result


def test_lyrics_tool():
    """Test de Lyrics Finder Tool"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Lyrics Finder Tool")
    print("="*60)
    
    result = lyrics_finder.search_lyrics("The Beatles", "Hey Jude")
    if "error" not in result:
        print("✅ PASSED - Letra encontrada")
        print(f"   {result['lines']} líneas, {result['length']} caracteres")
    else:
        print(f"❌ FAILED - {result['error']}")
    
    return "error" not in result


def test_detection():
    """Test de detección de uso de agente"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Detección de necesidad de agente")
    print("="*60)
    
    test_cases = [
        ("convierte 100 dólares a euros", True),
        ("traduce hello world", True),
        ("letra de Bohemian Rhapsody", True),
        ("¿cómo estás?", False),
        ("explica la inteligencia artificial", False),
    ]
    
    passed = 0
    for query, expected in test_cases:
        result = should_use_agent(query)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{query}' → Agente: {result} (esperado: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(test_cases)} casos correctos")
    return passed == len(test_cases)


def test_agent():
    """Test del agente completo"""
    print("\n" + "="*60)
    print("🧪 TEST 5: LangChain Agent")
    print("="*60)
    
    if not intelligent_agent:
        print("❌ FAILED - Agente no inicializado")
        return False
    
    # Test con query que requiere currency tool
    print("\n📝 Query: 'convierte 50 dólares a euros'")
    try:
        response = intelligent_agent.run("convierte 50 dólares a euros")
        print(f"✅ Respuesta recibida ({len(response)} chars)")
        print(f"   Preview: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        return False


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "TESTING SUITE" + " "*30 + "║")
    print("║" + " "*10 + "Bot Telegram con LangChain Agent" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "Currency Tool": test_currency_tool(),
        "Translator Tool": test_translator_tool(),
        "Lyrics Tool": test_lyrics_tool(),
        "Detection Logic": test_detection(),
        "LangChain Agent": test_agent(),
    }
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:15} - {test_name}")
    
    print("\n" + "-"*60)
    print(f"TOTAL: {passed}/{total} tests pasaron ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ Tu bot está listo para la defensa del bootcamp")
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron")
        print("Revisa los errores arriba y corrige antes de la defensa")
    
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)