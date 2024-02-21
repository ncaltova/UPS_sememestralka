import glob

from PIL import Image


def crop_to_content(image_path):
    print("cropping ", image_path)

    image=Image.open(image_path)
    imageBox = image.getbbox()
    cropped = image.crop(imageBox)
    cropped.save(image_path)

if __name__ == '__main__':
    for image_path in glob.glob("img/*.png"):
        crop_to_content(image_path)
