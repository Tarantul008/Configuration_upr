# test_converter.py
import pytest
import tempfile
import os
import sys
import xml.etree.ElementTree as ET
from converter import (
    remove_comments, parse_value, parse_array, parse_dict, split_elements,
    parse_constants, convert_config_to_xml, build_xml, build_xml_element, indent_xml,
    main, NAME_REGEX, NUMBER_REGEX, matches
)

def test_number_regex():
    assert NUMBER_REGEX.match("123")
    assert NUMBER_REGEX.match("0")
    assert NUMBER_REGEX.match("123.456")
    assert not NUMBER_REGEX.match("abc")
    assert not NUMBER_REGEX.match("123a")

def test_name_regex():
    assert NAME_REGEX.match("abc")
    assert NAME_REGEX.match("_abc")
    assert NAME_REGEX.match("abc123")
    assert not NAME_REGEX.match("1abc")
    assert not NAME_REGEX.match("-abc")

def test_matches():
    assert matches('(', ')')
    assert matches('[', ']')
    assert matches('{', '}')
    assert not matches('(', ']')
    assert not matches('{', ')')

def test_parse_value_number():
    constants = {}
    assert parse_value("123", constants) == 123
    assert parse_value("123.456", constants) == 123.456

def test_parse_value_array():
    constants = {}
    assert parse_value("array(1,2,3)", constants) == [1,2,3]

def test_parse_value_dict():
    constants = {}
    val = parse_value("{a=>1, b=>2}", constants)
    assert val == {'a':1, 'b':2}

def test_parse_value_constant():
    constants = {"myconst": 42}
    assert parse_value("myconst", constants) == 42

def test_parse_value_unknown_constant():
    constants = {}
    with pytest.raises(ValueError):
        parse_value("unknown", constants)

def test_parse_value_named_constant():
    constants = {"myconst": 42}
    with pytest.raises(ValueError):
        parse_value("|unknown|", constants)
    constants["known"] = 100
    assert parse_value("|known|", constants) == 100

def test_parse_array():
    constants = {}
    arr = parse_array("1, 2, 3", constants)
    assert arr == [1,2,3]

    arr_nested = parse_array("array(1,2), array(3,4)", constants)
    assert arr_nested == [[1,2],[3,4]]

def test_parse_dict():
    constants = {}
    d = parse_dict("a=>1, b=>2", constants)
    assert d == {"a":1, "b":2}

    d_nested = parse_dict("x=>{y=>1, z=>2}, w=>3", constants)
    assert d_nested == {"x":{"y":1,"z":2}, "w":3}

def test_split_elements_simple():
    elements = split_elements("1,2,3")
    assert elements == ["1","2","3"]

def test_split_elements_nested():
    elements = split_elements("array(1,2), {a=>1, b=>2}, 3")
    assert elements == ["array(1,2)", "{a=>1, b=>2}", "3"]

def test_split_elements_mismatched_brackets():
    with pytest.raises(ValueError):
        split_elements("array(1,2")

    with pytest.raises(ValueError):
        split_elements("array(1,2]]")

def test_parse_constants_simple():
    lines = [
        (1, "const1 = 123"),
        (2, "const2 = 456")
    ]
    result = parse_constants(lines)
    assert result == {"const1": 123, "const2":456}

def test_parse_constants_multiline():
    lines = [
        (1, "mydict = {"),
        (2, "   a=>1, b=>2"),
        (3, "}"),
        (4, "myarr = array("),
        (5, "   10, 20, 30"),
        (6, ")")
    ]
    result = parse_constants(lines)
    assert result == {"mydict":{"a":1,"b":2}, "myarr":[10,20,30]}

def test_parse_constants_error():
    lines = [
        (1, "1bad = 123"), # Неверное имя константы
    ]
    with pytest.raises(SyntaxError):
        parse_constants(lines)

    lines2 = [
        (1, "myval = {a=>1"), # Не закрытая скобка
    ]
    with pytest.raises(SyntaxError):
        parse_constants(lines2)

def test_build_xml():
    constants = {
        "value1": 123,
        "array1": [1,2,3],
        "dict1": {"a":1,"b":2},
    }
    tree = build_xml(constants)
    root = tree.getroot()
    assert root.tag == "configuration"
    # Проверим, что узлы созданы правильно
    value1 = root.find("value1")
    assert value1 is not None and value1.text == "123"

    array1 = root.find("array1")
    assert array1 is not None
    items = array1.findall("item")
    assert len(items) == 3
    assert items[0].text == "1"
    assert items[1].text == "2"
    assert items[2].text == "3"

    dict1 = root.find("dict1")
    assert dict1 is not None
    a = dict1.find("a")
    b = dict1.find("b")
    assert a is not None and a.text == "1"
    assert b is not None and b.text == "2"

def test_convert_config_to_xml_simple():
    content = """
    const1 = 123
    const2 = { a=>1, b=>2 }
    const3 = array(10,20,30)
    """
    xml_str = convert_config_to_xml(content)
    root = ET.fromstring(xml_str)
    assert root.tag == "configuration"
    const1 = root.find("const1")
    assert const1 is not None
    assert const1.text == "123"
    const2 = root.find("const2")
    assert const2 is not None
    assert const2.find("a").text == "1"
    assert const2.find("b").text == "2"
    const3 = root.find("const3")
    items = const3.findall("item")
    assert len(items) == 3

def test_convert_config_to_xml_errors():
    # Неправильный формат
    content = "1bad = 123"
    with pytest.raises(SyntaxError):
        convert_config_to_xml(content)

    # Неизвестная константа
    content2 = "val = unknown"
    with pytest.raises(SyntaxError):
        convert_config_to_xml(content2)

def test_main(tmp_path, monkeypatch):
    # Создаём временный файл с простым контентом
    p = tmp_path / "config.txt"
    p.write_text("const1 = 123\nconst2 = array(1,2,3)")

    # Перенаправляем аргументы командной строки
    monkeypatch.setattr(sys, 'argv', ['converter.py', str(p)])
    # Перенаправляем stdout для чтения результата
    from io import StringIO
    backup_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        main()
        output = sys.stdout.getvalue()
        # Проверяем что выдача содержит <const1>123</const1> и <const2><item>1</item>...
        assert "<const1>123</const1>" in output
        assert "<const2>" in output
        assert "<item>1</item>" in output
    finally:
        sys.stdout = backup_stdout
