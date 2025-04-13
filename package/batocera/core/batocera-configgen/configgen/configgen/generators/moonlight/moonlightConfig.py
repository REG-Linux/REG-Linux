#!/usr/bin/env python

import batoceraFiles
import os
import shutil
from settings.unixSettings import UnixSettings

moonlightCustom = batoceraFiles.CONF + '/moonlight'
moonlightConfigFile = moonlightCustom + '/moonlight.conf'
moonlightStagingConfigFile = moonlightCustom + '/staging/moonlight.conf'
moonlightGamelist = moonlightCustom + '/gamelist.txt'
moonlightMapping = dict()
moonlightMapping[1] = moonlightCustom + '/mappingP1.conf'
moonlightMapping[2] = moonlightCustom + '/mappingP2.conf'
moonlightMapping[3] = moonlightCustom + '/mappingP3.conf'
moonlightMapping[4] = moonlightCustom + '/mappingP4.conf'

def generateMoonlightConfig(system):

    moonlightStagingConfigFile = moonlightStagingConfigFile
    if not os.path.exists(moonlightCustom + '/staging'):
        os.makedirs(moonlightCustom + '/staging')

    # If user made config file exists, copy to staging directory for use
    if os.path.exists(moonlightConfigFile):
        shutil.copy(moonlightConfigFile, moonlightStagingConfigFile)
    else:
        # truncate existing config and create new one
        f = open(moonlightStagingConfigFile, "w").close()

        moonlightConfig = UnixSettings(moonlightStagingConfigFile, separator=' ')

        # resolution
        if system.isOptSet('moonlight_resolution'):
            if system.config["moonlight_resolution"] == "0":
                moonlightConfig.save('width', '1280')
                moonlightConfig.save('height', '720')
            elif system.config["moonlight_resolution"] == "1":
                moonlightConfig.save('width', '1920')
                moonlightConfig.save('height', '1080')
            elif system.config["moonlight_resolution"] == "2":
                moonlightConfig.save('width', '3840')
                moonlightConfig.save('height', '2160')
        else:
            moonlightConfig.save('width', '1280')
            moonlightConfig.save('height', '720')

        # rotate
        if system.isOptSet('moonlight_rotate'):
            moonlightConfig.save('rotate', system.config["moonlight_rotate"])
        else:
            moonlightConfig.save('rotate', '0')

        # framerate
        if system.isOptSet('moonlight_framerate'):
            if system.config["moonlight_framerate"] == "0":
                moonlightConfig.save('fps', '30')
            elif system.config["moonlight_framerate"] == "1":
                moonlightConfig.save('fps', '60')
            elif system.config["moonlight_framerate"] == "2":
                moonlightConfig.save('fps', '120')
        else:
            moonlightConfig.save('fps', '60')

        # bitrate
        if system.isOptSet('moonlight_bitrate'):
            if system.config["moonlight_bitrate"] == "0":
                moonlightConfig.save('bitrate', '5000')
            elif system.config["moonlight_bitrate"] == "1":
                moonlightConfig.save('bitrate', '10000')
            elif system.config["moonlight_bitrate"] == "2":
                moonlightConfig.save('bitrate', '20000')
            elif system.config["moonlight_bitrate"] == "3":
                moonlightConfig.save('bitrate', '50000')
        else:
            moonlightConfig.save('bitrate', '-1') #-1 sets Moonlight default

        # codec
        if system.isOptSet('moonlight_codec'):
            moonlightConfig.save('codec',system.config["moonlight_codec"])
        else:
            moonlightConfig.save('codec', 'auto')

        # sops (Streaming Optimal Playable Settings)
        if system.isOptSet('moonlight_sops'):
            moonlightConfig.save('sops', system.config["moonlight_sops"].lower())
        else:
            moonlightConfig.save('sops', 'true')

        # quit remote app on exit
        if system.isOptSet('moonlight_quitapp'):
            moonlightConfig.save('quitappafter', system.config["moonlight_quitapp"].lower())
        else:
            moonlightConfig.save('quitappafter', 'false')

        # view only
        if system.isOptSet('moonlight_viewonly'):
            moonlightConfig.save('viewonly', system.config["moonlight_viewonly"].lower())
        else:
            moonlightConfig.save('viewonly', 'false')

        # platform - we only select sdl (best compatibility)
        # required for controllers to work
        moonlightConfig.save('platform', 'sdl')

        ## Directory to store encryption keys
        moonlightConfig.save('keydir', moonlightCustom + '/keydir')

        # lan or wan streaming - ideally lan
        if system.isOptSet('moonlight_remote'):
            moonlightConfig.save('remote', system.config["moonlight_remote"])
        else:
            moonlightConfig.save('remote', 'no')

        ## Enable 5.1/7.1 surround sound
        if system.isOptSet('moonlight_surround'):
            moonlightConfig.save('surround', system.config["moonlight_surround"])
        else:
            moonlightConfig.save('#surround', '5.1')

        moonlightConfig.write()
