import pytest
from shrikenet.db import get_services


def test_get_close_storage_provider(app):
    with app.app_context():
        services = get_services()
        assert services is get_services()

    with pytest.raises(RuntimeError) as excinfo:
        get_services()

    assert "outside of application context" in str(excinfo.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("shrikenet.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called
