import pytest

# local imports
from utils.settings import APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK
from app import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app()
    if __name__ == "__main__":
        app.run_server(
            host=APP_HOST,
            port=APP_PORT,
            debug=APP_DEBUG,
            dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
        )

    with app.server.test_client() as client:
        yield client
