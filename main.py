import os
import random
import numpy as np
from datetime import datetime
from PIL import Image, ImageOps, ImageFilter, ImageDraw

# Optional import for advanced image processing
try:
    from scipy.ndimage import map_coordinates
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False
    print("Warning: scipy not found. Advanced image transformations (like 3D bulge) will be disabled.")

def apply_bulge_effect(image, bounding_box):
    """
    Applies a 3D bulge (spherical) effect to the image within the bounding box.
    """
    if not _SCIPY_AVAILABLE:
        print("Error: scipy is not available, cannot apply bulge effect.")
        return image # Return original image if scipy is missing

    width, height = image.size
    min_x, min_y, max_x, max_y = bounding_box
    
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    radius_x = (max_x - min_x) / 2
    radius_y = (max_y - min_y) / 2
    
    # Create coordinate grids
    x = np.arange(width)
    y = np.arange(height)
    xv, yv = np.meshgrid(x, y)
    
    # Normalize coordinates relative to center and radius
    # (dx, dy) will be in range [-1, 1] within the ellipse
    dx = (xv - center_x) / radius_x
    dy = (yv - center_y) / radius_y
    
    # Calculate distance from center in normalized space
    dist_sq = dx**2 + dy**2
    mask = dist_sq <= 1.0
    
    # Initialize output maps
    map_x = xv.astype(np.float32)
    map_y = yv.astype(np.float32)
    
    # Apply spherical transformation (Bulge effect)
    # The math: maps a flat point to a spherical surface
    # r_new = r_old / sqrt(1 - r_old^2) is one way, but we'll use a simpler power-based bulge
    # or a true spherical projection: sin(r * pi/2)
    dist = np.sqrt(dist_sq[mask])
    
    # Transformation factor: points near center move less, points near edge move more "inward"
    # to simulate the stretch of a sphere being flattened.
    # Actually, for a "bulge" looking out, we want the center pixels to be MAGNIFIED.
    
    # Avoid division by zero for dist=0 (center pixel)
    factor = np.ones_like(dist)
    non_zero_dist_mask = dist > 0
    factor[non_zero_dist_mask] = np.arcsin(dist[non_zero_dist_mask]) / (dist[non_zero_dist_mask] * (np.pi / 2))
    
    new_dx = dx[mask] * factor
    new_dy = dy[mask] * factor
    
    map_x[mask] = center_x + new_dx * radius_x
    map_y[mask] = center_y + new_dy * radius_y
    
    # Ensure coordinates are within bounds
    map_x = np.clip(map_x, 0, width - 1)
    map_y = np.clip(map_y, 0, height - 1)
    
    img_array = np.array(image)
    output_array = np.zeros_like(img_array)
    
    # For each channel
    for i in range(img_array.shape[2]):
        # Note: map_coordinates expects (y, x)
        output_array[:, :, i] = map_coordinates(img_array[:, :, i], [map_y, map_x], order=1, mode='reflect')
        
    return Image.fromarray(output_array)

def load_bounding_box(path):
    """
    Reads min_x, min_y, max_x, max_y from a text file.
    Supports comma or space separated values.
    """
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            content = f.read().strip().replace(',', ' ')
            coords = [int(v) for v in content.split()]
            if len(coords) == 4:
                return tuple(coords)
    except Exception as e:
        print(f"Warning: Failed to read bounding box from {path}: {e}")
    return None

def create_masked_overlay(background_path, target_path, mask_path, output_dir, bbox_path=None):
    """
    1. Detects bounding box from bbox_path (bounding_box.txt) or mask_path.
    2. Bulges both mask_path (apple_input) and target_path (apple_yake).
    3. Uses the bulged grayscale mask_path as the alpha channel for both layers.
    4. Composites all on top of background_path (apple_before).
    """
    if not all(os.path.exists(p) for p in [background_path, target_path, mask_path]):
        print("Error: One or more input files not found.")
        return

    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%y%m%d")
    random_num = random.randint(1000, 9999)
    filename = f"apple{date_str}{random_num}.png"
    output_path = os.path.join(output_dir, filename)

    try:
        with Image.open(mask_path) as mask_img, \
             Image.open(target_path) as target_img, \
             Image.open(background_path) as bg_img:
            
            # --- Determine Bounding Box ---
            bbox = None
            if bbox_path:
                bbox = load_bounding_box(bbox_path)
                if bbox:
                    print(f"Using bounding box from file: {bbox}")
            
            if not bbox:
                # Fall back to automatic detection from apple_input
                mask_gray_orig = mask_img.convert("L")
                mask_np = np.array(mask_gray_orig)
                coords = np.argwhere(mask_np >= 10)
                
                if coords.size == 0:
                    print("Error: No apple shape found for automatic bounding box detection.")
                    return
                    
                min_y, min_x = coords.min(axis=0)
                max_y, max_x = coords.max(axis=0)
                bbox = (min_x, min_y, max_x, max_y)
                print(f"Detected bounding box automatically: {bbox}")

            # --- Layer 1: Bulged Original Apple (from apple_input) ---
            if _SCIPY_AVAILABLE:
                bulged_apple = apply_bulge_effect(mask_img.convert("RGB"), bbox)
            else:
                bulged_apple = mask_img.convert("RGB")

            # Use bulged grayscale version as its own alpha channel
            bulged_apple_gray = bulged_apple.convert("L")
            # Apply slight anti-aliasing to the mask
            bulged_apple_gray = bulged_apple_gray.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            bulged_apple_rgba = bulged_apple.convert("RGBA")
            bulged_apple_rgba.putalpha(bulged_apple_gray)

            # --- Layer 2: Bulged Yake Texture (from apple_yake) ---
            if _SCIPY_AVAILABLE:
                bulged_yake = apply_bulge_effect(target_img.convert("RGB"), bbox)
            else:
                bulged_yake = target_img.convert("RGB")

            # Use the SAME bulged grayscale mask as alpha channel for yake
            clipped_yake_rgba = bulged_yake.convert("RGBA")
            clipped_yake_rgba.putalpha(bulged_apple_gray)

            # --- Final Composition ---
            final_composition = bg_img.convert("RGBA")
            
            # Paste bulged original apple (Layer 1)
            final_composition.paste(bulged_apple_rgba, (0, 0), bulged_apple_rgba)
            
            # Paste bulged yake texture (Layer 2)
            final_composition.paste(clipped_yake_rgba, (0, 0), clipped_yake_rgba)

            final_composition.save(output_path, "PNG")
            print(f"Success: Bounding box coordinated 3D overlay saved to {output_path}")
                
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    bg_file = os.path.join("dist", "apple_before.jpg")
    target_file = os.path.join("dist", "apple_yake.jpg")
    mask_file = os.path.join("input", "apple_input.jpg")
    bbox_file = os.path.join("input", "bounding_box.txt") # External bbox file
    
    output_dir = "output"
    create_masked_overlay(bg_file, target_file, mask_file, output_dir, bbox_file)
