from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import time
import pandas as pd
import matplotlib.pyplot as plt
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

options = webdriver.FirefoxOptions()
# options.add_argument('--headless')

service = Service(executable_path=GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

url = "https://lu.ru/sortament/lyustri/"
driver.get(url)
time.sleep(5)

# Прокручиваем страницу для подгрузки товаров (можно изменить количество прокруток)
for _ in range(7):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# Получаем HTML-код всей загруженной страницы
html = driver.page_source

# Создаём объект soup
# soup = BeautifulSoup(html, 'html.parser')
# Собираем цены
items = driver.find_elements(By.CSS_SELECTOR, "div.product-block")

prices = []

for item in items:
    try:
        price_element = item.find_element(By.CSS_SELECTOR, ".new-price span:not(.price_currency)")
        price_text = price_element.text.strip()
        price_int = int(price_text.replace('₽', '').replace(' ', '').replace('\u202f', ''))
        prices.append(price_int)
    except Exception as e:
        print(f"Ошибка при извлечении цены: {e}")
        continue

driver.quit()

# Сохраняем в CSV
df = pd.DataFrame({'Цена': prices})
df.to_csv('lus.csv', index=False)
print('Данные сохранены в lus.csv')

# Обработка данных
if not df.empty:
    mean_price = df['Цена'].mean()
    print(f'Средняя цена: {mean_price:.0f} руб.')

    # Гистограмма
    plt.figure(figsize=(10, 6))
    plt.hist(df['Цена'], bins=20, color='skyblue', edgecolor='black')
    plt.title('Гистограмма цен')
    plt.xlabel('Цена, руб.')
    plt.ylabel('Количество')
    plt.grid(True)
    plt.show()
else:
    print('Нет данных для анализа.')