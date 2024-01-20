from functools import reduce
import json
import re # regular expression
import os
from typing import List, TypedDict
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def initialize_driver() -> webdriver.Chrome:
  driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
  return driver

class KreamUrls(TypedDict):
  url: str
  category: str
  gender: str

class DataMapping:
  Category = {
    '64': '상의',
    '65': '하의',
    '34': '신발',
    '7': '패션잡화'
  }

  Gender = {
    'men': '남성',
    'women': '여성'
  }

  @staticmethod
  def get_category(category_key: str) -> str:
    return DataMapping.Category.get(category_key, '정의되지 않은 카테고리')
  
  @staticmethod
  def get_gender(gender_key: str) -> str:
    return DataMapping.Gender.get(gender_key, '남성/여성')

def create_data_json_name(target: KreamUrls):
  current_directory = os.getcwd()
  return f"{current_directory}/kream_data_{target['category']}_{target['gender']}.json"

def sanitize_price_text(price: str) -> int:
  return int(re.sub(r'[^0-9]', '', price))

def get_row_from_product(target: KreamUrls, product: Tag):
  url = product.find('a')['href']
  brand = product.select_one('a > .product_info_area > .title > .brand').text
  product_name = product.select_one('a > .product_info_area > .title > .product_info_product_name > .translated_name').text
  price = product.select_one('a > .price_area > .amount').text
  row = {
    'category': DataMapping.get_category(target['category']),
    'brand': brand,
    'gender': DataMapping.get_gender(target['gender']),
    'product': product_name,
    'price': sanitize_price_text(price),
    'url': url
  }
  return row

def save_rows_to_json(rows: List[dict], target: KreamUrls):
  print("saving file into " + create_data_json_name(target))
  with open(create_data_json_name(target), 'w', encoding="UTF-8") as file:
    json.dump(rows, file, ensure_ascii=False, indent=2)

def get_kream_rows_by_url(driver: webdriver.Chrome, target: KreamUrls):
  print(target['url'])
  driver.get(target['url'])
  soup = BeautifulSoup(driver.page_source, 'html.parser')
  products = soup.select('div.search_result_list > div.search_result_item.product')
  rows = list(map(lambda product: get_row_from_product(target, product), products))
  return rows

def process_kream_urls(driver: webdriver.Chrome, url: KreamUrls):
  rows = get_kream_rows_by_url(driver, url)
  save_rows_to_json(rows, url)

def process_kream_rows(driver: webdriver.Chrome, urls: List[KreamUrls]):
  list(map(lambda url: process_kream_urls(driver, url), urls))

def read_json_file_and_return(filename: str):
  with open(filename, 'r', encoding="UTF-8") as file:
    return json.load(file)

def merge_json_files_into_one():
  current_directory = os.getcwd()
  json_files = [pos_json for pos_json in os.listdir(current_directory) if pos_json.endswith('.json')]
  merged_json = reduce(lambda acc, filename: acc + read_json_file_and_return(filename), json_files, [])
  with open('kream_data.json', 'w', encoding="UTF-8") as file:
    json.dump(merged_json, file, ensure_ascii=False, indent=2)
    
def startup():
  print('start')
  driver = initialize_driver()
  process_kream_rows(driver, [
    { 'url': 'https://kream.co.kr/search?gender=&shop_category_id=64', 'category': '64', 'gender': '0' },
    { 'url': 'https://kream.co.kr/search?gender=men&shop_category_id=64', 'category': '64', 'gender': 'men' },
    { 'url': 'https://kream.co.kr/search?gender=women&shop_category_id=64', 'category': '64', 'gender': 'women' },
    { 'url': 'https://kream.co.kr/search?gender=&shop_category_id=65', 'category': '65', 'gender': '0' },
    { 'url': 'https://kream.co.kr/search?gender=men&shop_category_id=65', 'category': '65', 'gender': 'men' },
    { 'url': 'https://kream.co.kr/search?gender=women&shop_category_id=65', 'category': '65', 'gender': 'women' },
    { 'url': 'https://kream.co.kr/search?gender=&shop_category_id=34', 'category': '34', 'gender': '0' },
    { 'url': 'https://kream.co.kr/search?gender=men&shop_category_id=34', 'category': '34', 'gender': 'men' },
    { 'url': 'https://kream.co.kr/search?gender=women&shop_category_id=34', 'category': '34', 'gender': 'women' },
    { 'url': 'https://kream.co.kr/search?gender=&shop_category_id=7', 'category': '7', 'gender': '0' },
    { 'url': 'https://kream.co.kr/search?gender=men&shop_category_id=7', 'category': '7', 'gender': 'men' },
    { 'url': 'https://kream.co.kr/search?gender=women&shop_category_id=7', 'category': '7', 'gender': 'women' },
  ])
  driver.quit()
  merge_json_files_into_one()
  print('end')

if __name__ == '__main__':
  startup()
