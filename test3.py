"""
Script de Testing para el Agente LangChain
==========================================
Prueba las funcionalidades del agente sin necesidad de Telegram
"""

import sys
import os

# Agregar path del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.agent_handler import intelligent_agent, should_use_agent
from utils.tools import currency_converter, translator, lyrics_finder


def test_detection():
    """
    Prueba la detección de cuándo usar el agente
    """
    print("\n" + "="*70)
    print("🧪 TESTING: DETECCIÓN DE HERRAMIENTAS")
    print("="*70)
    
    test_queries = [
        # Currency
        ("convierte 100 dólares a euros", True),
        ("cuánto es 50 USD en MXN", True),
        ("precio del dólar en pesos", True),
        
        # Translation
        ("traduce hello world al español", True),
        ("cómo se dice good morning en español", True),
        ("qué significa bonjour", True),
        
        # Lyrics
        ("letra de Bohemian Rhapsody", True),
        ("busca la canción Hey Jude", True),
        ("quiero la letra de Imagine", True),
        
        # Normal (no debe usar agente)
        ("hola, cómo estás", False),
        ("cuéntame un chiste", False),
        ("qué es la inteligencia artificial", False),
    ]
    
    correct = 0
    total = len(test_queries)
    
    for query, expected in test_queries:
        result = should_use_agent(query)
        status = "✅" if result == expected else "❌"
        correct += (result == expected)
        
        print(f"{status} '{query}'")
        print(f"   Esperado: {expected}, Obtenido: {result}")
    
    print(f"\n📊 Resultado: {correct}/{total} correctos ({correct/total*100:.1f}%)")


def test_tools_directly():
    """
    Prueba las tools directamente (sin agente)
    """
    print("\n" + "="*70)
    print("🧪 TESTING: TOOLS DIRECTAMENTE")
    print("="*70)
    
    # Test 1: Currency
    print("\n1️⃣ Currency Converter:")
    print("-" * 50)
    result = currency_converter.convert(100, "USD", "EUR")
    print(currency_converter.format_result(result))
    
    # Test 2: Translator
    print("\n2️⃣ Translator:")
    print("-" * 50)
    result = translator.translate("Hello, how are you?", "en", "es")
    print(translator.format_result(result))
    
    # Test 3: Lyrics
    print("\n3️⃣ Lyrics Finder:")
    print("-" * 50)
    result = lyrics_finder.search_lyrics("The Beatles", "Hey Jude")
    print(lyrics_finder.format_result(result, max_lines=15))


def test_agent_queries():
    """
    Prueba el agente con queries reales
    """
    print("\n" + "="*70)
    print("🧪 TESTING: AGENTE CON QUERIES NATURALES")
    print("="*70)
    
    if not intelligent_agent:
        print("❌ Agente no disponible")
        return
    
    test_queries = [
        "convierte 100 dólares a euros",
        "traduce 'good morning' al español",
        "cuánto es 50 pesos mexicanos en dólares",
        # "letra de Imagine de John Lennon",  # Comentado porque puede ser largo
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {query}")
        print('-'*70)
        
        try:
            response = intelligent_agent.run(query)
            print(f"✅ Respuesta:\n{response}")
        except Exception as e:
            print(f"❌ Error: {e}")


def interactive_mode():
    """
    Modo interactivo para probar queries manualmente
    """
    print("\n" + "="*70)
    print("🤖 MODO INTERACTIVO")
    print("="*70)
    print("Escribe 'salir' para terminar\n")
    
    if not intelligent_agent:
        print("❌ Agente no disponible")
        return
    
    while True:
        try:
            query = input("Tu query: ").strip()
            
            if query.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta luego!")
                break
            
            if not query:
                continue
            
            # Mostrar si usará agente
            use_agent = should_use_agent(query)
            print(f"🔍 Usar agente: {'Sí' if use_agent else 'No'}")
            
            if use_agent:
                print("🤖 Procesando con agente...")
                response = intelligent_agent.run(query)
                print(f"\n✅ Respuesta:\n{response}\n")
            else:
                print("💭 Esta query usaría Gemini directo (no agente)\n")
            
            print("-" * 70)
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


def main():
    """
    Función principal del script de testing
    """
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║          🧪 TESTING DE AGENTE LANGCHAIN 🧪                 ║
    ║                                                            ║
    ║  Este script prueba el agente y las tools sin Telegram    ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n📋 MENÚ DE TESTING:")
        print("1. Test de detección (should_use_agent)")
        print("2. Test de tools directamente")
        print("3. Test de agente con queries")
        print("4. Modo interactivo")
        print("5. Ejecutar todos los tests")
        print("0. Salir")
        
        choice = input("\nElige una opción (0-5): ").strip()
        
        if choice == "1":
            test_detection()
        elif choice == "2":
            test_tools_directly()
        elif choice == "3":
            test_agent_queries()
        elif choice == "4":
            interactive_mode()
        elif choice == "5":
            test_detection()
            test_tools_directly()
            test_agent_queries()
        elif choice == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")