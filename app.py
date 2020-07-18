from PIL import Image, ImageDraw, ImageGrab, UnidentifiedImageError, ImageFont
from datetime import datetime
from colorthief import ColorThief
from os import getenv, path, mkdir, rename, startfile
from shutil import copyfile
from sys import argv
from tkinter import Tk, TclError
from dotenv import load_dotenv, set_key
from random import randint, choice
from itertools import permutations

load_dotenv()

# Variables to easily allow functionality modifications without having to do a messy replace
output_path =                  getenv("output_path",            "output")
tmp_path =                     getenv("tmp_path",               "output/tmp")
palette_filename =             getenv("palette_filename",       "palette.png")
colour_count =             int(getenv("colour_count",           5))
stroke_width =           float(getenv("stroke_width",           5))
inner_rectangle_margin = float(getenv("inner_rectangle_margin", 25))
thumbnail_width =          int(getenv("thumbnail_width",        1280))
thumbnail_height =         int(getenv("thumbnail_height",       720))
output_filename =              getenv("output_filename",        "thumbnail")
output_extension =             getenv("output_extension",       "PNG")
font_location =                getenv("font_location",          "C:/Windows/Fonts/Arial.ttf")
font_size =                int(getenv("font_size",              124))


# Variables that will be filled in over runtime, declared here for readability
colour_palette_image = None
thumbnail_text = ""
clipboard_has_image = False

# Step 0: preparation. Create output dir
if not path.isdir(output_path):
    mkdir(output_path)

if not path.isdir(tmp_path):
    mkdir(tmp_path)


# Step 1: identify what startup argument is given
# 1a: the image to take the colour pallete from
# 1b: the text to write on the thumbnail
# 1c: neither
if len(argv) >= 2:
    startup_arg = argv[1]
    if path.isfile(startup_arg):  # 1a
        colour_palette_image = startup_arg
    else:  # 1b
        thumbnail_text = startup_arg
else:  # 1c
    pass


# Step 2: get colour palette image
# This will come from a local image that is fed through one of three options
# 2a: startup arguments. If this is the case, put the palette in the tmp directory
# 2b: clipboard. If this is the case, grab it using Pillow
# 2c: manual input. If this is the case, prompt
if colour_palette_image != None: # 2a
    copyfile(colour_palette_image, path.join(tmp_path, palette_filename))
else:
    clipboard_image = ImageGrab.grabclipboard()
    if clipboard_image != None:  # 2b
        clipboard_image.save(path.join(tmp_path, palette_filename), "PNG")
        clipboard_has_image = True
    else:  # 2c
        def prompt_for_palette_image():
            try:
                path_to_palette_image = input("Path to image: ")
                with Image.open(path_to_palette_image) as image:
                    # If no failure here, save the image to tmp folder
                    image.save(path.join(tmp_path, palette_filename))
                return path_to_palette_image

            except FileNotFoundError:
                print("File not found!")
                prompt_for_palette_image()

            except UnidentifiedImageError:
                print("Image could not be opened or identified!")
                prompt_for_palette_image()

            except KeyboardInterrupt:
                print("Closing...")
                quit()

            except:
                print("Unkown error occurred!")
                prompt_for_palette_image()
        prompt_for_palette_image()


# Step 3: get colour palette from image
color_thief = ColorThief(path.join(tmp_path, palette_filename))
palette = color_thief.get_palette(color_count=colour_count)



# Step 4: get the text to place on the thumbnail
# This will be fed through one of two options:
# 4a: startup args
# 4b: clipboard (if the clipboard doesn't contain an image)
# 4c: manual input
# In case of 4a and 4b, still allow the user to change the input
if thumbnail_text != "":  # 4a
    pass
elif not clipboard_has_image:  # 4b
    try:
        tk = Tk()
        tk.withdraw()
        thumbnail_text = tk.clipboard_get()
    except TclError:
        pass
# 4a, 4b & 4c
thumbnail_text = input("Thumbnail text [{0}]: ".format(thumbnail_text)) or thumbnail_text
thumbnail_text = thumbnail_text.replace(r"\n", "\n")

# Step 5: 
#thumbnail_text_split = thu



# Step 5: generate every possible colour combination for the thumbnail
thumbnail_index = 1
thumbnail_font = ImageFont.truetype(font_location, size=font_size)

