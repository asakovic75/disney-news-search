import streamlit as st
import requests
import os
from datetime import datetime
import libsql_client
import asyncio
import pandas as pd
from contextlib import asynccontextmanager

# --- Настройки страницы ---
st.set_page_config(page_title="Новости и Обсуждения Disney", layout="wide")

st.markdown("""
<style>
    /* Устанавливаем светлый фон для всего приложения */
    .stApp {
        background-color: #f0f2f6; /* Светло-серый фон */
    }

    /* Делаем весь основной текст и подписи черными для лучшей читаемости */
    body, p, .st-emotion-cache-16txtl3, .st-emotion-cache-1629p8f p, .st-emotion-cache-1xarl3l {
        color: #111111;
    }

    /* Делаем заголовки тоже черными */
    h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
    }
    
    /* Убираем лишний верхний отступ */
    .st-emotion-cache-16txtl3 {
        padding-top: 2rem;
    }
    
    /* Стилизуем контейнер с комментарием, чтобы он был заметным на сером фоне */
    .st-emotion-cache-4d1qr0 {
        border-left: 5px solid #007bff; /* Синяя полоска слева */
        padding: 10px 15px;
        background-color: #ffffff; /* Белый фон для блока с комментарием */
        border-radius: 5px;
        color: #111111; /* Черный текст внутри комментария */
    }

</style>
""", unsafe_allow_html=True)

# --- Асинхронный менеджер контекста для управления подключениями к БД ---
@asynccontextmanager
async def get_db_client():
    """Создает клиент, отдает его и гарантированно закрывает после использования."""
    db_url = os.getenv("TURSO_URL")
    db_token = os.getenv("TURSO_TOKEN")
    
    if not db_url or not db_token:
        st.error("Не удалось подключиться к базе данных комментариев. Проверьте секреты TURSO_URL и TURSO_TOKEN в Streamlit Cloud.")
        st.stop()

    client = None
    try:
        client = libsql_client.create_client(url=db_url, auth_token=db_token)
        yield client
    finally:
        if client:
            await client.close()

# --- Асинхронные функции для работы с базой данных ---
async def init_db_async():
    async with get_db_client() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at DATETIME NOT NULL
            );
        """)

async def add_comment_async(name, comment):
    async with get_db_client() as db:
        await db.execute(
            "INSERT INTO comments (name, comment, created_at) VALUES (?, ?, ?)",
            [name, comment, datetime.now()]
        )

async def get_comments_async():
    async with get_db_client() as db:
        rs = await db.execute("SELECT name, comment, created_at FROM comments ORDER BY created_at DESC;")
        return pd.DataFrame(rs.rows, columns=[col for col in rs.columns])

# --- Функция для получения новостей ---
@st.cache_data(ttl=3600)
def fetch_news(search_query, in_title=False):
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return None, "Ключ API для новостей не найден."
    
    search_param = "qInTitle" if in_title else "q"
    url = (f"https://newsapi.org/v2/everything?"
           f"{search_param}={search_query}&"
           f"language=ru&"
           f"sortBy=publishedAt&"
           f"apiKey={api_key}")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("articles", []), None
        else:
            return None, f"Ошибка API. Статус: {response.status_code}"
    except Exception as e:
        return None, f"Ошибка сети: {e}"

# --- Инициализация БД ---
asyncio.run(init_db_async())

# === ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ===
st.title("🌐 Новости и Обсуждения Вселенной Disney")
st.divider()

st.header("🔍 Поиск новостей")
search_term = st.text_input("Введите ключевые слова для поиска в заголовках:", "Pixar")

if st.button("Найти"):
    if not search_term:
        st.warning("Пожалуйста, введите запрос для поиска.")
    else:
        with st.spinner("Ищу новости по вашему запросу..."):
            articles, error = fetch_news(search_term, in_title=True)
            if error:
                st.error(error)
            elif not articles:
                st.info(f"Новостей по запросу '{search_term}' не найдено.")
            else:
                st.success(f"Результаты поиска по запросу '{search_term}':")
                for article in articles[:10]:
                    st.subheader(article['title'])
                    st.caption(f"Источник: {article['source']['name']} | Опубликовано: {datetime.fromisoformat(article['publishedAt'].replace('Z', '')).strftime('%d.%m.%Y %H:%M')}")
                    st.write(article['description'])
                    st.markdown(f"[*Читать далее...*]({article['url']})")
                    st.divider()

st.header("🔥 Последние актуальные новости")
with st.spinner("Загружаю последние новости о Disney..."):
    latest_articles, error = fetch_news("Disney")
    if error:
        st.error(error)
    elif latest_articles:
        for article in latest_articles[:5]:
            st.subheader(article['title'])
            st.caption(f"Источник: {article['source']['name']} | Опубликовано: {datetime.fromisoformat(article['publishedAt'].replace('Z', '')).strftime('%d.%m.%Y %H:%M')}")
            st.markdown(f"[*Читать далее...*]({article['url']})")
            st.divider()

st.header("💬 Обсуждения и комментарии")

with st.form("comment_form", clear_on_submit=True):
    name = st.text_input("Ваше имя:")
    comment = st.text_area("Ваш комментарий:")
    submitted = st.form_submit_button("Отправить комментарий")
    if submitted:
        if name and comment:
            asyncio.run(add_comment_async(name, comment))
            st.success("Спасибо, ваш комментарий добавлен!")
            st.experimental_rerun()
        else:
            st.warning("Пожалуйста, заполните все поля.")

st.subheader("Последние комментарии")
all_comments = asyncio.run(get_comments_async())

if all_comments.empty:
    st.info("Комментариев пока нет. Будьте первым!")
else:
    for index, row in all_comments.iterrows():
        with st.container():
            created_time = row['created_at']
            if isinstance(created_time, str):
                try:
                    created_time = datetime.strptime(created_time, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    created_time = datetime.fromisoformat(created_time)
            
            st.text(f"👤 {row['name']} | 🕓 {created_time.strftime('%d.%m.%Y %H:%M')}")
            st.info(row['comment'])
