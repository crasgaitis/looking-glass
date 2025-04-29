# parses metadata from image file Name
# see here https://docs.google.com/document/d/1AEZMWzAEXVHJPKKtGQ3qxke9u5_bVmNdMZYkTWQ5Csk/edit?tab=t.0

import os

def parse_image_metadata(image_path):
    file_name = os.path.basename(image_path)
    base_name = os.path.splitext(file_name)[0]
    parts = base_name.split('_')
    if len(parts) == 6:
        image1_type = parts[0]
        image1_name = parts[1]
        image1_percent = parts[2]
        image2_type = parts[3]
        image2_name = parts[4]
        image2_percent = parts[5]

        image1_name = image1_name.title().replace('-', ' ')
        image2_name = image2_name.title().replace('-', ' ')

        return {
            "image1_type": image1_type,
            "image1_name": image1_name,
            "image1_percent": image1_percent,
            "image2_type": image2_type,
            "image2_name": image2_name,
            "image2_percent": image2_percent
        }
    else:
        raise ValueError("Filename does not match the expected format.")

if __name__ == "__main__":
    image_path = "friend_james-wilson_25_friend_jeremy-ma_75.png"
    metadata = parse_image_metadata(image_path)
    print(metadata)
