import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Учетные данные для входа на сайт PetFriends
email = "maks-efimov-2001@mail.ru"
password = "KvazarLibri2001"

@pytest.fixture
def driver():
    # Настройки для headless режима
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Устанавливаем драйвер для Chrome
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.implicitly_wait(10)  # Неявное ожидание для всех элементов
    yield driver
    driver.quit()

def test_petfriends(driver):
    # Шаг 1: Переходим на страницу авторизации
    driver.get("https://petfriends.skillfactory.ru/login")
    wait = WebDriverWait(driver, 20)  # Явное ожидание до 20 секунд

    try:
        # Вводим email
        email_input = wait.until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_input.send_keys(email)

        # Вводим пароль
        password_input = wait.until(
            EC.presence_of_element_located((By.ID, "pass"))
        )
        password_input.send_keys(password)

        # Нажимаем кнопку входа
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()

        # Шаг 2: Переходим на страницу "Мои питомцы"
        driver.get("https://petfriends.skillfactory.ru/my_pets")

        # Явное ожидание секции с питомцами
        pets_section = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#all_my_pets > table'))
        )

        rows = pets_section.find_elements(By.CSS_SELECTOR, "tr")
        total_pets = len(rows) - 1  # Минус 1, так как первая строка может быть заголовком
        assert total_pets > 0, "Не найдено ни одного питомца"

        names = set()
        pets_with_photo = 0
        all_pets = []

        for row in rows[1:]:  # Пропускаем первую строку (заголовки)
            cells = row.find_elements(By.CSS_SELECTOR, "td")

            # Проверяем, что количество ячеек соответствует ожиданиям
            assert len(cells) == 4, "Количество ячеек в строке таблицы не соответствует ожиданию"

            # Явные ожидания для данных питомцев
            name = wait.until(
                EC.visibility_of_element_located((By.XPATH, f"//tr[{rows.index(row) + 1}]/td[1]"))
            ).text.strip()
            breed = wait.until(
                EC.visibility_of_element_located((By.XPATH, f"//tr[{rows.index(row) + 1}]/td[2]"))
            ).text.strip()
            age = wait.until(
                EC.visibility_of_element_located((By.XPATH, f"//tr[{rows.index(row) + 1}]/td[3]"))
            ).text.strip()

            # Проверяем, что имя, возраст и порода не пустые
            assert name, "Имя питомца отсутствует"
            assert breed, "Порода питомца отсутствует"
            assert age, "Возраст питомца отсутствует"

            # Проверяем наличие фото в соответствующей ячейке
            try:
                img_element = row.find_element(By.TAG_NAME, "img")
                if img_element.get_attribute('src'):
                    pets_with_photo += 1
            except NoSuchElementException:
                pass

            # Собираем данные о питомцах
            all_pets.append((name, breed, age))
            names.add(name)  # Собираем имена для проверки уникальности

        # Проверка: у всех питомцев есть уникальные имена
        assert len(names) == total_pets, "Найдены питомцы с одинаковыми именами"

        # Проверка: хотя бы у одного питомца есть фото
        assert pets_with_photo > 0, "Ни у одного питомца нет фото"

        print(f"Всего питомцев: {total_pets}")
        print(f"Питомцев с фото: {pets_with_photo}")
        print("Данные о питомцах:", all_pets)

    except Exception as e:
        print(f"Ошибка при выполнении теста: {e}")
        print("Текущий HTML-код страницы:")
        print(driver.page_source)
        raise
