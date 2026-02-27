#!/usr/bin/env python3
"""
AUGUR Enterprise Platform - Тест всех сервисов
Запустите после docker-compose up
"""

import requests
import json
import time
from datetime import datetime

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(msg):
    print(f"{Colors.BLUE}▶ {msg}{Colors.END}")

def print_ok(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warn(msg):
    print(f"{Colors.YELLOW}⚠️ {msg}{Colors.END}")

# Список сервисов для проверки
SERVICES = [
    ("API Gateway", "http://localhost:8000/health"),
    ("Agent Service", "http://localhost:8001/health"),
    ("Orchestration", "http://localhost:8002/health"),
    ("Memory Service", "http://localhost:8003/health"),
    ("Governance", "http://localhost:8004/health"),
    ("Conflict Resolution", "http://localhost:8005/health"),
    ("Value Discovery", "http://localhost:8006/health"),
    ("Quantum Collective", "http://localhost:8007/health"),
    ("Frontend", "http://localhost:3000"),
    ("pgAdmin", "http://localhost:5050"),
    ("Neo4j", "http://localhost:7474")
]

def test_service(name, url):
    """Проверка одного сервиса"""
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            print_ok(f"{name:20} - работает (порт {url.split(':')[-1].split('/')[0]})")
            return True
        else:
            print_error(f"{name:20} - ошибка {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"{name:20} - не запущен")
        return False
    except Exception as e:
        print_error(f"{name:20} - ошибка: {str(e)[:50]}")
        return False

def test_api():
    """Тестирование API"""
    print_step("\nТестирование API...")
    
    # 1. Создание агента
    try:
        agent_data = {
            "name": "Test Agent",
            "type": "assistant",
            "description": "Test agent for platform verification",
            "capabilities": ["text-generation", "code-analysis"],
            "config": {"model": "gpt-4", "temperature": 0.7}
        }
        
        response = requests.post(
            "http://localhost:8001/agents",
            json=agent_data,
            timeout=5
        )
        
        if response.status_code == 200:
            agent = response.json()
            print_ok(f"Создан агент: {agent.get('name')} (ID: {agent.get('id')[:8]}...)")
            agent_id = agent.get('id')
        else:
            print_error(f"Не удалось создать агента: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка при создании агента: {str(e)}")
        return False
    
    # 2. Получение списка агентов
    try:
        response = requests.get("http://localhost:8001/agents", timeout=3)
        if response.status_code == 200:
            agents = response.json()
            print_ok(f"Получен список агентов: {len(agents)} шт.")
        else:
            print_error("Не удалось получить список агентов")
    except Exception as e:
        print_error(f"Ошибка при получении списка: {str(e)}")
    
    # 3. Проверка API Gateway
    try:
        response = requests.get("http://localhost:8000/", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print_ok(f"API Gateway: {data.get('service')} v{data.get('version')}")
        else:
            print_error("API Gateway не отвечает")
    except Exception as e:
        print_error(f"Ошибка API Gateway: {str(e)}")
    
    return True

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🧪 AUGUR Enterprise Platform - Тестирование                ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    print_step(f"Время тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_step("Проверка доступности сервисов...\n")
    
    # Проверяем все сервисы
    results = []
    for name, url in SERVICES:
        results.append(test_service(name, url))
    
    # Статистика
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\n{Colors.BLUE}📊 Статистика:{Colors.END}")
    print(f"   Всего сервисов: {total}")
    print(f"   {Colors.GREEN}Работает: {passed}{Colors.END}")
    if failed > 0:
        print(f"   {Colors.RED}Не работает: {failed}{Colors.END}")
    
    # Если основные сервисы работают, тестируем API
    if passed >= 3:  # Хотя бы 3 сервиса работают
        test_api()
    else:
        print_warn("\n⚠️ Слишком мало сервисов запущено. Запустите платформу:")
        print("   make -f Makefile.prod up-prod")
    
    print(f"\n{Colors.BLUE}📋 Доступные интерфейсы:{Colors.END}")
    print("   • Фронтенд:    http://localhost:3000")
    print("   • API Gateway: http://localhost:8000/docs")
    print("   • pgAdmin:     http://localhost:5050 (admin@augur.com / admin)")
    print("   • Neo4j:       http://localhost:7474 (neo4j / password)")
    
    print("\n" + "="*60)
    if failed == 0:
        print(f"{Colors.GREEN}✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Платформа работает.{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️ Тестирование завершено. {failed} сервисов не отвечают.{Colors.END}")
    print("="*60)

if __name__ == "__main__":
    main()
