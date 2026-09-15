"""
Set GPS coordinates on ONE work — for your live geotag verification demo.

WHY THIS EXISTS: real MPLADS.csv data has no GPS coordinates at all (no
government dataset we found has them). Photo verification only works
when a work HAS a registered latitude/longitude to compare against. The
realistic way to demo this live in front of judges is: pick one real (or
demo) work, set its coordinates to wherever you'll physically stand when
you take the demo photo on your phone, then upload that photo live.

Usage:
    python -m app.set_demo_location W-DEMO-001 28.6139 77.2090

Find your own current coordinates by opening Google Maps on your phone,
long-pressing your location, and copying the lat/long shown.
"""
import argparse

from .database import SessionLocal
from .models.work import Work


def set_location(work_id: str, lat: float, lon: float) -> None:
    db = SessionLocal()
    try:
        work = db.query(Work).filter(Work.work_id == work_id).first()
        if not work:
            print(f"No work found with work_id '{work_id}'.")
            return
        work.latitude = lat
        work.longitude = lon
        db.commit()
        print(f"Set {work_id} ({work.work_title}) location to ({lat}, {lon}).")
        print("Now upload a photo taken AT that location for that work — it should verify.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("work_id", help="e.g. W-DEMO-001 or WRK-REAL-000042")
    parser.add_argument("latitude", type=float)
    parser.add_argument("longitude", type=float)
    args = parser.parse_args()
    set_location(args.work_id, args.latitude, args.longitude)
