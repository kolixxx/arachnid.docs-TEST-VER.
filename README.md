# Arachnid Docs

Проект документации **Arachnid Docs** на базе Antora.

Документация хранится в формате AsciiDoc (`.adoc`) в каталоге `content`, а кастомный UI находится в каталоге `custom-ui`.

## Структура проекта

```text
arachnid.docs/
├── antora-playbook.yml
├── custom-ui/
│   ├── package.json
│   ├── gulpfile.js
│   └── build/
│       └── ui-bundle.zip
└── content/
    ├── antora.yml
    └── modules/
        └── ROOT/
            ├── nav.adoc
            ├── images/
            └── pages/
                ├── index.adoc
                ├── setup.adoc
                ├── usage.adoc
                └── ...
```

## Основные файлы

### `antora-playbook.yml`

Главный файл сборки Antora.

```yml
site:
  title: Arachnid Docs
  url: http://localhost
  start_page: arachnid::index.adoc

content:
  sources:
  - url: .
    branches: HEAD
    start_path: content

ui:
  bundle:
    url: ./custom-ui/build/ui-bundle.zip
```

Сборка запускается из корня проекта.  
Папка `content` подключается через `start_path`.

### `content/antora.yml`

Файл компонента документации.

```yml
name: arachnid
title: Arachnid Documentation
version: ~
nav:
- modules/ROOT/nav.adoc
```

Здесь задаётся имя компонента, название документации и файл навигации.

## Страницы документации

Страницы находятся в каталоге:

```text
content/modules/ROOT/pages/
```

Каждая страница — отдельный `.adoc` файл.
P.S. Файлы index.adoc, setup.adoc, usage.adoc в content/modules/ROOT/pages/ это страницы, которые были в самой первой версии проекта. В случае необходимости использовать этот репозиторий для прода, рекомендуется удалить эти страницы.
В content/modules/ROOT/pages/ лежат файлы самого верхнего уровня иерархии, внутри них уже будут находиться продукты. Например, Arachnid.NGFW (файл ngfw.adoc подключается в content/modules/ROOT/nav.adoc с указанием названия, которое будет отображаться на сайте при помощи "* xref:ngfw.adoc[Arachnid.NGFW]"
1 символ * обозначает первый уровень иерархии. А чтобы внутри Arachnid.NGFW была вкладка, например, Packet Filter(PF) используется уже "** xref:ngfw/pf/overview.adoc[Packet Filter (PF)]" с указанием пути до файла overview.adoc. Папка ngfw/ лежит рядом с файлом nav.adoc, поэтому целый путь до этого каталога указывать не нужно.
Пример страницы:

```adoc
= Arachnid.NGFW

Описание страницы.

== Раздел

Текст раздела.

=== Подраздел

Текст подраздела.
```

Заголовок страницы задаётся первой строкой через один знак `=`:

```adoc
= Название страницы
```

Разделы внутри страницы задаются через `==`, `===`, `====`.

## Навигация

Меню документации задаётся в файле:

```text
content/modules/ROOT/nav.adoc
```

Пример:

```adoc
* xref:index.adoc[Index]
* xref:setup.adoc[Setup]
* xref:usage.adoc[Usage]
* xref:ngfw.adoc[Arachnid.NGFW]
* xref:utm.adoc[Arachnid.UTM]
* xref:ad.adoc[Arachnid.AD]
* xref:tm.adoc[Arachnid.TM]
* xref:nac.adoc[Arachnid.NAC]
* xref:siem.adoc[Arachnid.SIEM]
* xref:uca.adoc[Arachnid.Unified Cybersecurity Architecture]
```

Формат пункта меню:

```adoc
* xref:имя-файла.adoc[Название в меню]
```

Например:

```adoc
* xref:ngfw.adoc[Arachnid.NGFW]
```

ссылается на страницу:

```text
content/modules/ROOT/pages/ngfw.adoc
```

## Как добавить новую страницу

Создать файл:

```text
content/modules/ROOT/pages/example.adoc
```

Добавить содержимое:

```adoc
= Example

Описание новой страницы.
```

Добавить страницу в навигацию:

```adoc
* xref:example.adoc[Example]
```

## Изображения

Изображения хранятся в каталоге:

```text
content/modules/ROOT/images/
```

Пример подключения изображения в `.adoc` файле:

```adoc
image::ngfw/strongswan/example.png[]
```

Путь указывается относительно каталога `images`.

## Сборка проекта

Для сборки используется Docker.

### 1. Клонировать проект

```bash
git clone https://gitlab.arachnd.ru/rnd/arachnid.docs.git
cd arachnid.docs
```

### 2. Собрать UI-бандл

```bash
cd custom-ui/
docker run --rm -v "${PWD}:/workspace" -w /workspace node:18 bash -c "npm install && npx gulp bundle"
cd ..
или
docker run --rm -v "${PWD}:/workspace" -w /workspace node:18 npx gulp bundle
если npm пакеты уже установлены
```

После сборки должен появиться файл:

```text
custom-ui/build/ui-bundle.zip
```

### 3. Собрать документацию Antora

Команду нужно запускать из корня проекта:

```bash
docker run -v "${PWD}:/antora" --rm -t antora/antora antora-playbook.yml
```

## Полная последовательность команд

```bash
git clone https://gitlab.arachnd.ru/rnd/arachnid.docs.git
cd arachnid.docs

cd custom-ui/
docker run --rm -v "${PWD}:/workspace" -w /workspace node:18 bash -c "npm install && npx gulp bundle"

cd ..
docker run -v "${PWD}:/antora" --rm -t antora/antora antora-playbook.yml
```

## Результат сборки

После успешной сборки Antora создаёт статический сайт.

Обычно результат находится в каталоге:

```text
build/site/
```

Для локального просмотра можно запустить python HTTP server:

```bash
python3 -m http.server 1337
```

После этого сайт будет доступен по адресу:

```text
http://localhost:1337
```
