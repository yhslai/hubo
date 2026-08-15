import os
import img2pdf
from PIL import Image
import subprocess
import sys

def heif_to_jpg(image_path):
    jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
    print(f"Converting {image_path} to {jpg_path}...") 
    subprocess.run(['magick', image_path, jpg_path], check=True)
    return jpg_path


def images_to_pdf(folder_path):
    image_files = sorted(os.listdir(folder_path))
    image_files_path = [os.path.join(folder_path, img) for img in image_files]

    img_data = []

    for img_file_path in image_files_path:
        if img_file_path.lower().endswith('.heic'):
            img_file_path = heif_to_jpg(img_file_path)
        img_data.append(img_file_path)

    pdf_path = f"{os.path.basename(folder_path)}.pdf"

    with open(pdf_path, "wb") as f:
        print(f"Converting {len(img_data)} images to {pdf_path}...")
        f.write(img2pdf.convert(img_data))


def check_magick():
    try:
        subprocess.run(['magick', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        print("Error: ImageMagick's 'magick' command is not available. Please install ImageMagick and make sure 'magick' command works.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ./images_to_pdf.py folder_path")
        sys.exit(1)

    check_magick()

    folder_path = sys.argv[1]

    images_to_pdf(folder_path)