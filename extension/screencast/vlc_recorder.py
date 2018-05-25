"""
#    QAutomate Ltd 2018. All rights reserved.
#
#    Copyright and all other rights including without limitation all intellectual property rights and title in or
#    pertaining to this material, all information contained herein, related documentation and their modifications and
#    new versions and other amendments (QAutomate Material) vest in QAutomate Ltd or its licensor's.
#    Any reproduction, transfer, distribution or storage or any other use or disclosure of QAutomate Material or part
#    thereof without the express prior written consent of QAutomate Ltd is strictly prohibited.
#
#    Distributed with QAutomate license.
#    All rights reserved, see LICENSE for details.
"""
import time

from extension.config import get_config_value
from extension.screencast import vlc


## Video recorder class
# VLC player is needed to be installed
#
# Uses VLC python bindings from vlc.py:
# http://wiki.videolan.org/Python_bindings
#
# tested with vlc 2.0.2
# Some information about recorded files:
# Running this code with different file extension:
# recorder = VlcRecorder()
# recorder.set_file(os.path.abspath(os.environ['temp'] + "/" + get_timestamp() + ".mp4"))
# recorder.start()
# time.sleep(10)
# recorder.stop()
#
# Recorded video results comparison:
#                     ogg     webm    mp4
# video_size(KB)      494     538     312
# recorded_time(sec)  5       8       9
# max_CPU_usage(%)    30      63      76
# max_mem_usage(MB)   143     267     541
class VlcRecorder:
    # video framerate
    _framerate = 24

    # strings contains information about video and audio codecs
    _ogg_codec = "vcodec=theo,vb=800,scale=1,acodec=vorb,ab=128,channels=2,samplerate=44100"
    _mp4_codec = "vcodec=h264,vb=0,scale=0,acodec=mp4a,ab=128,channels=2,samplerate=44100"
    _webm_codec = "vcodec=VP80,vb=2000,scale=0,acodec=vorb,ab=128,channels=2,samplerate=44100"

    ## Constructor
    # Initialize vlc, player objects and setting default path to file
    def __init__(self, path):
        # setting default file
        self.vlc = vlc.Instance("-I dummy")
        self.player = vlc.libvlc_media_player_new(self.vlc)
        ext = get_config_value("browser_capture_screen_cast_codec").lower()
        if ext == '' or ext not in ["ogg", "mp4", "webm"]:
            ext = "ogg"
        self.path_to_file = path

    ## Set current file
    # @param path_to_file: absolute path to file
    def set_file(self, path_to_file):
        self.path_to_file = path_to_file

    ## Get current file
    # @return: string, absilute path to file
    def get_file(self):
        return self.path_to_file

    ## Start video recording
    # Set current video file to player,
    # and start to record
    def start(self):
        #print "Start screen recording"
        self.player.set_media(self._get_media())
        self.player.play()

    ## Return boolean recording state
    # @return: True if is recording, else False
    def is_recording(self):
        return self.player.is_playing() == 1

    ## Stop video recording
    # Inside waits for timeout to record last seconds
    # and stop to record
    def stop(self):
        #print "Stop screen recording"
        codec = self._get_codec()
        if codec == VlcRecorder._mp4_codec:
            timeout = 1
        else:
            timeout = 2
        time.sleep(timeout)
        #print "Saving to file", self.get_file()
        self.player.stop()

    ## Return video codec string by file extension
    # @return: string with codec info
    def _get_codec(self):
        video_file = self.get_file()
        if video_file.lower().endswith("mp4"):
            codec = VlcRecorder._mp4_codec
        elif video_file.lower().endswith("ogg"):
            codec = VlcRecorder._ogg_codec
        else:
            codec = VlcRecorder._webm_codec
        return codec

    ## Return media object created with current file and codec
    # @return: media object
    def _get_media(self):
        video_file = self.get_file()
        codec = self._get_codec()
        media = self.vlc.media_new("screen://", ":screen-fps=%s" % self._framerate, ":sout=#transcode{%s}:file{dst=%s}" % (codec, video_file), ":sout-keep")
        return media

