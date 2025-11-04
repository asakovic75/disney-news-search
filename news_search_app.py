import streamlit as st
import requests
import os
from datetime import datetime
from urllib.parse import quote
import json

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

@st.cache_data(ttl=3600)
def fetch_google_news(search_query):
    """Ищет новости через Google News API от Serper.dev."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return None, "Ключ SERPER_API_KEY не найден в секретах."

    url = "https://google.serper.dev/news"
    payload = json.dumps({"q": search_query, "gl": "ru", "hl": "ru"})
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            results = response.json().get("news", [])
            return results, None
        else:
            return None, f"Ошибка API Serper. Статус: {response.status_code}, Ответ: {response.text}"
    except Exception as e:
        return None, f"Ошибка сети: {e}"

# === ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ===
st.title("🌐 Дайджест Новостей Вселенной Disney")
st.write("Поиск актуальных новостей на любых сайтах, включая официальные источники и тематические блоги.")
st.divider()

# --- Раздел "Последние актуальные новости" ---
st.header("🔥 Последние актуальные новости")

relevant_keywords = (
    'Disney OR Pixar OR Marvel OR Lucasfilm OR "Star Wars" OR Диснейленд '
    'site:thewaltdisneycompany.com OR site:daily.afisha.ru'
)

with st.spinner("Загружаю самые релевантные новости из Google..."):
    latest_articles, error = fetch_google_news(relevant_keywords)

    if latest_articles:
        st.success(f"Найдено свежих новостей: {len(latest_articles)}")

    if error:
        st.error(error)
    elif latest_articles:
        for article in latest_articles[:7]:
            st.subheader(article['title'])
            date_published_str = article.get('date', 'Дата неизвестна')
            st.caption(f"Источник: {article['source']} | Опубликовано: {date_published_str}")
            st.write(article.get('snippet', 'Описание отсутствует.')) # Используем snippet 
            st.markdown(f"[*Читать далее...*]({article['link']})")
            st.divider()
    else:
        st.info("Не удалось найти свежих новостей по ключевым темам Disney в Google.")

# --- Раздел "Поиск новостей" ---
st.header("🔍 Индивидуальный поиск в Google News")
search_term = st.text_input("Введите запрос для поиска (например, 'Avatar 4' или 'Bob Iger'):", "Toy Story 5")

if st.button("Найти"):
    if not search_term:
        st.warning("Пожалуйста, введите запрос для поиска.")
    else:
        with st.spinner(f"Ищу в Google News по запросу '{search_term}'..."):
            articles, error = fetch_google_news(search_term)

            if articles:
                st.success(f"Найдено результатов: {len(articles)}")

            if error:
                st.error(error)
            elif not articles:
                st.info(f"Новостей по запросу '{search_term}' не найдено.")
            else:
                for article in articles[:10]:
                    st.subheader(article['title'])
                    date_published_str = article.get('date', 'Дата неизвестна')
                    st.caption(f"Источник: {article['source']} | Опубликовано: {date_published_str}")
                    st.write(article.get('snippet', 'Описание отсутствует.'))
                    st.markdown(f"[*Читать далее...*]({article['link']})")
                    st.divider()
