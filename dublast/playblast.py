import os
from datetime import datetime
import bpy
from bpy.types import Operator
from bl_operators.presets import AddPresetBase
from bpy.app import version
from dublast.dublf.window import popup_camera_view

class DUBLAST_OT_playblast_preset_add( AddPresetBase, Operator ):
    """Renders and plays an animation playblast."""
    bl_idname = "render.playblast_preset_add"
    bl_label = "Add Playblast Preset"
    bl_description = "Add or remove a playblast preset"
    preset_menu = 'DUBLAST_MT_presets'

    # Common variable used for all preset values
    preset_defines = [ 'playblast = bpy.context.scene.playblast' ]

    # Properties to store in the preset
    preset_values = [
                        'playblast.increment',
                        'playblast.use_stamp',
                        'playblast.include_annotations',
                        'playblast.use_camera',
                        'playblast.use_scene_frame_range',
                        'playblast.frame_start',
                        'playblast.frame_end',
                        'playblast.frame_step',
                        'playblast.filepath',
                        'playblast.use_scene_name',
                        'playblast.use_scene_path',
                        'playblast.resolution_percentage',
                        'playblast.file_format',
                        'playblast.color_mode',
                        'playblast.color_mode_no_alpha',
                        'playblast.compression',
                        'playblast.quality',
                        'playblast.auto_size_stamp_font',
                        'playblast.font_size',
                        'playblast.use_stamp_date',
                        'playblast.use_stamp_time',
                        'playblast.use_stamp_render_time',
                        'playblast.use_stamp_frame',
                        'playblast.use_stamp_frame_range',
                        'playblast.use_stamp_memory',
                        'playblast.use_stamp_hostname',
                        'playblast.use_stamp_camera',
                        'playblast.use_stamp_lens',
                        'playblast.use_stamp_scene',
                        'playblast.use_stamp_marker',
                        'playblast.use_stamp_filename',
                        'playblast.use_stamp_note',
                        'playblast.stamp_foreground',
                        'playblast.stamp_background',
                        'playblast.stamp_note_text',
                        'playblast.shading',
                        'playblast.light',
                        'playblast.color_type',
                        'playblast.single_color',
                        'playblast.background_type',
                        'playblast.background_color',
                    ]

    # Directory to store the presets
    preset_subdir = 'playblast'

    remove_active = True

