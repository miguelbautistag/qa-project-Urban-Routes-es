import time
import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:

    #Localizadores
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    request_taxi_button = (By.CSS_SELECTOR, ".button.round")
    tariff_container = (By.CLASS_NAME, "tariff-container")
    comfort_button = (By.XPATH,
                      '//div[@class="tcard-title" and text()="Comfort"]/ancestor::div[contains(@class, "tcard")]')
    phone_button = (By.CLASS_NAME, 'np-button')
    phone_input = (By.ID, 'phone')
    phone_submit = (By.CSS_SELECTOR, '.button.full')
    enter_code = (By.XPATH, '//div[@class="input-container"]/input[@id="code"]')
    confirm_button = (By.XPATH, '//button[text()="Confirmar"]')
    payment_method = (By.CSS_SELECTOR, '.pp-button.filled')
    add_card = (By.CSS_SELECTOR, '.pp-row.disabled')
    card_number = (By.ID, 'number')
    card_code = (By.CSS_SELECTOR, 'input#code.card-input')
    card_box = (By.CLASS_NAME, 'card-wrapper')
    add_button = (By.XPATH, '//button[@class="button full" and text()="Agregar"]')
    payment_modal_close_button = (By.XPATH, '(//div[contains(@class, "payment-picker") and contains(@class, "open")]//button[contains(@class, "close-button") and contains(@class, "section-close")])[1]')
    message_driver = (By.ID, 'comment')
    blanket_and_tishue_locator = (By.CSS_SELECTOR, '.slider.round')
    ice_cream = (By.CLASS_NAME, 'counter-plus')
    book_taxi_button = (By.CLASS_NAME, 'smart-button-main')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def set_from(self, from_address):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.from_field)
        )
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def set_route(self, from_address, to_address):
        self.set_from(from_address)
        self.set_to(to_address)

    #Taxi Request
    def click_request_taxi(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.request_taxi_button)
        ).click()

    #Select Comfort
    def select_comfort_fare(self):
        self.wait.until(EC.element_to_be_clickable(self.comfort_button)).click()

    #Assert Comfort Selection - NEW ASSERT!!
    def verify_comfort_selected(self):
        comfort_element = self.driver.find_element(By.XPATH, '//div[@class="tcard-title" and text()="Comfort"]')
        assert comfort_element.is_displayed(), "La tarifa Comfort no está visible como se esperaba."

    #Phone Number
    def click_phone_number(self):
        self.wait.until(EC.element_to_be_clickable(self.phone_button)).click()

    def enter_fill_phone_number(self):
        phone_element = self.wait.until(EC.element_to_be_clickable(self.phone_input))
        phone_element.send_keys(data.phone_number)
        self.driver.find_element(*self.phone_submit).click()

    #Confirm Phone Code
    def enter_verification_code(self, code):
        code_field = self.wait.until(EC.presence_of_element_located(self.enter_code))
        code_field.send_keys(code)
        confirm_button = self.wait.until(EC.element_to_be_clickable(self.confirm_button))
        confirm_button.click()

    #Assert Phone Verified - NEW ASSERT!!
    def verify_phone_verified(self):
        assert self.driver.find_element(
            *self.payment_method).is_displayed(), "La verificación telefónica no redirigió a la pantalla de métodos de pago."

    #Add Credit Card
    def change_payment_method(self):
        self.driver.find_element(*self.payment_method).click()
        self.driver.find_element(*self.add_card).click()
        card_element = self.wait.until(EC.element_to_be_clickable(self.card_number))
        card_element.send_keys(data.card_number)
        self.wait.until(EC.visibility_of_element_located(self.card_code)).send_keys(data.card_code)
        self.driver.find_element(*self.card_box).click()
        self.driver.find_element(*self.add_button).click()
        close_btn = self.wait.until(EC.element_to_be_clickable(self.payment_modal_close_button))
        close_btn.click()

    #Assert Payment method add and window closed - NEW ASSERT!!
    def verify_payment_method_closed(self):
        picker = self.driver.find_element(By.CLASS_NAME, 'payment-picker')
        assert "open" not in picker.get_attribute("class"), "El modal de métodos de pago no se cerró correctamente."

    #Message to Driver
    def message_to_driver(self):
        self.wait.until(EC.visibility_of_element_located(self.message_driver)).send_keys(data.message_for_driver)

    #Assert Message to Driver - NEW ASSERT!!
    def verify_message_sent(self, expected_message):
        field = self.driver.find_element(*self.message_driver)
        actual_message = field.get_attribute("value")
        assert actual_message == expected_message, f"El mensaje al conductor no se ingresó correctamente. Esperado: '{expected_message}', pero fue: '{actual_message}'"

    #Request Blanket and Tishue
    def add_blanket_and_tishue(self):
        self.wait.until(EC.visibility_of_element_located(self.blanket_and_tishue_locator)).click()

    #Assert Blanket and Tishue Added: - NEW ASSERT!!
    def verify_blanket_requested(self):
        toggle = self.driver.find_element(*self.blanket_and_tishue_locator)
        assert toggle.is_displayed(), "El switch de cobijas y pañuelos no se activó correctamente."

    #Request 2 Ice Creams
    def add_ice_creams(self):
        self.driver.find_element(*self.ice_cream).click()
        self.driver.find_element(*self.ice_cream).click()

    #Assert Ice Cream Counter - NEW ASSERT!!
    def verify_ice_creams(self, expected_count=2):
        counter = self.driver.find_element(By.CLASS_NAME, 'counter-value')
        assert counter.text == str(expected_count), f"Se esperaban {expected_count} helados, pero hay {counter.text}"

    #Request Taxi
    def click_book_taxi_button(self):
        self.driver.find_element(*self.book_taxi_button).click()
        time.sleep(3)

    #Assert Taxi Requested - NEW ASSERT!!
    def verify_searching_taxi(self):
        searching = self.driver.find_element(By.CSS_SELECTOR, 'div.order.shown')
        assert searching.is_displayed(), "No se está mostrando el mensaje de búsqueda de taxi."

