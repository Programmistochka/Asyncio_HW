Асинхронное приложение по выгрузке данных с сайта StarrWars в БД (развернутую с помощью docker-compose на базе postgresql)

Для запуска необходимо:
1. Создание виртуального окружения с виртуальными переменными для БД (.env)
	python -m venv async_env
2. Активировать виртуальное окружение 
	async_env\Scripts\activate.bat
3. Установить requirements.txt
	pip install -r requirements.txt
4. При необходимости развернуть БД из Docker-контейнера 
	docker-compose up
5. Проверить порт подключения к БД в models.py
	Для запуска лок БД - 5432
	Для Docker контейнера с БД - 5431