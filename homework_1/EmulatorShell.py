import argparse
import zipfile
import io
import os
import sys
import shutil
import logging
import csv
from datetime import datetime

# Настройка логирования для CSV
def setup_logger_csv(log_path):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    class CSVHandler(logging.Handler):
        def __init__(self, log_path):
            super().__init__()
            self.log_path = log_path

            # Создаем файл с заголовками, если он не существует
            if not os.path.exists(log_path):
                with open(log_path, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["timestamp", "name", "level", "message"])

        def emit(self, record):
            log_entry = self.format(record).split(' | ')
            with open(self.log_path, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(log_entry)

    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    csv_handler = CSVHandler(log_path)
    csv_handler.setFormatter(formatter)

    logger.addHandler(csv_handler)
    return logger

class VirtualFileSystem:
    def __init__(self, zip_path, log_path):
        self.logger = setup_logger_csv(log_path)
        self.logger.debug("Initializing VirtualFileSystem")

        self.zip_path = zip_path

        # Загружаем zip-архив в оперативную память
        with open(zip_path, 'rb') as f:
            self.zip_memory = io.BytesIO(f.read())

        self.zip_file = zipfile.ZipFile(self.zip_memory, 'r')
        self.current_path = "/"

    def ls(self):
        self.logger.debug("Executing ls command")
        files = []
        for name in self.zip_file.namelist():
            if name.startswith(self.current_path.lstrip('/')):
                relative_path = name[len(self.current_path.lstrip('/')):].strip('/')
                if '/' not in relative_path:
                    files.append(relative_path)
        return files

    def cd(self, path):
        self.logger.debug(f"Executing cd command with path: {path}")
        if path == "..":
            if self.current_path != "/":
                self.current_path = "/".join(self.current_path.strip('/').split('/')[:-1]) + '/'
            return

        new_path = os.path.normpath(os.path.join(self.current_path, path)).replace("\\", "/") + '/'

        if any(name.startswith(new_path.lstrip('/')) and name.endswith('/') for name in self.zip_file.namelist()):
            self.current_path = new_path
        else:
            self.logger.error("Directory not found")
            raise FileNotFoundError("Directory not found")

    def date(self):
        self.logger.debug("Executing date command")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def rmdir(self, directory):
        self.logger.debug(f"Executing rmdir command for directory: {directory}")
        dir_path = os.path.normpath(os.path.join(self.current_path, directory)).replace("\\", "/").lstrip('/') + '/'

        if not any(name.startswith(dir_path) and name != dir_path for name in self.zip_file.namelist()):
            new_zip_memory = io.BytesIO()
            with zipfile.ZipFile(new_zip_memory, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                for item in self.zip_file.infolist():
                    if not item.filename.startswith(dir_path):
                        new_zip.writestr(item, self.zip_file.read(item.filename))

            self.zip_memory = new_zip_memory
            self.zip_file = zipfile.ZipFile(self.zip_memory, 'r')
            self._save_changes()
        else:
            self.logger.error("Directory is not empty or does not exist")
            raise OSError("Directory is not empty or does not exist")

    def _save_changes(self):
        self.logger.debug("Saving changes to zip file")
        with open(self.zip_path, 'wb') as f:
            f.write(self.zip_memory.getvalue())

    def exit(self):
        self.logger.debug("Executing exit command")
        self.zip_file.close()
        sys.exit()

def run_cli(vfs):
    while True:
        try:
            command = input(f"{vfs.current_path}$ ").strip()
            if command.startswith('ls'):
                files = vfs.ls()
                print('\n'.join(files))
            elif command.startswith('cd'):
                path = command[3:].strip()
                vfs.cd(path)
            elif command == 'date':
                print(vfs.date())
            elif command.startswith('rmdir'):
                directory = command[6:].strip()
                vfs.rmdir(directory)
            elif command == 'exit':
                vfs.exit()
            else:
                vfs.logger.warning(f"Unknown command: {command}")
                print("Command not found")
        except Exception as e:
            vfs.logger.error(f"Error while executing command '{command}': {e}")
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument('zip_path', help='Path to the virtual file system zip archive')
    parser.add_argument('log_path', help='Path to the log file (CSV format)')
    args = parser.parse_args()

    vfs = VirtualFileSystem(args.zip_path, args.log_path)
    run_cli(vfs)

if __name__ == '__main__':
    main()
