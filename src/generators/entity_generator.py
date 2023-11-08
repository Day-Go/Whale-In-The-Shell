from abc import ABC, abstractmethod

class EntityGenerator(ABC):

    @abstractmethod
    def create(self):
        """Create a new entity (agent or organization)."""
        pass

    @abstractmethod
    def update(self, entity):
        """Update an existing entity."""
        pass

    @abstractmethod
    def deactivate(self, entity):
        """Deactivate an entity."""
        pass
