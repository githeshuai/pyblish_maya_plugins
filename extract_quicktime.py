import os
import contextlib

import pyblish.api
import pyblish_magenta.plugin
from pyblish_magenta.vendor import capture

from maya import cmds


@pyblish.api.log
class ExtractQuicktime(pyblish_magenta.api.Extractor):
    """Extract review instances as a quicktime

    Arguments:
        startFrame (float): Start frame of output
        endFrame (float): End frame of output
        width (int): Width of output in pixels
        height (int): Height of output in pixels
        format (str): Which format to use for the given filename,
            defaults to "qt"
        compression (str): Which compression to use with the given
            format, defaults to "h264"
        offScreen (bool): Capture off-screen
        maintainAspectRatio (bool): Whether or not to modify height for width
            in order to preserve the current aspect ratio.
        show (str): Space-separated list of which node-types to show,
            e.g. "nurbsCurves polymeshes"

    """

    families = ["review"]
    hosts = ["maya"]
    optional = True
    label = "Quicktime"

    def process(self, instance):
        self.log.info("Extracting capture..")

        camera = instance[0]

        current_min_time = cmds.playbackOptions(minTime=True, query=True)
        current_max_time = cmds.playbackOptions(maxTime=True, query=True)

        default_width = cmds.getAttr("defaultResolution.width")
        default_height = cmds.getAttr("defaultResolution.height")

        width = instance.data('width') or default_width
        height = instance.data('height') or default_height
        start_frame = instance.data('startFrame') or current_min_time
        end_frame = instance.data('endFrame') or current_max_time

        format = instance.data('format') or 'qt'
        compression = instance.data('compression') or 'h264'
        off_screen = instance.data('offScreen', False)
        maintain_aspect_ratio = instance.data('maintainAspectRatio', True)

        cam_opts = capture.CameraOptions()

        # Set viewport settings
        view_opts = capture.ViewportOptions()
        view_opts.displayAppearance = "smoothShaded"

        if 'show' in instance.data():
            for nodetype in instance.data('show').split():
                self.log.info("Overriding show: %s" % nodetype)
                if hasattr(view_opts, nodetype):
                    setattr(view_opts, nodetype, True)
                else:
                    self.log.warning("Specified node-type in 'show' not "
                                     "recognised: %s" % nodetype)
        else:
            view_opts.polymeshes = True
            view_opts.nurbsSurfaces = True

        # Ensure name of camera is valid
        path = self.temp_dir(instance)

        if format == 'image':
            # Append sub-directory for image-sequence
            path = os.path.join(path, camera)
        else:
            path = os.path.join(path, instance.name + ".mov")

        self.log.info("Outputting to %s" % path)

        with maintained_time():
            output = capture.capture(
                camera=camera,
                width=width,
                height=height,
                filename=path,
                start_frame=start_frame,
                end_frame=end_frame,
                format=format,
                viewer=False,
                compression=compression,
                off_screen=off_screen,
                maintain_aspect_ratio=maintain_aspect_ratio,
                viewport_options=view_opts,
                camera_options=cam_opts)

        instance.set_data("reviewOutput", output)


@contextlib.contextmanager
def maintained_time():
    ct = cmds.currentTime(query=True)
    try:
        yield
    finally:
        cmds.currentTime(ct, edit=True)
