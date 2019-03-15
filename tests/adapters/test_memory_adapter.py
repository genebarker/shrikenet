from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.entities.storage_provider import StorageProvider


class TestGeneralProperties:

    def test_is_a_storage_provider(self):
        provider = MemoryAdapter()
        assert isinstance(provider, StorageProvider)
