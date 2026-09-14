"""Deterministic duplicate-work detection for API requests."""
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
import re


@dataclass
class DuplicatePair:
	work_id_a: str
	work_id_b: str
	similarity: float
	distance_m: float
	reason: str


def _tokens(value: str) -> set[str]:
	return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 2}


def _similarity(left: str, right: str) -> float:
	a, b = _tokens(left), _tokens(right)
	return len(a & b) / len(a | b) if a and b else 0.0


def _distance_m(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
	earth_radius = 6371000
	d_lat, d_lon = radians(lat_b - lat_a), radians(lon_b - lon_a)
	value = sin(d_lat / 2) ** 2 + cos(radians(lat_a)) * cos(radians(lat_b)) * sin(d_lon / 2) ** 2
	return 2 * earth_radius * asin(sqrt(value))


def find_duplicate_clusters(works: list) -> list[DuplicatePair]:
	results = []
	for index, left in enumerate(works):
		for right in works[index + 1:]:
			similarity = _similarity(left.description, right.description)
			distance = _distance_m(left.latitude, left.longitude, right.latitude, right.longitude)
			if similarity >= 0.82 and distance <= 500:
				results.append(DuplicatePair(left.work_id, right.work_id, round(similarity, 3), round(distance, 1), "High semantic similarity and geographic proximity"))
	return results
