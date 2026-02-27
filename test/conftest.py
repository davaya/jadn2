import os
import pytest

OUT_DIR = 'Out'

@pytest.fixture(scope='session')
def session_data():
    print('Performing overall setup')
    os.makedirs(OUT_DIR, exist_ok=True)
    yield {'output_dir': OUT_DIR}
    print('Performing overall teardown')