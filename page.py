'''
Page.py
All the pages representations and locators are here.
The main are:
    SearchPage -  the page with the search result
    ItemPage - a page when clicking on an item
    CartPage - the cart with the added items
'''
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def quit(self):
        self.driver.quit()

    def get_web_elements(self):
        return None


class BaseLocators:
    ITEM_ASIN = "data-asin"


class SearchPageLocators(BaseLocators):
    SEARCH_URL = "https://www.amazon.com/{0}/s?k={0}&page={1}"

    ITEMS_PATH = "//*[@id='search']/div[1]/div[2]/div/span[3]/div[1]/div"

    ITEM_NAME = ".//*[@class='a-size-medium a-color-base a-text-normal']"
    ITEM_DATE = ".//*[@class='a-size-base a-color-secondary a-text-normal']"

    ITEM_STARS_PATH = \
        ".//div[@class='a-section a-spacing-none a-spacing-top-micro']"
    ITEM_STARS = ".//span[@{}]"
    ITEM_STARS_KEY = "aria-label"

    ITEM_REVIEWS = ".//div[@class='a-row a-size-small']/span/a"

    ITEM_AUTHORS_PATH = ".//div[@class='a-row a-size-base a-color-secondary']"
    ITEM_AUTHORS = ".//*[starts-with(@class,'a-size-base')]"
    ITEM_AUTHORS_END_SYMBOL = "|"
    # amazon internal used words we ignore when searching for the authors.
    IGNORED_AUTHORS = ['by', ', et al.', ',', 'and']

    ITEM_PRICE_SYMBOL = ".//*[@class='a-price-symbol']"
    ITEM_PRICE_WHOLE = ".//*[@class='a-price-whole']"
    ITEM_PRICE_FRACTION = ".//*[@class='a-price-fraction']"

    ITEM_LINK = ".//a[@class='a-link-normal a-text-normal']"


class SearchPage(BasePage):
    def __init__(self, driver, key):
        super().__init__(driver)
        self.locators = SearchPageLocators()
        self.key = key

    def get_page_num(self, num):
        # Will get the page number #num with the search key
        self.driver.get(self.locators.SEARCH_URL.format(self.key, num))

    def get_web_elements(self):
        return self.driver.find_elements_by_xpath(self.locators.ITEMS_PATH)

    def get_item_name(self, element):
        item_name = element.find_element_by_xpath(self.locators.ITEM_NAME).text
        return item_name

    def get_item_date(self, element):
        date = ""
        try:
            date = element.find_element_by_xpath(self.locators.ITEM_DATE).text
        except NoSuchElementException:
            pass
        return date

    def get_item_stars(self, element):
        num = 0
        try:
            stars = element.find_element_by_xpath(
                self.locators.ITEM_STARS_PATH)
            num_of_stars = stars.find_element_by_xpath(
                self.locators.ITEM_STARS.format(self.locators.ITEM_STARS_KEY))
            num_of_stars.get_attribute(self.locators.ITEM_STARS_KEY)
            # e.g 4.5 out of 5 stars, we need just the first word
            num = float(num_of_stars.get_attribute(
                self.locators.ITEM_STARS_KEY).partition(' ')[0])
        except ValueError:
            pass
        except NoSuchElementException:
            pass
        return num

    def get_item_reviews(self, element):
        num = "0"
        try:
            num = element.find_element_by_xpath(
                self.locators.ITEM_REVIEWS).text
        except NoSuchElementException:
            pass

        return num

    def get_item_price(self, element):
        price_symbol = ''
        price_whole = '0'
        price_fraction = '00'
        try:
            price_symbol = element.find_element_by_xpath(
                self.locators.ITEM_PRICE_SYMBOL).text
        except NoSuchElementException:
            pass

        try:
            price_whole = element.find_element_by_xpath(
                self.locators.ITEM_PRICE_WHOLE).text
        except NoSuchElementException:
            pass

        try:
            price_fraction = element.find_element_by_xpath(
                self.locators.ITEM_PRICE_FRACTION).text
        except NoSuchElementException:
            pass

        return price_symbol + price_whole + '.' + price_fraction

    def get_item_authors(self, element):
        authors = []
        authors_loc = element.find_element_by_xpath(
            self.locators.ITEM_AUTHORS_PATH)
        authors_list = authors_loc.find_elements_by_xpath(
            self.locators.ITEM_AUTHORS)
        for author in authors_list:
            # this marks the end of the authors,
            # the rest of the results are not relevant
            if author.text == self.locators.ITEM_AUTHORS_END_SYMBOL:
                break
            # e.g by Cem Kaner , James Bach , et al.
            if author.text not in self.locators.IGNORED_AUTHORS:
                authors.append(author.text)
        return authors

    def get_item_asin(self, element):
        return element.get_attribute(self.locators.ITEM_ASIN)

    def get_item_link(self, element):
        return element.find_element_by_xpath(self.locators.ITEM_LINK)


class ItemLocators(BaseLocators):
    ITEM_ADD_TO_CART = "//input[@id = 'add-to-cart-button']"


class ItemPage(BasePage):
    def __init__(self, driver, link):
        super().__init__(driver)
        self.locators = ItemLocators()
        link.click()
        # waiting to the item to be added to the cart.
        # TODO: wait for the page to load using wait.until
        time.sleep(3)

    def add_to_cart(self):
        self.driver.find_element_by_xpath(
            self.locators.ITEM_ADD_TO_CART).send_keys(Keys.ENTER)


class CartLocators(BaseLocators):
    ITEM_PATH = "//div[@data-asin]"
    CART_URL = "https://www.amazon.com/gp/cart/view.html?ref_=nav_cart"


class CartPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.locators = CartLocators()
        self.driver.get(self.locators.CART_URL)

    def get_cart_item_asin(self):
        try:
            item = self.driver.find_element_by_xpath(self.locators.ITEM_PATH)
            return item.get_attribute(self.locators.ITEM_ASIN)
        except NoSuchElementException:
            return -1
