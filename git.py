from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

base_url = "http://books.toscrape.com/index.html"

#data from a book

def scrape_book(book_url):

    book_info = requests.get(book_url).content
    book_soup = BeautifulSoup(book_info, "html.parser")
    book_table_data = book_soup.find_all(name="tr")
    book_data = {}
    for row in book_table_data:
        key = row.find(name="th").getText()
        value = row.find(name="td").getText()
        book_data[key] = value
    return book_data

#all books data in a page
        
def scrape_page(page_url):
    books_data = []
    page_content = requests.get(page_url).content
    page_soup = BeautifulSoup(page_content,"html.parser")
    page_books = page_soup.find_all(name="li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

    for book in page_books:
        book_url = book.findChild(name="a").get("href")
        book_url = urljoin(base_url, book_url)
        book_data = scrape_book(book_url)
        books_data.append(book_data)
    return books_data

#all page all books data

page_count = 1
data = []

while True:
  page_url = f"https://books.toscrape.com/catalogue/page-{page_count}.html"
  status = requests.get(page_url).status_code
  # break the loop if we exceed the total page count
  if status == 404:
    break

  page_data = scrape_page(page_url)
  data.extend(page_data) # do not use .append() since the function returns a list
  print(f"Page: {page_count} is SUCCESSFULLY scraped")

  page_count += 1

def fix(item):
  item['Price (excl. tax)'] = float(item['Price (excl. tax)'][1:])
  item['Price (incl. tax)'] = float(item['Price (incl. tax)'][1:])
  item['Tax'] = float(item['Tax'][1:])
  availability = item.pop('Availability')
  item['is_available'] = True if availability.split("(")[0].strip() == 'In stock' else False
  item['quantity_available'] = int(availability.split("(")[-1][:-1].split()[0])
  return item

formatted_data = [fix(item.copy()) for item in data]
