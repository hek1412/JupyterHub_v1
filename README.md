# JupyterHub_v1
## Описание проекта JupyterHub с Docker и GitHub OAuth

Этот проект представляет собой создание JupyterHub, работающего в контейнере Docker, с поддержкой GPU через NVIDIA runtime, аутентификации пользователей через GitHub OAuth и использования DockerSpawner для динамического создания окружений для каждого пользователя с кастомным образом 
 ноутбука юпитера.

---

## Содержание
1. [Структура проекта](#структура-проекта)
2. [Создание Docker-образа](#создание-docker-образа)
3. [Docker Compose](#docker-compose)
4. [Dockerfile](#dockerfile)
5. [Конфигурация JupyterHub](#конфигурация-jupyterhub)
6. [Переменные окружения](#переменные-окружения)
7. [Запуск JupyterHub](#запуск-JupyterHub)

---

## Структура проекта

```
jupyterhub
│
├── docker-compose.yaml
│
├── Dockerfile.jupyterhub
│
├──jupyterhub_config.py
│
└── jupytercastom/
      ├── Dockerfile.jupyterlab
      └── requirements.txt
```

---

## Создание Docker-образа

Сначалоа необходимо создать Docker-образ с необходимыми зависимостями для работы пользовательских контейнеров в JupyterHub, а затем опубликовать его в Docker Hub для дальнейшего использования.
Переходим в директорию `jupytercastom/` и собираем образ на базе  `quay.io/jupyter/pytorch-notebook:cuda12-python-3.11.8` и установкой дополнительных библиотек.

```
docker build -t jupyterlab-v2 -f Dockerfile.jupyterlab .
```
проверяем наличие образа
```
docker images
```
Логинимся
```
docker login
```
Присваиваем тэг
```
docker tag jupyterlab-v2  hek1412/dockerfile.jupyterlab_v2:latest 
```
Отправляем собранный образ, тепеь он доступен из репозитория
```
docker push hek1412/dockerfile.jupyterlab_v2:latest
```
![image](https://github.com/user-attachments/assets/9bc522e4-2671-42e6-9b98-bb0ae2ea784b)


---

## Docker Compose

### Создаем `docker-compose.yaml` для разворачивания jupyterhub 
(предварительно переходим в директорию jupyterhub) 
```
services:
  jupyterhub:
    build:
      context: .
      dockerfile: Dockerfile.jupyterhub
    restart: always
    image: jupyterhub
    container_name: jupyterhub
    networks:
      - jupyterhub-network
    volumes:
      - "./jupyterhub_config.py:/srv/jupyterhub/jupyterhub_config.py" # Монтируем конфигурационный файл
      - "/var/run/docker.sock:/var/run/docker.sock:rw"               # Даем доступ к Docker daemon
      - "jupyterhub-data:/srv/jupyterhub/data"                       # Общий том для данных
    ports:
      - "35001:8000"                                                 # Открываем порт для JupyterHub
    environment:
      - JUPYTERHUB_BASE_URL=/hub                                     # Базовый URL для JupyterHub
      - JUPYTERHUB_URL=http://skayfaks.keenetic.pro:35001            # Полный URL JupyterHub
      - GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID}                         # ID клиента GitHub OAuth
      - GITHUB_TOKEN=${GITHUB_TOKEN}                                 # Токен GitHub OAuth
    runtime: nvidia                                                  # Используем NVIDIA runtime
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia                                         # Резервируем все доступные GPU
              count: all
              capabilities: [gpu]

volumes:
  jupyterhub-data:                                                   # Общий том для хранения данных

networks:
  jupyterhub-network:
    name: jupyterhub-network                                         # Создаем сеть для контейнеров
```

---

## Dockerfile

### Создаем `Dockerfile.jupyterhub` для сборки образа нашего jupyterhub

```
FROM jupyterhub/jupyterhub:latest
WORKDIR /srv/jupyterhub

# Обновляем пакеты и устанавливаем необходимые зависимости
RUN apt-get update -y && \
    python3 -m pip install --no-cache-dir \
    dockerspawner \
    python-dotenv \
    oauthenticator

# Копируем конфигурационный файл
COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py

# Запускаем JupyterHub с указанным конфигурационным файлом
CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]
```

---

## Конфигурация JupyterHub

### Создаем `jupyterhub_config.py` с параметрами:

```
c.JupyterHub.bind_url = 'http://:8000'                           # URL, на котором будет запущен JupyterHub
c.JupyterHub.hub_bind_url = 'http://0.0.0.0:8081'                # URL для внутреннего общения между компонентами
c.JupyterHub.start_timeout = 360                                 # Максимальное время ожидания старта процесса (секунды)
c.JupyterHub.shutdown_no_activity_timeout = 600                  # Автоматическое завершение работы при простоях (секунды)
c.JupyterHub.shutdown_on_logout = True                           # Автоматическая остановка сервера при выходе из системы
c.DockerSpawner.use_internal_ip = True                           # Использование внутренних IP-адресов Docker
c.JupyterHub.authenticator_class = GitHubOAuthenticator          # Использование GitHub OAuth
c.GitHubOAuthenticator.client_id = os.getenv('GITHUB_CLIENT_ID') # ID клиента GitHub OAuth
c.GitHubOAuthenticator.client_secret = os.getenv('GITHUB_TOKEN') # Секретный токен GitHub OAuth
c.GitHubOAuthenticator.oauth_callback_url = 'https://jupiter45.skayfaks.keenetic.pro/hub/oauth_callback'
c.OAuthenticator.admin_users = {'hek1412'}                       # Администраторы JupyterHub
c.GitHubOAuthenticator.allowed_organizations = {'1T45git'}       # Разрешенные организации GitHub
c.GitHubOAuthenticator.scope = ['read:user', 'user:email', 'read:org']
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'       # Использование DockerSpawner
c.DockerSpawner.image = 'hek1412/dockerfile.jupyterlab_v2:latest' # Образ Docker для пользовательских контейнеров
c.DockerSpawner.network_name = "jupyterhub-network"              # Имя сети Docker
c.DockerSpawner.notebook_dir = '/home/jovyan/work'               # Рабочая директория внутри контейнера
c.DockerSpawner.volumes = { 'jupyterhub-data_{username}': '/home/jovyan/work' } # Монтирование томов для пользователей
c.DockerSpawner.debug = True                                     # Включение режима отладки
c.DockerSpawner.extra_create_kwargs = { 'runtime': 'nvidia' }    # Настройка NVIDIA runtime
c.DockerSpawner.extra_host_config = {
    'device_requests': [
        {
            'Driver': 'nvidia',
            'Count': -1,
            'Capabilities': [['gpu']],
        }
    ]
}
c.JupyterHub.cookie_secret_file = os.path.join(data_dir, 'jupyterhub_cookie_secret')
c.JupyterHub.db_url = "sqlite:////srv/jupyterhub/data/jupyterhub.sqlite"
c.JupyterHub.log_level = 'DEBUG'
c.JupyterHub.metrics_enabled = True                              # Включение сбора метрик
c.JupyterHub.metrics_port = 8000                                 # Порт для метрик
c.JupyterHub.authenticate_prometheus = False                     # Отключаем аутентификацию Prometheus
```

---

## Переменные окружения

Создаём файл `.env` с следующими переменными:

```
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_TOKEN=your_github_token
```

Значения `your_github_client_id` и `your_github_token` нужно получить в GitHub.

---

## Запуск JupyterHub

```
docker compose build
docker-compose up -d
```

Теперь у нас работает JupyterHub `http://skayfaks.keenetic.pro:35001/hub` с поддержкой GPU, аутентификацией через GitHub и динамическим созданием окружений для пользователей!

