# GIS Dataset Audit

## Current state

No GIS datasets were found in the repository.

The following file types are absent in the local workspace:
- `.shp`
- `.shx`
- `.dbf`
- `.prj`
- `.geojson`
- `.kml`
- `.kmz`
- `.gpkg`

This means the application cannot yet create or validate the required polygons for:
- state boundaries
- district boundaries
- parliamentary constituencies
- project point-in-polygon checks

## Required GIS datasets

| Dataset | Requirement | Status | Notes |
|---|---|---|---|
| Parliamentary constituencies | Mandatory | Missing | Required for MP and constituency boundaries |
| State boundaries | Mandatory | Missing | Required for hierarchy and scoping |
| District boundaries | Mandatory | Missing | Required for project-location mismatch alerts |
| Project GPS | Mandatory if supplied by external source | Missing | Current work CSV has no coordinates |

## Expected geometry handling

If a valid shapefile is later imported, the application should:
1. Validate CRS and convert to EPSG:4326 when necessary.
2. Check geometry validity and remove duplicate polygons.
3. Store geometry in PostGIS using `GEOGRAPHY` or `GEOMETRY` with proper SRID.
4. Add spatial indexes.
5. Expose simplified GeoJSON to the frontend.

## Risk of fabrication

The project must not invent project GPS or constituency centroids. If no verified coordinates exist, the platform should mark the location as `GPS_UNAVAILABLE` and permit future verified capture rather than fake location data.

## Required next action

Acquire and validate the official DataMeet shapefiles and district boundary datasets before implementing the GIS layers. Until then, all spatial features must remain explicitly unavailable in the app.
