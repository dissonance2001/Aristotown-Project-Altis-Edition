from __future__ import absolute_import
from toontown.toonbase.ToontownGlobals import *

wainscottingBase = [Vec4(0.8, 0.5, 0.3, 1.0), Vec4(0.699, 0.586, 0.473, 1.0), Vec4(0.473, 0.699, 0.488, 1.0)]
wallpaperBase = [Vec4(1.0, 1.0, 0.7, 1.0),
 Vec4(0.8, 1.0, 0.7, 1.0),
 Vec4(0.4, 0.5, 0.4, 1.0),
 Vec4(0.5, 0.7, 0.6, 1.0)]
wallpaperBorderBase = [Vec4(1.0, 1.0, 0.7, 1.0),
 Vec4(0.8, 1.0, 0.7, 1.0),
 Vec4(0.4, 0.5, 0.4, 1.0),
 Vec4(0.5, 0.7, 0.6, 1.0)]
doorBase = [Vec4(1.0, 1.0, 0.7, 1.0)]
floorBase = [Vec4(0.746, 1.0, 0.477, 1.0), Vec4(1.0, 0.684, 0.477, 1.0)]
baseScheme = {'TI_wainscotting': wainscottingBase,
 'TI_wallpaper': wallpaperBase,
 'TI_wallpaper_border': wallpaperBorderBase,
 'TI_door': doorBase,
 'TI_floor': floorBase}
colors = {DonaldsDock: {'TI_wainscotting': wainscottingBase,
               'TI_wallpaper': wallpaperBase,
               'TI_wallpaper_border': wallpaperBorderBase,
               'TI_door': doorBase,
               'TI_floor': floorBase},
 ToontownCentral: {'TI_wainscotting': wainscottingBase,
                   'TI_wallpaper': wallpaperBase,
                   'TI_wallpaper_border': wallpaperBorderBase,
                   'TI_door': doorBase + [Vec4(0.8, 0.5, 0.3, 1.0)],
                   'TI_floor': floorBase},
 TheBrrrgh: baseScheme,
 MinniesMelodyland: baseScheme,
 DaisyGardens: baseScheme,
 OutdoorZone: baseScheme,
 GoofySpeedway: baseScheme,
 YeOlde: baseScheme,
 DonaldsDreamland: {'TI_wainscotting': wainscottingBase,
                    'TI_wallpaper': wallpaperBase,
                    'TI_wallpaper_border': wallpaperBorderBase,
                    'TI_door': doorBase,
                    'TI_floor': floorBase},
 Tutorial: {'TI_wainscotting': wainscottingBase,
            'TI_wallpaper': wallpaperBase,
            'TI_wallpaper_border': wallpaperBorderBase,
            'TI_door': doorBase + [Vec4(0.8, 0.5, 0.3, 1.0)],
            'TI_floor': floorBase},
 Toonseltown: {'TI_wainscotting': [Vec4(0.666, 0.733, 0.835, 1.0), Vec4(0.423, 0.572, 0.796, 1.0)],
                'TI_wallpaper': [Vec4(0.219, 0.831, 0.831, 1.0), Vec4(0.24, 0.76, 0.89, 1.0), Vec4(0.9, 0.9, 0.9, 1.0), Vec4(0.25, 0.64, 0.91, 1.0)],
                'TI_wallpaper_border': wallpaperBorderBase,
                'TI_door': doorBase + [Vec4(0.8, 0.5, 0.3, 1.0)],
                'TI_floor': [Vec4(0.25, 0.64, 0.91, 1.0), Vec4(0.9, 0.9, 0.9, 1.0), Vec4(0.38, 0.63, 1.0, 1.0)]},
 MyEstate: baseScheme}
