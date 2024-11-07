## 1 Задание
На сайте https://onlywei.github.io/explain-git-with-d3 или http://git-school.github.io/visualizing-git/ (цвета могут отличаться, есть команды undo/redo) с помощью команд эмулятора git получить следующее состояние проекта (сливаем master с first, перебазируем second на master): см. картинку ниже. Прислать свою картинку.
```
git commit
git branch first
git commit
git commit
git checkout first
git commit
git commit
git checkout master
git merge first
git checkout HEAD^
git checkout HEAD^
git checkout HEAD^
git checkout -b second
git commit
git commit
git rebase master
git checkout master
git rebase second
git checkout HEAD^
git checkout HEAD^
git checkout HEAD^
git checkout HEAD^
git checkout HEAD^
```
![image](https://github.com/user-attachments/assets/5c0db3e1-b8b1-4bde-b60f-ec6e01413f6a)

## 2 Задание
Создать локальный git-репозиторий. Задать свои имя и почту (далее – coder1). Разместить файл prog.py с какими-нибудь данными. Прислать в текстовом виде диалог с git.
```
Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1
$ git init
Initialized empty Git repository in C:/Users/Виталий/Desktop/Pract_4.1/.git/

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git config --global user.name "coder1"

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git config --global user.email "coder1@something.com"

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ echo "print('Git')" > prog.py

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git status
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        prog.py

nothing added to commit but untracked files present (use "git add" to track)

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git add prog.py
warning: in the working copy of 'prog.py', LF will be replaced by CRLF the next time Git touches it

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git commit -m "Добавлен файл prog.py"
[master (root-commit) a4bc2b3] Добавлен файл prog.py
 1 file changed, 1 insertion(+)
 create mode 100644 prog.py

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git log
commit a4bc2b302dd3e90e956b8c5b4e96b00bf3cda52b (HEAD -> master)
Author: coder1 <coder1@something.com>
Date:   Tue Oct 29 19:34:28 2024 +0300

    Добавлен файл prog.py
```

## 3 Задание
Создать рядом с локальным репозиторием bare-репозиторий с именем server. Загрузить туда содержимое локального репозитория. Команда git remote -v должна выдать информацию о server! Синхронизировать coder1 с server.
```
Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git init --bare server.git
Initialized empty Git repository in C:/Users/Виталий/Desktop/Pract_4.1/server.gi
t/
git remote add origin /c/users/виталий/desktop/pract_4.1/server.git
Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git push --all origin
Enumerating objects: 3, done.
Counting objects: 100% (3/3), done.
Writing objects: 100% (3/3), 249 bytes | 83.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To C:/users/виталий/desktop/pract_4.1/server.git
 * [new branch]      master -> master
Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git remote -v
origin  C:/users/виталий/desktop/pract_4.1/server.git (fetch)
origin  C:/users/виталий/desktop/pract_4.1/server.git (push)


Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git push --tags origin
Everything up-to-date

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git remote -v
origin  C:/users/виталий/desktop/pract_4.1/server.git (fetch)
origin  C:/users/виталий/desktop/pract_4.1/server.git (push)
```
Клонировать репозиторий server в отдельной папке. Задать для работы с ним произвольные данные пользователя и почты (далее – coder2). Добавить файл readme.md с описанием программы. Обновить сервер.
```
Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1 (master)
$ git clone /c:/users/виталий/desktop/pract_4.1/server.git Pract_4.2
Cloning into 'Pract_4.2'...
done.

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1/pract_4.2 (master)
$ git config user.name "coder 2"

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1/pract_4.2 (master)
$ git config user.email "coder2@corp.com"

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1/pract_4.2 (master)
$ echo "Сперва был создан локальный git-репозиторий coder 1, потом был создан bare-репозиторий server, а сейчас был склонирован репозиторий server" > README.md

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1/pract_4.2 (master)
$ git add README.me

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1/pract_4.2 (master)
$ git add README.md
warning: in the working copy of 'README.md', LF will be replaced by CRLF the next time
 Git touches it

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1/pract_4.2 (master)
$ git commit -m "Добавлено описание программы в README.md"
[master 344970f] Добавлено описание программы в README.md
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
Виталий@Vitalik MINGW64 /c/users/виталий/desktop/pract_4.1/pract_4.2 (master)
$ git push origin master
Enumerating objects: 4, done.
Counting objects: 100% (4/4), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 462 bytes | 231.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To c:/users/виталий/desktop/pract_4.1/server.git
   a4bc2b3..344970f  master -> master
```

Coder1 получает актуальные данные с сервера. Добавляет в readme в раздел об авторах свою информацию и обновляет сервер.

Coder2 добавляет в readme в раздел об авторах свою информацию и решает вопрос с конфликтами.

Прислать список набранных команд и содержимое git log.
```
Виталий@Vitalik MINGW64 /c/users/виталий/desktop/Pract_4.1 (master)
$ git pull origin master
remote: Enumerating objects: 4, done.
remote: Counting objects: 100% (4/4), done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
Unpacking objects: 100% (3/3), 442 bytes | 17.00 KiB/s, done.
From C:/users/виталий/desktop/pract_4.1/server
 * branch            master     -> FETCH_HEAD
   a4bc2b3..344970f  master     -> origin/master
Updating a4bc2b3..344970f
Fast-forward
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/Pract_4.1 (master)
$ echo "Информация об авторе coder1" > README.md

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/Pract_4.1 (master)
$ git add README.md
warning: in the working copy of 'README.md', LF will be replaced by CRLF the nex
t time Git touches it

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/Pract_4.1 (master)
$ git commit -m "coder 1 info"
[master 6bf5414] coder 1 info
 1 file changed, 1 insertion(+), 1 deletion(-)

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/Pract_4.1 (master)
$ git push origin master
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (3/3), 314 bytes | 314.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To C:/users/виталий/desktop/pract_4.1/server.git
   344970f..6bf5414  master -> master





Виталий@Vitalik MINGW64 /c/users/виталий/desktop/Pract_4.1/Pract_4.2 (master)
$ git pull origin master
remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
Unpacking objects: 100% (3/3), 294 bytes | 13.00 KiB/s, done.
From c:/users/виталий/desktop/pract_4.1/server
 * branch            master     -> FETCH_HEAD
   344970f..6bf5414  master     -> origin/master
Updating 344970f..6bf5414
Fast-forward
 README.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/Pract_4.1/Pract_4.2 (master)
$ git add README.md

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/Pract_4.1/Pract_4.2 (master)
$ git commit -m "coder 2 info"
[master 342636f] coder 2 info
 1 file changed, 1 insertion(+)

Виталий@Vitalik MINGW64 /c/users/виталий/desktop/Pract_4.1/Pract_4.2 (master)
$ git push origin master
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 313 bytes | 313.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To c:/users/виталий/desktop/pract_4.1/server.git
   6bf5414..342636f  master -> master



commit 342636f0e78ee0b7b05dd3596a615112e8de0706 (HEAD -> master, origin/master, origin/HEAD)
Author: coder 2 <coder2@corp.com>
Date:   Thu Nov 7 21:53:09 2024 +0300

    coder 2 info

commit 6bf5414fc8c660b10269fd865b0ce80f3314f075
Author: coder1 <coder1@something.com>
Date:   Thu Nov 7 21:32:52 2024 +0300

    coder 1 info

commit 344970ffc83db44f86e0f25eb34527428146ef3f
Author: coder 2 <coder2@corp.com>
Date:   Mon Nov 4 14:16:02 2024 +0300

    Добавлено описание программы в README.md

commit a4bc2b302dd3e90e956b8c5b4e96b00bf3cda52b
Author: coder1 <coder1@something.com>
Date:   Tue Oct 29 19:34:28 2024 +0300

    Добавлен файл prog.py

```

## 4 Задание
Написать программу на Питоне (или другом ЯП), которая выводит список содержимого всех объектов репозитория. Воспользоваться командой "git cat-file -p". Идеальное решение – не использовать иных сторонних команд и библиотек для работы с git.
```
import subprocess

def get_git_objects():
    """Получить список всех объектов в репозитории с их SHA и именами (если есть)."""
    result = subprocess.run(
        ["git", "rev-list", "--all", "--objects"],
        stdout=subprocess.PIPE,
        text=True
    )
    objects = result.stdout.strip().splitlines()
    return [line.split()[0] for line in objects if line]  # Извлекаем только SHA объектов

def display_object_content(object_id):
    """Вывести содержимое объекта по его SHA с помощью git cat-file -p."""
    result = subprocess.run(
        ["git", "cat-file", "-p", object_id],
        stdout=subprocess.PIPE,
        text=True
    )
    print(f"Object ID: {object_id}")
    print(result.stdout)
    print("=" * 40)  # Разделитель для удобства чтения

def main():
    objects = get_git_objects()
    for object_id in objects:
        display_object_content(object_id)

if __name__ == "__main__":
    main()
```

```
$ python list_git_objects.py
Object ID: 6bf5414fc8c660b10269fd865b0ce80f3314f075
tree c89518558ab06b1c075bda718ede6498c711cea6
parent 344970ffc83db44f86e0f25eb34527428146ef3f
author coder1 <coder1@something.com> 1731004372 +0300
committer coder1 <coder1@something.com> 1731004372 +0300

coder 1 info

========================================
Object ID: 344970ffc83db44f86e0f25eb34527428146ef3f
tree e1e579d6bf93fff57dcc6ee24d258ff4b052069d
parent a4bc2b302dd3e90e956b8c5b4e96b00bf3cda52b
author coder 2 <coder2@corp.com> 1730718962 +0300
committer coder 2 <coder2@corp.com> 1730718962 +0300

Р”РѕР±Р°РІР»РµРЅРѕ РѕРїРёСЃР°РЅРёРµ РїСЂРѕРіСЂР°РјРјС‹ РІ README.md

========================================
Object ID: a4bc2b302dd3e90e956b8c5b4e96b00bf3cda52b
tree 47ba9058c19b3d3503461229794d3f0515a0d4b4
author coder1 <coder1@something.com> 1730219668 +0300
committer coder1 <coder1@something.com> 1730219668 +0300

Р”РѕР±Р°РІР»РµРЅ С„Р°Р№Р» prog.py

========================================
Object ID: c89518558ab06b1c075bda718ede6498c711cea6
100644 blob 97cce33e253421927478cb6e78697fa84cafffe6    README.md
100644 blob 23956e122ecf9cbeaf9493401d81637afe14e94d    prog.py

========================================
```
