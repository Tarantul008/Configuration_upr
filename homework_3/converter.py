#!/usr/bin/env python3
# coding: utf-8

import argparse
import re
import sys
import xml.etree.ElementTree as ET

# Регулярные выражения для парсинга
NAME_REGEX = re.compile(r'^[_a-z][a-z0-9_]*$')  # Обновлено для разрешения цифр
NUMBER_REGEX = re.compile(r'^\d+(\.\d+)?$')

def remove_comments(content):
    # Удаление многострочных комментариев #[ ... ]#
    content = re.sub(r'#\[(.*?)\]#', '', content, flags=re.DOTALL)
    # Удаление однострочных комментариев ' ...
    content = re.sub(r"'.*$", '', content, flags=re.MULTILINE)
    return content

def parse_value(token, constants):
    token = token.strip()
    # Проверка на число
    if NUMBER_REGEX.match(token):
        if '.' in token:
            return float(token)
        else:
            return int(token)
    # Проверка на массив
    elif token.startswith('array(') and token.endswith(')'):
        inner = token[6:-1]
        return parse_array(inner, constants)
    # Проверка на словарь
    elif token.startswith('{') and token.endswith('}'):
        inner = token[1:-1]
        return parse_dict(inner, constants)
    # Проверка на константу
    elif token.startswith('|') and token.endswith('|'):
        const_name = token[1:-1]
        if const_name in constants:
            return constants[const_name]
        else:
            raise ValueError(f"Неизвестная константа: {const_name}")
    # Проверка на имя константы
    elif NAME_REGEX.match(token):
        if token in constants:
            return constants[token]
        else:
            raise ValueError(f"Неизвестная константа: {token}")
    else:
        raise ValueError(f"Неверное значение: {token}")

def parse_array(content, constants):
    elements = split_elements(content)
    return [parse_value(elem, constants) for elem in elements]

def parse_dict(content, constants):
    items = split_elements(content, separator=',')
    result = {}
    for item in items:
        if '=>' not in item:
            raise ValueError(f"Неверный синтаксис словаря: {item}")
        key, value = item.split('=>', 1)
        key = key.strip()
        value = value.strip()
        if not NAME_REGEX.match(key):
            raise ValueError(f"Неверное имя ключа в словаре: {key}")
        result[key] = parse_value(value, constants)
    return result

def split_elements(s, separator=','):
    elements = []
    bracket_stack = []
    current = []
    i = 0
    while i < len(s):
        c = s[i]
        if c in '([{':
            bracket_stack.append(c)
        elif c in ')]}':
            if not bracket_stack:
                raise ValueError(f"Несоответствующая закрывающая скобка: {c}")
            opening = bracket_stack.pop()
            if not matches(opening, c):
                raise ValueError(f"Несоответствие скобок: {opening} и {c}")
        elif c == separator and not bracket_stack:
            elements.append(''.join(current).strip())
            current = []
            i +=1
            continue
        current.append(c)
        i +=1
    if bracket_stack:
        raise ValueError("Несоответствующие скобки в выражении.")
    if current:
        elements.append(''.join(current).strip())
    return elements

def matches(opening, closing):
    pairs = { '(':')', '[':']', '{':'}' }
    return pairs.get(opening) == closing

def parse_constants(lines):
    constants = {}
    buffer = ''
    current_name = None
    start_line_num = 0

    for line_num, line in lines:
        stripped = line.strip()
        if not stripped:
            continue  # Пропуск пустых строк

        if current_name is None:
            if '=' in stripped:
                parts = stripped.split('=', 1)
                name = parts[0].strip()
                value = parts[1].strip()
                if not NAME_REGEX.match(name):
                    raise SyntaxError(f"Неверное имя константы '{name}' на строке {line_num}")
                if value.endswith('{') or value.endswith('array('):
                    # Начало многострочного значения
                    buffer = value
                    current_name = name
                    start_line_num = line_num
                else:
                    # Однострочное значение
                    try:
                        parsed_value = parse_value(value, constants)
                        constants[name] = parsed_value
                    except ValueError as e:
                        raise SyntaxError(f"Ошибка на строке {line_num}: {e}")
            else:
                # Вывод отладочной информации
                print(f"=== Неожиданная строка на {line_num}: '{stripped}' ===", file=sys.stderr)
                raise SyntaxError(f"Ожидалось объявление константы на строке {line_num}")
        else:
            # Внутри многострочного значения
            buffer += ' ' + stripped
            # Проверка, закрыта ли скобка
            open_brackets = buffer.count('(') + buffer.count('{') + buffer.count('[')
            close_brackets = buffer.count(')') + buffer.count('}') + buffer.count(']')
            if open_brackets == close_brackets:
                # Завершение многострочного значения
                try:
                    parsed_value = parse_value(buffer, constants)
                    constants[current_name] = parsed_value
                    buffer = ''
                    current_name = None
                except ValueError as e:
                    raise SyntaxError(f"Ошибка на строке {start_line_num}-{line_num}: {e}")
    if current_name is not None:
        raise SyntaxError(f"Не закрытое объявление константы '{current_name}' начиная с строки {start_line_num}")
    return constants

def build_xml(constants):
    root = ET.Element('configuration')
    for key, value in constants.items():
        elem = build_xml_element(key, value)
        root.append(elem)
    return ET.ElementTree(root)

def build_xml_element(name, value):
    elem = ET.Element(name)
    if isinstance(value, dict):
        for k, v in value.items():
            child = build_xml_element(k, v)
            elem.append(child)
    elif isinstance(value, list):
        for item in value:
            child = build_xml_element('item', item)
            elem.append(child)
    else:
        elem.text = str(value)
    return elem

def indent_xml(elem, level=0):
    # Альтернативная функция для отступов в XML для Python < 3.9
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent_xml(child, level+1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

def convert_config_to_xml(content, debug=False):
    """
    Функция для конвертации конфигурации в XML.
    Используется для тестирования.
    """
    # Удаление комментариев
    content_no_comments = remove_comments(content)

    if debug:
        # Вывод контента без комментариев для отладки
        print("=== Контент без комментариев ===", file=sys.stderr)
        print(content_no_comments, file=sys.stderr)
        print("=== Конец контента без комментариев ===", file=sys.stderr)

    # Разделение на строки с номерами для сообщений об ошибках
    lines = content_no_comments.split('\n')
    numbered_lines = list(enumerate(lines, start=1))

    # Парсинг констант
    constants = parse_constants(numbered_lines)

    # Построение XML
    xml_tree = build_xml(constants)
    indent_xml(xml_tree.getroot())
    xml_string = ET.tostring(xml_tree.getroot(), encoding='unicode')
    return xml_string

def main():
    parser = argparse.ArgumentParser(description='Конвертер конфигурационного языка в XML.')
    parser.add_argument('input_file', help='Путь к входному файлу.')
    parser.add_argument('--debug', action='store_true', help='Включить режим отладки.')
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        xml_string = convert_config_to_xml(content, debug=args.debug)
        print(xml_string)
    except SyntaxError as e:
        print(f"Синтаксическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Неизвестная ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
