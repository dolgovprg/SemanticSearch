from elasticsearch import Elasticsearch
from fastapi import FastAPI
import xml.etree.ElementTree as ET
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer

# Загрузка и считывание данных из XML файлов
def load_data_from_xml(catalog_xml, descriptions_xml):
    catalog_tree = ET.parse(catalog_xml)
    catalog_root = catalog_tree.getroot()

    descriptions_tree = ET.parse(descriptions_xml)
    descriptions_root = descriptions_tree.getroot()

    return catalog_root, descriptions_root

# Сопоставление описаний с товарами используя SKU
def match_descriptions_with_products(catalog, descriptions):
    data_dict = {}

    for description in descriptions:
        sku = description.get('sku')
        description_text = description.text

        if sku in data_dict:
            data_dict[sku]['description'] = description_text
        else:
            data_dict[sku] = {'description': description_text}

    for product in catalog:
        sku = product.get('sku')

        if sku in data_dict:
            data_dict[sku]['product_name'] = product.find('name').text
            data_dict[sku]['price'] = float(product.find('price').text)

    return data_dict

# Установка и настройка библиотеки ElasticSearch
def setup_elasticsearch():
    es = Elasticsearch(['localhost'])
    index_name = 'products'
    es.indices.create(index=index_name, ignore=400)
    return es, index_name

# Сохранение данных в ElasticSearch
def save_data_to_elasticsearch(es, index_name, data_dict):
    for sku, data in data_dict.items():
        es.index(index=index_name, id=sku, body=data)

# Создание векторов записей
def create_vectors(data_dict):
    descriptions = [data['description'] for data in data_dict.values()]
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(descriptions).toarray()
    return vectors

# Сохранение векторов в ElasticSearch
def save_vectors_to_elasticsearch(es, index_name, data_dict, vectors):
    for i, (sku, data) in enumerate(data_dict.items()):
        data['vector'] = vectors[i].tolist()
        es.index(index=index_name, id=sku, body=data)


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}



# Основная функция для выполнения всех шагов
""" def main():
    # Загрузка данных
    catalog, descriptions = load_data_from_xml('catalog.xml', 'descriptions.xml')

    # Сопоставление описаний с товарами
    data_dict = match_descriptions_with_products(catalog, descriptions)

    # Установка и настройка ElasticSearch
    es, index_name = setup_elasticsearch()

    # Сохранение данных в ElasticSearch
    save_data_to_elasticsearch(es, index_name, data_dict)

    # Создание векторов записей
    vectors = create_vectors(data_dict)

    # Сохранение векторов в ElasticSearch
    save_vectors_to_elasticsearch(es, index_name, data_dict, vectors)

# Вызов основной функции
if __name__ == "__main__":
    main()


 """