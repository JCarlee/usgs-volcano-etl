"""
Volcano data update script that fetches the latest USGS volcano data and updates a GIS feature layer.

This script downloads current volcano data from the USGS API in GeoJSON format and updates
a hosted feature layer in ArcGIS Portal. Authentication is handled via keyring credentials.

Dependencies:
    - arcgis
    - keyring
    - requests

Configuration:
    Requires config.ini file with USGS and PORTAL sections containing connection details.
"""
import configparser
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import keyring as kr
import requests
from arcgis.features import FeatureLayerCollection
from arcgis.gis import GIS
from requests.exceptions import ChunkedEncodingError, RequestException

# Use pathlib for path handling
SCRIPT_DIR = Path(__file__).parent
WORKING_DIR = SCRIPT_DIR.parent

# Setup logging
LOG_PATH = WORKING_DIR / "04 Scripts" / "logs" / "volcano.log"
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

# Load config
config = configparser.ConfigParser()
CONFIG_PATH = WORKING_DIR / "04 Scripts" / "config" / "config.ini"
config.read(CONFIG_PATH)


def sign_in_to_gis(portal_url: str, username: str, password: str) -> GIS:
    """Sign into an online GIS portal and return the GIS object.

    Args:
        portal_url: The URL of the GIS portal.
        username: The username for the GIS portal.
        password: The password for the GIS portal.

    Returns:
        An authenticated GIS object.
    """
    print(f'Signing into {portal_url}...')
    gis = GIS(portal_url, username, password)
    print('Done.')
    return gis


def get_portal_item(gis: GIS, item_id: str) -> Optional[GIS]:
    """Retrieve an item from the GIS portal.

    Args:
        gis: An authenticated GIS object.
        item_id: The ID of the item to retrieve.

    Returns:
        The portal item if found, None otherwise.

    Raises:
        Exception: If item retrieval fails
    """
    try:
        portal_item = gis.content.get(item_id)
        if portal_item is None:
            raise Exception(f"Portal item {item_id} not found")
        return portal_item
    except Exception as e:
        logging.error(f"Failed to retrieve portal item: {e}")
        raise


def ingest() -> Path:
    """Download geojson data from the USGS API and save it to a file.

    Returns:
        The file path of the saved geojson file.
    """
    url = config['USGS']['url']
    try:
        with requests.get(url=url) as response:
            response.raise_for_status()
            data = response.json()
    except (ChunkedEncodingError, RequestException) as ex:
        logging.error(f"Failed to download data: {ex}")
        sys.exit(1)

    geojson_path = WORKING_DIR / "01 Projects and Data" / "Data" / "Volcano.geojson"
    print('Writing geojson...')
    with open(geojson_path, 'w') as file:
        json.dump(data, file)
    print('Done.')
    return geojson_path


def replace_flayer(feature_layer_to_update, geojson_to_upload: Path) -> None:
    """Replace input feature layer with input geojson file.

    Args:
        feature_layer_to_update: GIS hosted feature layer.
        geojson_to_upload: Filepath of geojson file.
    """
    print('Overwriting feature layer...')
    collection = FeatureLayerCollection.fromitem(feature_layer_to_update)
    collection.manager.overwrite(str(geojson_to_upload))
    print('Done.')


if __name__ == '__main__':
    try:
        start = datetime.datetime.now()

        geojson_file = ingest()

        portal = sign_in_to_gis(
            config['PORTAL']['url'],
            config['PORTAL']['username'],
            kr.get_password("PORTAL", config['PORTAL']['username'])
        )
        feature_layer = get_portal_item(portal, config['PORTAL']['item_id'])
        replace_feature_layer(feature_layer, geojson_file)

        end = datetime.datetime.now()
        logging.info(f'Total time: {end - start}')
    except Exception as e:
        logging.exception("Unhandled exception occurred")
        print(f"{e} (see log for details)")