# GitHub и хостинг

## 1. Пуш в существующий репозиторий

Подготовленная папка: `C:\Users\1\Documents\Codex\hotel-manager\hotel-manager`.
Здесь уже есть Git, ветка `main` и remote `origin`:
`https://github.com/squrrrty/hotel-manager.git`.
Папка `qa-runtime` находится снаружи и в коммит этой папки не попадёт.
Повторно выполнять git init не нужно.

Откройте PowerShell:

```powershell
cd C:\Users\1\Documents\Codex\hotel-manager\hotel-manager
git remote -v
git status
git add .
git status
git commit -m "Improve hotel features, UI and hosting setup"
git push -u origin main
```

Второй `git status` покажет состав коммита. `.env` и `.venv` в нём быть не должно;
`.env.example`, миграции и requirements должны быть.
При первом push GitHub может предложить авторизацию через браузер.

Если `git` не найден, установите Git for Windows с https://git-scm.com/download/win
и откройте PowerShell заново. На этом компьютере также есть встроенный Git Codex;
его можно использовать без установки, выполнив перед командами:

```powershell
Set-Alias git 'C:\Users\1\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe'
```

Если Git попросит указать автора коммита, выполните **со своими данными**:

```powershell
git config user.name "Ваше имя"
git config user.email "Ваш email GitHub"
```

Затем повторите commit и push. Если push отклонён из-за новых коммитов на GitHub:

```powershell
git pull --rebase origin main
git push -u origin main
```

При конфликте разрешите его перед push. Принудительная перезапись истории не нужна.

## 2. Если нужен другой новый репозиторий

Создайте на GitHub пустой репозиторий без README, .gitignore и лицензии:
файлы и история уже есть локально. Скопируйте его HTTPS-адрес:

```powershell
git remote set-url origin https://github.com/ВАШ_ЛОГИН/ВАШ_РЕПОЗИТОРИЙ.git
git add .
git commit -m "Prepare HotelManager for hosting"
git push -u origin main
```

## 3. Настройки Linux-хостинга

Нужен Web Service для Python и отдельная PostgreSQL. После подключения
GitHub-репозитория укажите:

| Поле | Значение |
| --- | --- |
| Branch | main |
| Root directory | пусто, если run.py лежит в корне GitHub-репозитория |
| Python | 3.13.17, также указан в .python-version |
| Build command | pip install -r requirements-hosting.txt |
| Start command | sh start.sh |

`start.sh` включает production-режим, применяет миграции и запускает
Gunicorn с двумя рабочими процессами. Порт берётся из PORT, который обычно
задаёт хостинг. Без PORT используется 8000. Секреты задаются в настройках
хостинга, `.env` в репозиторий не загружается.

| Переменная окружения | Что указать |
| --- | --- |
| APP_ENV | production |
| DATABASE_URL | строка подключения к PostgreSQL, выданная хостингом |
| SECRET_KEY | случайная строка минимум 32 символа |
| ADMIN_USERNAME | ваш логин администратора, например admin |
| ADMIN_PASSWORD | свой пароль минимум 12 символов |

Сгенерировать SECRET_KEY локально:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Полученную строку вставьте в окружение хостинга. Поддерживаются DATABASE_URL
с префиксами `postgres://`, `postgresql://`, `postgresql+psycopg2://`.
Все используют существующий psycopg2. При требовании SSL используйте параметры
подключения провайдера, например `?sslmode=require`: они сохраняются.
Для production нужен HTTPS: сессионная cookie отправляется только по HTTPS.

После первого успешного развёртывания откройте Shell/Console самого сервиса:

```sh
python seed.py
```

Эта команда создаст роли, вашего администратора, категории и начальные номера.
На хостинге тестовые гости и брони не создаются, `admin123` не используется.
Повторный запуск не меняет пароль уже существующего пользователя:
изменение ADMIN_PASSWORD само по себе не обновит созданный пароль.
Для первой публикации используйте новую пустую базу хостинга.

Если Shell недоступен, временно выполните один deploy со Start command:

```sh
python -m flask --app run db upgrade && python seed.py && sh start.sh
```

После инициализации верните `sh start.sh`. Для временной команды тоже задайте
все переменные окружения выше, включая APP_ENV=production.

Локальную `.env` и содержимое `qa-runtime/pgdata` загружать не нужно.
Перенос существующих данных — отдельный экспорт/импорт PostgreSQL;
push отправляет только код. Ссылка GitHub сама по себе сайт не запускает.

После публикации проверьте: вход со своим паролем → добавление гостя →
бронь → обновление страницы. Данные должны оставаться в PostgreSQL.

## Что подготовлено

- `run.py`: отключён debug; локальный запуск работает по-прежнему.
- `gunicorn.conf.py`, `start.sh`, `Procfile`: запуск на Linux-хостинге.
- `requirements-hosting.txt`: проверенные версии приложения + Gunicorn 26.2.0.
  Локальный requirements.txt не изменён.
- `app/config.py`: настройки окружения и HTTPS-cookie.
- `app/__init__.py`: проверка обязательных настроек production.
- `app/csrf.py`: токен во всех POST-формах защищает изменения от чужих сайтов.
- `seed.py`: свой пароль администратора и начальные данные без демо-брони.
- `.gitignore`: исключены .env, окружение, дампы, архивы и журналы.
- `.gitattributes`: у shell-скриптов сохраняются переносы строк LF.

Официальные инструкции: [Flask / Gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/)
и [пример размещения Flask](https://render.com/docs/deploy-flask).
Gunicorn работает на Linux; здесь проверены приложение и настройки на Windows,
запуск самого Gunicorn на хостинге ещё не выполнен.
