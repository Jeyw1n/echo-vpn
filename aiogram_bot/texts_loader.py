import yaml

# Функция для загрузки текстов из YAML-файла
def load_texts(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
texts = load_texts('texts.yaml')
