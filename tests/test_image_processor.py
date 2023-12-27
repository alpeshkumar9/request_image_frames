import os
import pytest
import pandas as pd
import numpy as np
from PIL import Image as PILImage
import imghdr

from models import Image as ImageModel


class TestImageProcessor:

    def test_read_csv_data(self, test_image_processor_instance):
        data = test_image_processor_instance.read_csv_data()
        assert isinstance(data, pd.DataFrame)
        assert not data.empty

    @pytest.mark.parametrize(
        "input_data, expected_output, expected_logs",
        [
            # No missing values
            (
                pd.DataFrame({'depth': [1, 2], 'value': [3, 4]}),
                pd.DataFrame({'depth': [1, 2], 'value': [3, 4]}),
                []
            ),
            # Numeric missing values
            (
                pd.DataFrame({'depth': [1, None], 'value': [3, 4]}),
                pd.DataFrame({'depth': [1, 1], 'value': [3, 4]}),
                ["Missing values in column depth replaced with 1.0."]
            ),
            # Non-numeric data conversion
            (
                pd.DataFrame({'depth': [1, 2], 'value': ['a', 'b']}),
                pd.DataFrame({'depth': [1, 2], 'value': [0, 0]}),
                ["Non-numeric data found in column value. Converting to numeric."]
            ),
        ]
    )
    def test_preprocess_data(
        self, input_data, expected_output, expected_logs,
        caplog, test_image_processor_instance, test_image_directory
    ):
        caplog.clear()
        processor = test_image_processor_instance
        output = processor.preprocess_data(input_data)
        pd.testing.assert_frame_equal(
            output, expected_output, check_dtype=False)
        assert [record.message for record in caplog.records] == expected_logs

    @pytest.mark.parametrize(
        "pixel_values, new_width, expected_size",
        [
            (pd.Series([0, 128, 255] * 50), 150, (150, 1)),  # Standard resize
            (pd.Series([0, 128, 255] * 100), 300, (300, 1)),  # Larger resize
            (pd.Series([0, 128, 255] * 25), 75, (75, 1)),     # Smaller resize
        ]
    )
    def test_create_resized_image(
        self, pixel_values, new_width, expected_size, test_image_processor_instance
    ):
        resized_image = test_image_processor_instance.create_resized_image(
            pixel_values, new_width=new_width)

        assert isinstance(resized_image, PILImage.Image)
        assert resized_image.size == expected_size

        resized_image_array = np.array(resized_image)
        assert resized_image_array[0, 0] == pixel_values[0]
        assert resized_image_array[0, -1] == pixel_values.iloc[-1]

    @pytest.mark.parametrize(
        "input_array, expected_color",
        [
            (np.zeros((10, 10), dtype=np.uint8),
             (68, 1, 84, 255)),  # Black (viridis color)
        ]
    )
    def test_apply_color_map(
        self, input_array, expected_color, test_image_processor_instance
    ):
        grayscale_image = PILImage.fromarray(input_array)
        color_mapped_image = test_image_processor_instance.apply_color_map(
            grayscale_image)
        assert isinstance(color_mapped_image, PILImage.Image)

        color_mapped_array = np.array(color_mapped_image)
        np.testing.assert_array_equal(color_mapped_array[0, 0], expected_color)

    @pytest.mark.parametrize(
        "input_image, expected_format",
        [
            (PILImage.new('RGB', (10, 10)), 'png'),  # RGB image
            (PILImage.new('L', (10, 10)), 'png'),  # Grayscale image
            (PILImage.new('RGBA', (10, 10)), 'png'),  # RGBA image
        ]
    )
    def test_convert_image_to_binary(
        self, input_image, expected_format, test_image_processor_instance
    ):
        binary_data = test_image_processor_instance.convert_image_to_binary(
            input_image)
        assert isinstance(binary_data, bytes)

        detected_format = imghdr.what(None, h=binary_data)
        assert detected_format == expected_format, f"Expected format {expected_format}, but got {detected_format}"

    @pytest.mark.parametrize(
        "depth, binary_image, should_raise_error",
        [
            # Creation of a new record
            (10.5, b'sample_binary_data_1', False),
            # Update of an existing record
            (10.5, b'sample_binary_data_2', False),
            # Unique constraint violation
            ('test', b'sample_binary_data_3', True),
            # Different data, new record
            (15.0, b'sample_binary_data_4', False),
            # Corrupted/invalid data
            ('test', b'', True),
        ]
    )
    def test_save_image_to_db(self, depth, binary_image, should_raise_error, test_image_processor_instance, test_db_instance, caplog):
        with test_db_instance.get_db() as session:
            if should_raise_error:
                with pytest.raises(Exception):
                    assert "Error in saving/updating image to database:" in caplog.text
            else:
                test_image_processor_instance.save_image_to_db(
                    session, depth, binary_image)
                saved_image = session.query(ImageModel).filter(
                    ImageModel.depth == depth).first()
                assert saved_image is not None
                assert saved_image.image == binary_image

    def test_save_image_to_file(self, test_image_processor_instance):
        depth = 12.0
        image = PILImage.new('RGB', (10, 10))
        filepath = test_image_processor_instance.save_image_to_file(
            image, depth)

        assert os.path.isfile(filepath)
