def scale_rgb(color, scale):
    cr = int(color[0] * scale)
    if cr > 255:
        r = 255
    elif cr < 0:
        r = 0
    else:
        r = cr

    cg = int(color[1] * scale)
    if cg > 255:
        g = 255
    elif cg < 0:
        g = 0
    else:
        g = cg

    cb = int(color[2] * scale)
    if cb > 255:
        b = 255
    elif cb < 0:
        b = 0
    else:
        b = cb

    return (r, g, b)