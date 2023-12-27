import os
import pandas as pd
import numpy as np
from PIL import Image as PILImage
import io
import logging
from typing import List, Tuple
from sqlalchemy.orm import Session
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from models import Image as ImageModel


class ImageProcessor:
    def __init__(self, csv_file_path: str, image_directory: str = 'data/images') -> None:
        """
        Initialize the ImageProcessor.

        Args:
            csv_file_path (str): The path to the CSV file containing image data.
            image_directory (str, optional): The directory to save processed images. Defaults to 'data/images'.
        """
        self.csv_file_path = csv_file_path
        self.image_directory = image_directory
        self.logger = logging.getLogger('ImageProcessor')
        self.logger.info(
            f"Initialized ImageProcessor with CSV file path: {csv_file_path}")

    def process_images(self, db: Session) -> None:
        try:
            img_data = pd.read_csv(self.csv_file_path)
            preprocessed_data = self.preprocess_data(img_data)
            for _, row in preprocessed_data.iterrows():
                depth, image = self.process_row(row)
                try:
                    self.save_image_to_db(db, depth, image)
                except Exception as e:
                    self.logger.error(f"Error saving image to database: {e}")
        except Exception as e:
            self.logger.error(f"Error processing images: {e}")

    def read_csv_data(self) -> pd.DataFrame:
        """
        Read image data from the CSV file.

        Returns:
            pd.DataFrame: A DataFrame containing image data.
        """
        return pd.read_csv(self.csv_file_path)

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the image data from the CSV file.

        Args:
            data (pd.DataFrame): The raw DataFrame containing image data.

        Returns:
            pd.DataFrame: The preprocessed DataFrame.
        """
        for column in data.columns:
            if data[column].isnull().any():
                if pd.api.types.is_numeric_dtype(data[column]):
                    replacement_value = data[column].mean()
                    data[column].fillna(replacement_value, inplace=True)
                    self.logger.info(
                        f"Missing values in column {column} replaced with {replacement_value}.")
                else:
                    data[column].fillna('CustomValue', inplace=True)
                    self.logger.info(
                        f"Missing non-numeric values in column {column} replaced with 'CustomValue'.")

            if not pd.api.types.is_numeric_dtype(data[column]):
                self.logger.warning(
                    f"Non-numeric data found in column {column}. Converting to numeric.")
                data[column] = pd.to_numeric(
                    data[column], errors='coerce').fillna(0)

        return data

    def process_row(self, row: pd.Series) -> Tuple[float, bytes]:
        """
        Process a single row of image data.

        Args:
            row (pd.Series): A row of image data from the CSV file.

        Returns:
            Tuple[float, bytes]: A tuple containing the image depth and binary image data.
        """
        depth = row.pop('depth')
        resized_img = self.create_resized_image(row)
        color_mapped_img = self.apply_color_map(resized_img)
        return depth, self.convert_image_to_binary(color_mapped_img)

    def create_resized_image(self, data_row: pd.Series, new_width: int = 150) -> PILImage.Image:
        """
        Create a resized image from a row of pixel values.

        Args:
            data_row (pd.Series): A row of pixel values.
            new_width (int, optional): The width of the resized image. Defaults to 150.

        Returns:
            PILImage.Image: The resized image.
        """
        pixel_values = data_row.values.astype(np.uint8)
        img = PILImage.fromarray(pixel_values.reshape((1, -1)), 'L')
        return img.resize((new_width, 1), PILImage.BILINEAR)

    def apply_color_map(self, image: PILImage.Image) -> PILImage.Image:
        """
        Apply a color map to a grayscale image.

        Args:
            image (PILImage.Image): The input grayscale image.

        Returns:
            PILImage.Image: The color-mapped image.
        """
        gray_image_array = np.array(image)
        colored_array = cm.viridis(gray_image_array)
        return PILImage.fromarray((colored_array * 255).astype(np.uint8))

    def convert_image_to_binary(self, image: PILImage.Image) -> bytes:
        """
        Convert a PIL image to binary format.

        Args:
            image (PILImage.Image): The input PIL image.

        Returns:
            bytes: The binary image data.
        """
        with io.BytesIO() as byte_io:
            image.save(byte_io, format='PNG')
            return byte_io.getvalue()

    def save_image_to_db(self, db: Session, depth: float, binary_image: bytes) -> None:
        """
        Save an image to the database, or update it if it already exists.

        Args:
            db (Session): The database session to use for saving the image.
            depth (float): The depth associated with the image.
            binary_image (bytes): The binary image data.
        """
        try:
            existing_image = db.query(ImageModel).filter(
                ImageModel.depth == depth).first()

            if existing_image:
                existing_image.image = binary_image
                self.logger.info(f"Updated image at depth: {depth}")
            else:
                new_image = ImageModel(depth=depth, image=binary_image)
                db.add(new_image)
                self.logger.info(f"Saved new image at depth: {depth}")

            db.commit()
        except Exception as e:
            db.rollback()
            self.logger.error(
                f"Error in saving/updating image to database: {e}")
            raise e

    def get_images_by_depth_range(self, db: Session, depth_min: float, depth_max: float) -> List[Tuple[float, PILImage.Image]]:
        """
        Retrieve images from the database within a specified depth range.

        Args:
            db (Session): The database session to use for querying images.
            depth_min (float): The minimum depth value.
            depth_max (float): The maximum depth value.

        Returns:
            List[Tuple[float, PILImage.Image]]: A list of tuples containing image depth and PIL images.
        """
        images = db.query(ImageModel).filter(
            ImageModel.depth.between(depth_min, depth_max)).all()
        if not images:
            raise ValueError(
                f"No images found within the depth range: {depth_min} - {depth_max}")
        return [(image.depth, PILImage.open(io.BytesIO(image.image))) for image in images]

    def save_image_to_file(self, image: PILImage.Image, depth: float) -> str:
        """
        Save an image to a file on disk.

        Args:
            image (PILImage.Image): The image to be saved.
            depth (float): The depth associated with the image.

        Returns:
            str: The file path where the image is saved.
        """
        os.makedirs(self.image_directory, exist_ok=True)
        filename = f"image_{depth}.png"
        filepath = f"{self.image_directory}/{filename}"
        image.save(filepath, format='PNG')
        return filepath

    def plot_image_with_color_map(self, image: PILImage.Image) -> None:
        """
        Plot an image with a color map using Matplotlib.

        Args:
            image (PILImage.Image): The image to be plotted.
        """
        image_array = np.array(image)
        plt.imshow(image_array, cmap='viridis')
        plt.colorbar()
        plt.axis('off')
        plt.show()
