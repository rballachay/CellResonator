from src.utils import process_config

def test_process_config_2files():
    inlet="tests/data/test_folder"
    data_items = process_config(inlet,2)
    print(data_items)

