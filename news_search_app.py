import streamlit as st
import requests
import os
from datetime import datetime
import libsql_client

# --- Настройки страницы ---
st.set_page_config(page_title="Новости и Обсуждения Disney", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; }
    .st-emotion-cache-16txtl3 { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

db_url = os.getenv("TURSO_URL")
db_token = os.getenv("TURSO_TOKEN")
db_client = None

if db_url and db_token:
    try:
        # Создаем клиент для подключения к БД
        db_client = libsql_client.create_client(url=db_url, auth_token=db_token)
    except Exception as e:
        st.error(f"Не удалось создать клиент для базы данных: {e}")
        st.stop()
else:
    st.error("Не удалось подключиться к базе данных комментариев. Проверьте секреты TURSO_URL и TURSO_TOKEN в Streamlit Cloud.")
    st.stop()

# --- Функции для работы с базой данных ---
def init_db():
    if db_client:
        db_client.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at DATETIME NOT NULL
            );
        """)

def add_comment(name, comment):
    if db_client:
        db_client.execute(
            "INSERT INTO comments (name, comment, created_at) VALUES (?, ?, ?)",
            [name, comment, datetime.now()]
        )

def get_comments():
    if db_client:
        rs = db_client.execute("SELECT name, comment, created_at FROM comments ORDER BY created_at DESC;")
        return pd.DataFrame(rs.rows, columns=[col for col in rs.columns])
    return pd.DataFrame()


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

# --- Инициализация базы данных ---
init_db()


# === НАЧАЛО ИНТЕРФЕЙСА ПРИЛОЖЕНИЯ ===
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
            add_comment(name, comment)
            st.success("Спасибо, ваш комментарий добавлен!")
        else:
            st.warning("Пожалуйста, заполните все поля.")

st.subheader("Последние комментарии")
all_comments = get_comments()

if all_comments.empty:
    st.info("Комментариев пока нет. Будьте первым!")
else:
    for index, row in all_comments.iterrows():
        with st.container():
            if isinstance(row['created_at'], str):
                created_time = datetime.fromisoformat(row['created_at'])
            else:
                created_time = row['created_at']
            st.text(f"👤 {row['name']} | 🕓 {created_time.strftime('%d.%m.%Y %H:%M')}")
            st.info(row['comment'])
