import asyncio
import aiohttp
import datetime
from more_itertools import chunked
from models import Base, SwapiPeople, Session, engine

MAX_CHUNK_SIZE = 10 # Константа для разбиения данных в запросах
async def get_people(people_id):
    print(f'people_id = {people_id}')
    session = aiohttp.ClientSession()
    print(f'session = {session}')
    response = await session.get(f'https://swapi.dev/api/people/{people_id}')
    json_data = await response.json()
    await session.close()
    return json_data

async def get_film_name(film_link):
    #print(f'film_link = {film_link}')
    new_session = aiohttp.ClientSession()
    #print(f'session = {session}')
    response = await new_session.get(film_link)
    json_data = await response.json()
    film_name = json_data.get('title')
    await new_session.close()    
    return film_name

async def get_specie_name(specie_link):
    #print(f'specie_link = {film_link}')
    new_session = aiohttp.ClientSession()
    #print(f'session = {session}')
    response = await new_session.get(specie_link)
    json_data = await response.json()
    specie_name = json_data.get('name')
    await new_session.close()  
    return specie_name

async def get_starship_name(starship_link):
    #print(f'specie_link = {film_link}')
    new_session = aiohttp.ClientSession()
    #print(f'session = {session}')
    response = await new_session.get(starship_link)
    json_data = await response.json()  
    starship_name = json_data.get('name')
    await new_session.close()
    return starship_name



async def insert_to_db(people_json_list):
    #print(people_json_list)
    async with Session() as session_db:
        numb = 0
        swapi_people_list = []
        for people in people_json_list:
            numb += 1
            #print(f"people - {numb}: {people}\n")
            
            #Получение списка названий по списку ссылок фильмов
            films_list = people.get('films')
            if len(films_list) > 0:
                #Получение корутин по ссылке film
                films_names = [get_film_name(film_link) for film_link in films_list] # создание списка для хранения корутин
                #Получение списка с названием фильмов в асинхроне
                films_list = await asyncio.gather(*films_names)              
                films_list = ', '.join(films_list)               
            else:
                films_list = ' '
            #print(f'films_names: {films_list}')

            #Получение списка названий по списку ссылок species
            species_list = people.get('species')
            #print(f'species {species_list}')
            if len(species_list) > 0:
                #Получение корутин по ссылке specie
                species_names = [get_specie_name(specie_link) for specie_link in species_list] # создание списка для хранения корутин
                #Получение списка с названием фильмов в асинхроне
                species_list = await asyncio.gather(*species_names)              
                #print(f'species_names: {species_list}')
                species_list = ', '.join(species_list)
            else:
                species_list = ' '
            #print(f'species_names: {species_list}')

            #Получение списка названий по списку ссылок starships
            starships_list = people.get('starships')
            #print(f'starships {starships_list}')
            if len(starships_list) > 0:
                #Получение корутин по ссылке starships
                starships_names = [get_starship_name(starship_link) for starship_link in starships_list] # создание списка для хранения корутин
                #Получение списка с названием фильмов в асинхроне
                starships_list = await asyncio.gather(*starships_names)              
                #print(f'starships_names: {starships_list}')
                starships_list = ', '.join(starships_list)
            else:
                starships_list = ' '
            #print(f'starships_names: {starships_list}')

            swapi_people_persdict={'name': people.get('name'),
                                   'birth_year': people.get('birth_year'),
                                    'eye_color': people.get('eye_color'),
                                    'films': films_list,
                                    'gender': people.get('gender'),
                                    'hair_color': people.get('hair_color'),
                                    'height': people.get('height'),
                                    'homeworld': people.get('homeworld'),
                                    'mass': people.get('mass'),
                                    'skin_color': people.get('skin_color'),
                                    'species': species_list,
                                    'starships': starships_list,
                                    'vehicles': people.get('vehicles')}
            swapi_people_list.append({'id': numb,  'json': swapi_people_persdict})
        print(f'swapi_people_list: {swapi_people_list}')
        swapi_people = [SwapiPeople(json=p) for p in swapi_people_list]                                
        print('-------'*20)
        print(f'swapi_people: {swapi_people}')
        session_db.add_all(swapi_people)
        print('----------------SESSION.ADD_ALL - OK--------------')
        await session_db.commit()


async def main():
    
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)

    # Все запросы группируются в партии по MAX_CHUNK_SIZE
    for ids_chunk in chunked(range(1, 4), MAX_CHUNK_SIZE):
        get_people_coros = [get_people(people_id) for people_id in ids_chunk] # создание списка для хранения корутин
        #print('создан список для хранения корутин')
        people_json_list = await asyncio.gather(*get_people_coros) # формирование списка
        asyncio.create_task(insert_to_db(people_json_list)) # создание задачи на вставку данных в БД
        #print(f'Созданы задачи на вставку для ids_chunk: {ids_chunk}')
        #print(f'task_sets: {asyncio.all_tasks()}')
        #print('********************')

    current_task = asyncio.current_task() # определение текущей задачи (для данной функции main())
    task_sets = asyncio.all_tasks() # формирование списка задач, которые должны быть выполнены до завершения работы с БД
    #print(f'task_sets: {task_sets}')
    task_sets.remove(current_task) # из набора задач удаляется текущая задача main
    #print(f'current_task: {current_task}')
    #print(f'ОЖИДАНИЕ чтобы все задания на вставку завершились')
    await asyncio.gather(*task_sets) # ожидание что все задания на вставку завершились
    #print(f'Все задания на вставку завершились. task_sets: {task_sets}')
    await engine.dispose() # завершение работы с базой данных
    #print(f'Работа с БД завершена')

start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)