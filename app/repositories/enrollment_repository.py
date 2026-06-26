"""
REPOSITORY layer — the only place in the app that contains SQL or touches sqlite3.

EnrollmentRepository encapsulates ALL database queries.
Controllers call methods here and receive plain Python objects/lists.
"""

from __future__ import annotations

from typing import Any

from app.repositories.db import get_connection


class EnrollmentRepository:
    """All SQL lives here. Controllers never import sqlite3 or write SQL."""

    # ------------------------------------------------------------------
    # Feature 1 — Total enrollment per year (with optional modality filter)
    # ------------------------------------------------------------------

    def get_total_by_year(self, modality: str | None = None) -> list[dict[str, Any]]:
        """
        Returns list of {year, total} sorted by year.
        modality: None = all, 'EaD', or 'Presencial'
        """
        conn = get_connection()
        try:
            cur = conn.cursor()
            if modality and modality in ("EaD", "Presencial"):
                cur.execute(
                    """
                    SELECT year, SUM(students_count) AS total
                    FROM   enrollments
                    WHERE  modality = ?
                    GROUP  BY year
                    ORDER  BY year
                    """,
                    (modality,),
                )
            else:
                cur.execute(
                    """
                    SELECT year, SUM(students_count) AS total
                    FROM   enrollments
                    GROUP  BY year
                    ORDER  BY year
                    """
                )
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Features 2 & 3 — Top-10 courses in 2023 by modality
    # ------------------------------------------------------------------

    def get_top_courses_2023(self, modality: str) -> list[dict[str, Any]]:
        """
        Returns top-10 courses for given modality in 2023.
        modality: 'EaD' or 'Presencial'
        """
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT   course_name, SUM(students_count) AS total
                FROM     enrollments
                WHERE    year = 2023
                  AND    modality = ?
                GROUP BY course_name
                ORDER BY total DESC
                LIMIT    10
                """,
                (modality,),
            )
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Features 4 & 5 — Top institutions in 2023 by modality (+ adm filter)
    # ------------------------------------------------------------------

    def get_top_institutions_2023(
        self,
        modality: str,
        adm_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Returns top-15 institutions by enrollment in 2023 for given modality.
        adm_filter: None = all, 'Públicas', or 'Privadas'
        """
        conn = get_connection()
        try:
            cur = conn.cursor()
            params: list[Any] = [modality]
            adm_clause = ""

            if adm_filter == "Públicas":
                adm_clause = "AND administrative_category LIKE 'Pública%'"
            elif adm_filter == "Privadas":
                adm_clause = "AND administrative_category LIKE 'Privada%'"

            cur.execute(
                f"""
                SELECT   institution_name,
                         institution_acronym,
                         administrative_category,
                         SUM(students_count) AS total
                FROM     enrollments
                WHERE    year = 2023
                  AND    modality = ?
                  {adm_clause}
                GROUP BY institution_name
                ORDER BY total DESC
                LIMIT    15
                """,
                params,
            )
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Feature 6 — Course timeline (year-by-year evolution)
    # ------------------------------------------------------------------

    def get_course_timeline(
        self,
        course_name: str,
        modality: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Returns {year, total} for the given course across all years.
        modality: None = both combined, 'EaD', or 'Presencial'
        """
        conn = get_connection()
        try:
            cur = conn.cursor()
            if modality and modality in ("EaD", "Presencial"):
                cur.execute(
                    """
                    SELECT   year, SUM(students_count) AS total
                    FROM     enrollments
                    WHERE    course_name = ?
                      AND    modality = ?
                    GROUP BY year
                    ORDER BY year
                    """,
                    (course_name, modality),
                )
            else:
                cur.execute(
                    """
                    SELECT   year, SUM(students_count) AS total
                    FROM     enrollments
                    WHERE    course_name = ?
                    GROUP BY year
                    ORDER BY year
                    """,
                    (course_name,),
                )
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_all_course_names(self) -> list[str]:
        """Returns sorted list of distinct course names."""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT DISTINCT course_name FROM enrollments ORDER BY course_name"
            )
            return [row[0] for row in cur.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Feature 7 — Pandemic impact: enrollment totals 2019-2022
    # ------------------------------------------------------------------

    def get_pandemic_totals(
        self,
        filter_type: str | None = None,
        filter_value: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Returns {year, total} for 2019-2022.
        filter_type: 'degree' or 'category'
        filter_value: e.g. 'Bacharelado', 'Licenciatura', 'Públicas', 'Privadas'
        """
        conn = get_connection()
        try:
            cur = conn.cursor()
            extra_clause = ""
            params: list[Any] = []

            if filter_type == "degree" and filter_value:
                extra_clause = "AND degree_type = ?"
                params.append(filter_value)
            elif filter_type == "category" and filter_value:
                if filter_value == "Públicas":
                    extra_clause = "AND administrative_category LIKE 'Pública%'"
                elif filter_value == "Privadas":
                    extra_clause = "AND administrative_category LIKE 'Privada%'"

            cur.execute(
                f"""
                SELECT   year, SUM(students_count) AS total
                FROM     enrollments
                WHERE    year BETWEEN 2019 AND 2022
                  {extra_clause}
                GROUP BY year
                ORDER BY year
                """,
                params,
            )
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Home overview stats
    # ------------------------------------------------------------------

    def get_overview_stats(self) -> dict[str, Any]:
        """Returns basic summary numbers for the home page."""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT SUM(students_count) FROM enrollments WHERE year = 2023")
            total_2023 = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(DISTINCT course_name) FROM enrollments")
            distinct_courses = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(DISTINCT institution_name) FROM enrollments")
            distinct_ies = cur.fetchone()[0] or 0

            cur.execute("SELECT MIN(year), MAX(year) FROM enrollments")
            row = cur.fetchone()
            year_min, year_max = row[0], row[1]

            return {
                "total_2023": total_2023,
                "distinct_courses": distinct_courses,
                "distinct_ies": distinct_ies,
                "year_min": year_min,
                "year_max": year_max,
            }
        finally:
            conn.close()
