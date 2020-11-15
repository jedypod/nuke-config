# # NOTE: These defaults are now set in defaults.py
# # I leave this file with everything commented out
# # as an example of how to accomplish the same thing with a tcl method.

# #---------------------------------------------------------------------------
# #       W = Total image width in pixels
# #       H = Total image height in pixels
# #       x = left edge of active region
# #       y = bottom edge of active region
# #       r = right edge of active region
# #       t = top edge of active region
# #      pa = pixel-aspect ratio (width/height of a pixel)
# #    name = the name displayed in the menus
# #
# # xyrt may be omitted to set them to 0 0 W H.
# # if xyrt are omitted, you can also omit pa and it is set to 1.0
# #---------------------------------------------------------------------------
# #              W    H   x   y    r    t   pa   name
# #---------------------------------------------------------------------------

# # Video
# add_format "854 480                      1.0   SD_480p"
# add_format "960 540                      1.0   SD_540p"
# add_format "1280  720                    1.0   HD_720p"
# add_format "1920 1080                    1.0   HD_1080p"
# add_format "3840 2160                    1.0   UHD_4k"

# # Film
# add_format "2048 1556                    1.0   2K_Super_35_full-ap"
# add_format "1828 1556                    2.0   2K_Cinemascope"
# add_format "2048 1080                    1.0   2K_DCP"

# add_format "4096 3112                    1.0   4K_Super_35_full-ap"
# add_format "3656 3112                    2.0   4K_Cinemascope"
# add_format "4096 2160                    1.0   4K_DCP"

# # Square
# add_format "256  256                     1.0   square_256"
# add_format "512  512                     1.0   square_512"
# add_format "1024 1024                    1.0   square_1K"
# add_format "2048 2048                    1.0   square_2K"
# add_format "4096 4096                    1.0   square_4K"

# # Latlong
# add_format "1024 512                     1.0   latlong_1k"
# add_format "2048 1024                    1.0   latlong_2k"
# add_format "4096 2048                    1.0   latlong_4k"
# add_format "8192 4096                    1.0   latlong_8k"
# add_format "10240 5120                   1.0   latlong_10k"
# add_format "12288 6144                   1.0   latlong_12k"
# add_format "16384 8192                   1.0   latlong_16k"


# # Set the default full and proxy formats:
# knob_default root.format "1920 1080 1"
# knob_default root.proxy_format "960 540 1"
