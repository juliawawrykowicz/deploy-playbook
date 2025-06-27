import os
from pathlib import Path
from PIL import Image
import pillow_avif  # noqa: F401 - needed to enable AVIF support in PIL

# Configuration
INPUT_DIR = Path(r"C:\git\mkdocs-material\src\overrides\assets\images\layers")
OUTPUT_DIR = Path(r"C:\git\mkdocs-material\material\overrides\assets\images\layers")
SCALES = [1, 2, 3, 4]  # for @1x, @2x, etc.
AVIF_QUALITY = 80  # 0-100
WEBP_QUALITY = 80
WEBP_ALPHA_QUALITY = 100

# Create output directory if needed
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Supported image extensions
SUPPORTED_EXTENSIONS = [".png", ".jpg", ".jpeg"]

def generate_images(image_path):
    img = Image.open(image_path).convert("RGBA")
    base_name = image_path.stem
    ext = image_path.suffix.lower()

    for scale in SCALES:
        suffix = "" if scale == 1 else f"@{scale}x"

        # Resize
        if scale != 1:
            #resized = img.resize((img.width * scale, img.height * scale), Image.Resampling.LANCZOS) 
            resized = img.resize((3840 * scale, 3746 * scale), Image.Resampling.LANCZOS) #3840 x 3746
        else:
            resized = img.copy()

        # Save PNG
        png_out = OUTPUT_DIR / f"{base_name}{suffix}.png"
        resized.save(png_out, format="PNG", optimize=True)
        print(f"Saved {png_out}")

        # Save AVIF
        avif_out = OUTPUT_DIR / f"{base_name}{suffix}.avif"
        resized.save(avif_out, format="AVIF", quality=AVIF_QUALITY)
        print(f"Saved {avif_out}")

        # Save WEBP
        webp_out = OUTPUT_DIR / f"{base_name}{suffix}.webp"
        resized.save(
            webp_out,
            format="WEBP",
            lossless=True,         # ensures no compression artifacts on alpha
            quality=WEBP_QUALITY,            # tweak lossy quality if switching to lossy mode
            alpha_quality=WEBP_ALPHA_QUALITY      # preserve full alpha fidelity :contentReference[oaicite:1]{index=1}
        )
        print(f"Saved {webp_out}")

def main():
    for image_file in INPUT_DIR.iterdir():
        if image_file.suffix.lower() in SUPPORTED_EXTENSIONS:
            generate_images(image_file)

if __name__ == "__main__":
    main()
