import os
import tempfile
import importlib
import json

import pytest


def setup_module(module):
    # set DB_PATH to a temp file before importing app
    module.tmp_db = tempfile.NamedTemporaryFile(delete=False)
    os.environ['DB_PATH'] = module.tmp_db.name

    # import the app after setting DB_PATH
    import backend_api
    importlib.reload(backend_api)
    module.app = backend_api.app


def teardown_module(module):
    try:
        os.unlink(module.tmp_db.name)
    except Exception:
        pass


def test_save_list_get_delete_portfolio():
    client = app.test_client()

    # invalid post (missing name ok -> Untitled but invalid stocks)
    res = client.post('/portfolios', json={"name": "Test", "stocks": "notalist"})
    assert res.status_code == 400

    # valid save
    payload = {"name": "MyTest", "stocks": [{"symbol": "AAPL", "quantity": 10}]}
    res = client.post('/portfolios', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    pid = data['id']

    # list
    res = client.get('/portfolios')
    assert res.status_code == 200
    lst = res.get_json().get('portfolios', [])
    assert any(p['id'] == pid for p in lst)

    # get
    res = client.get(f'/portfolios/{pid}')
    assert res.status_code == 200
    got = res.get_json()
    assert got['name'] == 'MyTest'
    assert isinstance(got['stocks'], list)

    # delete
    res = client.delete(f'/portfolios/{pid}')
    assert res.status_code == 200

    # get again -> 404
    res = client.get(f'/portfolios/{pid}')
    assert res.status_code == 404


def test_calculate_validation_and_empty():
    client = app.test_client()

    # empty payload
    res = client.post('/calculate', json=[])
    assert res.status_code == 400

    # invalid item structure
    res = client.post('/calculate', json=[{"symbol": "", "quantity": 0}])
    assert res.status_code == 400

    # valid (will attempt to fetch price but may return error) - we check not 500
    res = client.post('/calculate', json=[{"symbol": "AAPL", "quantity": 1}])
    assert res.status_code in (200, 400)
