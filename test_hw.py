import pytest
import datetime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


email = "volodkops@list.ru"
password = "226592"


def wait(driver, sec):
    return WebDriverWait(driver, sec)

@pytest.fixture(scope="session")
def get_data():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=chrome_options)
    # Запускаем страницу в браузере
    driver.get("https://petfriends.skillfactory.ru/")
    # Регистрируемся
    driver.implicitly_wait(3)
    wait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[class$='btn-success']"))).click()
    # Выбраем ссылку акаунт уже есть
    wait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/login']"))).click()
    # вводим email
    input_email = wait(driver, 3).until(EC.presence_of_element_located((By.ID, "email")))
    input_email.send_keys(email)
    # вводим пароль
    input_pass = driver.find_element(By.ID, "pass")
    input_pass.send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    # Переходим на страницу с моими питомцами
    my_pets = wait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/nav/div[1]/ul/li[1]/a")))
    my_pets.click()
    # получим объект информацию о пользователе
    my_info = driver.find_elements(By.XPATH, "/html/body/div[1]/div/div[1]")
    # получим объект строк списка питомцев
    tr_table_my_pets = driver.find_elements(By.XPATH, "//tbody//tr")
    # вернем количество питомцев у пользователя и тело данных питомцев
    # и время для логирования
    data = datetime.datetime.now().strftime('%H_%M_%S')
    yield my_info, tr_table_my_pets, data
    driver.quit()

class TestPetFriends():

    def test_compare_my_info_and_data_my_pets(self, get_data):
        my_info, tr_table_my_pets, date = get_data
        to_list_my_info = my_info[0].text.split("\n")
        # получим строку c количеством питомцев
        count_my_pets_in_my_info = to_list_my_info[1]
        # преобразуем в число удалим
        count_my_pets_in_my_info = int(
            count_my_pets_in_my_info[count_my_pets_in_my_info.find(":") + 1:].replace(" ", ""))
     # сверим питомцев
        assert count_my_pets_in_my_info == len(tr_table_my_pets)


    def test_only_half_without_photos(self, get_data):
        _, tr_table_my_pets, date = get_data
        # получим фото
        count_with_a_foto = 0
        count_without_photos = 0
        for item in tr_table_my_pets:
            if item.find_element(By.XPATH, "th//img").get_attribute('src') == "":
                count_without_photos += 1
            else:
                count_with_a_foto += 1
        assert count_with_a_foto > count_without_photos

    def test_there_is_a_name_breed_age(self, get_data):
        # Проверим, что у всех питомцев есть атриубуты
        _, tr_table_my_pets, date = get_data
        there_is_a_name_breed_age = True
        for i in range(len(tr_table_my_pets)):
            if not there_is_a_name_breed_age:
                break
            for j in range(1, 4):
                if tr_table_my_pets[i].find_element(By.XPATH, "td[{}]".format(j)).text == "":
                    there_is_a_name_breed_age = False
                    break
        assert there_is_a_name_breed_age

    def test_all_names_are_different(self, get_data):
        # Проверим, что у питомцев разные имена.
        _, tr_table_my_pets, date = get_data
        all_names_are_different = True
        list_names = []
        for i in range(len(tr_table_my_pets)):
            name = tr_table_my_pets[i].find_element(By.XPATH, "td[1]").text
            if name in list_names:
                all_names_are_different = False
                break
            list_names.append(name)
        assert all_names_are_different

