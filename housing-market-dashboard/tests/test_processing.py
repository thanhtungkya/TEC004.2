from src.processing.transform_data import transform_records


def test_transform_records_handles_empty_input():
    result = transform_records([])
    assert result.empty