class DUBLAST_OT_playblast( Operator ):
    """Renders and plays an animation playblast."""
    bl_idname = "render.playblast"
    bl_label = "Playblast"
    bl_description = "Render and play an animation playblast"
    bl_option = {'REGISTER'}

    overwrite: bpy.props.BoolProperty(default = True)

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):

        # Check for updates
        bpy.ops.dublast.updatebox('INVOKE_DEFAULT', discreet = True)
        
        scene = context.scene
        playblast = scene.playblast
        render = scene.render

        # Setup Annotations (convert to grease pencil)
        annotationsObj = None
        annotationsData = scene.grease_pencil
        # Blender 2.x : we need to convert annotations to actual grease pencil
        if playblast.include_annotations and version[0] < 3 and annotationsData:
                # Create object and add to scene
                annotationsObj = bpy.data.objects.new("Annotations", annotationsData)
                scene.collection.objects.link(annotationsObj)
                annotationsObj.show_in_front = True
                annotationsData = annotationsObj.data
                annotationsData.stroke_thickness_space = 'SCREENSPACE'
                for layer in annotationsData.layers:
                    if version[0] >= 0 and version[1] >= 90:
                        layer.use_lights = False
                    layer.tint_color = layer.channel_color
                    layer.tint_factor = 1.0
                    thickness = annotationsObj.grease_pencil_modifiers.new("Thickness", 'GP_THICK')
                    thickness.normalize_thickness = True
                    thickness.thickness = layer.thickness
                    thickness.layer = layer.info
        # Blender 3.x : annotations are visible by default, we need to hide them
        annotationLayersVisibility = []
        if not playblast.include_annotations and version[0] >= 3 and annotationsData:
            for layer in annotationsData.layers:
                annotationLayersVisibility.append(layer.annotation_hide)
                layer.annotation_hide = True

        # Keep previous values
        resolution_percentage = render.resolution_percentage
        resolution_x = render.resolution_x
        resolution_y = render.resolution_y
        frame_start = scene.frame_start
        frame_end = scene.frame_end
        frame_step = scene.frame_step
        filepath = render.filepath
        file_format = render.image_settings.file_format
        color_mode = render.image_settings.color_mode
        quality = render.image_settings.quality
        compression = render.image_settings.compression
        use_stamp = render.use_stamp
        stamp_font_size = render.stamp_font_size
        stamp_foreground = render.stamp_foreground
        stamp_background = render.stamp_background
        color_depth = render.image_settings.color_depth

        use_stamp_date = render.use_stamp_date
        use_stamp_render_time = render.use_stamp_render_time
        use_stamp_time = render.use_stamp_time
        use_stamp_frame = render.use_stamp_frame
        use_stamp_frame_range = render.use_stamp_frame_range
        use_stamp_memory = render.use_stamp_memory
        use_stamp_hostname = render.use_stamp_hostname
        use_stamp_camera = render.use_stamp_camera
        use_stamp_lens = render.use_stamp_lens
        use_stamp_scene = render.use_stamp_scene
        use_stamp_marker = render.use_stamp_marker
        use_stamp_filename = render.use_stamp_filename
        use_stamp_note = render.use_stamp_note
        stamp_note_text = render.stamp_note_text

        scformat = render.ffmpeg.format
        codec = render.ffmpeg.codec
        constant_rate_factor = render.ffmpeg.constant_rate_factor
        gopsize = render.ffmpeg.gopsize
        audio_codec = render.ffmpeg.audio_codec
        audio_bitrate = render.ffmpeg.audio_bitrate
        ffmpeg_preset = render.ffmpeg.ffmpeg_preset 

        # Set playblast settings
        render.resolution_percentage = 100
        render.resolution_x = int( playblast.resolution_percentage / 100 * render.resolution_x )
        render.resolution_y = int( playblast.resolution_percentage / 100 * render.resolution_y )
        if render.resolution_x % 4 != 0:
            render.resolution_x = render.resolution_x - (render.resolution_x % 4)
        if render.resolution_y % 4 != 0:
            render.resolution_y = render.resolution_y - (render.resolution_y % 4)

        if not playblast.use_scene_frame_range:
            scene.frame_start = playblast.frame_start
            scene.frame_end = playblast.frame_end
            scene.frame_step = playblast.frame_step

        blend_filepath = bpy.data.filepath
        blend_dir = os.path.dirname(blend_filepath)
        blend_file = bpy.path.basename(blend_filepath)
        blend_name = os.path.splitext(blend_file)[0]

        if playblast.use_scene_path and not blend_filepath == "":
            playblast.filepath = blend_dir + "/"
            playblast.use_scene_name = True
        if playblast.filepath == "":
            playblast.filepath = render.filepath
        
        if playblast.use_scene_name:
            if not scene.name == "Scene" or blend_name == "":
                name = scene.name + "_"
            else:
                name = blend_name + "_"
            if not playblast.filepath.endswith("/") and not playblast.filepath.endswith("\\"):
                playblast.filepath = playblast.filepath + "/"
            render.filepath = playblast.filepath + name
        else:
            render.filepath = playblast.filepath

        if playblast.increment == True or not self.overwrite:
            # Let's just add the date in the name
            render.filepath = render.filepath + datetime.now().isoformat(sep=' ', timespec='seconds').replace(':', '-') + '_'
            
           
        if playblast.file_format == 'MP4':
            render.image_settings.file_format = 'FFMPEG'
            render.ffmpeg.format = 'MPEG4'
            render.ffmpeg.codec = 'H264'
            if playblast.quality < 17:
                render.ffmpeg.constant_rate_factor = 'LOWEST'
            elif playblast.quality < 33:
                render.ffmpeg.constant_rate_factor = 'VERYLOW'
            elif playblast.quality < 50:
                render.ffmpeg.constant_rate_factor = 'LOW'
            elif playblast.quality < 67:
                render.ffmpeg.constant_rate_factor = 'MEDIUM'
            elif playblast.quality < 85:
                render.ffmpeg.constant_rate_factor = 'HIGH'
            elif playblast.quality < 100:
                render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
            else:
                render.ffmpeg.constant_rate_factor = 'LOSSLESS'
            render.ffmpeg.ffmpeg_preset = 'REALTIME'
            render.ffmpeg.gopsize = 1
            render.ffmpeg.audio_codec = 'AAC'
            render.ffmpeg.audio_bitrate = 128
        else:
            render.image_settings.file_format = playblast.file_format
        if playblast.file_format == 'PNG':
            render.image_settings.color_mode = playblast.color_mode
        else:
            render.image_settings.color_mode = playblast.color_mode_no_alpha
        render.image_settings.quality = playblast.quality
        render.image_settings.compression = playblast.compression

        render.use_stamp = playblast.use_stamp

        if playblast.auto_size_stamp_font == True:
            render.stamp_font_size = int( render.stamp_font_size * playblast.resolution_percentage / 100 )
        else:
            render.stamp_font_size = playblast.font_size

        render.stamp_foreground = playblast.stamp_foreground
        render.stamp_background = playblast.stamp_background

        render.use_stamp_date = playblast.use_stamp_date
        render.use_stamp_render_time = playblast.use_stamp_render_time
        render.use_stamp_time = playblast.use_stamp_time
        render.use_stamp_frame = playblast.use_stamp_frame
        render.use_stamp_frame_range = playblast.use_stamp_frame_range
        render.use_stamp_memory = playblast.use_stamp_memory
        render.use_stamp_hostname = playblast.use_stamp_hostname
        render.use_stamp_camera = playblast.use_stamp_camera
        render.use_stamp_lens = playblast.use_stamp_lens
        render.use_stamp_scene = playblast.use_stamp_scene
        render.use_stamp_marker = playblast.use_stamp_marker
        render.use_stamp_filename = playblast.use_stamp_filename
        render.use_stamp_note = playblast.use_stamp_note
        render.stamp_note_text = playblast.stamp_note_text
        spaces_shading = list()

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        s = {
                            "shading":space.shading.type,
                            "light":space.shading.light,
                            "single_color":space.shading.single_color,
                            "color_type":space.shading.color_type,
                            "wireframe_color_type":space.shading.wireframe_color_type,
                            "background_type":space.shading.background_type,
                            "background_color":space.shading.background_color,
                            "view_perspective":space.region_3d.view_perspective,
                            "view_matrix":space.region_3d.view_matrix
                            }
                        spaces_shading.append((space, s))
                        if playblast.use_camera == True:
                            space.region_3d.view_perspective = 'CAMERA'
                        space.shading.type = playblast.shading
                        space.shading.light = playblast.light
                        if playblast.shading == 'SOLID':
                            space.shading.color_type = playblast.color_type
                        elif playblast.shading == 'WIREFRAME':
                            space.shading.wireframe_color_type = playblast.wireframe_color_type
                        space.shading.single_color = playblast.single_color
                        space.shading.background_type = playblast.background_type
                        space.shading.background_color = playblast.background_color
                        break

        # Render and play
        bpy.ops.render.opengl( animation = True, view_context = True )
        bpy.ops.render.play_rendered_anim( )

        for s in spaces_shading:
            space = s[0]
            s = s[1]
            if playblast.use_camera == True:
                space.region_3d.view_perspective = s["view_perspective"]
                space.region_3d.view_matrix = s["view_matrix"]
            space.shading.type = s["shading"]
            space.shading.light = s["light"]
            space.shading.single_color = s["single_color"]
            if space.shading.type == 'SOLID':
                space.shading.color_type = s["color_type"]
            elif space.shading.type == 'WIREFRAME':
                space.shading.wireframe_color_type = s["wireframe_color_type"]
            space.shading.background_color = s["background_color"]
            space.shading.background_type = s["background_type"]

        # Re-set settings
        render.resolution_percentage = resolution_percentage
        render.resolution_x = resolution_x
        render.resolution_y = resolution_y
        scene.frame_start = frame_start
        scene.frame_end = frame_end
        scene.frame_step = frame_step
        render.filepath = filepath
        render.image_settings.file_format = file_format

        render.ffmpeg.format = scformat
        render.ffmpeg.codec = codec
        render.ffmpeg.constant_rate_factor = constant_rate_factor
        render.ffmpeg.ffmpeg_preset = ffmpeg_preset 
        render.ffmpeg.gopsize = gopsize
        render.ffmpeg.audio_codec = audio_codec
        render.ffmpeg.audio_bitrate = audio_bitrate

        render.image_settings.compression = compression
        render.image_settings.color_mode = color_mode
        render.image_settings.quality = quality
        render.image_settings.color_depth = color_depth
        render.use_stamp = use_stamp
        render.stamp_font_size = stamp_font_size

        render.stamp_foreground = stamp_foreground
        render.stamp_background = stamp_background

        render.use_stamp_date = use_stamp_date
        render.use_stamp_render_time = use_stamp_render_time
        render.use_stamp_time = use_stamp_time
        render.use_stamp_frame = use_stamp_frame
        render.use_stamp_frame_range = use_stamp_frame_range
        render.use_stamp_memory = use_stamp_memory
        render.use_stamp_hostname = use_stamp_hostname
        render.use_stamp_camera = use_stamp_camera
        render.use_stamp_lens = use_stamp_lens
        render.use_stamp_scene = use_stamp_scene
        render.use_stamp_marker = use_stamp_marker
        render.use_stamp_filename = use_stamp_filename
        render.use_stamp_note = use_stamp_note
        render.stamp_note_text = stamp_note_text

        # Remove annotations
        if annotationsObj:
            bpy.data.objects.remove(annotationsObj)

        # Reset annnotation visibility
        if not playblast.include_annotations and version[0] >= 3 and annotationsData:
            for i, layer in enumerate(annotationsData.layers):
                layer.annotation_hide = annotationLayersVisibility[i]

        return {'FINISHED'}

classes = (
    DUBLAST_OT_playblast_preset_add,
    DUBLAST_OT_playblast,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)