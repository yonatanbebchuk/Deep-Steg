from PIL import Image
from dataset_tools.encode_dataset import encode_image_with_0, encode_image_with_1
from neural_nets.auto_encoder import auto_encode
import numpy as np


def display_image(img_array):
    display = Image.fromarray(img_array)
    display.show()


def display_triplet(orig_image, clearance_level):
    image_with_key = encode_image_with_0(orig_image) if clearance_level == 0 else encode_image_with_1(orig_image)
    image_with_key = image_with_key.reshape(28, 28)

    auto_encoded_image = auto_encode(orig_image, clearance_level)

    trip = np.concatenate([orig_image, image_with_key, auto_encoded_image], axis=0)
    display_image(trip)