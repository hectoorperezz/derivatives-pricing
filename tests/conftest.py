def pytest_configure(config):
    """Register markers when tests are executed from an installed wheel."""
    config.addinivalue_line("markers", "regression: regression tests")
