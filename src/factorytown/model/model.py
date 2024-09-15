from .registry import RecordRegistry
    
class FactoryTownModel:
    records: RecordRegistry
    
    def __init__(self):
        self.records = RecordRegistry(self, "model")
