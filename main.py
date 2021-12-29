from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import time


class App:

    def __init__(self):
        self.bot = webdriver.Chrome()
        self.bot.set_window_size(1500, 1000)
        self.bot.set_window_position(200, 20)

    def run(self, file_name):
        """
        Reads product url and product sizes from input file.
        """

        with open(file_name, 'r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]

        for line in lines:
            words = line.split(',')
            url = words[0]
            sizes = words[1:]
            sizes = [size.strip(' []') for size in sizes]

            self.add_to_cart(url, sizes)
        

    def add_to_cart(self, url, sizes):
        """
        Adds product to cart with given sizes, if sizes are available and collects required data.
        """

        bot = self.bot
        bot.get(url)

        title = bot.find_element(By.XPATH, '//*[@id="product-detail-app"]/div/div[2]/div[1]/div[2]/div[1]/div/div/div[1]/h1/span')
        title = str(title.text).split()
        sku = title[-1]

        try:
            price = bot.find_element(By.XPATH, '//*[@id="product-detail-app"]/div/div[2]/div[1]/div[2]/div[1]/div/div/div[4]/div/div/span')
        except NoSuchElementException:
            price = bot.find_element(By.XPATH, '//*[@id="product-detail-app"]/div/div[2]/div[1]/div[2]/div[1]/div/div/div[4]/div/div/div[3]/div[2]/span')
        price = price.text

        size_variants = bot.find_element(By.XPATH, '//*[@id="product-detail-app"]/div/div[2]/div[1]/div[2]/div[3]/div[2]')
        avl_sizes = size_variants.find_elements(By.TAG_NAME, 'div')
        not_avl_sizes = size_variants.find_elements(By.CLASS_NAME, 'so')

        avl_sizes = [size for size in avl_sizes if size not in not_avl_sizes]

        added_sizes = []
        for s in avl_sizes:
            if s.text in sizes:
                s.click()
                time.sleep(5)
                try:
                    cart_button = bot.find_element(By.XPATH, '//*[@id="product-detail-app"]/div/div[2]/div[1]/div[2]/div[5]/button')
                    cart_button.click()
                except NoSuchElementException:
                    print('size not available')
                else:
                    added_sizes.append(int(s.text))
                time.sleep(5)

        if added_sizes:
            self.mark_ordered(url, added_sizes, sku, price)

    def mark_ordered(self, url, added_sizes, sku, price):
        """
        Marks product as ordered which gets added to cart with available sizes and stores other required data to the output file.
        """

        line = f'{url}, {added_sizes} , ordered, {sku}, {price}\n'
        with open('output.csv', 'a') as f:
            f.write(line)
        return True


if __name__ == '__main__':
    app = App()

    app.run('input.csv')

    app.bot.quit()
