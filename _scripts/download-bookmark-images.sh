#!/bin/bash
# Script to download bookmark images and save them locally

# Create images directory
mkdir -p _assets/images/bookmarks

echo "Downloading bookmark images..."

# Reading image
echo "  - Downloading reading.webp..."
wget -q -O _assets/images/bookmarks/reading.webp \
  "https://iiif.micr.io/RaHJE/0,0,2446,3940/%5E640,/0/default.webp"

# Media image
echo "  - Downloading media.jpg..."
wget -q -O _assets/images/bookmarks/media.jpg \
  "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/%22Cavaquinho%22_%28c.1914-1915%29_-_Amadeo_de_Souza-Cardoso_%281897-1918%29_%2834175133244%29.jpg/960px-%22Cavaquinho%22_%28c.1914-1915%29_-_Amadeo_de_Souza-Cardoso_%281897-1918%29_%2834175133244%29.jpg?20170603220548"

# System image
echo "  - Downloading system.jpg..."
wget -q -O _assets/images/bookmarks/system.jpg \
  "https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Picabia_Machine_Turn.jpg/389px-Picabia_Machine_Turn.jpg?20050503053835"

# Curiosities image
echo "  - Downloading curiosities.jpg..."
wget -q -O _assets/images/bookmarks/curiosities.jpg \
  "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Francisco_de_Goya_-_Don_Manuel_Osorio_Manrique_de_Zu%C3%B1iga.jpg/500px-Francisco_de_Goya_-_Don_Manuel_Osorio_Manrique_de_Zu%C3%B1iga.jpg?20160907175354"

echo ""
echo "✓ Downloaded all images to _assets/images/bookmarks/"
echo ""
echo "Next steps:"
echo "1. Update _data/bookmarks.yml to use local paths:"
echo "   image: /_assets/images/bookmarks/reading.webp"
echo "2. Run: _scripts/gen-bookmarks.sh"
echo "3. Run: quarto render bookmarks/"
