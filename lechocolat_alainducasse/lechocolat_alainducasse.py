import re
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
import time
from lxml import html

def reload_product(token, id_product, id_customization, group_value, quantity):
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'controller': 'product',
        'token': token,
        'id_product': id_product,
        'id_customization': id_customization,
        'group[6]': group_value,
        'qty': quantity,
    }

    data = {
        'quickview': '0',
        'ajax': '1',
        'action': 'refresh',
        'quantity_wanted': quantity,
    }

    response = requests.post(
        'https://www.lechocolat-alainducasse.com/uk/index.php',
        params=params,
        headers=headers,
        data=data,
    )

    return response.text

def get_product_data(soup):
    form = soup.find('form', id='add-to-cart-or-refresh')

    if form:
        input_fields = form.find_all('input')

        params = {}
        for field in input_fields:
            name = field.get('name')
            value = field.get('value')
            if name and value:
                params[name] = value

        token = params.get('token', '')
        id_product = params.get('id_product', '')
        id_customization = params.get('id_customization', '')
        group_value = params.get('group[6]', '')
        quantity = params.get('qty', '')

        response_text = reload_product(token, id_product, id_customization, group_value, quantity)

        json_data = json.loads(response_text)
        product_details = json_data.get('product_details', '').strip()
        soup = BeautifulSoup(product_details, 'html.parser')
        product_details_div = soup.select('#product-details')

        if product_details_div:
            data_product_value = product_details_div[0].get('data-product')
            varaint_data = json.loads(data_product_value)

            price = varaint_data.get('price', '')
            description = varaint_data.get('meta_description', '')
            title = varaint_data.get('meta_title', '')
            link = varaint_data.get('link', '')

            features_dict = {}
            for features_data in varaint_data.get('features', []):
                features_dict[features_data.get('name', '')] = features_data.get('value', '')

            availability_message = varaint_data.get('availability_message', '')

            image_list = []
            for image_dict in varaint_data.get('images', [])[0].get('bySize', []):
                image_link = varaint_data.get('images', [])[0].get('bySize', {}).get(image_dict, {}).get('url', '')
                image_list.append(image_link)

            image_list = list(set(image_list))

            unit = varaint_data.get('attributes', {}).get('6', {}).get('name', '')
            price_float = float(re.search(r'\d+\.\d+', price).group())

            product_data = {
                'title': title,
                'selling_price': price_float,
                'unit': unit,
                'availability': availability_message,
                'description': description,
                'link': link,
                'features': features_dict,
                'images': image_list
            }
            return product_data

    return None

