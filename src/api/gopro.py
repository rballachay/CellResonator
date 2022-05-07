from goprocam import GoProCamera

"""
Documentation

Note that using the gopro in this fashion requires the Gopro to be connected to the wifi network. 

For information on pairing gopro to wifi, see here:
https://gopro.com/help/articles/block/How-to-Pair-the-Camera-with-the-GoPro-App?fbclid=IwAR2d_xqmcIdRE1XMKMUuP83p0I0H9O-bS8PllFN6mZSfeLkVtMXvpmqPZKs#HERO7_HERO8_MAX



"""


def gopro_stream():
    gpCam = GoProCamera.GoPro()
    return "udp://127.0.0.1:10000"
