import copy
from datetime import datetime, timezone
from operator import attrgetter

import pytest

from shrikenet.adapters.memory import Memory
from shrikenet.entities.rules import Rules


class TestMemory:

    @staticmethod
    def get_storage_provider():
        return Memory()

    @pytest.fixture
    def storage_provider(self):
        provider = self.get_storage_provider()
        provider.open()
        yield provider
        provider.close()