def get_pdp_variant_data(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.title.get_text()

        description_element = soup.select_one('#product_tab_informations p:nth-child(1)')
        description = description_element.get_text(strip=True) if description_element else None

        breadcrumb_elements = soup.select('.breadcrumb li span')
        breadcrumb_list = [element.get_text(strip=True) for element in breadcrumb_elements]

        selling_price_tag = soup.find("meta", property="product:price:amount")
        selling_price_value = selling_price_tag["content"] if selling_price_tag else None

        selling_price_currency_tag = soup.find("meta", property="product:price:currency")
        selling_price_currency_value = selling_price_currency_tag["content"] if selling_price_currency_tag else None



        weight_element = soup.find(class_="productCard__weight")

        if weight_element:
            weight_text = weight_element.get_text(strip=True)

            unit = weight_text.split()[-1]


        else:
            unit = None

        message_tag = soup.find('p', class_='mailAlert__message')

        if message_tag and "This product is unavailable" in message_tag.get_text():
            availability = "Out of Stock"
        else:
            availability = "In Stock"

        og_image_tag = soup.find("meta", property="og:image")
        og_image_url = og_image_tag["content"] if og_image_tag else None

        image_links = soup.select('.productImages__list li a')
        image_urls = [link['href'] for link in image_links]

        key_value_pairs = {}
        elements = soup.select('.wysiwyg-title-default')
        for element in elements:
            key = element.get_text(strip=True)
            next_p = element.find_next_sibling('p')
            value = next_p.get_text(strip=True) if next_p else None
            key_value_pairs[key] = value


        temp_dict = {
            "title": title,
            "url": url,
            "description": description,
            "breadcrumb": breadcrumb_list,
            "images": image_urls,
            "features": key_value_pairs,
            "image": og_image_url,
            "original_price": selling_price_value,
            "selling_price": selling_price_value,
            "availability": availability,
            "unit": unit,
            "category": category,
        }
        return temp_dict

    else:
        print(url)
        return None


def scrape_product_info(url, category):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.title.get_text()

        description_element = soup.select_one('#product_tab_informations p:nth-child(1)')
        description = description_element.get_text(strip=True) if description_element else None

        breadcrumb_elements = soup.select('.breadcrumb li span')
        breadcrumb_list = [element.get_text(strip=True) for element in breadcrumb_elements]

        image_links = soup.select('.productImages__list li a')
        image_urls = [link['href'] for link in image_links]

        key_value_pairs = {}
        elements = soup.select('.wysiwyg-title-default')
        for element in elements:
            key = element.get_text(strip=True)
            next_p = element.find_next_sibling('p')
            value = next_p.get_text(strip=True) if next_p else None
            key_value_pairs[key] = value

        og_image_tag = soup.find("meta", property="og:image")
        og_image_url = og_image_tag["content"] if og_image_tag else None

        selling_price_tag = soup.find("meta", property="product:price:amount")
        selling_price_value = selling_price_tag["content"] if selling_price_tag else None

        selling_price_currency_tag = soup.find("meta", property="product:price:currency")
        selling_price_currency_value = selling_price_currency_tag[
            "content"] if selling_price_currency_tag else None

        weight_element = soup.find(class_="productCard__weight")
        if weight_element:
            weight_text = weight_element.get_text(strip=True)
            unit = weight_text.split()[-1]
        else:
            unit = ''


        variant_products = soup.select('.linkedProducts__list li a')
        varinat_list = []
        if variant_products:
            for product in variant_products:
                link = product['href']
                variant_response = get_pdp_variant_data(link)
                varinat_list.append(variant_response)
        try:
            varaint_json = get_product_data(soup)
            varinat_list.append(varaint_json)
        except:
            pass


        message_tag = soup.find('p', class_='mailAlert__message')
        if message_tag and "This product is unavailable" in message_tag.get_text():
            availability = "Out of Stock"
        else:
            availability = "In Stock"


    else:
        print("Failed to retrieve the page. Status code:", response.status_code)
        print(url)
        return None

    temp_dict = {
        "title": title,
        "url": url,
        "description": description,
        "breadcrumb":breadcrumb_list,
        "images": image_urls,
        "features": key_value_pairs,
        "image": og_image_url,
        "original_price": selling_price_value,
        "selling_price": selling_price_value,
        "availability": availability,
        "variants":varinat_list,
        "unit": unit,
        "category": category,
    }
    return temp_dict


def get_pdp_urls(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        product_links = soup.select("#js-product-list .productMiniature a")
        urls = [link['href'] for link in product_links]
        return urls
    else:
        return []
def get_category_urls(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        menu_items = soup.select('.siteMenuItem')
        data = {}
        for item in menu_items:
            try:
                link = item.select_one('a')['href']
                content = item.select_one('a span').text.strip()
                data[content] = link
            except Exception as e:
                pass
        return data



if __name__ == "__main__":
    FINAL_LIST_DATA = []
    url = "https://www.lechocolat-alainducasse.com/uk/"
    category_dict = get_category_urls(url)
    pdp_dict = {}
    for category, category_url in category_dict.items():
        print(category)
        pdp_links = get_pdp_urls(category_url)
        for pdp_url in pdp_links:
            print(pdp_url)
            pdp_data = scrape_product_info(pdp_url, category)
            FINAL_LIST_DATA.append(pdp_data)

    try:

        with open(r'C:\Users\ajinkya.ghodvinde\Desktop\adaptmind\scrape_data\output\lechocolat.json', 'w') as json_file:
            json.dump(FINAL_LIST_DATA, json_file)
    except:
        pass