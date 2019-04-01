from selenium import webdriver
import page
import csv

WEB_DRIVER_PATH = "Drivers\\chromedriver.exe"
SEARCH_KEY = "software testing"
CSV_FILE = "results.csv"

'''
SearchItem object represents an item in amazon.
'''


class SearchItem:
    def __init__(self):
        self.authors = []
        self.price = ""
        self.num_stars = 0
        self.num_reviews = "0"
        self.item_name = 0
        self.item_date = 0
        self.link = ""
        self.asin = 0

    '''
    get the item as an array of values.
    '''
    def serialize(self):
        data = [self.item_name]
        data += [self.item_date]

        # Can have more than one author, this is the reason for the weirdness
        authors = ""
        for author in self.authors:
            authors += author + '|'
        authors = authors[:-1]
        data += [authors]
        data += [self.price]
        data += [self.num_stars]
        data += [self.num_reviews]

        return data

    @staticmethod
    def get_headers(self):
        return ["Item Name", "Item Date", "Authors",
                "Price", "#stars", "#reviews"]


'''
Writes a list of SearchItems to csv file.
'''


def write_to_csv(result_list):
    csv_lines = [SearchItem.get_headers(None)]
    for result in result_list:
        csv_lines += [result.serialize()]

    with open(CSV_FILE, 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csv_lines)


'''
Adds an item to cart, then goes to the cart and verifies the item is there.
'''


def check_add_to_cart(driver, element):
    item_page = page.ItemPage(driver, element.link)
    item_page.add_to_cart()

    cart_page = page.CartPage(driver)
    # asin is a unique identifier of amazon items
    cart_item_asin = cart_page.get_cart_item_asin()
    if cart_item_asin == element.asin:
        print('Item was added successfully to cart.')
    else:
        print('Failed adding item to cart.')


'''
Iterates over the first 4 pages in amazon after searching "software testing".
Write each item to SearchItem object and returns a list of those items.
'''


def get_search_results(search_page):
    results = []
    for i in range(1, 5):
        print("Getting page number: {}.".format(i))
        search_page.get_page_num(i)
        item_data_list = search_page.get_web_elements()

        for item_data in item_data_list:
            amazon_item = SearchItem()
            amazon_item.item_name = search_page.get_item_name(item_data)
            amazon_item.item_date = search_page.get_item_date(item_data)
            amazon_item.authors = search_page.get_item_authors(item_data)
            amazon_item.price = search_page.get_item_price(item_data)
            amazon_item.num_stars = search_page.get_item_stars(item_data)
            amazon_item.num_reviews = search_page.get_item_reviews(item_data)
            amazon_item.asin = search_page.get_item_asin(item_data)
            amazon_item.link = search_page.get_item_link(item_data)
            results.append(amazon_item)

    return results


def main():
    print("Starting test.")
    driver = webdriver.Chrome(WEB_DRIVER_PATH)
    search_page = page.SearchPage(driver, SEARCH_KEY)
    search_results = get_search_results(search_page)

    print("Writing results to csv.")
    write_to_csv(search_results)

    # Not all elements have add to cart,
    # in addition we might have stale links here.
    # TODO: get random element
    # TODO: get link url instead of using click
    # TODO: verify that the result have add to cart function,
    # if not choose random again
    print("Check adding to the cart.")
    check_add_to_cart(driver, search_results[search_results.__len__() - 2])

    search_page.quit()


if __name__ == '__main__':
    main()
