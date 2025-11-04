import streamlit as st
import requests
import os
from datetime import datetime
from urllib.parse import quote

# --- Настройки страницы ---
st.set_page_config(page_title="Новости Вселенной Disney", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; }
    body, p, .st-emotion-cache-16txtl3, .st-emotion-cache-1629p8f p, .st-emotion-cache-1xarl3l, h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
    }
    .st-emotion-cache-16txtl3 { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- Функция для получения новостей ---
@st.cache_data(ttl=3600)
def fetch_news(search_query):
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return None, "Ключ API для новостей не найден."
    
    encoded_query = quote(search_query)
    
    url = (f"https://newsapi.org/v2/everything?"
           f"qInTitle={encoded_query}&"
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

# === ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ===
st.title("🌐 Дайджест новостей вселенной Disney")
st.divider()

# --- Раздел "Последние актуальные новости" ---
st.header("🔥 Последние актуальные новости")

# детализированный список ключевых слов
relevant_keywords = (
    'Disney OR "The Walt Disney Company" OR '
    'Pixar OR "Pixar Animation Studios" OR '
    'Marvel OR "Marvel Studios" OR MCU OR '
    'Lucasfilm OR "Star Wars" OR "Индиана Джонс" OR '
    '"20th Century Studios" OR "Searchlight Pictures" OR '
    '"National Geographic" OR '
    'ESPN OR '
    '"Walt Disney Animation Studios" OR '
    'Disneyland OR "Disneyland Resort" OR '
    '"Walt Disney World" OR '
    '"Disney Cruise Line" OR '
    '"Inside Out" OR "Головоломка" OR '
    '"The Mandalorian & Grogu" OR "Мандалорец" OR '
    '"Moana" OR "Моана" OR '
    '"Zootopia" OR "Зверополис" OR '
    '"Frozen" OR "Холодное сердце"'
)

with st.spinner("Загружаю самые релевантные новости..."):
    latest_articles, error = fetch_news(relevant_keywords)
    if error:
        st.error(error)
    elif latest_articles:
        for article in latest_articles[:7]: # 7 новостей 
            st.subheader(article['title'])
            try:
                date_published = datetime.fromisoformat(article['publishedAt'].replace('Z', '')).strftime('%d.%m.%Y %H:%M')
            except:
                date_published = "Неизвестно"
            
            st.caption(f"Источник: {article['source']['name']} | Опубликовано: {date_published}")
            st.markdown(f"[*Читать далее...*]({article['url']})")
            st.divider()
    else:
        st.info("Не удалось найти свежих новостей по ключевым темам Disney.")

# --- Раздел "Поиск новостей" ---
st.header("🔍 Индивидуальный поиск новостей")
search_term = st.text_input("Введите ключевые слова для поиска в заголовках (например, 'Avatar 4' или 'Bob Iger'):", "Toy Story 5")

if st.button("Найти"):
    if not search_term:
        st.warning("Пожалуйста, введите запрос для поиска.")
    else:
        with st.spinner(f"Ищу новости по запросу '{search_term}'..."):
            articles, error = fetch_news(search_term)
            if error:
                st.error(error)
            elif not articles:
                st.info(f"Новостей по запросу '{search_term}' не найдено.")
            else:
                st.success(f"Результаты поиска по запросу '{search_term}':")
                for article in articles[:10]:
                    st.subheader(article['title'])
                    try:
                        date_published = datetime.fromisoformat(article['publishedAt'].replace('Z', '')).strftime('%d.%m.%Y %H:%M')
                    except:
                        date_published = "Неизвестно"

                    st.caption(f"Источник: {article['source']['name']} | Опубликовано: {date_published}")
                    if article['description']:
                      st.write(article['description'])
                    st.markdown(f"[*Читать далее...*]({article['url']})")
                    st.divider()

