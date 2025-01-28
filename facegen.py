import os
import torch
import numpy as np
from torchvision.utils import save_image
from pathlib import Path
import requests
import PIL
import time

# Ensure you have the StyleGAN3 repository cloned locally
STYLEGAN3_DIR = r"stylegan3"
# TODO: Change the MODEL_URL to the desired StyleGAN3 model
MODEL_URL = "https://api.ngc.nvidia.com/v2/models/nvidia/research/stylegan3/versions/1/files/stylegan3-r-ffhq-1024x1024.pkl"
OUTPUT_DIR = "facegen/generated_faces"
TRUNCATION = 0.4 # Balances the accuracy and diversity of the generated images. Lower values give more realistic faces.
RANDOM_SEED = 18
NUM_IMAGES = 5

# Add StyleGAN3 utilities to the path
import sys
sys.path.insert(1, STYLEGAN3_DIR)

# Import necessary modules from StyleGAN3
from stylegan3 import dnnlib
import legacy
from legacy import load_network_pkl

# Download pre-trained StyleGAN3 model
def download_model(model_path):
    model_dir = os.path.dirname(model_path)
    os.makedirs(model_dir, exist_ok=True) # Create the directory if it doesn't exist
    if not os.path.exists(model_path):
        print("Downloading StyleGAN3 pre-trained model...")
        response = requests.get(MODEL_URL, stream=True)
        with open(model_path, "wb") as f:
            f.write(response.content)
        print("Download complete.")

# Load the StyleGAN3 generator
def load_generator(model_path):
    print("Loading pre-trained model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    with open(model_path, "rb") as f:
        generator = legacy.load_network_pkl(f)["G_ema"].to(device)  # Load generator
    return generator

# Generate and save images
def generate_images(generator, num_images=5, truncation=1.0, seed=42):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    generator = generator.to(device)

    np.random.seed(seed)
    for i in range(num_images):
        z = torch.from_numpy(np.random.randn(1, generator.z_dim)).to(device)  # Random latent vector
        c = None  # Assuming no conditioning, set to appropriate value if needed
        with torch.no_grad():
            img = generator(z, c, truncation_psi=truncation, noise_mode="const")
        img = (img.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)  # Scale to 0-255
        img_path = Path(OUTPUT_DIR) / f"face_{i+1}.png"
        PIL.Image.fromarray(img[0].cpu().numpy(), "RGB").save(img_path)
        print(f"Saved image: {img_path}")

if __name__ == "__main__":
    model_path = "facegen/stylegan3_model.pkl"
    download_model(model_path)
    generator = load_generator(model_path)
    start_time = time.time()
    generate_images(generator, num_images=NUM_IMAGES, seed=RANDOM_SEED, truncation=TRUNCATION)
    print(f"Time taken: {time.time() - start_time:.2f} seconds")
    print("Time per image: {:.2f} seconds".format((time.time() - start_time) / NUM_IMAGES))
