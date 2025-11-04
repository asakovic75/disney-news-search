import streamlit as st
import requests
import os

# --- Настройки страницы ---
st.set_page_config(page_title="Новости Disney", layout="centered")

# --- Заголовок приложения ---
st.title("Поиск актуальных новостей о The Walt Disney Company")
st.write("Этот инструмент ищет самые свежие новости по вашему запросу в реальном времени.")

# --- Получаем API ключ из секретов Streamlit ---
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# --- Поле для ввода поискового запроса ---
search_term = st.text_input("Введите ключевые слова для поиска:", "Disney")

# --- Кнопка для запуска поиска ---
if st.button("Найти новости"):
    if not NEWS_API_KEY:
        st.error("Ключ API для новостей не найден. Убедитесь, что он добавлен в секреты Streamlit.")
    elif not search_term:
        st.warning("Пожалуйста, введите запрос для поиска.")
    else:
        # --- Выполняем запрос к NewsAPI ---
        url = (f"https://newsapi.org/v2/everything?"
               f"q={search_term}&"
               f"language=ru&"
               f"sortBy=popularity&"
               f"apiKey={NEWS_API_KEY}")

        with st.spinner("Ищу свежие новости..."):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])

                    if not articles:
                        st.info(f"Новостей по запросу '{search_term}' не найдено.")
                    else:
                        st.success(f"Найдено {len(articles)} новостей. Вот самые популярные:")
                        # --- Отображаем найденные статьи ---
                        for article in articles[:10]:  # Показываем только топ-10
                            st.divider()
                            st.subheader(article['title'])
                            st.write(f"**Источник:** {article['source']['name']}")
                            if article['author']:
                                st.write(f"**Автор:** {article['author']}")

                            st.write(article['description'])
                            st.markdown(f"[Читать далее на сайте источника]({article['url']})")
                else:
                    st.error(f"Произошла ошибка при обращении к API. Статус: {response.status_code}")

            except Exception as e:

                st.error(f"Произошла ошибка сети: {e}")
