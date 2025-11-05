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

# --- Функция для поиска новостей через Google (Serper.dev) ---
@st.cache_data(ttl=1800) # Кэшируем результат на 30 минут
def fetch_google_news(search_query):
    """Ищет новости через Google News API от Serper.dev."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return None, "Ключ SERPER_API_KEY не найден в секретах."

    url = "https://google.serper.dev/news"
    # Добавляем в запрос требование искать только за последнюю неделю для свежести
    payload = json.dumps({"q": search_query, "gl": "ru", "hl": "ru", "tbs": "qdr:w"})
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
st.title("🌐 Дайджест новостей вселенной Disney")
st.write("Автоматический поиск самых актуальных новостей о компаниях, проектах и парках Disney.")
st.divider()

# --- Раздел "Последние актуальные новости" ---
st.header("🔥 Последние релевантные новости")

# Каждая фраза в кавычках ищется как единое целое. Оператор OR ищет хотя бы одно совпадение.
relevant_keywords = (
    # Корпоративные новости
    '"The Walt Disney Company" OR TWDC OR "Bob Iger" OR "Disney earnings" OR '
    # Студии и бренды
    'Pixar OR "Marvel Studios" OR MCU OR Lucasfilm OR "Star Wars" OR '
    '"20th Century Studios" OR "Searchlight Pictures" OR "Walt Disney Animation Studios" OR '
    # Парки и продукты
    'Disneyland OR "Walt Disney World" OR "Disney Cruise Line" OR "Disney merchandise" OR '
    # Платформы
    '"Disney+" OR "Disney Plus" OR Hulu OR '
    # Конкретные проекты (добавлены русские аналоги)
    '"Inside Out" OR "Головоломка" OR "The Mandalorian & Grogu" OR "Мандалорец" OR '
    '"Moana" OR "Моана" OR "Zootopia" OR "Зверополис" OR "Frozen" OR "Холодное сердце" OR '
    '"Toy Story 5" OR "Snow White" OR "Avatar"'
)

with st.spinner("Загружаю самые релевантные новости из Google за последнюю неделю..."):
    latest_articles, error = fetch_google_news(relevant_keywords)

    if error:
        st.error(error)
    elif latest_articles:
        st.success(f"Найдено свежих новостей по вашим ключевым темам: {len(latest_articles)}")
        for article in latest_articles[:10]: # Показываем до 10 новостей
            st.subheader(article['title'])
            date_published_str = article.get('date', 'Дата неизвестна')
            st.caption(f"Источник: {article['source']} | Опубликовано: {date_published_str}")
            st.write(article.get('snippet', 'Описание отсутствует.'))
            st.markdown(f"[*Читать далее...*]({article['link']})")
            st.divider()
    else:
        st.info("Не удалось найти свежих новостей по вашим ключевым темам за последнюю неделю.")

# --- Раздел "Индивидуальный поиск" ---
st.header("🔍 Индивидуальный поиск")
st.write("Здесь вы можете использовать более специфичные запросы из вашего списка, например, с именами руководителей или юридическими терминами.")

# Примеры для пользователя
st.info('Примеры запросов: `Bob Chapek`, ` Zootopia`, ` Toy Story 5`')

search_term = st.text_input("Введите ваш точный запрос для поиска:", "")

if st.button("Найти"):
    if not search_term:
        st.warning("Пожалуйста, введите запрос для поиска.")
    else:
        with st.spinner(f"Ищу в Google News по запросу '{search_term}'..."):
            articles, error = fetch_google_news(search_term)

            if error:
                st.error(error)
            elif not articles:
                st.info(f"Новостей по запросу '{search_term}' не найдено.")
            else:
                st.success(f"Найдено результатов: {len(articles)}")
                for article in articles[:15]:
                    st.subheader(article['title'])
                    date_published_str = article.get('date', 'Дата неизвестна')
                    st.caption(f"Источник: {article['source']} | Опубликовано: {date_published_str}")
                    st.write(article.get('snippet', 'Описание отсутствует.'))
                    st.markdown(f"[*Читать далее...*]({article['link']})")
                    st.divider()


