"""
MODEL layer — the 'M' in MVC.

Defines the single Enrollment dataclass that represents one row
of the enrollments table. No SQL, no sqlite3, no DB access here.
This class is the plain in-memory representation of a data point.
"""

from dataclasses import dataclass


@dataclass
class Enrollment:
    """One enrollment record: course × year × institution × modality."""

    id: int
    year: int
    state: str
    city: str
    institution_name: str
    institution_acronym: str
    organization_type: str
    administrative_category: str  # e.g. "Pública Federal", "Privada com fins lucrativos"
    course_name: str              # normalized uppercase course name
    course_detail: str            # detailed / full course name
    degree_type: str              # Bacharelado | Licenciatura | Tecnológico
    modality: str                 # EaD | Presencial
    students_count: int
