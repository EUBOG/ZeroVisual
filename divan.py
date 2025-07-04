from playwright.sync_api import sync_playwright
import pandas as pd
import time
import matplotlib.pyplot as plt

url = "https://www.divan.ru/category/divany "

prices = []

with sync_playwright() as p:
    # Запуск браузера с пользовательским агентом
    browser = p.chromium.launch(headless=False)  # headless=True — фоновый режим
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    page = context.new_page()

    print("Открываем страницу...")
    try:
        page.goto(url, timeout=60000)  # увеличенный таймаут до 60 секунд
    except Exception as e:
        print(f"[ERROR] Не удалось загрузить страницу: {e}")
        page.screenshot(path="timeout_error.png")  # сохраняем скриншот для диагностики
        context.close()
        exit()

    # Ждём загрузки товаров
    time.sleep(5)

    # Прокручиваем страницу для подгрузки товаров
    for _ in range(7):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

    # Получаем элементы цен
    price_elements = page.query_selector_all("span.ui-LD-ZU.KIkOH")

    print(f"Найдено {len(price_elements)} цен")
    for el in price_elements:
        text = el.inner_text().strip()
        print(f"Исходная цена: {text}")  # Для отладки
        try:
            # Чистим текст цены: оставляем только цифры
            cleaned_text = ''.join(filter(str.isdigit, text))
            if cleaned_text:
                price = int(cleaned_text)
                prices.append(price)
            else:
                print(f"Не удалось извлечь цену из: {text}")
        except Exception as e:
            print(f"Ошибка при обработке цены: {e}")

    context.close()

# Сохраняем в CSV
df = pd.DataFrame({'Цена': prices})
df.to_csv('divan.csv', index=False)
print('Данные сохранены в divan.csv')

# Гистограмма
if not df.empty:
    mean_price = df['Цена'].mean()
    print(f'Средняя цена: {mean_price:.0f} руб.')

    plt.figure(figsize=(10, 6))
    plt.hist(df['Цена'], bins=20, color='skyblue', edgecolor='black')
    plt.title('Гистограмма цен')
    plt.xlabel('Цена, руб.')
    plt.ylabel('Количество')
    plt.grid(True)
    plt.show()
else:
    print('Нет данных для анализа.')