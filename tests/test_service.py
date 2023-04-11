import pytest

from opendata_toronto_doors_open import service

from . import fixtures


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ([], None),
        (["I am a single line string."], "I am a single line string."),
        (
            ["I am a multiple line string.", "Look at me!"],
            "I am a multiple line string.\nLook at me!",
        ),
    ),
)
def test_transform_2019_multi_line_string(value, expected_result):
    result = service.transform_2019_multi_line_string(value)
    assert result == expected_result


@pytest.mark.parametrize(
    "address, expected_result",
    (
        (
            fixtures.BUILDING_ADDRESS_2019,
            {
                "street_address": fixtures.BUILDING_ADDRESS_2019[
                    "dot_buildingAddress"
                ],
                "postal_code": fixtures.BUILDING_ADDRESS_2019["dot_postal"],
                "latitude": 43.6477554326,
                "longitude": -79.3947484327,
            },
        ),
    ),
)
def test_transform_2019_address(address, expected_result):
    result = service.transform_2019_address(address)
    assert result == expected_result


@pytest.mark.parametrize(
    "links, expected_result",
    (
        (
            fixtures.BUILDING_LINKS_2019,
            {
                "url": fixtures.BUILDING_LINKS_2019["dot_url"],
                "facebook_url": fixtures.BUILDING_LINKS_2019["dot_faceBook"],
                "flickr_url": fixtures.BUILDING_LINKS_2019["dot_flickr"],
                "instagram_url": fixtures.BUILDING_LINKS_2019["dot_instagram"],
                "twitter_url": fixtures.BUILDING_LINKS_2019["dot_twitter"],
                "youtube_url": None,
            },
        ),
    ),
)
def test_transform_2019_links(links, expected_result):
    result = service.transform_2019_links(links)
    assert result == expected_result


@pytest.mark.parametrize(
    "architecture, expected_result",
    (
        (
            fixtures.BUILDING_ARCHITECTURE_2019,
            {
                "year_constructed": fixtures.BUILDING_ARCHITECTURE_2019[
                    "dot_year"
                ]
            },
        ),
    ),
)
def test_transform_2019_architecture(architecture, expected_result):
    result = service.transform_2019_architecture(architecture)
    assert result == expected_result


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ("Unknown", None),
        (1921, 1921),
    ),
)
def test_transform_2016_year_constructed(value, expected_result):
    result = service.transform_2016_year_constructed(value)
    assert result == expected_result


@pytest.mark.parametrize(
    "year, data",
    (
        (2016, fixtures.BUILDING_2016),
        (2017, fixtures.BUILDING_2017),
        (2018, fixtures.BUILDING_2018),
        (2019, fixtures.BUILDING_2019),
    ),
)
def test_building__transform_data(year, data):
    service.Building.transform_data(year, data)
