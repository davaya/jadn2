import os
import pytest

OUT_DIR = 'Out'

@pytest.fixture(scope='session')
def overall_setup():
    print('Performing overall setup')
    os.makedirs(OUT_DIR, exist_ok=True)
    yield OUT_DIR