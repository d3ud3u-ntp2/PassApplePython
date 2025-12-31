import os
from PIL import Image, ImageOps

def invert_image(input_path, output_path):
    """
    Reads an image, inverts its colors, and saves it.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with Image.open(input_path) as img:
            # Handle RGBA images (inverting alpha doesn't make sense usually)
            if img.mode == 'RGBA':
                r, g, b, a = img.split()
                rgb_img = Image.merge('RGB', (r, g, b))
                inverted_image = ImageOps.invert(rgb_img)
                r2, g2, b2 = inverted_image.split()
                final_img = Image.merge('RGBA', (r2, g2, b2, a))
            else:
                final_img = ImageOps.invert(img.convert('RGB'))

            final_img.save(output_path)
            print(f"Success: Inverted image saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Default paths
    input_file = os.path.join("input", "apple_input.jpg")
    output_file = os.path.join("output", "apple_inverted.jpg")

    invert_image(input_file, output_file)
