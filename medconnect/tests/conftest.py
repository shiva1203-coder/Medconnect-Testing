import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture
def app_client(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["FLASK_ENV"] = "development"

    from app import create_app
    from database.database import create_all

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        create_all()

    return app.test_client(), app
