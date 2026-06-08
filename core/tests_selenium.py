from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import os

class SecurityRegressionTests(StaticLiveServerTestCase):
    fixtures = ['testdb.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")

        if os.environ.get('CI'):
            opts.binary_location = '/usr/bin/firefox'
            service = Service(executable_path='/usr/local/bin/geckodriver')
            cls.selenium = WebDriver(service=service, options=opts)
        else:
            cls.selenium = WebDriver(options=opts)

        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_role_restriction(self):
        """AUDITORIA: L'analista no ha d'entrar a /admin/"""
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))

        self.selenium.find_element(By.NAME, "username").send_keys("analista1")
        self.selenium.find_element(By.NAME, "password").send_keys("analista1234")
        self.selenium.find_element(By.CSS_SELECTOR, "[type=submit]").click()

        WebDriverWait(self.selenium, 10).until(
            lambda d: '/login' not in d.current_url
        )

        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))

        self.assertNotEqual(
            self.selenium.title,
            "Site administration | Django site admin"
        )
