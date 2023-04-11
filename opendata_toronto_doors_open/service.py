from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

import requests
from sqlite_utils import Database
from sqlite_utils.db import Table


def get_doorsoepn_dataset_url(package_id: str) -> str:
    """
    Get the DoorsOpen dataset URL from the OpenData Toronto pacakge ID.
    """
    response = requests.get(
        url="https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show",
        params={"id": package_id},
        timeout=(5, 30),
    )
    response.raise_for_status()
    data = response.json()

    result = data["result"]
    if "json" not in result["formats"].lower():
        raise ValueError("OpenData package does not have a JSON resource.")

    resources = result["resources"]
    resource_json_format = next(
        filter(lambda r: "json" == r["format"].lower(), resources)
    )

    return resource_json_format["url"]


def get_doors_open_dataset(url: str) -> List[Dict[str, Any]]:
    """
    Get the individual DoorsOpen dataset.
    """
    response = requests.get(url, timeout=(5, 30))
    response.raise_for_status()
    return response.json()


def transform_2019_multi_line_string(value: List[str]) -> Optional[str]:
    """
    Transform a multiple line string from DoorsOpen Toronto 2019 dataset.
    """
    if not value:
        return None

    return "\n".join(value)


def transform_2019_address(address: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform an address dictionary from DoorsOpen Toronto 2019 dataset.
    """
    return {
        "street_address": address["dot_buildingAddress"],
        "postal_code": address["dot_postal"],
        "latitude": float(address["dot_Latitude"]),
        "longitude": float(address["dot_Longitude"]),
    }


def transform_2019_links(links: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform the links dictionary from DoorsOpen Toronto 2019 dataset.
    """
    data = {}

    for url_type, url in links.items():
        if url_type == "dot_youTube":
            key = "youtube_url"
        elif url_type == "dot_flickr":
            key = "flickr_url"
        elif url_type == "dot_url":
            key = "url"
        elif url_type == "dot_twitter":
            key = "twitter_url"
        elif url_type == "dot_instagram":
            key = "instagram_url"
        elif url_type == "dot_faceBook":
            key = "facebook_url"
        else:
            continue

        data[key] = url if url != "http://" else None

    return data


def transform_2019_architecture(architecture: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform the year constructed from DoorsOpen Toronto 2019 dataset.
    """
    data = {}

    if architecture["dot_year"]:
        data["year_constructed"] = architecture["dot_year"]

    return data


def transform_2016_year_constructed(value: str) -> Optional[int]:
    """
    Transform the year constructed from DoorsOpen Toronto 2016 dataset.
    """
    if value == "Unknown":
        return None

    return int(value)


@dataclass
class Building:
    """
    A dataclass of the building that is taken part in DoorsOpen Toronto.
    """

    # Year the property participated in DoorsOpen Toronto.
    year: int

    id: int
    name: str
    description: str
    visitor_experience: str

    # The building address
    street_address: Optional[str] = None
    locality: str = "Toronto"
    country_name: str = "Canada"
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Architecture
    year_constructed: Optional[int] = None

    # URLs
    url: Optional[str] = None
    facebook_url: Optional[str] = None
    flickr_url: Optional[str] = None
    instagram_url: Optional[str] = None
    twitter_url: Optional[str] = None
    youtube_url: Optional[str] = None

    @classmethod
    def transform_data(cls, year: int, data: Dict[str, Any]):
        """
        Transform data from the DoorsOpen dataset.
        """
        defaults = {}

        if year in [2016, 2017, 2018]:
            defaults["id"] = data["_id"]
            defaults["name"] = data["Building Name"]
            defaults["description"] = data["Building Description"]
            defaults["visitor_experience"] = data["Visitor Experience"]
            defaults["street_address"] = data["Building Address"]
            defaults["postal_code"] = data["Postal Code"]
            defaults["latitude"] = data["Latitude"]
            defaults["longitude"] = data["Longitude"]
            defaults["url"] = data["Website"] or None
            defaults["facebook_url"] = data["Facebook"] or None
            defaults["flickr_url"] = data["Flickr"] or None
            defaults["instagram_url"] = data["Instagram"] or None
            defaults["twitter_url"] = data["Twitter"] or None
            defaults["youtube_url"] = data["YouTube"] or None
        elif year == 2019:
            defaults["id"] = data["dot_documentID"]
            defaults["name"] = data["dot_buildingName"]
            defaults["description"] = transform_2019_multi_line_string(
                data["dot_FullDescription"]
            )
            defaults["visitor_experience"] = transform_2019_multi_line_string(
                data["dot_VisitorExperience"]
            )
            defaults.update(transform_2019_address(data["dot_Address"]))
            defaults.update(transform_2019_links(data["dot_Links"]))
            defaults.update(
                transform_2019_architecture(data["dot_Architecture"])
            )
        else:
            raise NotImplementedError(
                f"We do not know about datasets for the year {year}."
            )

        return cls(year=year, **defaults)


def open_database(db_path: str) -> Database:
    """
    Open the DoorsOpen Database.
    """
    return Database(db_path)


def build_tables(db: Database):
    """
    Build the SQLite database structure.
    """
    buildings_table: Table = db.table("buildings")  # type: ignore

    if buildings_table.exists() is False:
        buildings_table.create(
            columns={
                "id": str,
                "year": int,
                "name": str,
                "description": str,
                "visitor_experience": str,
            },
            pk=("id", "year"),
        )
        buildings_table.enable_fts(
            ["name", "description", "visitor_experience"], create_triggers=True
        )


def save_doorsopen_dataset(buildings: List[Building], buildings_table: Table):
    """
    Save DoorsOpen Toronto dataset.
    """
    buildings_table.upsert_all(
        records=[asdict(building) for building in buildings],
        pk=("id", "year"),
    )
