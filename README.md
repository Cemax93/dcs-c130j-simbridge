# DCS C-130J SimBridge

A small Windows desktop utility that bridges SimBrief flight plans into the
DCS C-130J-30 module.

The application lets you review and adjust the route before writing it to
`user_data.db`. It supports custom waypoints, runway overrides, optional FAF
generation, and map-based editing when `tkintermapview` is installed.

## Requirements

- Windows
- Python 3.10 or newer
- Tkinter (included with the standard Python Windows installer)
- Optional: `tkintermapview` for the interactive map

Install the optional map dependency with:

```powershell
py -3 -m pip install -r requirements.txt
```

## Run

```powershell
py -3 main.py
```

## Workflow

1. Enter a SimBrief username or Pilot ID and fetch the latest plan.
2. Select a theater and adjust departure/arrival airports or runways if
   needed.
3. Review the generated waypoints. Rows can be added, edited, deleted, or
   reordered.
4. Use **Export Flight Plan** to create a shareable `.simbridge.json` file,
   or use **Import Flight Plan** to load one received from another operator.
5. Choose the DCS `user_data.db` file and insert the route.

The database is updated in place. Make a backup before importing a route.

## License

This project is released under the MIT License. You may use, modify, and
redistribute it, provided that the original copyright notice and license are
retained in copies or substantial portions of the project.

If you publish a modified version, please clearly credit **DCS C-130J
SimBridge** and link back to this repository.

## Project layout

```text
main.py                 Application entry point
dcs_c130j_simbridge/app.py       Tkinter application controller
dcs_c130j_simbridge/config.py    External theater loading
dcs_c130j_simbridge/data.py      Built-in theater and airport data
dcs_c130j_simbridge/dialogs.py   Waypoint editor dialog
dcs_c130j_simbridge/geo.py       Coordinate and route formatting helpers
dcs_c130j_simbridge/flightplan.py Portable flight-plan file format
tests/                  Tests for side-effect-free route logic
```

## Sharing flight plans

The **Export Flight Plan** action creates a versioned JSON file containing the
route name, theater, and waypoint data. It does not contain a DCS database path,
SimBrief credentials, or any machine-specific information. Send the resulting
`.simbridge.json` file to another operator; they can load it with **Import
Flight Plan** and insert it into their own local DCS database.

## Custom theaters

Use **Export theaters.json** in the application to create an editable theater
database next to `main.py`. The file can be edited and loaded again on the next
start. Existing built-in theaters are used when no custom file is present.

## Tests

```powershell
py -3 -m unittest discover -s tests
```
