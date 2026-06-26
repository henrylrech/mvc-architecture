CREATE TABLE IF NOT EXISTS enrollments (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    year                   INTEGER  NOT NULL,
    state                  TEXT     NOT NULL,
    city                   TEXT     NOT NULL,
    institution_name       TEXT     NOT NULL,
    institution_acronym    TEXT,
    organization_type      TEXT,
    administrative_category TEXT    NOT NULL,
    course_name            TEXT     NOT NULL,
    course_detail          TEXT,
    degree_type            TEXT     NOT NULL,
    modality               TEXT     NOT NULL,
    students_count         INTEGER  NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_year        ON enrollments(year);
CREATE INDEX IF NOT EXISTS idx_modality    ON enrollments(modality);
CREATE INDEX IF NOT EXISTS idx_course      ON enrollments(course_name);
CREATE INDEX IF NOT EXISTS idx_institution ON enrollments(institution_name);
CREATE INDEX IF NOT EXISTS idx_adm_cat     ON enrollments(administrative_category);
CREATE INDEX IF NOT EXISTS idx_degree      ON enrollments(degree_type);

-- Composite indexes for the actual query patterns
CREATE INDEX IF NOT EXISTS idx_year_modality     ON enrollments(year, modality);
CREATE INDEX IF NOT EXISTS idx_year_modality_adm ON enrollments(year, modality, administrative_category);
CREATE INDEX IF NOT EXISTS idx_course_modality   ON enrollments(course_name, modality);
CREATE INDEX IF NOT EXISTS idx_year_degree       ON enrollments(year, degree_type);
