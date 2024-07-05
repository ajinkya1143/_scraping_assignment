import re
import requests
import pandas as pd
import json
import concurrent.futures

from bs4 import BeautifulSoup
import time

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

def stock_status(count):
    if int(count) > 0:
        availability_status = 'InStock'
    else:
        availability_status = 'OutOfStock'

    return availability_status


def get_nutrition_data(nutrition_list):
    if nutrition_list is not None:
        extracted_data = {
            'serving_size': None,
            'calories_per_serving': None,
            'servings_per_container': None,
            'details': []
        }

        for entry in nutrition_list:
            serving_size = entry['serving_size']
            calories_per_serving = entry['calories_per_serving']
            servings_per_container = entry['servings_per_container']

            for detail in entry['details']:
                extracted_detail = {
                    'nutritional_item': detail.get('nutritional_item'),
                    'amount': detail.get('amount'),
                    'percent_dv': detail.get('percent_dv')
                }
                extracted_data['details'].append(extracted_detail)

            extracted_data['serving_size'] = serving_size
            extracted_data['calories_per_serving'] = calories_per_serving
            extracted_data['servings_per_container'] = servings_per_container

        return extracted_data
    else:
        None


def get_all_skus():
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    sku_list = []

    for page_number in range(1, 3):
        json_data = {
            'operationName': 'SearchProducts',
            'variables': {
                'storeCode': 'TJ',
                'availability': '1',
                'published': '1',
                'categoryId': 8,
                'currentPage': page_number,
                'pageSize': 1000,
            },
            'query': 'query SearchProducts($categoryId: String, $currentPage: Int, $pageSize: Int, $storeCode: String = "TJ", $availability: String = "1", $published: String = "1") {\n  products(\n    filter: {store_code: {eq: $storeCode}, published: {eq: $published}, availability: {match: $availability}, category_id: {eq: $categoryId}}\n    currentPage: $currentPage\n    pageSize: $pageSize\n  ) {\n    items {\n      sku\n      item_title\n      category_hierarchy {\n        id\n        name\n        __typename\n      }\n      primary_image\n      primary_image_meta {\n        url\n        metadata\n        __typename\n      }\n      sales_size\n      sales_uom_description\n      price_range {\n        minimum_price {\n          final_price {\n            currency\n            value\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      retail_price\n      fun_tags\n      item_characteristics\n      __typename\n    }\n    total_count\n    pageInfo: page_info {\n      currentPage: current_page\n      totalPages: total_pages\n      __typename\n    }\n    aggregations {\n      attribute_code\n      label\n      count\n      options {\n        label\n        value\n        count\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
        }

        try:
            response = requests.post('https://www.traderjoes.com/api/graphql', headers=headers, json=json_data,timeout=30)
        except:
            continue
        response_json = response.json()

        for product in response_json['data']['products']['items']:
            sku_list.append(product['sku'])
    return sku_list



def get_pdp_data(product_id):
    json_data = {
        'operationName': 'SearchProduct',
        'variables': {
            'storeCode': 'TJ',
            'published': '1',
            'sku': '{}'.format(product_id),
        },
        'query': 'query SearchProduct($sku: String, $storeCode: String = "TJ", $published: String = "1") {\n  products(\n    filter: {sku: {eq: $sku}, store_code: {eq: $storeCode}, published: {eq: $published}}\n  ) {\n    items {\n      category_hierarchy {\n        id\n        url_key\n        description\n        name\n        position\n        level\n        created_at\n        updated_at\n        product_count\n        __typename\n      }\n      item_story_marketing\n      product_label\n      fun_tags\n      primary_image\n      primary_image_meta {\n        url\n        metadata\n        __typename\n      }\n      other_images\n      other_images_meta {\n        url\n        metadata\n        __typename\n      }\n      context_image\n      context_image_meta {\n        url\n        metadata\n        __typename\n      }\n      published\n      sku\n      url_key\n      name\n      item_description\n      item_title\n      item_characteristics\n      item_story_qil\n      use_and_demo\n      sales_size\n      sales_uom_code\n      sales_uom_description\n      country_of_origin\n      availability\n      new_product\n      promotion\n      price_range {\n        minimum_price {\n          final_price {\n            currency\n            value\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      retail_price\n      nutrition {\n        display_sequence\n        panel_id\n        panel_title\n        serving_size\n        calories_per_serving\n        servings_per_container\n        details {\n          display_seq\n          nutritional_item\n          amount\n          percent_dv\n          __typename\n        }\n        __typename\n      }\n      ingredients {\n        display_sequence\n        ingredient\n        __typename\n      }\n      allergens {\n        display_sequence\n        ingredient\n        __typename\n      }\n      created_at\n      first_published_date\n      last_published_date\n      updated_at\n      related_products {\n        sku\n        item_title\n        primary_image\n        primary_image_meta {\n          url\n          metadata\n          __typename\n        }\n        price_range {\n          minimum_price {\n            final_price {\n              currency\n              value\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        retail_price\n        sales_size\n        sales_uom_description\n        category_hierarchy {\n          id\n          name\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    total_count\n    page_info {\n      current_page\n      page_size\n      total_pages\n      __typename\n    }\n    __typename\n  }\n}\n',
    }

    try:
        pdp_response = requests.post('https://www.traderjoes.com/api/graphql', cookies=None, headers=headers,
                                     json=json_data,timeout=30)
    except:
        return None

    if pdp_response.status_code == 200:
        try:
            pdp_json_data = json.loads(pdp_response.text)
            for data in pdp_json_data['data']['products']['items']:
                temp_dict = {
                    'brand': "Traders Joe's",
                    'title': data['item_title'],
                    'description': BeautifulSoup(data['item_story_marketing'], 'html.parser').text,
                    'image': "https://www.traderjoes.com" + data.get('primary_image'),
                    'images': [None if data.get('context_image') is None or data.get(
                        'primary_image') is None else 'https://www.traderjoes.com' + data.get('context_image'),
                               "https://www.traderjoes.com" + data.get('primary_image')],
                    'retail_price': data['retail_price'],
                    'final_price': str(data['price_range']['minimum_price']['final_price'].get('value', [])),
                    'url': 'https://www.traderjoes.com/home/products/pdp/' + str(product_id),
                    'product_id': int(data['sku']),
                    'category': data['category_hierarchy'][1].get('name', None),
                    'sales_size': str(data.get('sales_size')) + " " + data['sales_uom_description'],
                    'availability': stock_status(data['availability']),
                    'Buzzwords': [words for words in data.get('fun_tags', [])],
                    'nutrition': get_nutrition_data(data['nutrition']),
                    'ingredients': None if data.get('ingredients') is None else [detail["ingredient"] for detail in
                                                                                 data['ingredients']],
                    'country_of_origin': data['country_of_origin']
                }
                return temp_dict

        except Exception as e:
            print(e)

if __name__ == "__main__":
    FINAL_LIST_DATA = []
    sku_list = get_all_skus()

    for ind, sku in enumerate(sku_list):
        try:
            pdp_json = get_pdp_data(sku)
            print(ind)
        except:
            continue
        FINAL_LIST_DATA.append(pdp_json)

    with open(r'../output/traderjoes.json', 'w') as outfile:
        json.dump(FINAL_LIST_DATA, outfile)