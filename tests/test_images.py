import unittest
import cv2
import numpy as np
from qolhelpers.images import threshold_and_crop


class TestImagesModule(unittest.TestCase):
    def test_cropped_image_shape(self):
        # Create a synthetic image with two blobs
        synthetic_image = np.zeros((200, 200), dtype=np.uint8)
        cv2.rectangle(synthetic_image, (50, 50), (100, 100), 255, -1)
        cv2.rectangle(synthetic_image, (120, 120), (170, 170), 255, -1)

        # Convert the grayscale image to a BGR image
        synthetic_image = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2BGR)

        # Call the function with the synthetic image
        cropped_image = threshold_and_crop(synthetic_image, 10)

        # Verify the shape of the cropped image
        self.assertEqual(cropped_image.shape, (141, 141, 3))


if __name__ == '__main__':
    unittest.main()