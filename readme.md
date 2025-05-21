# USGS Volcano Data ETL Script

Python script to fetch the latest USGS volcano data and update an ArcGIS Portal feature layer automatically.

## Features

- Downloads current volcano data from the USGS API (GeoJSON format)
- Saves the data locally as a GeoJSON file
- Authenticates securely with ArcGIS Portal
- Updates a hosted feature layer with the new data

## Prerequisites

- Python 3.x
- Required Python packages:
  - `arcgis`
  - `keyring`
  - `requests`

Install dependencies with:

```bash
pip install arcgis keyring requests
```

## Configuration

Create a `config.ini` file in the `04 Scripts/config/` directory with the following structure:

```ini
[USGS]
url = <USGS API endpoint URL>

[PORTAL]
url = <ArcGIS Portal URL>
username = <portal username>
item_id = <feature layer item ID>
```

**Note:**  
- Store your ArcGIS Portal password securely using `keyring` (see below).
- Ensure the `item_id` corresponds to the hosted feature layer you want to update.

## Storing Portal Credentials

To avoid storing your password in plain text, use the `keyring` library:

```bash
python
>>> import keyring
>>> keyring.set_password("<ArcGIS Portal URL>", "<portal username>", "<your password>")
```

## Usage

Run the script from the project root:

```bash
python 04\ Scripts\volcano_update.py
```

- The script will fetch the latest volcano data and update the specified ArcGIS feature layer.
- Logs and errors will be printed to the console.

## Directory Structure

```
usgs-volcano-etl/
├── 04 Scripts/
│   ├── volcano_update.py
│   └── config/
│       └── config.ini
├── data/
│   └── volcanoes.geojson
└── readme.md
```

## Troubleshooting

- **Authentication errors:** Ensure your credentials are stored in `keyring` and match the config.
- **Permission errors:** Verify your ArcGIS Portal user has edit access to the feature layer.
- **API errors:** Check the USGS API endpoint URL in your config file.

## License

This project is licensed under the MIT License.

## References

- [USGS Volcano Hazards Program](https://volcanoes.usgs.gov/)
- [ArcGIS Python API Documentation](https://developers.arcgis.com/python/)
- [keyring Documentation](https://pypi.org/project/keyring/)

