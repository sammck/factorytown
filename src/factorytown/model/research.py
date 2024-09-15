from ..internal_types import *
from .registry import Record, RecordRef, RecordId

class Research(Record):
    @classmethod
    def get_record_name(cls, record: RecordId) -> str:
        """Get the name of a research record, given the research name, the record, or a reference to the record.
        
        Research is a special case because all research record names are prefixed with "[Research]" to
        disambiguate with GameObjects that may have the same name as the research.
        """
        if isinstance(record, str):
            record_name = record
            if not record_name.startswith("[Research]"):
                record_name = f"[Research]{record_name}"
        elif isinstance(record, RecordRef):
            record_name = record.record_name
        else:
            assert isinstance(record, Record)
            record_name = record.record_name
        return record_name
    def __str__(self):
        return f"{self.__class__.__name__}({self.common_str()})"
