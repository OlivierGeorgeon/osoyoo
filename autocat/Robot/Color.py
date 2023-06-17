import colorsys
from ..Memory.EgocentricMemory.Experience import FLOOR_COLORS


def category_color(color_sensor):
    """Categorize the color from the sensor measure"""
    # https://www.w3.org/wiki/CSS/Properties/color/keywords
    # https://www.colorspire.com/rgb-color-wheel/
    # https://www.pinterest.fr/pin/521713938063708448/
    hsv = colorsys.rgb_to_hsv(float(color_sensor['red']) / 256.0, float(color_sensor['green']) / 256.0,
                              float(color_sensor['blue']) / 256.0)

    # 'red'  # Hue = 0 -- 0.0, 0.0, sat 0.59
    color_index = 1
    if hsv[0] < 0.98:
        if hsv[0] > 0.9:
            # 'deepPink'  # Hue = 0.94, 0.94, 0.94, 0.96, 0.95, sat 0.54
            color_index = 7
        elif hsv[0] > 0.6:  # 0.7  # 0.6
            # 'orchid'  # Hue = 0.83 -- 0.66, sat 0.25
            color_index = 6
        elif hsv[0] > 0.5:
            # 'deepSkyBlue'  # Hue = 0.59 -- 0.57, 0.58 -- 0.58, sat 0.86
            color_index = 5
        elif hsv[0] > 0.28:
            # 'limeGreen'  # Hue = 0.38, 0.35, 0.37 -- 0.29, 0.33, 0.29, 0.33 -- 0.36, sat 0.68
            color_index = 4
        elif hsv[0] > 0.175:
            # 'gold'  # Hue = 0.25, 0.26 -- 0.20 -- 0.20, 0.20, 0.184, 0.2 -- 0.24, sat 0.68
            color_index = 3
        elif hsv[0] > 0.05:
            # 'orange'
            color_index = 2

    # Floor in lyon
    if (hsv[0] < 0.6) and (hsv[1] < 0.3):  # 0.45  // violet (0.66,0.25,0.398) in DOLL
        #if hsv[0] < 0.7:  # 0.6
            # Not saturate, not violet
            # Floor. Saturation: Table bureau 0.16. Sol bureau 0.17, table olivier 0.21, sol olivier: 0.4, 0.33
        color_index = 0
        #else:
            # Not saturate but violet
        #    color = 'orchid'  # Hue = 0.75, 0.66 -- 0.66, Saturation = 0.24, 0.34, 0.2 -- 0.2
        #    color_index = 6

    # Yoga mat at DOLL (0.16,0.34,0.42)
    # if hsv[2] < 0.43:
    #     color_index = 0

    # Rug at DOLL
    if (0.2 < hsv[0] < 0.45) and (hsv[1] < 0.45):
        color_index = 0

    print("Color: ", hsv, FLOOR_COLORS[color_index])
    return color_index
