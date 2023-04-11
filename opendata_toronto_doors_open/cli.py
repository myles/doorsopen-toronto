import click
from sqlite_utils.db import Table

from . import service


@click.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
def cli(db_path):
    """
    Save data from Toronto's OpenDoors into a SQLite database.
    """
    db = service.open_database(db_path)
    buildings_table: Table = db.table("buildings")  # type: ignore

    years_to_package_id = [
        (2019, "doors-open-toronto-2019"),
        (2018, "doors-open-toronto-2018"),
        (2017, "doors-open-toronto-2017"),
        (2016, "doors-open-toronto-2016"),
    ]

    for year, package_id in years_to_package_id:
        dataset_url = service.get_doorsoepn_dataset_url(package_id)
        dataset = service.get_doors_open_dataset(dataset_url)

        buildings = [
            service.Building.transform_data(year=year, data=data)
            for data in dataset
        ]

        service.save_doorsopen_dataset(
            buildings=buildings, buildings_table=buildings_table
        )
