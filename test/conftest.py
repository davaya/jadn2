import os
import pytest
from test_convert_rt import abs_dir, OUT_DIR


@pytest.fixture(scope='session')
def session_data():
    print(f'Performing overall setup')
    os.makedirs(abs_dir(OUT_DIR), exist_ok=True)
    yield {}
    print('Performing overall teardown')