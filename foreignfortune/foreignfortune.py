import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def get_product_data(pdp_link, category_name,final_list_data):
    pdp_response = requests.get(pdp_link)
    if pdp_response.status_code ==200:
        pdp_soup = BeautifulSoup(pdp_response.text,'lxml')
        pdp_data = pdp_soup.find('script',{'id':'ProductJson-product-template'})
        pdp_data = json.loads(pdp_data.text)

        product_id = pdp_data.get('id','')
        handle = pdp_data.get('handle','')
        title = pdp_data.get('title')
        mrp = pdp_data.get('price_max', 0) / 100
        selling_price = pdp_data.get('price', 0) / 100
        brand = pdp_data.get('vendor','')
        description = pdp_data.get('description','')
        options = pdp_data.get('options',[])
        image = "https:" + pdp_data.get('featured_image', '')
        images_pre = pdp_data.get('images', [])
        images = ['https:' + img for img in images_pre]

        match = re.search(r'productVariants":\s*(\[{.*?}\])', pdp_response.text)
        if match:
            variants_data = match.group(1)
            product_variants = json.loads(variants_data)
            variant_list = []
            for variant_value in product_variants:
                variant_data = {
                    "id": variant_value['id'],
                    "price": variant_value['price']['amount'],
                    "variant_name": variant_value['title'],
                    "image": "https:" + variant_value['image']['src'],
                }
                for product_variant in pdp_data['variants']:
                    if int(product_variant['id']) == int(variant_value['id']):
                        for rank, option_value in enumerate(options):
                            option_value_index = product_variant['options'][rank]
                            variant_data[str(option_value)] = option_value_index
                variant_list.append(variant_data)
        else:
            variant_list = []

        temp_dict = {
            "brand": brand,
            "description": description,
            "image": image,
            "images": images,
            "variants": variant_list,
            "original_price": mrp,
            "selling_price": selling_price,
            "title": title,
            "url": "https://foreignfortune.com/products/" + handle,
            "product_id": handle,
            "category": category_name,
        }
        final_list_data.append(temp_dict)


if __name__ == "__main__":
    FINAL_LIST_DATA = []
    df = pd.DataFrame()
    response = requests.get('https://foreignfortune.com/')
    soup = BeautifulSoup(response.text,'lxml')
    categories_list = soup.find(id = 'SiteNav').find_all('li')

    for category in categories_list:

        base_link = 'https://foreignfortune.com'
        raw_category_link = category.find(attrs='site-nav__link site-nav__link--main')['href']
        category_link = base_link + raw_category_link
        category_name= raw_category_link.split('/')[-1]
        print(category_name)
        page_c = 1
        while True:
            category_link = 'https://foreignfortune.com/collections/{}?page={}'.format(category_name,page_c)
            category_response = requests.get(category_link)
            category_soup = BeautifulSoup(category_response.text,'lxml')
            collection_list = category_soup.find(attrs='grid grid--uniform grid--view-items').find_all('a')

            if not category_soup.find(attrs='grid-view-item product-card'):
                break

            for product in collection_list:
                pdp_link = base_link + product['href']
                get_product_data(pdp_link, category_name,FINAL_LIST_DATA)


            page_c+=1
    with open(r'../output/foreignfortune_data.json', 'w') as outfile:
        json.dump(FINAL_LIST_DATA, outfile)