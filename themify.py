import sys
from datetime import datetime
import requests
from PIL import Image
import random
from rasterfont import *

DEBUG = False

color_lookup = {'Desktop': (255, 0, 255, 255),
                'Inactive Border': (170, 0, 85, 255),
                'Inactive Title Bar': (255, 0, 0, 255),
                'Inactive Title Bar Text': (43, 94, 145, 255),
                'Active Border': (255, 255, 0, 255),
                'Active Title Bar': (124, 123, 39, 255),
                'Active Title Bar Text': (170, 85, 170, 255),
                'Menu Bar': (14, 54, 255, 255),
                'Menu Text': (0, 170, 85, 255),
                'Disabled Text': (190, 189, 189, 255),
                'Highlighted Text': (255, 255, 255, 255),
                'Highlight': (159, 195, 177, 255), 
                'Application Workspace': (0, 255, 0, 255),
                'Window Background': (146, 12, 208, 255),
                'Window Text': (165, 242, 255, 255),
                'Button Highlight': (170, 170, 85, 255),
                'Button Face': (134, 138, 142, 255),
                'Button Shadow': (248, 194, 194, 255),
                'Button Text': (0, 0, 0, 255),
                'Scrollbars': (0, 255, 255, 255)
}


def hex_to_rgb(hexcolor):
    """
    Given a hex color, return its RGB value equivalent as a tuple
    """
    hexcolor = hexcolor.strip('#')
    rgb = tuple(int(hexcolor[i:i+2], 16) for i in (0, 2 ,4))
    return rgb


def get_color_palette(palette_id=None):
    """
    Get a random color palette using the Colour Lovers API. 
    Simplify the result a bit, and convert hex to rgb.
    """
    if palette_id:
        url ='https://www.colourlovers.com/api/palette/%s?format=json' % palette_id
    else:
        url = 'https://www.colourlovers.com/api/palettes/random?format=json'
    
    r = requests.get(url).json()
    
    # Can't accept palettes with only one color
    while len( set(r[0]['colors']) ) == 1:
    
        if palette_id:
            return None
        else:
            # Pick a new random palette
            r = requests.get(url).json() 

    palette_dict = {
                    'title': r[0]['title'], 
                    'count': len(r[0]['colors']),
                    'id': r[0]['id'],
                    'username': r[0]['userName']
                    }

    colors = []
    for hex_color in r[0]['colors']:
        
        rgb = hex_to_rgb(hex_color)        

        color_dict = { 'hex': hex_color, 'rgb': rgb}
        colors.append(color_dict)
    
    palette_dict['colors'] = colors

    # Create a filename safe version of title
    palette_dict['filename'] = "".join([c for c in palette_dict['title'] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    palette_dict['filename'] = palette_dict['filename'].replace(' ', '_')
    palette_dict['filename'] = palette_dict['filename'].lower()

    # Add attribution to image




    if DEBUG:
        print palette_dict['id']

    return palette_dict


def make_theme(palette):
    """
    Given a dictionary of a color palette, return a dicitonary
    of theme color settings. 
    """

    fields = ['Desktop', 'Inactive Border', 'Inactive Title Bar', 'Inactive Title Bar Text', 'Active Border', 'Active Title Bar', 'Active Title Bar Text', 'Menu Bar', 'Menu Text', 'Disabled Text', 'Highlighted Text', 'Highlight', 'Application Workspace', 'Window Background', 'Window Text', 'Button Highlight', 'Button Face', 'Button Shadow', 'Button Text', 'Scrollbars']

    theme_dict = {}

    for field in fields:
        color_choice = random.choice(palette['colors'])
        theme_dict[field] = color_choice['rgb']

    while theme_dict['Active Title Bar'] == theme_dict['Active Title Bar Text']:
        theme_dict['Active Title Bar Text'] = random.choice(palette['colors'])['rgb']

    while theme_dict['Active Title Bar'] == theme_dict['Inactive Title Bar']:
        theme_dict['Inactive Title Bar'] = random.choice(palette['colors'])['rgb']

    while theme_dict['Inactive Title Bar'] == theme_dict['Inactive Title Bar Text']:
        theme_dict['Inactive Title Bar Text'] = random.choice(palette['colors'])['rgb']

    while theme_dict['Menu Bar'] == theme_dict['Menu Text']:
        theme_dict['Menu Text'] = random.choice(palette['colors'])['rgb']

    while theme_dict['Desktop'] == theme_dict['Highlight']:
        theme_dict['Highlight'] = random.choice(palette['colors'])['rgb']

    while theme_dict['Highlight'] == theme_dict['Highlighted Text']:
        theme_dict['Highlighted Text'] = random.choice(palette['colors'])['rgb']


    while theme_dict['Button Face'] == theme_dict['Button Text']:
        theme_dict['Button Text'] = random.choice(palette['colors'])['rgb']

    while theme_dict['Window Background'] == theme_dict['Window Text']:
        theme_dict['Window Text'] = random.choice(palette['colors'])['rgb']

    while theme_dict['Desktop'] == theme_dict['Disabled Text']:
        theme_dict['Disabled Text'] = random.choice(palette['colors'])['rgb']

    filename = palette['filename']
    title = palette['title']
    # title = '%s by %s' % (palette['title'], palette['username'] )

    attribution_dict = {'title': palette['title'], 'filename': palette['filename'], 'id': palette['id'], 'username': palette['username']}

    return theme_dict, attribution_dict

def theme_screenshot(theme_dict, title, filename, username):
    """
    Creates actual image. Loops through each pixel in
    template and does a find/replace, based on supplied theme dictionary.
    """
    img = Image.open('template.gif')
    img = img.convert("RGBA")

    # Add title to select bar in image
    img = print_to_image(img, title, 40, 103, 'system_spritesheet.png')

    pixdata = img.load()

    # Clean the background noise, if color != white, then set to black.
    # change with your color
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            for k, v in color_lookup.items():
                if pixdata[x, y] == v:
                    pixdata[x, y] = theme_dict[k]
                    break

    if DEBUG:
        path = "generated/%s.png" % filename
        img.show()
    else:
        path = "tweetme"

    img.save("%s.png" % path, "PNG")
    return img


def generate_image(palette_id=None):

    pal = get_color_palette(palette_id)
    theme_dict, attribution_dict = make_theme(pal)
    img = theme_screenshot(theme_dict, attribution_dict['title'], attribution_dict['filename'], attribution_dict['username'])

    if not DEBUG:
        with open("attribution.txt", "a") as attribution_log:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            palette_link = 'https://www.colourlovers.com/palette/%s/' % attribution_dict['id']
            attrib_text = '%s %s by %s %s' % (timestamp, attribution_dict['title'], attribution_dict['username'], palette_link ) 
            attribution_log.write(attrib_text + '\n')






