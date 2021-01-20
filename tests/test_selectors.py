import pytest
from spatula import CSS, XPath, SimilarLink, SelectorError, Selector


class DummySelector(Selector):
    """ make a selector where we can control how many results it has """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_items(self, num_matches):
        return list(range(num_matches))


def test_num_items():
    ds = DummySelector(num_items=3)

    # correct number
    assert ds.match(3) == [0, 1, 2]

    # incorrect number
    with pytest.raises(SelectorError):
        ds.match(0)

    # override expected number
    assert ds.match(2, num_items=2) == [0, 1]

    # override and error
    with pytest.raises(SelectorError):
        assert ds.match(3, num_items=2)


def test_min_items():
    ds = DummySelector(min_items=3)

    # correct number
    assert ds.match(3) == [0, 1, 2]

    # incorrect number
    with pytest.raises(SelectorError):
        ds.match(2)

    # override expected number
    assert ds.match(2, min_items=2) == [0, 1]

    # override and error
    with pytest.raises(SelectorError):
        assert ds.match(3, min_items=4)


def test_max_items():
    ds = DummySelector(max_items=3)

    # correct number
    assert ds.match(3) == [0, 1, 2]

    # incorrect number
    with pytest.raises(SelectorError):
        ds.match(4)

    # override expected number
    assert ds.match(4, max_items=4) == [0, 1, 2, 3]

    # override and error
    with pytest.raises(SelectorError):
        assert ds.match(5, max_items=4)
