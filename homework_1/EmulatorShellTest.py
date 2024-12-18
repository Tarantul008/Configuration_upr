import unittest
import io
import zipfile
import os
from EmulatorShell import VirtualFileSystem  # Предполагается, что основной код вынесен в virtual_file_system.py

class TestVirtualFileSystem(unittest.TestCase):

    def setUp(self):
        # Создаем виртуальный ZIP-архив в памяти
        self.zip_memory = io.BytesIO()
        with zipfile.ZipFile(self.zip_memory, 'w') as zf:
            zf.writestr('folder1/', '')  # Пустая директория
            zf.writestr('folder1/file1.txt', 'Hello')  # Файл в folder1
            zf.writestr('folder2/', '')  # Пустая директория
        self.zip_memory.seek(0)

        # Сохраняем архив на диск
        self.zip_path = 'test_vfs.zip'
        with open(self.zip_path, 'wb') as f:
            f.write(self.zip_memory.getvalue())

        self.log_path = 'test_log.csv'
        self.vfs = VirtualFileSystem(self.zip_path, self.log_path)

    def tearDown(self):
        # Удаляем тестовые файлы после завершения тестов
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def test_ls(self):
        # Тестируем команду ls в корневом каталоге
        files = self.vfs.ls()
        self.assertIn('folder1', files)
        self.assertIn('folder2', files)
        self.assertNotIn('file1.txt', files)

    def test_cd(self):
        # Тестируем переход в существующую директорию
        self.vfs.cd('folder1')
        self.assertEqual(self.vfs.current_path, '/folder1/')

        # Тестируем возврат вверх
        self.vfs.cd('..')
        self.assertEqual(self.vfs.current_path, '/')

        # Тестируем несуществующую директорию
        with self.assertRaises(FileNotFoundError):
            self.vfs.cd('nonexistent')

    def test_date(self):
        # Проверяем формат даты
        date_str = self.vfs.date()
        self.assertRegex(date_str, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

    def test_rmdir(self):
        # Удаляем пустую директорию
        self.vfs.rmdir('folder2')
        files = self.vfs.ls()
        self.assertNotIn('folder2', files)

        # Удаляем непустую директорию (должна быть ошибка)
        with self.assertRaises(OSError):
            self.vfs.rmdir('folder1')

    def test_logging(self):
        # Проверяем запись логов
        self.vfs.ls()  # Выполняем команду
        with open(self.log_path, 'r') as f:
            logs = f.readlines()
        self.assertTrue(any("Executing ls command" in log for log in logs))

if __name__ == '__main__':
    unittest.main()