def generate_thumbnail(thumbnail_index, colour_one, colour_two, colour_three, colour_four, colour_five):
    with Image.new("RGBA", (thumbnail_width, thumbnail_height)) as thumbnail:
        draw = ImageDraw.Draw(thumbnail, "RGBA")

        # Background rectangle
        draw.rectangle([
            0, 
            0, 
            thumbnail_width, 
            thumbnail_height
            ], fill=colour_one)

        # Foreground rectangle
        draw.rectangle([
            inner_rectangle_margin, 
            inner_rectangle_margin, 
            thumbnail_width - inner_rectangle_margin, 
            thumbnail_height - inner_rectangle_margin
            ], fill=colour_two)


        # Upper left -> bottom inner rectangle
        """
         -------------------------
        ||                       |
        ||                       |
        ||                       |
        ||                       |
        ||                       |
        ||                       |
         -------------------------
        """
        draw.rectangle([
            inner_rectangle_margin, 
            inner_rectangle_margin, 
            inner_rectangle_margin * 2,
            thumbnail_height - inner_rectangle_margin
            ], fill=colour_three)
        
        # Bottom right -> upper inner rectangle
        """
        -------------------------
        |                       ||
        |                       ||
        |                       ||
        |                       ||
        |                       ||
        |                       ||
        -------------------------
        """
        draw.rectangle([
            thumbnail_width - inner_rectangle_margin * 2,
            inner_rectangle_margin,
            thumbnail_width - inner_rectangle_margin,
            thumbnail_height - inner_rectangle_margin
            ], fill=colour_four)


        # Upper left -> right inner rectangle
        """
        =========================
        |                       |
        |                       |
        |                       |
        |                       |
        |                       |
        |                       |
        -------------------------
        """
        draw.rectangle([
            inner_rectangle_margin, 
            inner_rectangle_margin, 
            thumbnail_width - inner_rectangle_margin, 
            inner_rectangle_margin * 2
            ], fill=colour_three)
   
        # Bottom right -> left inner rectangle
        """
        -------------------------
        |                       |
        |                       |
        |                       |
        |                       |
        |                       |
        |                       |
        =========================
        """
        draw.rectangle([
            inner_rectangle_margin, 
            thumbnail_height - inner_rectangle_margin * 2, 
            thumbnail_width - inner_rectangle_margin, 
            thumbnail_height - inner_rectangle_margin
            ], fill=colour_four)

        

        # Bottom left corner
        """
         -------------------------
         |                       |
         |                       |
         |                       |
         |                       |
         |                       |
        ||                       |
         ===----------------------
        """
        draw.polygon([
            (inner_rectangle_margin, thumbnail_height - inner_rectangle_margin * 2), 
            (inner_rectangle_margin, thumbnail_height - inner_rectangle_margin), 
            (inner_rectangle_margin * 2, thumbnail_height - inner_rectangle_margin)
            ], fill=colour_one)
        
        # Top right corner
        """
        ----------------------===
        |                       ||
        |                       ||
        |                       |
        |                       |
        |                       |
        |                       |
        -------------------------
        """
        draw.polygon([
            (thumbnail_width - inner_rectangle_margin * 2, inner_rectangle_margin),
            (thumbnail_width - inner_rectangle_margin, inner_rectangle_margin),
            (thumbnail_width - inner_rectangle_margin, inner_rectangle_margin * 2),
            ], fill=colour_one)
        

        # Top left corner
        """
         ===----------------------
        ||                       |
        ||                       |
         |                       |
         |                       |
         |                       |
         |                       |
         -------------------------
        """
        draw.polygon(
            [
                (inner_rectangle_margin, inner_rectangle_margin),
                (inner_rectangle_margin * 2, inner_rectangle_margin),
                (inner_rectangle_margin, inner_rectangle_margin * 2),
            ], fill=colour_one)
        

        # Bottom right corner
        """
        -------------------------
        |                       |
        |                       |
        |                       |
        |                       |
        |                       ||
        |                       ||
        ----------------------===
        """
        draw.polygon(
            [
                (thumbnail_width - inner_rectangle_margin * 2, thumbnail_height - inner_rectangle_margin),
                (thumbnail_width - inner_rectangle_margin, thumbnail_height - inner_rectangle_margin * 2),
                (thumbnail_width - inner_rectangle_margin, thumbnail_width - inner_rectangle_margin),
            ], fill=colour_one)


        # Text positioning thanks to https://stackoverflow.com/a/1970930/5522348
        text_width, text_height = draw.multiline_textsize(thumbnail_text, font=thumbnail_font)
        draw.multiline_text(
            ((thumbnail_width - text_width) / 2, (thumbnail_height - text_height) / 2 - 15), 
            thumbnail_text, colour_five, font=thumbnail_font)

        thumbnail.save(path.join(tmp_path, "{0}-{1}.{2}".format(output_filename, thumbnail_index, output_extension)), output_extension.upper())

        thumbnail_index += 1
        return thumbnail_index

combinations = permutations(palette, colour_count)
thumbnail_index = 0
print("Generating thumbnails...")
first_thumbnail_checked = True
for combination in combinations:
    thumbnail_index = generate_thumbnail(thumbnail_index, combination[0], combination[1], combination[2], combination[3], combination[4])
    print("Generated thumbnail #" + str(thumbnail_index))
    if not first_thumbnail_checked:
        first_thumbnail_checked = True
        startfile(tmp_path)
        print("Be sure ")
        contin = input("First thumbnail generated. Press ENTER/y to ? ([y]/n): ")
        
        break



# Step 6: cleanup
if path.isdir(tmp_path):
    thumbnail_dir = path.join(output_path, datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
    rename(tmp_path, thumbnail_dir)
    startfile(thumbnail_dir)