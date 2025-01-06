import os
from PIL import Image
import piexif
import re


def parse_folder_name_to_datetime(folder_name):
    # Try to extract the date from the folder name and format it properly
   
    try:
        # First, try to match a common date format like YYYY-MM-DD
        date_match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", folder_name)
        if date_match:
            year, month, day = date_match.groups()
            # Default to 12:00:00 for time if only the date is provided
            return f"{year}:{month}:{day} 12:00:00"
        
        date_match = re.match(r"^(\d{4})_(\d{2})_(\d{2})$", folder_name)
        if date_match:
            year, month, day = date_match.groups()
            # Default to 12:00:00 for time if only the date is provided
            return f"{year}:{month}:{day} 12:00:00"
        

        # If it doesn't match a simple date, you can add more formats or default handling
        # Here I just return a default string, but you could modify based on other formats
        return "2025:01:01 12:00:00"  # Example fallback value
        
    except Exception as e:
        print(f"Error parsing folder name '{folder_name}': {e}")
        return "2025:01:01 12:00:00"  # Default fallback if parsing fails


def set_date_created(image_path, folder_name):

    date_created = parse_folder_name_to_datetime(folder_name)

    try:
         # Open the image to access its EXIF data
        img = Image.open(image_path)

        # Get the EXIF data (may need to check if 'exif' exists)
        exif_data = img.info.get('exif', b"")
        
        if exif_data:
            # If EXIF data exists, load it
            exif_dict = piexif.load(exif_data)
        else:
            # If EXIF data does not exist, create an empty EXIF structure
            exif_dict = piexif.load(piexif.dump({}))
            
        # EXIF DateTimeOriginal tag is 36867 (0x9003)
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_created
        
        # Convert back to bytes and save to the image
        exif_bytes = piexif.dump(exif_dict)
        img.save(image_path, exif=exif_bytes)
        print(f"Updated DateCreated for {image_path} to {date_created}")

    except Exception as e:
        print(f"Failed to update {image_path}: {e}")


def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        # Get the folder name (it should be in the format "YYYY-MM-DD")
        folder_name = os.path.basename(root)
        
        # Loop through files in the directory
        for file in files:
            if file.lower().endswith('.jpg'):
                file_path = os.path.join(root, file)
                set_date_created(file_path, folder_name)


if __name__ == "__main__":
    # Set the directory you want to process
    target_directory = "./out/FOTO"

    # Start processing
    process_directory(target_directory)