class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        # no lo modifiques, ya que necesitamos un registro adicional habilitado para recuperar el código de confirmación del teléfono
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
        cls.driver = webdriver.Chrome(options=options)

#1 Test Set Route
    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_from(address_from)
        routes_page.set_to(address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

#2 Test Request Taxi (Comfort)
    def test_select_comfort_fare(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_from(data.address_from)
        routes_page.set_to(data.address_to)
        routes_page.click_request_taxi()
        routes_page.select_comfort_fare()
        routes_page.verify_comfort_selected()

#3 Test Fill Phone Number
    def test_fill_phone_number(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_from(data.address_from)
        routes_page.set_to(data.address_to)
        routes_page.click_request_taxi()
        routes_page.select_comfort_fare()
        routes_page.click_phone_number()
        routes_page.enter_fill_phone_number()
        confirmation_code = retrieve_phone_code(self.driver)
        print(f"Código de confirmación obtenido: {confirmation_code}")
        routes_page.enter_verification_code(confirmation_code)
        routes_page.verify_phone_verified()

#4 Test Change Payment Method
    def test_change_payment_method(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_from(data.address_from)
        routes_page.set_to(data.address_to)
        routes_page.click_request_taxi()
        routes_page.select_comfort_fare()
        routes_page.click_phone_number()
        routes_page.enter_fill_phone_number()
        confirmation_code = retrieve_phone_code(self.driver)
        print(f"Código de confirmación obtenido: {confirmation_code}")
        routes_page.enter_verification_code(confirmation_code)
        routes_page.change_payment_method()
        routes_page.verify_payment_method_closed()

#5 Test Message Driver
    def test_message_driver(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_from(data.address_from)
        routes_page.set_to(data.address_to)
        routes_page.click_request_taxi()
        routes_page.select_comfort_fare()
        routes_page.click_phone_number()
        routes_page.enter_fill_phone_number()
        confirmation_code = retrieve_phone_code(self.driver)
        print(f"Código de confirmación obtenido: {confirmation_code}")
        routes_page.enter_verification_code(confirmation_code)
        routes_page.change_payment_method()
        routes_page.message_to_driver()
        routes_page.verify_message_sent(data.message_for_driver)

#6 Test Request Blanket and Tishue
    def test_request_blanket(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_from(data.address_from)
        routes_page.set_to(data.address_to)
        routes_page.click_request_taxi()
        routes_page.select_comfort_fare()
        routes_page.click_phone_number()
        routes_page.enter_fill_phone_number()
        confirmation_code = retrieve_phone_code(self.driver)
        print(f"Código de confirmación obtenido: {confirmation_code}")
        routes_page.enter_verification_code(confirmation_code)
        routes_page.change_payment_method()
        routes_page.message_to_driver()
        routes_page.add_blanket_and_tishue()
        routes_page.verify_blanket_requested()

#7 Test Request 2 Ice Creams  - NEW TEST INCLUDED!!
    def test_request_ice_creams(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_from(data.address_from)
        routes_page.set_to(data.address_to)
        routes_page.click_request_taxi()
        routes_page.select_comfort_fare()
        routes_page.click_phone_number()
        routes_page.enter_fill_phone_number()
        confirmation_code = retrieve_phone_code(self.driver)
        print(f"Código de confirmación obtenido: {confirmation_code}")
        routes_page.enter_verification_code(confirmation_code)
        routes_page.change_payment_method()
        routes_page.message_to_driver()
        routes_page.add_blanket_and_tishue()
        routes_page.add_ice_creams()
        routes_page.verify_ice_creams()

#8 Test Window Search Taxi
    def test_window_seach_taxi(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_from(data.address_from)
        routes_page.set_to(data.address_to)
        routes_page.click_request_taxi()
        routes_page.select_comfort_fare()
        routes_page.click_phone_number()
        routes_page.enter_fill_phone_number()
        confirmation_code = retrieve_phone_code(self.driver)
        print(f"Código de confirmación obtenido: {confirmation_code}")
        routes_page.enter_verification_code(confirmation_code)
        routes_page.change_payment_method()
        routes_page.message_to_driver()
        routes_page.add_blanket_and_tishue()
        routes_page.add_ice_creams()
        routes_page.click_book_taxi_button()
        routes_page.verify_searching_taxi()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()