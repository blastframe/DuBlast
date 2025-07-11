import os
import bpy
from bpy.types import Panel, Menu
from bl_ui.utils import PresetPanel

class DUBLAST_MT_presets(Menu):
    bl_label = 'Playblast Presets'
    preset_subdir = 'playblast'
    preset_operator = 'script.execute_preset'
    draw = Menu.draw_preset

class DUBLAST_PT_Playblast_presets(PresetPanel, Panel):
    bl_label = "Playblast Presets"
    preset_subdir = "playblast"
    preset_operator = "script.execute_preset"
    preset_add_operator = "render.playblast_preset_add"

class DUBLAST_PT_Playblast_Settings( Panel ):
    bl_label = "Playblast"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    def draw_header_preset(self, _context):
        DUBLAST_PT_Playblast_presets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        playblast_settings = bpy.context.scene.playblast
        rows = layout.row(align=False)
        rows.operator('render.playblast', text="Playblast", icon= 'FILE_MOVIE')
        row = rows.row(align=True)
        row.prop(playblast_settings, 'increment', icon="LINENUMBERS_ON", toggle=True)
        row.prop(playblast_settings, 'use_stamp', icon="INFO", toggle=True)
        row.prop(playblast_settings, 'include_annotations', icon="STROKE", toggle=True)

class DUBLAST_PT_Scene( Panel ):
    bl_label = ""
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "DUBLAST_PT_Playblast_Settings"

    def draw_header(self,context):
        self.layout.label(text="Scene", icon="SCENE_DATA")

    def draw(self, context):
        layout = self.layout
        #layout.use_property_split = False
        layout.use_property_decorate = False  # No animation.
        # Add settings for the current scene
        playblast_settings = bpy.context.scene.playblast
        
        col = layout.column(align=False)
        col.use_property_split = True
        col.prop( playblast_settings, "use_camera") #, icon="VIEW_CAMERA"
        col.prop( playblast_settings, "use_scene_frame_range")  #, icon="PREVIEW_RANGE"
        layout.separator()

        if not playblast_settings.use_scene_frame_range:
            layout = self.layout
            layout.use_property_split = True
            col = layout.column(align=True)
            col.prop(playblast_settings, "frame_start", text="Frame Start")
            col.prop(playblast_settings, "frame_end", text="End")
            col.prop(playblast_settings, "frame_step", text="Step")

class DUBLAST_PT_Shading( Panel ):
    bl_label = ""
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "DUBLAST_PT_Playblast_Settings"

    def draw_header(self,context):
        self.layout.label(text="Shading", icon="SHADING_TEXTURE")

    def draw_solid_shading(self, layout, playblast_settings):
        layout.use_property_split = False
        layout.label(text='Lighting')
        layout.prop( playblast_settings, "light", expand=True )
        col = layout.column()
        col.label(text='Color')
        col.grid_flow(columns=3, align=True).prop(playblast_settings, "color_type", expand=True)
        if playblast_settings.color_type == 'SINGLE':
            col.row().prop(playblast_settings, "single_color")

    def draw_wireframe_shading(self, layout, playblast_settings):
        layout.use_property_split = False
        col = layout.column()
        col.label(text='Color')
        col.grid_flow(columns=3, align=True).prop(playblast_settings, "wireframe_color_type", expand=True)

    def draw_background(self, layout, playblast_settings):
        col = layout.column()
        col.use_property_split = False
        col.label(text='Background')
        col.row().prop( playblast_settings, "background_type", expand=True )
        if playblast_settings.background_type == 'VIEWPORT':
            col.row().prop(playblast_settings, "background_color")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False  # No animation.
        # Add settings for the current scene
        playblast_settings = bpy.context.scene.playblast

        layout.use_property_split = False
        layout.label(text='Viewport Shading')
        layout.prop( playblast_settings, "shading", expand=True )
        if playblast_settings.shading == "SOLID":
            self.draw_solid_shading(layout,playblast_settings)
            self.draw_background(layout,playblast_settings)
        elif playblast_settings.shading == 'WIREFRAME':
            self.draw_wireframe_shading(layout,playblast_settings)
            self.draw_background(layout,playblast_settings)
            

class DUBLAST_PT_Output( Panel ):
    bl_label = ""
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_parent_id = "DUBLAST_PT_Playblast_Settings"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self,context):
        self.layout.label(text="Output", icon="OUTPUT")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        # Add settings for the current scene
        playblast_settings = bpy.context.scene.playblast

        layout.prop( playblast_settings, "resolution_percentage", slider = True )
        layout.prop( playblast_settings, "file_format" )
        if playblast_settings.file_format == 'PNG':
            layout.prop( playblast_settings, "color_mode" )
            layout.prop( playblast_settings, "compression", slider = True )
        else:
            layout.prop( playblast_settings, "color_mode_no_alpha" )
            layout.prop( playblast_settings, "quality", slider = True )

        #layout.use_property_split = False
        layout.prop(playblast_settings, "use_scene_path")
        if not playblast_settings.use_scene_path:
            col = layout.column()
            col.prop( playblast_settings, "filepath" )
            col.prop( playblast_settings, "use_scene_name")

class DUBLAST_PT_Metadata( Panel ):
    bl_label = ""
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_parent_id = "DUBLAST_PT_Playblast_Settings"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self,context):
        self.layout.label(text="Metadata", icon="INFO")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        playblast_settings = bpy.context.scene.playblast
        
        layout.prop( playblast_settings, "auto_size_stamp_font" )
        row = layout.row()
        if not playblast_settings.auto_size_stamp_font:
            row.prop( playblast_settings, "font_size" )

        layout.prop( playblast_settings, "stamp_foreground" )
        layout.prop( playblast_settings, "stamp_background" )

        layout.separator()

        if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 90:
            col = layout.column(heading="Include")
        else:
            col = layout

        metadata = [
            "use_stamp_camera",
            "use_stamp_date",
            "use_stamp_filename",
            "use_stamp_frame",
            "use_stamp_frame_range",
            "use_stamp_hostname",
            "use_stamp_lens",
            "use_stamp_marker",
            "use_stamp_memory",
            "use_stamp_render_time",
            "use_stamp_scene",
            "use_stamp_time",
            "use_stamp_note",
        ]

        row = None
        cf = layout.column_flow(columns=2, align=False)
        for m in metadata:
            cf.enabled = playblast_settings.use_stamp 
            cf.prop( playblast_settings, m )
            if m == "use_stamp_note" and playblast_settings.use_stamp_note == True:
                cf.enabled = playblast_settings.use_stamp
                cf.prop( playblast_settings, "stamp_note_text" )

classes = (
    DUBLAST_MT_presets,
    DUBLAST_PT_Playblast_presets,
    DUBLAST_PT_Playblast_Settings,
    DUBLAST_PT_Scene,
    DUBLAST_PT_Shading,
    DUBLAST_PT_Output,
    DUBLAST_PT_Metadata,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Save default presets!
    preset_path = os.path.join(
        bpy.utils.resource_path('USER'),
        "scripts", "presets", "playblast"
        )

    if not os.path.isdir(preset_path):
        os.makedirs(preset_path)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)