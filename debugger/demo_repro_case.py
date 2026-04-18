from django.test import SimpleTestCase


class DemoReproFailureTests(SimpleTestCase):
    """
    Dedicated repro-command failure for the analyzer demo.

    This module is intentionally not named test*.py, so it is excluded from the
    default Django test discovery. Run it explicitly when you want a real
    failing stack trace from this repo.
    """

    def test_intentional_failure_route_smoke(self):
        self.client.get("/__demo__/intentional-failure/")
