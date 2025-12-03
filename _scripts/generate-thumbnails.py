#!/usr/bin/env python3
"""generate-thumbnails.py

Auto-generate thumbnails from original photos.

Scans _assets/images/photos/<collection>/originals/ and creates
corresponding thumbnails in _assets/images/photos/<collection>/thumbnails/

Features:
- Configurable thumbnail width (default: 300px)
- Maintains aspect ratio
- JPEG output with configurable quality
- Skips existing thumbnails unless --force is used
- Handles various image formats (JPEG, PNG, WebP, etc.)
"""

import argparse
import logging
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow is required: pip install Pillow", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

ROOT = Path(__file__).resolve().parents[1]
PHOTOS_DIR = ROOT / "_assets" / "images" / "photos"

# Default settings
DEFAULT_WIDTH = 300
DEFAULT_QUALITY = 85


def generate_thumbnail(src: Path, dst: Path, width: int, quality: int) -> bool:
    """Generate a thumbnail from source image.
    
    Args:
        src: Path to original image
        dst: Path to save thumbnail
        width: Target width in pixels (height auto-calculated)
        quality: JPEG quality (1-100)
    
    Returns:
        True if thumbnail was created, False otherwise
    """
    try:
        with Image.open(src) as img:
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode in ('RGBA', 'P', 'LA'):
                # Create white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate new height maintaining aspect ratio
            orig_width, orig_height = img.size
            
            # Only resize if image is larger than target width
            if orig_width > width:
                ratio = width / orig_width
                new_height = int(orig_height * ratio)
                img = img.resize((width, new_height), Image.Resampling.LANCZOS)
            
            # Save as JPEG
            dst.parent.mkdir(parents=True, exist_ok=True)
            img.save(dst, 'JPEG', quality=quality, optimize=True)
            return True
            
    except Exception as e:
        logging.error("Failed to process %s: %s", src, e)
        return False


def process_collection(collection_dir: Path, width: int, quality: int, force: bool) -> tuple[int, int]:
    """Process all images in a collection's originals folder.
    
    Args:
        collection_dir: Path to collection folder (e.g., banaras/)
        width: Target thumbnail width
        quality: JPEG quality
        force: Regenerate existing thumbnails
    
    Returns:
        Tuple of (created_count, skipped_count)
    """
    originals_dir = collection_dir / "originals"
    thumbnails_dir = collection_dir / "thumbnails"
    
    if not originals_dir.exists():
        logging.warning("No originals folder in %s", collection_dir.name)
        return (0, 0)
    
    created = 0
    skipped = 0
    
    # Supported image extensions
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff'}
    
    for src in originals_dir.iterdir():
        if src.suffix.lower() not in extensions:
            continue
        
        # Output as .jpg regardless of input format
        dst = thumbnails_dir / (src.stem + '.jpg')
        
        if dst.exists() and not force:
            skipped += 1
            continue
        
        if generate_thumbnail(src, dst, width, quality):
            logging.info("Created: %s", dst.relative_to(ROOT))
            created += 1
        else:
            skipped += 1
    
    return (created, skipped)


def main():
    parser = argparse.ArgumentParser(
        description="Generate thumbnails from original photos"
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=DEFAULT_WIDTH,
        help=f"Thumbnail width in pixels (default: {DEFAULT_WIDTH})"
    )
    parser.add_argument(
        "--quality", "-q",
        type=int,
        default=DEFAULT_QUALITY,
        help=f"JPEG quality 1-100 (default: {DEFAULT_QUALITY})"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Regenerate existing thumbnails"
    )
    parser.add_argument(
        "--collection", "-c",
        type=str,
        default=None,
        help="Process only this collection (e.g., 'banaras')"
    )
    
    args = parser.parse_args()
    
    if not PHOTOS_DIR.exists():
        logging.error("Photos directory not found: %s", PHOTOS_DIR)
        sys.exit(1)
    
    total_created = 0
    total_skipped = 0
    
    if args.collection:
        # Process single collection
        collection_dir = PHOTOS_DIR / args.collection
        if not collection_dir.exists():
            logging.error("Collection not found: %s", args.collection)
            sys.exit(1)
        collections = [collection_dir]
    else:
        # Process all collections
        collections = [d for d in PHOTOS_DIR.iterdir() if d.is_dir()]
    
    for collection_dir in collections:
        logging.info("Processing collection: %s", collection_dir.name)
        created, skipped = process_collection(
            collection_dir, args.width, args.quality, args.force
        )
        total_created += created
        total_skipped += skipped
    
    logging.info(
        "Done: %d thumbnails created, %d skipped",
        total_created, total_skipped
    )


if __name__ == '__main__':
    main()
