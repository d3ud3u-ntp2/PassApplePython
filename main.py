import os
from PIL import Image, ImageOps

def remove_black_background(input_path, output_path):
    """
    Reads an image, removes black pixels (makes them transparent), and saves it as a PNG.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with Image.open(input_path) as img:
            # Ensure image is in RGBA mode for transparency
            img = img.convert("RGBA")
            datas = img.getdata()

            new_data = []
            for item in datas:
                # If pixel is black (or very close to black), make it transparent
                # Threshold for "black" set to 30 to catch near-black compression artifacts
                if item[0] < 30 and item[1] < 30 and item[2] < 30:
                    new_data.append((0, 0, 0, 0))
                else:
                    new_data.append(item)

            img.putdata(new_data)
            img.save(output_path, "PNG")
            print(f"Success: Background removed image saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Default paths
    input_file = os.path.join("input", "apple_input.jpg")
    output_file = os.path.join("dist", "apple_before.png")

    remove_black_background(input_file, output_file)
