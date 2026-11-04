from sqlalchemy import inspect

from studyforge.db import init_db
from studyforge.models import Base


def test_init_db_creates_all_tables(tmp_path):
    db_file = tmp_path / "data" / "test.db"
    engine = init_db(str(db_file))
    expected = set(Base.metadata.tables.keys())
    actual = set(inspect(engine).get_table_names())
    assert expected <= actual
    assert db_file.exists()
