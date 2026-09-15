# Business logic for citizen ratings and MPLADS performance rankings

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.rating import Rating
from ..models.work import Work, WorkStatus


class RatingService:
    """
    Handles citizen ratings and calculation of the
    MPLADS Citizen Performance Index.
    """

    # Weight assigned to each citizen feedback category.
    WEIGHTS = {
        "quality": 0.30,
        "usefulness": 0.25,
        "timeliness": 0.20,
        "maintenance": 0.15,
        "satisfaction": 0.10,
    }

    @staticmethod
    def calculate_overall(data) -> float:
        """
        Calculate the overall rating on a 1–5 scale.
        """

        score = (
            data.quality_score
            * RatingService.WEIGHTS["quality"]
            + data.usefulness_score
            * RatingService.WEIGHTS["usefulness"]
            + data.timeliness_score
            * RatingService.WEIGHTS["timeliness"]
            + data.maintenance_score
            * RatingService.WEIGHTS["maintenance"]
            + data.satisfaction_score
            * RatingService.WEIGHTS["satisfaction"]
        )

        return round(score, 2)

    @staticmethod
    def create_rating(
        db: Session,
        citizen_id,
        data,
    ):
        """
        Create a rating for a work.

        A citizen can submit only one rating
        for a particular work.
        """

        # Find the work using its public work_id.
        work = (
            db.query(Work)
            .filter(Work.work_id == data.work_id)
            .first()
        )

        if not work:
            return None, "Work not found"

        # Check whether this citizen has already
        # rated this work.
        existing = (
            db.query(Rating)
            .filter(
                Rating.citizen_id == citizen_id,
                Rating.work_id == work.id,
            )
            .first()
        )

        if existing:
            return None, "You have already rated this work"

        # Calculate weighted overall rating.
        overall = RatingService.calculate_overall(data)

        rating = Rating(
            work_id=work.id,
            citizen_id=citizen_id,
            quality_score=data.quality_score,
            usefulness_score=data.usefulness_score,
            timeliness_score=data.timeliness_score,
            maintenance_score=data.maintenance_score,
            satisfaction_score=data.satisfaction_score,
            overall_score=overall,
            comment=data.comment,
            is_verified=True,
        )

        db.add(rating)
        db.commit()
        db.refresh(rating)

        return rating, None

    @staticmethod
    def get_mp_rankings(
        db: Session,
        state=None,
        constituency=None,
    ):
        """
        Calculate MPLADS Citizen Performance Index
        rankings for MPs.

        Only COMPLETED works are considered.
        """

        query = (
            db.query(
                Work.mp_name.label("mp_name"),
                Work.state.label("state"),
                Work.constituency.label("constituency"),

                func.avg(
                    Rating.quality_score
                ).label("quality"),

                func.avg(
                    Rating.usefulness_score
                ).label("usefulness"),

                func.avg(
                    Rating.timeliness_score
                ).label("timeliness"),

                func.avg(
                    Rating.maintenance_score
                ).label("maintenance"),

                func.avg(
                    Rating.satisfaction_score
                ).label("satisfaction"),

                func.count(
                    Rating.id
                ).label("responses"),

                func.count(
                    func.distinct(Work.id)
                ).label("works"),
            )
            .join(
                Rating,
                Rating.work_id == Work.id,
            )
            .filter(
                Work.status == WorkStatus.COMPLETED
            )
        )

        # State-level filtering.
        if state:
            query = query.filter(
                Work.state == state
            )

        # Constituency-level filtering.
        if constituency:
            query = query.filter(
                Work.constituency == constituency
            )

        rows = (
            query
            .group_by(
                Work.mp_name,
                Work.state,
                Work.constituency,
            )
            .all()
        )

        results = []

        for row in rows:

            # Weighted score on a 1–5 scale.
            weighted_score = (
                float(row.quality or 0)
                * RatingService.WEIGHTS["quality"]
                + float(row.usefulness or 0)
                * RatingService.WEIGHTS["usefulness"]
                + float(row.timeliness or 0)
                * RatingService.WEIGHTS["timeliness"]
                + float(row.maintenance or 0)
                * RatingService.WEIGHTS["maintenance"]
                + float(row.satisfaction or 0)
                * RatingService.WEIGHTS["satisfaction"]
            )

            # Convert 1–5 score to 0–100.
            citizen_performance_index = round(
                (weighted_score / 5) * 100,
                1,
            )

            results.append(
                {
                    "mp_name": row.mp_name,
                    "state": row.state,
                    "constituency": row.constituency,

                    "citizen_performance_index":
                        citizen_performance_index,

                    "quality":
                        round(float(row.quality or 0), 2),

                    "usefulness":
                        round(float(row.usefulness or 0), 2),

                    "timeliness":
                        round(float(row.timeliness or 0), 2),

                    "maintenance":
                        round(float(row.maintenance or 0), 2),

                    "satisfaction":
                        round(float(row.satisfaction or 0), 2),

                    "verified_works":
                        row.works,

                    "citizen_responses":
                        row.responses,
                }
            )

        # Highest performance index comes first.
        results.sort(
            key=lambda item:
                item["citizen_performance_index"],
            reverse=True,
        )

        # Assign ranking numbers.
        for rank, item in enumerate(
            results,
            start=1,
        ):
            item["rank"] = rank

        return results