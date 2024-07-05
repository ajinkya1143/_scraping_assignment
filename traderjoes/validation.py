import json


class Validation:
    def __init__(self, data):
        self.data = data
        self.errors = []

    def validate_pdp_data(self):
        for pdp_json in pdps_json:

            mandatory_fields = ['title', 'images', 'product_id','retail_price']

            if pdp_json is None:
                continue
            self.validate_price(pdp_json)

            self.validate_mandatory_attributes(pdp_json,mandatory_fields)


        return self.errors




    def validate_price(self,product_data):
        selling_price = product_data.get('final_price')
        original_price = product_data.get('retail_price')
        if selling_price is not None and original_price is not None:
            if not selling_price <= original_price:
                self.errors.append(f"Sale price {selling_price} is greater than original price {original_price} for product {product_data['title']}")

    def validate_mandatory_attributes(self,product_data,mandatory_fields):
        for key in mandatory_fields:
            if not product_data.get(key):
                self.errors.append(f"Missing mandatory field: {key} for product :{product_data['title']}")




if __name__ == "__main__":
    with open(r'C:\Users\ajinkya.ghodvinde\Desktop\adaptmind\scrape_data\output\traderjoes.json',
              "r") as f:
        pdps_json = json.load(f)


        validator = Validation(pdps_json)
        errors = validator.validate_pdp_data()

        if errors:
            print("Validation errors:")
            for error in errors:
                print(error)
        else:
            print("All products are valid.")
