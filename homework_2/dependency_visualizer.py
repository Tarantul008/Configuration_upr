#!/usr/bin/env python3
import argparse
import subprocess
import sys
import urllib.request
import urllib.error
import json
from typing import Dict, List, Set
import tempfile
import os
import re
from datetime import datetime

def parse_arguments():
    parser = argparse.ArgumentParser(description='Визуализатор зависимостей Python-пакетов.')
    parser.add_argument('--visualizer', type=str, required=True, help='Путь к программе для визуализации графов (plantuml.jar).')
    parser.add_argument('--package', type=str, required=True, help='Имя анализируемого пакета.')
    parser.add_argument('--max-depth', type=int, default=3, help='Максимальная глубина анализа зависимостей.')
    parser.add_argument('--repository', type=str, required=True, help='URL-адрес репозитория.')
    return parser.parse_args()

def fetch_package_info(package_name: str) -> Dict:
    url = f'https://pypi.org/pypi/{package_name}/json'
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = response.read()
                return json.loads(data)
            else:
                print(f"Ошибка: Не удалось получить информацию о пакете '{package_name}'. HTTP статус: {response.status}")
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} при попытке получить пакет '{package_name}'.")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason} при попытке получить пакет '{package_name}'.")
        sys.exit(1)

def extract_dependencies(package_info: Dict) -> List[str]:
    info = package_info.get('info', {})
    requires_dist = info.get('requires_dist', [])
    dependencies = []
    if not requires_dist:
        return dependencies
    for dep in requires_dist:
        # Удаляем условия после ';'
        dep = dep.split(';')[0].strip()
        # Используем регулярное выражение для извлечения имени пакета
        match = re.match(r'^([A-Za-z0-9_\-\.]+)', dep)
        if match:
            dep_name = match.group(1)
            dependencies.append(dep_name)
            print(f"Извлечена зависимость: '{dep_name}' из строки '{dep}'")
        else:
            print(f"Не удалось извлечь имя пакета из строки зависимости: '{dep}'")
    return dependencies

def build_dependency_graph(package_name: str, max_depth: int, repository: str) -> Dict[str, Set[str]]:
    graph = {}
    visited = set()

    def dfs(current_package: str, depth: int):
        if depth > max_depth:
            print(f"Достигнута максимальная глубина ({max_depth}) для пакета '{current_package}'.")
            return
        if current_package in visited:
            print(f"Пакет '{current_package}' уже был обработан. Пропуск.")
            return
        print(f"Обработка пакета '{current_package}' на глубине {depth}.")
        visited.add(current_package)
        package_info = fetch_package_info(current_package)
        dependencies = extract_dependencies(package_info)
        graph[current_package] = set(dependencies)
        for dep in dependencies:
            dfs(dep, depth + 1)

    dfs(package_name, 1)
    return graph

def generate_plantuml(graph: Dict[str, Set[str]], repository: str) -> str:
    plantuml = ["@startuml"]
    plantuml.append(f"title Зависимости пакета с репозиторием {repository}")
    for package, deps in graph.items():
        for dep in deps:
            plantuml.append(f'"{package}" --> "{dep}"')
    plantuml.append("@enduml")
    return "\n".join(plantuml)

def visualize_graph(plantuml_code: str, visualizer_path: str, output_directory: str, package_name: str):
    # Создаём уникальное имя файла на основе имени пакета и текущего времени
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    plantuml_filename = f"dependency_graph_{package_name}_{timestamp}.puml"
    plantuml_path = os.path.join(output_directory, plantuml_filename)
    
    # Сохраняем PlantUML код в файл
    with open(plantuml_path, 'w', encoding='utf-8') as f:
        f.write(plantuml_code)
    print(f"Файл PlantUML создан: {plantuml_path}")

    # Определяем путь для выходного изображения
    output_image = os.path.splitext(plantuml_path)[0] + ".png"
    
    try:
        # Генерируем изображение с помощью PlantUML
        print(f"Запуск PlantUML: java -jar {visualizer_path} {plantuml_path}")
        subprocess.run(['java', '-jar', visualizer_path, plantuml_path], check=True)
        print(f"Визуализация успешно завершена. Изображение сохранено как '{output_image}'.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при вызове визуализатора: {e}")
    finally:
        # Удаляем .puml файл после генерации изображения
        try:
            os.remove(plantuml_path)
            print(f"Временный файл {plantuml_path} удалён.")
        except OSError as e:
            print(f"Не удалось удалить временный файл {plantuml_path}: {e}")

def main():
    args = parse_arguments()
    
    # Определяем директорию, где находится скрипт
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    graph = build_dependency_graph(args.package, args.max_depth, args.repository)
    plantuml_code = generate_plantuml(graph, args.repository)
    visualize_graph(plantuml_code, args.visualizer, script_directory, args.package)

if __name__ == '__main__':
    main()
