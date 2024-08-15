# class Car:
#     def __init__(self, brand, model, year, color, tramission_type, engine):
#         self.brand = brand
#         self.model = model
#         self.year = year
#         self.color = color
#         self.tramission_type = tramission_type
#         self.engine = engine
        
#     def speed(self):
#         return self.engine
    
# # my_car = Car("Porshe", "911", "2021", "red", "mannual", "v8")
# # print(my_car.speed())

# class MyCar(Car):
#     print("done")

# my_motor = MyCar("Porshe", "911", "2021", "red", "mannual", "v8")

import requests

url = 'https://dummyjson.com/products'
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    for x in data['products']:
        name = x['title']
        print(name)