import pytest
from fastapi.testclient import TestClient
from main import app


class TestMainEndpoints:
    @pytest.mark.parametrize(
        "depth_min, depth_max, expected_status_code, expect_error",
        [
            # Valid range, expecting a non-empty response
            (9040, 9041, 200, False),
            # Valid range but no results, expecting a 404 response
            (10000, 11000, 404, True),
            # Invalid range (non-numeric), expecting an error response (404 or 422 depending on API design)
            ("abc", "def", 422, True),
            # Negative range, expecting a 404 response if the API treats this as invalid
            (-100, -1, 404, True),
            # Zero range, expecting a 404 response if no images are found
            (0, 0, 404, True),
        ]
    )
    def test_get_images(
        self,
        test_client: TestClient,
        depth_min,
        depth_max,
        expected_status_code,
        expect_error
    ):
        response = test_client.get(
            f"/images/?depth_min={depth_min}&depth_max={depth_max}")
        assert response.status_code == expected_status_code

        if expect_error:
            assert "detail" in response.json()
