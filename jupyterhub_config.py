from dockerspawner import DockerSpawner
from oauthenticator.github import GitHubOAuthenticator
from dotenv import load_dotenv
import os 
c = get_config()

# Основные настройки JupyterHub
c.JupyterHub.bind_url = 'http://:8000'
c.JupyterHub.hub_bind_url = 'http://0.0.0.0:8081'
c.JupyterHub.start_timeout = 360 # параметр задает максимальное время (в секундах), в течение которого JupyterHub ожидает, что будет произведён успешный запуск контролируемого процесса
c.JupyterHub.shutdown_no_activity_timeout = 600 #  Таймаут для автоматического завершения работы контейнеров при отсутствии активности (10 минут)
c.JupyterHub.shutdown_on_logout = True # автоматически останавливает сервер пользователя, как только он выходит из системы
c.DockerSpawner.use_internal_ip = True # параметр управляет использованием внутренних IP-адресов Docker

# Конфигурация аутентификации OAuth от GitHub
c.JupyterHub.authenticator_class = GitHubOAuthenticator
c.GitHubOAuthenticator.client_id = os.getenv('GITHUB_CLIENT_ID')
c.GitHubOAuthenticator.client_secret = os.getenv('GITHUB_TOKEN')
c.GitHubOAuthenticator.oauth_callback_url = 'https://jupiter45.skayfaks.keenetic.pro/hub/oauth_callback'
c.OAuthenticator.admin_users = {'hek1412'}
c.GitHubOAuthenticator.allowed_organizations = {'1T45git'}
c.GitHubOAuthenticator.scope = ['read:user','user:email', 'read:org']
# c.Authenticator.open_signup = True # позволяют пользователям регистрироваться самостоятельно (может и не нужно)

# Настраиваем Spawner для использования Docker
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = 'hek1412/dockerfile.jupyterlab_v2:latest' # Указывает образ Docker, который будет использоваться для запуска каждого пользователя
c.Spawner.http_timeout = 180 # указывает максимальное время (в секундах), в течение которого JupyterHub будет ожидать, что спаунер (Spawner) запустит сервер пользователя
c.DockerSpawner.network_name = "jupyterhub-network" # Имя сети Docker, которое будет использоваться
c.Spawner.start_timeout = 240 # временной интервал в секундах, после которого процесс запуска будет считаться неудачным, если не завершится

# Настройка монтирования тома для каждого пользователя
notebook_dir = '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir # Каталог, который будет монтироваться в контейнере для хранения файлов Jupyter
# Задаем монтирование: общий том с поддиректориями для каждого пользователя
c.DockerSpawner.volumes = { 'jupyterhub-data_{username}': '/home/jovyan/work'}

# доп настройки
# c.DockerSpawner.remove = True # Автоматически удаляет контейнеры после их остановки (может быть убрать, что бы не слетала среда)
c.DockerSpawner.debug = True # Включает отладку для более детальной диагностики, если что-то пойдет не так
# c.DockerSpawner.cpu_limit = 4 # лимиты CPU
# c.DockerSpawner.mem_limit = '16G' # лимиты памяти
c.JupyterHub.active_server_limit = 6 # максимальное количество активных серверов
c.JupyterHub.shutdown_no_activity_timeout = 600 #  Таймаут для автоматического завершения работы контейнеров при отсутствии активности (10 минут)
c.JupyterHub.shutdown_on_logout = True # автоматически останавливает сервер пользователя, как только он выходит из системы

# Настроить команду запуска для jupyterhub-singleuser
c.DockerSpawner.extra_create_kwargs = {
    'runtime': 'nvidia'
}
# Настроить дополнительные параметры для GPU
c.DockerSpawner.extra_host_config = {
    'device_requests': [
        {
            'Driver': 'nvidia',
            'Count': -1,
            'Capabilities': [['gpu']],
        }
    ]
}

data_dir = '/srv/jupyterhub/data' # дирректория для секретов
c.JupyterHub.cookie_secret_file = os.path.join(data_dir, 'jupyterhub_cookie_secret') # параметр указывает путь к файлу, который хранит секретные данные для куки-файлов, используемые для обеспечения безопасности сеансов пользователей в JupyterHub
c.JupyterHub.db_url = "sqlite:////srv/jupyterhub/data/jupyterhub.sqlite" # Указывает использовать SQLite для хранения данных JupyterHub
c.JupyterHub.log_level = 'DEBUG' # Устанавливает уровень логирования на DEBUG
# Сбор метрик
c.JupyterHub.metrics_enabled = True
c.JupyterHub.metrics_port = 8000
c.JupyterHub.authenticate_prometheus = False

# Указываем, что контейнеры должны быть привязаны к пользователю
# c.DockerSpawner.use_internal_ip = True # нужно тестить

#  SSL
# c.JupyterHub.ssl_key = 'jupyterhub.key'
# c.JupyterHub.ssl_cert = 'jupyterhub.crt'
# or letsencrypt:
# c.JupyterHub.ssl_key = '/etc/letsencrypt/live/hub-tutorial.jupyter.org/privkey.pem'
# c.JupyterHub.ssl_cert = '/etc/letsencrypt/live/hub-tutorial.jupyter.org/fullchain.pem'
# public https port
# c.JupyterHub.port = 443

# Опционально: установка ресурсоемкости контейнеров, лимиты CPU и памяти
# c.DockerSpawner.cpu_limit = 1
# c.DockerSpawner.mem_limit = '2G'

# # NEXT Конфигурация аутентификации OAuth от GitHub
# from oauthenticator.github import GitHubOAuthenticator
# c.JupyterHub.authenticator_class = GitHubOAuthenticator
# c.GitHubOAuthenticator.client_id = 'YOUR_GITHUB_CLIENT_ID'
# c.GitHubOAuthenticator.client_secret = 'YOUR_GITHUB_CLIENT_SECRET'
# c.GitHubOAuthenticator.oauth_callback_url = 'http://skayfaks.keenetic.pro:35001/hub/oauth_callback'

# c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
# c.JupyterHub.port = 8000  # Указывает, на каком порту слушать (35001/8000)
# c.JupyterHub.hub_ip = '0.0.0.0'
# c.JupyterHub.hub_connect_ip = 'jupyterhub'
# c.JupyterHub.hub_port = 8081
# c.JupyterHub.hub_connect_ip = 'http://skayfaks.keenetic.pro:35001'
# c.JupyterHub.base_url = '/'  # Базовый URL
# URL-адрес для доступа из внешнего мира
# c.JupyterHub.bind_url = 'http://skayfaks.keenetic.pro:35001'

# cschranz/gpu-jupyter:v1.7_cuda-12.2_ubuntu-22.04_python-only

