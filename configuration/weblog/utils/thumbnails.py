from PIL import Image


def create_thumbnail(
    path,
    size=(600, 400),
):

    image = Image.open(path)

    image.thumbnail(size)

    image.save(path)
