"""
CONTROLLER layer — single EnrollmentController covering all routes.

Handles all features (1–7): aggregated data and evolution analyses.
Controllers call Repository methods directly, perform any business-level
calculations, and return Template responses.
No SQL, no sqlite3 here — only Repository method calls.
"""

from __future__ import annotations

from litestar import Controller, get
from litestar.response import Template

from app.repositories.enrollment_repository import EnrollmentRepository

_repo = EnrollmentRepository()


def _pct_change(old: int | float, new: int | float) -> float | None:
    """Percentage change from old to new. Returns None if old == 0."""
    if old == 0:
        return None
    return round((new - old) / old * 100, 2)


class EnrollmentController(Controller):
    path = ""

    # ------------------------------------------------------------------
    # Feature 1 — Total enrollment by year
    # ------------------------------------------------------------------

    @get("/enrollment/enrollment-by-year", name="enrollment_by_year")
    async def enrollment_by_year(self, modality: str = "Todos") -> Template:
        mod = None if modality == "Todos" else modality
        rows = _repo.get_total_by_year(mod)
        labels = [str(r["year"]) for r in rows]
        values = [r["total"] for r in rows]
        return Template(
            "aggregated/enrollment_by_year.html",
            context={"modality": modality, "labels": labels, "values": values, "rows": rows},
        )

    @get("/enrollment/enrollment-by-year/chart", name="enrollment_by_year_chart")
    async def enrollment_by_year_chart(self, modality: str = "Todos") -> Template:
        """HTMX partial."""
        mod = None if modality == "Todos" else modality
        rows = _repo.get_total_by_year(mod)
        labels = [str(r["year"]) for r in rows]
        values = [r["total"] for r in rows]
        return Template(
            "partials/_enrollment_chart.html",
            context={"modality": modality, "labels": labels, "values": values, "rows": rows},
        )

    # ------------------------------------------------------------------
    # Features 2 & 3 — Top courses
    # ------------------------------------------------------------------

    @get("/enrollment/top-courses/{modality:str}", name="top_courses")
    async def top_courses(self, modality: str) -> Template:
        safe = modality if modality in ("EaD", "Presencial") else "Presencial"
        rows = _repo.get_top_courses_2023(safe)
        return Template(
            "aggregated/top_courses.html",
            context={"modality": safe, "rows": rows},
        )

    @get("/enrollment/top-courses/{modality:str}/table", name="top_courses_table")
    async def top_courses_table(self, modality: str) -> Template:
        """HTMX partial."""
        safe = modality if modality in ("EaD", "Presencial") else "Presencial"
        rows = _repo.get_top_courses_2023(safe)
        return Template(
            "partials/_ranking_table.html",
            context={"modality": safe, "rows": rows, "rank_type": "courses"},
        )

    # ------------------------------------------------------------------
    # Features 4 & 5 — Top institutions
    # ------------------------------------------------------------------

    @get("/enrollment/top-institutions/{modality:str}", name="top_institutions")
    async def top_institutions(self, modality: str, adm_filter: str = "Todos") -> Template:
        safe = modality if modality in ("EaD", "Presencial") else "Presencial"
        adm = None if adm_filter == "Todos" else adm_filter
        rows = _repo.get_top_institutions_2023(safe, adm)
        return Template(
            "aggregated/top_institutions.html",
            context={"modality": safe, "adm_filter": adm_filter, "rows": rows, "rank_type": "institutions"},
        )

    @get("/enrollment/top-institutions/{modality:str}/table", name="top_institutions_table")
    async def top_institutions_table(self, modality: str, adm_filter: str = "Todos") -> Template:
        """HTMX partial."""
        safe = modality if modality in ("EaD", "Presencial") else "Presencial"
        adm = None if adm_filter == "Todos" else adm_filter
        rows = _repo.get_top_institutions_2023(safe, adm)
        return Template(
            "partials/_ranking_table.html",
            context={"modality": safe, "adm_filter": adm_filter, "rows": rows, "rank_type": "institutions"},
        )

    # ------------------------------------------------------------------
    # Feature 6 — Course timeline
    # ------------------------------------------------------------------

    @get("/enrollment/course-timeline", name="course_timeline")
    async def course_timeline(self, course: str = "", modality: str = "Todos") -> Template:
        course_names = _repo.get_all_course_names()
        labels: list[str] = []
        values: list[int] = []
        if course:
            mod = None if modality == "Todos" else modality
            rows = _repo.get_course_timeline(course, mod)
            labels = [str(r["year"]) for r in rows]
            values = [r["total"] for r in rows]
        return Template(
            "evolution/course_timeline.html",
            context={
                "course_names": course_names,
                "selected_course": course,
                "modality": modality,
                "labels": labels,
                "values": values,
            },
        )

    @get("/enrollment/course-timeline/chart", name="course_timeline_chart")
    async def course_timeline_chart(self, course: str = "", modality: str = "Todos") -> Template:
        """HTMX partial."""
        labels: list[str] = []
        values: list[int] = []
        if course:
            mod = None if modality == "Todos" else modality
            rows = _repo.get_course_timeline(course, mod)
            labels = [str(r["year"]) for r in rows]
            values = [r["total"] for r in rows]
        return Template(
            "partials/_timeline_chart.html",
            context={"selected_course": course, "modality": modality, "labels": labels, "values": values},
        )

    # ------------------------------------------------------------------
    # Feature 7 — Pandemic impact
    # ------------------------------------------------------------------

    @get("/enrollment/pandemic-impact", name="pandemic_impact")
    async def pandemic_impact(self, filter_type: str = "degree", filter_value: str = "Bacharelado") -> Template:
        rows = _repo.get_pandemic_totals(filter_type, filter_value)
        yearly_changes, overall_pct = self._build_pandemic_summary(rows)
        return Template(
            "evolution/pandemic_impact.html",
            context={
                "filter_type": filter_type,
                "filter_value": filter_value,
                "labels": [str(r["year"]) for r in rows],
                "values": [r["total"] for r in rows],
                "yearly_changes": yearly_changes,
                "overall_pct": overall_pct,
            },
        )

    @get("/enrollment/pandemic-impact/summary", name="pandemic_impact_summary")
    async def pandemic_impact_summary(self, filter_type: str = "degree", filter_value: str = "Bacharelado") -> Template:
        """HTMX partial."""
        rows = _repo.get_pandemic_totals(filter_type, filter_value)
        yearly_changes, overall_pct = self._build_pandemic_summary(rows)
        return Template(
            "partials/_pandemic_summary.html",
            context={
                "filter_type": filter_type,
                "filter_value": filter_value,
                "labels": [str(r["year"]) for r in rows],
                "values": [r["total"] for r in rows],
                "yearly_changes": yearly_changes,
                "overall_pct": overall_pct,
            },
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_pandemic_summary(self, rows: list) -> tuple[list[dict], float | None]:
        yearly_changes = []
        for i, row in enumerate(rows):
            pct = None if i == 0 else _pct_change(rows[i - 1]["total"], row["total"])
            yearly_changes.append({"year": row["year"], "total": row["total"], "pct": pct})
        overall_pct = _pct_change(rows[0]["total"], rows[-1]["total"]) if len(rows) >= 2 else None
        return yearly_changes, overall_pct
