import os
import random
from datetime import datetime
from PIL import Image, ImageOps

def overlay_transparent_apple(background_path, overlay_path, output_dir):
    """
    Removes black background from overlay image and places it on top of the background image.
    Generates a filename with current date and a random number.
    """
    if not os.path.exists(background_path):
        print(f"Error: Background file {background_path} not found.")
        return
    if not os.path.exists(overlay_path):
        print(f"Error: Overlay file {overlay_path} not found.")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate dynamic filename: apple[YYMMDD][randomnumber].png
    date_str = datetime.now().strftime("%y%m%d")
    random_num = random.randint(1000, 9999)
    filename = f"apple{date_str}{random_num}.png"
    output_path = os.path.join(output_dir, filename)

    try:
        # 1. Process the overlay image (remove black background)
        with Image.open(overlay_path) as overlay_img:
            overlay_img = overlay_img.convert("RGBA")
            datas = overlay_img.getdata()

            new_data = []
            for item in datas:
                # If pixel is black (or very close to black), make it transparent
                if item[0] < 30 and item[1] < 30 and item[2] < 30:
                    new_data.append((0, 0, 0, 0))
                else:
                    new_data.append(item)
            overlay_img.putdata(new_data)

            # 2. Open the background image
            with Image.open(background_path) as bg_img:
                bg_img = bg_img.convert("RGBA")
                
                # Paste the transparent apple at (0, 0)
                bg_img.paste(overlay_img, (0, 0), overlay_img)
                
                # Save as PNG
                bg_img.save(output_path, "PNG")
                print(f"Success: Dynamic overlay image saved to {output_path}")
                
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Input paths
    bg_file = os.path.join("dist", "apple_before.jpg")
    overlay_file = os.path.join("input", "apple_input.jpg")
    
    # Output directory
    output_dir = "output"

    overlay_transparent_apple(bg_file, overlay_file, output_dir)
