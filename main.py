import os
import random
from datetime import datetime
from PIL import Image, ImageOps

def create_masked_overlay(background_path, target_path, mask_path, output_dir):
    """
    1. Clips target_path using mask_path (black = transparent).
    2. Overlays the clipped result onto background_path.
    3. Saves with a dynamic filename.
    """
    if not os.path.exists(background_path):
        print(f"Error: Background file {background_path} not found.")
        return
    if not os.path.exists(target_path):
        print(f"Error: Target file {target_path} not found.")
        return
    if not os.path.exists(mask_path):
        print(f"Error: Mask file {mask_path} not found.")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate dynamic filename: apple[YYMMDD][randomnumber].png
    date_str = datetime.now().strftime("%y%m%d")
    random_num = random.randint(1000, 9999)
    filename = f"apple{date_str}{random_num}.png"
    output_path = os.path.join(output_dir, filename)

    try:
        # 1. Open all images
        with Image.open(mask_path) as mask_img, \
             Image.open(target_path) as target_img, \
             Image.open(background_path) as bg_img:
            
            # 2. Create the mask (black = 0, non-black = 255)
            mask_l = mask_img.resize(target_img.size).convert("L")
            mask_data = mask_l.getdata()
            new_mask_data = []
            for pixel in mask_data:
                if pixel < 30: # Threshold for black
                    new_mask_data.append(0)
                else:
                    new_mask_data.append(255)
            mask_l.putdata(new_mask_data)

            # 3. Clip the target image
            clipped_img = target_img.convert("RGBA")
            clipped_img.putalpha(mask_l)

            # 4. Overlay onto background
            bg_rgba = bg_img.convert("RGBA")
            # Paste at (0, 0) - assuming they are aligned
            bg_rgba.paste(clipped_img, (0, 0), clipped_img)

            # 5. Save as PNG
            bg_rgba.save(output_path, "PNG")
            print(f"Success: Masked overlay image saved to {output_path}")
                
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Input paths
    bg_file = os.path.join("dist", "apple_before.jpg")
    target_file = os.path.join("dist", "apple_yake.jpg")
    mask_file = os.path.join("input", "apple_input.jpg")
    
    # Output directory
    output_dir = "output"

    create_masked_overlay(bg_file, target_file, mask_file, output_dir)
