from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2
import time
import dotenv
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, WebDriverException
from pydantic import BaseModel
from typing import List
import asyncio
import concurrent.futures

dotenv.load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Вы можете указать конкретные домены, если хотите ограничить доступ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def connect_db():
    dbname = os.environ.get('DB_NAME')
    dbuser = os.environ.get('DB_USER')
    dbpassword = os.environ.get('DB_PASSWORD')
    dbhost = os.environ.get('DB_HOST')
    dbport = os.environ.get('DB_PORT')

    conn = psycopg2.connect(
        dbname=dbname,
        user=dbuser,
        password=dbpassword,
        host=dbhost,
        port=dbport
    )
    return conn

def insert_vacancy(conn, company, title, meta_info, salary, skills, link):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO vacancies (company, vacancy, location, salary, skills, link)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """, (company, title, meta_info, salary, skills, link))
        conn.commit()
        return cur.fetchone()[0]

def parse_habr(query):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    conn = connect_db()

    try:
        driver.get('https://career.habr.com')

        search_input = driver.find_element(By.CSS_SELECTOR, '.l-page-title__input')
        search_input.send_keys(query)
        search_input.send_keys(Keys.RETURN)

        time.sleep(1)

        while True:
            vacancies = driver.find_elements(By.CLASS_NAME, 'vacancy-card__info')
            for vacancy in vacancies:
                try:
                    company_element = vacancy.find_element(By.CLASS_NAME, 'vacancy-card__company-title')
                    company = company_element.text
                except NoSuchElementException:
                    company = 'Компания не указана'

                title_element = vacancy.find_element(By.CLASS_NAME, 'vacancy-card__title')
                title = title_element.text
                link = title_element.find_element(By.TAG_NAME, 'a').get_attribute('href')

                try:
                    meta_element = vacancy.find_element(By.CLASS_NAME, 'vacancy-card__meta')
                    meta_info = meta_element.text
                except NoSuchElementException:
                    meta_info = 'Местоположение не указано'

                try:
                    salary = vacancy.find_element(By.CLASS_NAME, 'vacancy-card__salary').text
                except NoSuchElementException:
                    salary = 'ЗП не указана'

                try:
                    skills = vacancy.find_element(By.CLASS_NAME, 'vacancy-card__skills').text
                except NoSuchElementException:
                    skills = 'Скиллы не указаны'

                vacancy_id = insert_vacancy(conn, company, title, meta_info, salary, skills, link)

                print(f'Компания: {company}\nВакансия: {title}\nСсылка: {link}\nМестоположение и режим работы: {meta_info}\nЗарплата: {salary}\nСкиллы: {skills}')

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'a.button-comp--appearance-pagination-button[rel="next"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                
                for _ in range(3):
                    try:
                        driver.execute_script("arguments[0].click();", next_button)
                        break
                    except StaleElementReferenceException:
                        next_button = driver.find_element(By.CSS_SELECTOR, 'a.button-comp--appearance-pagination-button[rel="next"]')
                        time.sleep(1)
                else:
                    break
                
                time.sleep(1)
            except (NoSuchElementException, ElementClickInterceptedException):
                break

    except WebDriverException as e:
        logging.error(f"WebDriverException occurred: {e}")
        raise
    finally:
        driver.quit()
        conn.close()

class Vacancy(BaseModel):
    company: str
    vacancy: str
    location: str
    salary: str
    skills: str
    link: str

class SearchResult(BaseModel):
    company: str
    vacancy: str
    location: str
    salary: str
    skills: str
    link: str

@app.get("/search", response_model=List[SearchResult])
async def search(query: str):
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM vacancies;")
        initial_count = cur.fetchone()[0]
    conn.close()

    await run_parse_habr(query)

    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("SELECT company, vacancy, location, salary, skills, link FROM vacancies WHERE id > %s ORDER BY id LIMIT 5;", (initial_count,))
        rows = cur.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="Новых вакансий не найдено")
    
    return [SearchResult(company=row[0], vacancy=row[1], location=row[2], salary=row[3], skills=row[4], link=row[5]) for row in rows]

@app.get("/search_by_company", response_model=List[SearchResult])
async def search_by_company(company_name: str):
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("SELECT company, vacancy, location, salary, skills, link FROM vacancies WHERE company ILIKE %s ORDER BY RANDOM() LIMIT 5;", (f"%{company_name}%",))
        rows = cur.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"Никаких вакансий не найдено для компании: '{company_name}'")

    return [SearchResult(company=row[0], vacancy=row[1], location=row[2], salary=row[3], skills=row[4], link=row[5]) for row in rows]

@app.get("/search_by_vacancy", response_model=List[SearchResult])
async def search_by_vacancy(vacancy_query: str):
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("SELECT company, vacancy, location, salary, skills, link FROM vacancies WHERE vacancy ILIKE %s ORDER BY RANDOM() LIMIT 5;", (f"%{vacancy_query}%",))
        rows = cur.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"Никаких вакансий не найдено по запросу: '{vacancy_query}'")

    return [SearchResult(company=row[0], vacancy=row[1], location=row[2], salary=row[3], skills=row[4], link=row[5]) for row in rows]

async def run_parse_habr(query):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor, parse_habr, query)
