from ..internal_types import *

from .registry import Record, RecordRef, RecordId

def get_record_name(record: RecordId) -> str:
    """Get the name of a record, given the name, the record, or a reference to the record."""
    
    if isinstance(record, str):
        record_name = record
    elif isinstance(record, RecordRef):
        record_name = record.record_name
    else:
        assert isinstance(record, Record)
        record_name = record.record_name
    return record_name
