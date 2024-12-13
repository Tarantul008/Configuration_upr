import unittest
from unittest.mock import patch, mock_open, MagicMock
import dependency_visualizer
import json
import urllib.error
import os
from datetime import datetime  # Добавлен импорт datetime

class TestDependencyVisualizer(unittest.TestCase):

    @patch('dependency_visualizer.urllib.request.urlopen')
    def test_fetch_package_info_success(self, mock_urlopen):
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"info": {"requires_dist": ["dep1", "dep2>=2.0"]}}).encode('utf-8')
        
        result = dependency_visualizer.fetch_package_info("testpackage")
        self.assertIn("info", result)
        self.assertIn("requires_dist", result["info"])
        self.assertEqual(result["info"]["requires_dist"], ["dep1", "dep2>=2.0"])

    @patch('dependency_visualizer.urllib.request.urlopen')
    def test_fetch_package_info_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url='https://pypi.org/pypi/testpackage/json',
            code=404,
            msg='Not Found',
            hdrs=None,
            fp=None
        )
        with self.assertRaises(SystemExit) as cm:
            dependency_visualizer.fetch_package_info("testpackage")
        self.assertEqual(cm.exception.code, 1)

    def test_extract_dependencies(self):
        package_info = {
            "info": {
                "requires_dist": [
                    "dep1",
                    "dep2>=2.0",
                    "dep3; python_version>='3.6'",
                    "dep4[extra]>=1.5",
                    "charset-normalizer<4,>=2",
                    "PySocks!=1.5.7,>=1.5.6",
                    "pysocks!=1.5.7,<2.0,>=1.5.6",
                    "invalid-dep!"
                ]
            }
        }
        with patch('builtins.print') as mock_print:
            dependencies = dependency_visualizer.extract_dependencies(package_info)
            expected = ["dep1", "dep2", "dep3", "dep4", "charset-normalizer", "PySocks", "pysocks", "invalid-dep"]
            self.assertEqual(dependencies, expected)
            # Проверяем, что 'invalid-dep!' не был добавлен, но 'invalid-dep' добавлен
            self.assertNotIn("invalid-dep!", dependencies)
            # Проверяем, что были выведены соответствующие сообщения
            self.assertTrue(mock_print.called)
            expected_calls = [
                unittest.mock.call("Извлечена зависимость: 'dep1' из строки 'dep1'"),
                unittest.mock.call("Извлечена зависимость: 'dep2' из строки 'dep2>=2.0'"),
                unittest.mock.call("Извлечена зависимость: 'dep3' из строки 'dep3'"),
                unittest.mock.call("Извлечена зависимость: 'dep4' из строки 'dep4[extra]>=1.5'"),
                unittest.mock.call("Извлечена зависимость: 'charset-normalizer' из строки 'charset-normalizer<4,>=2'"),
                unittest.mock.call("Извлечена зависимость: 'PySocks' из строки 'PySocks!=1.5.7,>=1.5.6'"),
                unittest.mock.call("Извлечена зависимость: 'pysocks' из строки 'pysocks!=1.5.7,<2.0,>=1.5.6'"),
                unittest.mock.call("Извлечена зависимость: 'invalid-dep' из строки 'invalid-dep!'")
                # Удален вызов для "Не удалось извлечь..."
            ]
            mock_print.assert_has_calls(expected_calls, any_order=False)

    def test_extract_dependencies_empty(self):
        package_info = {
            "info": {
                "requires_dist": None
            }
        }
        dependencies = dependency_visualizer.extract_dependencies(package_info)
        self.assertEqual(dependencies, [])

    def test_generate_plantuml(self):
        graph = {
            "packageA": {"packageB", "packageC"},
            "packageB": {"packageD"},
            "packageC": set(),
            "packageD": set()
        }
        repository = "https://example.com/repo"
        plantuml = dependency_visualizer.generate_plantuml(graph, repository)
        expected_lines = [
            "@startuml",
            'title Зависимости пакета с репозиторием https://example.com/repo',
            '"packageA" --> "packageB"',
            '"packageA" --> "packageC"',
            '"packageB" --> "packageD"',
            "@enduml"
        ]
        for line in expected_lines:
            self.assertIn(line, plantuml)

    @patch('dependency_visualizer.subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    @patch('dependency_visualizer.os.remove')
    @patch('dependency_visualizer.datetime')  # Патчируем datetime в модуле dependency_visualizer
    def test_visualize_graph(self, mock_datetime, mock_remove, mock_file, mock_subprocess_run):
        # Настройка фиктивной даты и времени для предсказуемого имени файла
        mock_datetime.now.return_value = datetime(2024, 12, 12, 23, 50, 47)
        mock_datetime.strftime = datetime.strftime

        plantuml_code = "@startuml\n@enduml"
        visualizer_path = "C:\\PlantUML\\plantuml.jar"
        output_directory = "C:\\Users\\Пользователь\\Desktop\\конфигурационka\\vital2"
        package_name = "testpackage"

        dependency_visualizer.visualize_graph(plantuml_code, visualizer_path, output_directory, package_name)

        # Ожидаемое имя файла с временной меткой
        expected_plantuml_filename = f"dependency_graph_{package_name}_20241212235047.puml"
        expected_plantuml_path = os.path.join(output_directory, expected_plantuml_filename)

        # Проверяем, что PlantUML код записан в файл
        mock_file.assert_called_with(expected_plantuml_path, 'w', encoding='utf-8')
        mock_file().write.assert_called_with(plantuml_code)

        # Проверяем, что subprocess.run был вызван с правильными аргументами
        mock_subprocess_run.assert_called_with(['java', '-jar', visualizer_path, expected_plantuml_path], check=True)

        # Проверяем, что временный файл удалён
        mock_remove.assert_called_with(expected_plantuml_path)

    @patch('dependency_visualizer.fetch_package_info')
    def test_build_dependency_graph(self, mock_fetch):
        mock_fetch.side_effect = [
            {"info": {"requires_dist": ["dep1", "dep2"]}},  # packageA
            {"info": {"requires_dist": ["dep3"]}},          # dep1
            {"info": {"requires_dist": []}},                # dep3
            {"info": {"requires_dist": []}},                # dep2
        ]
        graph = dependency_visualizer.build_dependency_graph("packageA", max_depth=2, repository="https://example.com")
        expected_graph = {
            "packageA": {"dep1", "dep2"},
            "dep1": {"dep3"},
            "dep2": set()
            # 'dep3' не должен быть добавлен, так как max_depth=2
        }
        self.assertEqual(graph, expected_graph)

    @patch('dependency_visualizer.fetch_package_info')
    def test_build_dependency_graph_max_depth(self, mock_fetch):
        mock_fetch.side_effect = [
            {"info": {"requires_dist": ["dep1"]}},          # packageA
            {"info": {"requires_dist": ["dep2"]}},          # dep1
            {"info": {"requires_dist": ["dep3"]}},          # dep2
            {"info": {"requires_dist": []}},                # dep3
        ]
        graph = dependency_visualizer.build_dependency_graph("packageA", max_depth=2, repository="https://example.com")
        expected_graph = {
            "packageA": {"dep1"},
            "dep1": {"dep2"}
            # 'dep2' не должен содержать 'dep3', так как depth=3 > max_depth=2
        }
        self.assertEqual(graph, expected_graph)
        self.assertNotIn("dep3", graph)  # 'dep3' не должен быть в графе

if __name__ == '__main__':
    unittest.main()
