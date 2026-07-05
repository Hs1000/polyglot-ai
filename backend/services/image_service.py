from PIL import Image


class ImageService:

    @staticmethod
    def load(file_path):

        return Image.open(file_path)