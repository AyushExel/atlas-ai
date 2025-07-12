from PIL import Image
import os

def create_dummy_image(path, color):
    img = Image.new('RGB', (100, 100), color=color)
    img.save(path)

if __name__ == "__main__":
    os.makedirs("dummy_data/my_complex_dataset/PNGImages", exist_ok=True)
    os.makedirs("dummy_data/my_complex_dataset/PedMasks", exist_ok=True)
    create_dummy_image("dummy_data/my_complex_dataset/PNGImages/1.png", "red")
    create_dummy_image("dummy_data/my_complex_dataset/PNGImages/2.png", "green")
    create_dummy_image("dummy_data/my_complex_dataset/PNGImages/3.png", "blue")
    create_dummy_image("dummy_data/my_complex_dataset/PedMasks/1_mask.png", "white")
    create_dummy_image("dummy_data/my_complex_dataset/PedMasks/2_mask.png", "white")
    create_dummy_image("dummy_data/my_complex_dataset/PedMasks/3_mask.png", "white")
