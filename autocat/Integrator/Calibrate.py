import circle_fit as cf


def compass_calibration(points):
    """Return the tuple that represents the offset of the center of the circle defined by the points"""
    # print(repr(points))
    if points.shape[0] > 2:
        # Find the center of the circle made by the compass points
        xc, yc, r, sigma = cf.taubinSVD(points)
        # print("Fit circle", xc, yc, r, sigma)
        if 130 < r < 550:  # 400
            return round(xc), round(yc)
        else:
            print("Compass calibration failed. Radius out of bound: " + str(round(r)))
    else:
        print("Compass calibration failed. Insufficient points: " + str(points.shape[0]))
    return None
