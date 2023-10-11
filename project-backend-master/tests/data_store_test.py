import pytest
from src.data_store import data_store
from src.other import clear_v1


# Test set function of data store
def test_invalid_store():
    with pytest.raises(TypeError):
        store = []
        data_store.set(store)
    clear_v1