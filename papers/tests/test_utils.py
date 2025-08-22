from unittest.mock import Mock

import pytest

from papers.models import Tag
from papers.utils import normalize_doi, travers_inferred


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("10.1000/182", "10.1000/182"),
        ("doi:10.1000/182", "10.1000/182"),
        ("DOI:10.1000/182", "10.1000/182"),
        ("https://doi.org/10.1000/182", "10.1000/182"),
        ("http://dx.doi.org/10.1000/182", "10.1000/182"),
        ("\thttps://doi.org/10.1000/182\n", "10.1000/182"),
        ("", ""),
        ("   DOI:10.1000/182   ", "10.1000/182"),
    ],
)
def test_normalize_doi_valid_cases(input_value, expected_output):
    assert normalize_doi(input_value) == expected_output


def test_normalize_doi_non_string_input():
    non_string_inputs = [123, None, {}, [], 3.14]
    for input_value in non_string_inputs:
        assert normalize_doi(input_value) == input_value


def test_travers_inferred():
    # Create mock tags
    tag1 = Mock(spec=Tag)
    tag2 = Mock(spec=Tag)
    tag3 = Mock(spec=Tag)
    tag4 = Mock(spec=Tag)

    # Set up names for better test readability
    tag1.name = "tag1"
    tag2.name = "tag2"
    tag3.name = "tag3"
    tag4.name = "tag4"

    # Set up the relationships:
    # tag1 -> tag2 -> tag3
    #     \-> tag4
    tag1.inferred_tags.all.return_value = [tag2, tag4]
    tag2.inferred_tags.all.return_value = [tag3]
    tag3.inferred_tags.all.return_value = []
    tag4.inferred_tags.all.return_value = []

    # Create a mock queryset that returns tag1
    mock_queryset = Mock()
    mock_queryset.all.return_value = [tag1]

    # Get all tags from the traversal
    result = list(travers_inferred(mock_queryset))

    # Check that all tags are present in the result
    assert len(result) == 4
    assert result[0] == tag1
    assert result[1] == tag2
    assert result[2] == tag3
    assert result[3] == tag4

    # Verify that .all() was called on each tag's inferred_tags
    mock_queryset.all.assert_called_once()
    tag1.inferred_tags.all.assert_called_once()
    tag2.inferred_tags.all.assert_called_once()
    tag3.inferred_tags.all.assert_called_once()
    tag4.inferred_tags.all.assert_called_once()


def test_travers_inferred_empty():
    # Test with an empty queryset
    mock_queryset = Mock()
    mock_queryset.all.return_value = []

    result = list(travers_inferred(mock_queryset))
    assert len(result) == 0
    mock_queryset.all.assert_called_once()


def test_travers_inferred_circular():
    # Create mock tags for testing circular references
    tag1 = Mock(spec=Tag)
    tag2 = Mock(spec=Tag)

    # Set up names for better test readability
    tag1.id = 1
    tag1.name = "tag1"
    tag2.id = 2
    tag2.name = "tag2"

    # Create circular reference: tag1 -> tag2 -> tag1
    tag1.inferred_tags.all.return_value = [tag2]
    tag2.inferred_tags.all.return_value = [tag1]

    mock_queryset = Mock()
    mock_queryset.all.return_value = [tag1]

    # The function should handle circular references without infinite recursion
    result = list(travers_inferred(mock_queryset))

    # We should get both tags exactly once, despite the circular reference
    assert len(result) == 2
    assert result[0] == tag1
    assert result[1] == tag2
