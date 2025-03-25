Простой сервис аналитики посещаемости веб-страниц/серверов на Python/FastAPI/Uvicorn

Для дашборда используется Flask

Данные хранятся в MySQL

Установка/настройка:
`git clone https://github.com/Terc1a/analytics.git`
`cd analytics`
`python3 -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`
`python3 main2.py`
`cd webpanel/`
`python3 app.py`

Файлы, которые требуют настройки:
	`nginx-conf/site-conf(в зависимости от того что используете):`
	`В первом location:`
		`location / {`
					  `mirror /mirror;  # Дублируем запрос`
		    		  `mirror_request_body on;  # Если нужно дублировать тело запроса`
		`**ниже нужные вам хедеры**`
		`}`
	
		location /mirror {
		    internal;  # Важно: только для внутренних запросов
		    
		    # Основной proxy_pass на второй порт
		    proxy_pass http://адрес:порт$request_uri;
		    proxy_pass_request_body on;
		    
		        **ниже нужные вам хедеры**
		}
	config.yaml:
		Укажите в соответствующих полях данные для доступа к вашему серверу MySQL
	app.py/main2.py:
		Укажите адрес/порт для запуска серверов
