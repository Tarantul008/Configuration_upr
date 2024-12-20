## Задача 1

Написать программу на Питоне, которая транслирует граф зависимостей civgraph в makefile в духе примера выше. Для мало знакомых с Питоном используется упрощенный вариант civgraph: civgraph.json.

```
import json

def parse_civgraph(civgraph_file):
    with open(civgraph_file, 'r') as file:
        data = json.load(file)
    return data

def generate_makefile(data, output_file):
    with open(output_file, 'w') as file:
        for target, dependencies in data.items():
            dep_str = " ".join(dependencies) if dependencies else ""
            file.write(f"{target}: {dep_str}\n")
            file.write(f"\t@echo {target}\n\n")

def main():
    output_file = "Makefile"
    civgraph_file = "civgraph.json"

    data = parse_civgraph(civgraph_file)

    generate_makefile(data, output_file)
    print(f"Makefile был сгенерирован в {output_file}")

if __name__ == "__main__":
    main()
```

Команды для запуска:

python main.py 

make mathematics

![image](https://github.com/user-attachments/assets/0534804f-2e6d-4a72-961c-535aeda592da)


## Задача 2

```
import json
import os

TASKS_FILE = "tasks.txt"


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()


def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        f.write('\n'.join(tasks))


def load_dependency_graph(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке файла {filename}: {e}")
        return {}


def generate_makefile(dependency_graph, target_task):
    visited_tasks = set()
    tasks_to_process = []
    completed_tasks = load_tasks()

    def process_task(task):
        if task in visited_tasks or task in completed_tasks:
            return
        visited_tasks.add(task)
        for dependency in dependency_graph.get(task, []):
            process_task(dependency)
        tasks_to_process.append(task)

    process_task(target_task)

    if not tasks_to_process:
        print("Все задачи уже были выполнены.")
    else:
        for task in tasks_to_process:
            if task not in completed_tasks:
                print(f"{task}")
                completed_tasks.add(task)

        save_tasks(completed_tasks)


if __name__ == '__main__':
    # Загружаем граф зависимостей из файла
    dependency_graph = load_dependency_graph('civgraph.json')

    if not dependency_graph:
        print("Не удалось загрузить граф зависимостей. Программа завершена.")
    else:
        target_task = input('>make ')
        generate_makefile(dependency_graph, target_task)

```

Команды для запуска:

python main.py 

>make mathematics

![image](https://github.com/user-attachments/assets/90f9028a-84c4-4673-8afa-01dba3f56799)


## Задача 3

```
import json
import os

TASKS_FILE = "completed_tasks.txt"


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()


def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        f.write('\n'.join(tasks))


def load_dependency_graph(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке {filename}: {e}")
        return {}


def generate_makefile(dependency_graph, target_task):
    visited_tasks = set()
    tasks_to_process = []
    completed_tasks = load_tasks()

    def process_task(task):
        if task in visited_tasks or task in completed_tasks:
            return
        visited_tasks.add(task)
        for dependency in dependency_graph.get(task, []):
            process_task(dependency)
        tasks_to_process.append(task)

    process_task(target_task)

    if not tasks_to_process:
        print("Все задачи уже были выполнены.")
    else:
        for task in tasks_to_process:
            if task not in completed_tasks:
                print(f"{task}")
                completed_tasks.add(task)

        save_tasks(completed_tasks)


def clean():
    if os.path.exists(TASKS_FILE):
        os.remove(TASKS_FILE)
        print(f"Файл с завершенными задачами {TASKS_FILE} удален.")
    else:
        print("Файл с завершенными задачами не найден. Нечего очищать.")


if __name__ == '__main__':
    dependency_graph = load_dependency_graph('civgraph.json')

    if not dependency_graph:
        print("Не удалось загрузить граф зависимостей. Программа завершена.")
    else:
        action = input('Выберите действие make/clean: ')

        if action == 'make':
            target_task = input('>make ')
            generate_makefile(dependency_graph, target_task)
        elif action == 'clean':
            clean()
        else:
            print("Неизвестное действие. Пожалуйста, введите 'build' или 'clean'.")
```

Команды для запуска:

python main.py

make clean

make mathematics

![image](https://github.com/user-attachments/assets/0d600df8-e836-4756-a684-4903ff3cc6f2)
