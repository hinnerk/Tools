#!/usr/bin/env python3.5

import sys, math, os

def print_error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def industry_to_pixel(name):
    resolutions = {
        "4k": (4096, 2160),     # cinematic 4k
        "uhd": (3840, 2160),    # consumer "4k"
        "8k": (7680, 4320),
        "hd": (1280, 720),
        "full hd": (1920, 1080),
    }
    # add aliases:
    resolutions["uhd-2"] = resolutions["8k"]
    resolutions["1080p"] = resolutions["full hd"]
    resolutions["1080i"] = resolutions["full hd"]
    resolutions["1080"] = resolutions["full hd"]
    resolutions["720p"] = resolutions["hd"]
    resolutions["720"] = resolutions["hd"]

    return resolutions[name.lower()]
    

def calc_dpi(phy_size, pixel_w, pixel_h=None):
    
    # look ups and assertions
    if isinstance(pixel_w, str) and pixel_h is None:
        pixel_w, pixel_h = industry_to_pixel(pixel_w)

    assert isinstance(pixel_w, (int, float))
    assert isinstance(pixel_h, (int, float))
    assert isinstance(phy_size, (int, float))
    
    # calculate the value
    virt_size = math.sqrt(pixel_h**2 + pixel_w**2)
    return virt_size / phy_size, pixel_w, pixel_h


if __name__ == '__main__':
    phys = float(sys.argv[1])
    if len(sys.argv) == 3:
        x = sys.argv[2]
        y = None
    elif len(sys.argv) == 4:
        x = float(sys.argv[2])
        y = float(sys.argv[3])
    else:
        print("INSERT HELP TEXT HERE.")
        sys.exit(23)
    try:
        dpi, x, y = calc_dpi(phys, x, y)
    except:
        print("Uuups, ERROR!")
        sys.exit(100)
    else:
        print(phys, "inch @", x, "x", y, "pixel means a resolution of", round(dpi), "dpi.")
        sys.exit(0)