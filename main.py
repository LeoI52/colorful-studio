"""
@author : Léo IMBERT
@created : 21/12/2024
@updated : 17/04/2025

current_canvas.itemconfigure(current_canvas.find_closest(current_canvas.canvasx(event.x), current_canvas.canvasy(event.y)), fill="#FFFFFF")
"""

#? Importations
from tkinter.filedialog import askopenfilename
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk
import time
import sys

#? Tooltip Class
class CTkToolTip(tk.Toplevel):

    def __init__(self, widget:any=None, message:str=None, delay:float=0.2, follow:bool=True, x_offset:int=+20, y_offset:int=+10, bg_color:str=None, corner_radius:int=10, border_width:int=0, border_color:str=None, alpha:float=0.95, padding:tuple=(10, 2), **message_kwargs):

        super().__init__()

        self.widget = widget

        self.withdraw()

        # Disable ToolTip's title bar
        self.overrideredirect(True)

        if sys.platform.startswith("win"):
            self.transparent_color = self.widget._apply_appearance_mode(
                ctk.ThemeManager.theme["CTkToplevel"]["fg_color"])
            self.attributes("-transparentcolor", self.transparent_color)
            self.transient()
        elif sys.platform.startswith("darwin"):
            self.transparent_color = 'systemTransparent'
            self.attributes("-transparent", True)
            self.transient(self.master)
        else:
            self.transparent_color = '#000001'
            corner_radius = 0
            self.transient()

        self.resizable(width=True, height=True)

        # Make the background transparent
        self.config(background=self.transparent_color)

        # StringVar instance for msg string
        self.messageVar = ctk.StringVar()
        self.message = message
        self.messageVar.set(self.message)

        self.delay = delay
        self.follow = follow
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.corner_radius = corner_radius
        self.alpha = alpha
        self.border_width = border_width
        self.padding = padding
        self.bg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"] if bg_color is None else bg_color
        self.border_color = border_color
        self.disable = False

        # visibility status of the ToolTip inside|outside|visible
        self.status = "outside"
        self.last_moved = 0
        self.attributes('-alpha', self.alpha)

        if sys.platform.startswith("win"):
            if self.widget._apply_appearance_mode(self.bg_color) == self.transparent_color:
                self.transparent_color = "#000001"
                self.config(background=self.transparent_color)
                self.attributes("-transparentcolor", self.transparent_color)

        # Add the message widget inside the tooltip
        self.transparent_frame = tk.Frame(self, bg=self.transparent_color)
        self.transparent_frame.pack(padx=0, pady=0, fill="both", expand=True)

        self.frame = ctk.CTkFrame(self.transparent_frame, bg_color=self.transparent_color,
                                            corner_radius=self.corner_radius,
                                            border_width=self.border_width, fg_color=self.bg_color,
                                            border_color=self.border_color)
        self.frame.pack(padx=0, pady=0, fill="both", expand=True)

        self.message_label = ctk.CTkLabel(self.frame, textvariable=self.messageVar, **message_kwargs)
        self.message_label.pack(fill="both", padx=self.padding[0] + self.border_width,
                                pady=self.padding[1] + self.border_width, expand=True)

        if self.widget.winfo_name() != "tk":
            if self.frame.cget("fg_color") == self.widget.cget("bg_color"):
                if not bg_color:
                    self._top_fg_color = self.frame._apply_appearance_mode(
                        ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"])
                    if self._top_fg_color != self.transparent_color:
                        self.frame.configure(fg_color=self._top_fg_color)

        # Add bindings to the widget without overriding the existing ones
        self.widget.bind("<Enter>", self.on_enter, add="+")
        self.widget.bind("<Leave>", self.on_leave, add="+")
        self.widget.bind("<Motion>", self.on_enter, add="+")
        self.widget.bind("<B1-Motion>", self.on_enter, add="+")
        self.widget.bind("<Destroy>", lambda _: self.hide(), add="+")

    def show(self) -> None:
        """
        Enable the widget.
        """
        self.disable = False

    def on_enter(self, event) -> None:
        """
        Processes motion within the widget including entering and moving.
        """

        if self.disable:
            return
        self.last_moved = time.time()

        # Set the status as inside for the very first time
        if self.status == "outside":
            self.status = "inside"

        # If the follow flag is not set, motion within the widget will make the ToolTip dissapear
        if not self.follow:
            self.status = "inside"
            self.withdraw()

        # Calculate available space on the right side of the widget relative to the screen
        root_width = self.winfo_screenwidth()
        widget_x = event.x_root
        space_on_right = root_width - widget_x

        # Calculate the width of the tooltip's text based on the length of the message string
        text_width = self.message_label.winfo_reqwidth()

        # Calculate the offset based on available space and text width to avoid going off-screen on the right side
        offset_x = self.x_offset
        if space_on_right < text_width + 20:  # Adjust the threshold as needed
            offset_x = -text_width - 20  # Negative offset when space is limited on the right side

        # Offsets the ToolTip using the coordinates od an event as an origin
        self.geometry(f"+{event.x_root + offset_x}+{event.y_root + self.y_offset}")

        # Time is in integer: milliseconds
        self.after(int(self.delay * 1000), self._show)

    def on_leave(self, event=None) -> None:
        """
        Hides the ToolTip temporarily.
        """

        if self.disable: return
        self.status = "outside"
        self.withdraw()

    def _show(self) -> None:
        """
        Displays the ToolTip.
        """

        if not self.widget.winfo_exists():
            self.hide()
            self.destroy()

        if self.status == "inside" and time.time() - self.last_moved >= self.delay:
            self.status = "visible"
            self.deiconify()

    def hide(self) -> None:
        """
        Disable the widget from appearing.
        """
        if not self.winfo_exists():
            return
        self.withdraw()
        self.disable = True

    def is_disabled(self) -> None:
        """
        Return the window state
        """
        return self.disable

    def get(self) -> None:
        """
        Returns the text on the tooltip.
        """
        return self.messageVar.get()

    def configure(self, message:str=None, delay:float=None, bg_color:str=None, **kwargs):
        """
        Set new message or configure the label parameters.
        """
        if delay: self.delay = delay
        if bg_color: self.frame.configure(fg_color=bg_color)

        self.messageVar.set(message)
        self.message_label.configure(**kwargs)

#? Tools Enumerators
CURSOR = 0
MOVE = 1
HAND = 2
ZOOM = 3
LINE = 4
SQUARE = 5
CIRCLE = 6
POLYGON = 7
PENCIL = 8
ERASER = 9
TEXT = 10
IMAGE = 11

#? App Class
class App(ctk.CTk):

    def __init__(self):
        #? Style Variables
        self.title_name = "Colorful Studio"
        self.font_name = "Ubuntu"
        self.theme_number = 0
        self.themes = {0:["#1E1E2E", "#353552", "#E63946", "#FF4F5A", "#FFFFFF"],
                       1:["#2B3A42", "#3D5A6C", "#4CAF50", "#66BB6A", "#F1F8E9"],
                       2:["#0B0C10", "#1F2833", "#66FCF1", "#45A29E", "#0B0C10"]}
        self.background_color = self.themes.get(self.theme_number)[0]
        self.highlight_color = self.themes.get(self.theme_number)[1]
        self.action_color = self.themes.get(self.theme_number)[2]
        self.hover_action_color = self.themes.get(self.theme_number)[3]
        self.text_color = self.themes.get(self.theme_number)[4]

        #? Window Configuration
        super().__init__(self.background_color)
        self.title(self.title_name)
        self.geometry("1270x650+0+0")

        #? Variables
        self.selected_tool = ctk.IntVar(value=CURSOR)
        self.pressed_special_keys = set()
        self.crtl_z_items = []
        self.current_line_number = "line_0"
        self.canvas_number = 0
        self.selected_canvas_item = None
        self.images = []
        self.current_image_index = 0
        self.polygon_points = []
        self.line_points = []
        self.anchors_dict = {
            "Center": "center",
            "Top left": "nw",
            "Top right": "ne",
            "Bottom left": "sw",
            "Bottom right": "se",
            "Top": "n",
            "Bottom": "s",
            "Left": "w",
            "Right": "e"
        }
        self.patterns_dict = {
            "Filled": "",
            "Thick": "gray75",
            "Semi thick": "gray50",
            "Semi thin": "gray25",
            "Thin": "gray12",
            "Flowers": "@./assets/flowers_pattern.xbm",
            "Silk": "@./assets/silk_pattern.xbm",
            "Floor": "@./assets/floor_pattern.xbm",
            "Stars": "@./assets/stars_pattern.xbm",
            "Circles": "@./assets/circles_pattern.xbm",
            "Waves": "@./assets/waves_pattern.xbm"
        }

        #? Images
        self.cursor_icon = ImageTk.PhotoImage(image=Image.open("./assets/cursor_icon.png").resize((40, 40)))
        self.move_icon = ImageTk.PhotoImage(image=Image.open("./assets/move_icon.png").resize((40, 40)))
        self.zoom_icon = ImageTk.PhotoImage(image=Image.open("./assets/zoom_icon.png").resize((40, 40)))
        self.hand_icon = ImageTk.PhotoImage(image=Image.open("./assets/hand_icon.png").resize((40, 40)))
        self.line_icon = ImageTk.PhotoImage(image=Image.open("./assets/line_icon.png").resize((40, 40)))
        self.square_icon = ImageTk.PhotoImage(image=Image.open("./assets/square_icon.png").resize((40, 40)))
        self.circle_icon = ImageTk.PhotoImage(image=Image.open("./assets/circle_icon.png").resize((40, 40)))
        self.polygon_icon = ImageTk.PhotoImage(image=Image.open("./assets/polygon_icon.png").resize((40, 40)))
        self.pencil_icon = ImageTk.PhotoImage(image=Image.open("./assets/pencil_icon.png").resize((40, 40)))
        self.eraser_icon = ImageTk.PhotoImage(image=Image.open("./assets/eraser_icon.png").resize((40, 40)))
        self.text_icon = ImageTk.PhotoImage(image=Image.open("./assets/text_icon.png").resize((40, 40)))
        self.image_icon = ImageTk.PhotoImage(image=Image.open("./assets/image_icon.png").resize((40, 40)))

        #? Main Widgets
        self.frame_tools_selection = ctk.CTkFrame(self, 300, 150, fg_color=self.highlight_color)
        self.tabview_canvas = ctk.CTkTabview(self, 650, 600, fg_color=self.highlight_color, segmented_button_fg_color=self.highlight_color, segmented_button_selected_color=self.action_color, segmented_button_selected_hover_color=self.hover_action_color, segmented_button_unselected_color=self.highlight_color, segmented_button_unselected_hover_color=self.hover_action_color, text_color=self.text_color, corner_radius=10)
        self.tabview_settings = ctk.CTkTabview(self, 300, 600, fg_color=self.highlight_color, segmented_button_fg_color=self.highlight_color, segmented_button_selected_color=self.action_color, segmented_button_selected_hover_color=self.hover_action_color, segmented_button_unselected_color=self.highlight_color, segmented_button_unselected_hover_color=self.hover_action_color, text_color=self.text_color, corner_radius=10)
        self.tabview_canvas._segmented_button.configure(font=(self.font_name, 14))
        self.tabview_settings._segmented_button.configure(font=(self.font_name, 14))
        self.frame_tools_selection.place(x=5, y=38)
        self.tabview_canvas.place(x=638, y=20, anchor="n")
        self.tabview_settings.place(x=1272, y=20, anchor="ne")

        #? Frame Tools Selection Widgets
        self.radiobutton_cursor = tk.Radiobutton(self.frame_tools_selection, image=self.cursor_icon, indicatoron=False, variable=self.selected_tool, value=CURSOR, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options())
        self.radiobutton_move = tk.Radiobutton(self.frame_tools_selection, image=self.move_icon, indicatoron=False, variable=self.selected_tool, value=MOVE, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options())
        self.radiobutton_zoom = tk.Radiobutton(self.frame_tools_selection, image=self.zoom_icon, indicatoron=False, variable=self.selected_tool, value=ZOOM, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options())
        self.radiobutton_hand = tk.Radiobutton(self.frame_tools_selection, image=self.hand_icon, indicatoron=False, variable=self.selected_tool, value=HAND, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options())
        self.radiobutton_line = tk.Radiobutton(self.frame_tools_selection, image=self.line_icon, indicatoron=False, variable=self.selected_tool, value=LINE, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options(self.frame_line_options))
        self.radiobutton_square = tk.Radiobutton(self.frame_tools_selection, image=self.square_icon, indicatoron=False, variable=self.selected_tool, value=SQUARE, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options(self.frame_square_options))
        self.radiobutton_circle = tk.Radiobutton(self.frame_tools_selection, image=self.circle_icon, indicatoron=False, variable=self.selected_tool, value=CIRCLE, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options(self.frame_circle_options))
        self.radiobutton_polygon = tk.Radiobutton(self.frame_tools_selection, image=self.polygon_icon, indicatoron=False, variable=self.selected_tool, value=POLYGON, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options(self.frame_polygon_options))
        self.radiobutton_pencil = tk.Radiobutton(self.frame_tools_selection, image=self.pencil_icon, indicatoron=False, variable=self.selected_tool, value=PENCIL, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options(self.frame_pencil_options))
        self.radiobutton_eraser = tk.Radiobutton(self.frame_tools_selection, image=self.eraser_icon, indicatoron=False, variable=self.selected_tool, value=ERASER, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options())
        self.radiobutton_text = tk.Radiobutton(self.frame_tools_selection, image=self.text_icon, indicatoron=False, variable=self.selected_tool, value=TEXT, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options(self.frame_text_options))
        self.radiobutton_image = tk.Radiobutton(self.frame_tools_selection, image=self.image_icon, indicatoron=False, variable=self.selected_tool, value=IMAGE, background=self.action_color, selectcolor=self.hover_action_color, command=lambda: self.place_options(self.frame_image_options))
        self.radiobutton_cursor.place(x=10, y=10)
        self.radiobutton_move.place(x=60, y=10)
        self.radiobutton_zoom.place(x=110, y=10)
        self.radiobutton_hand.place(x=160, y=10)
        self.radiobutton_line.place(x=10, y=60)
        self.radiobutton_square.place(x=60, y=60)
        self.radiobutton_circle.place(x=110, y=60)
        self.radiobutton_polygon.place(x=160, y=60)
        self.radiobutton_pencil.place(x=10, y=110)
        self.radiobutton_eraser.place(x=60, y=110)
        self.radiobutton_text.place(x=110, y=110)
        self.radiobutton_image.place(x=160, y=110)

        #? Line Options Widgets
        self.frame_line_options = ctk.CTkFrame(self, 300, 280, fg_color=self.highlight_color)
        ctk.CTkLabel(self.frame_line_options, text="Line Options", font=(self.font_name, 20), text_color=self.text_color).place(relx=0.5, y=10, anchor="n")
        ctk.CTkLabel(self.frame_line_options, text="Line thickness :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=40)
        ctk.CTkLabel(self.frame_line_options, text="Line color :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=80)
        ctk.CTkLabel(self.frame_line_options, text="Line style :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=120)
        ctk.CTkLabel(self.frame_line_options, text="Line head :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=160)
        ctk.CTkLabel(self.frame_line_options, text="Line pattern :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=200)
        self.slider_line_thickness = ctk.CTkSlider(self.frame_line_options, width=150, from_=1, to=20, number_of_steps=19, button_color=self.action_color, button_hover_color=self.hover_action_color, progress_color=self.action_color, fg_color=self.background_color, command=lambda value: self.tooltip_line_thickness.configure(message=str(int(value))))
        self.tooltip_line_thickness = CTkToolTip(self.slider_line_thickness, message="5", bg_color=self.background_color, corner_radius=10)
        self.button_line_color = ctk.CTkButton(self.frame_line_options, 30, 30, 100, text="", fg_color="#000000", hover_color="#000000", command=lambda: self.change_button_color(self.button_line_color))
        self.option_menu_line_style = ctk.CTkOptionMenu(self.frame_line_options, values=["Normal", "Dashed"], font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.option_menu_line_head = ctk.CTkOptionMenu(self.frame_line_options, values=["Normal", "Arrow", "Double arrow"], font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.option_menu_line_pattern = ctk.CTkOptionMenu(self.frame_line_options, values=list(self.patterns_dict.keys()), font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.switch_line_smooth = ctk.CTkSwitch(self.frame_line_options, text="Smooth", font=(self.font_name, 14), text_color=self.text_color, fg_color=self.background_color, progress_color=self.action_color, switch_height=20, switch_width=40)
        self.slider_line_thickness.set(5)
        self.slider_line_thickness.place(x=110, y=47)
        self.button_line_color.place(x=90, y=80)
        self.option_menu_line_style.place(x=90, y=120)
        self.option_menu_line_head.place(x=90, y=160)
        self.option_menu_line_pattern.place(x=100, y=200)
        self.switch_line_smooth.place(x=10, y=240)

        #? Square Options Widgets
        self.frame_square_options = ctk.CTkFrame(self, 300, 320, fg_color=self.highlight_color)
        ctk.CTkLabel(self.frame_square_options, text="Square Options", font=(self.font_name, 20), text_color=self.text_color).place(relx=0.5, y=10, anchor="n")
        ctk.CTkLabel(self.frame_square_options, text="Outline thickness :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=40)
        ctk.CTkLabel(self.frame_square_options, text="Outline color :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=80)
        ctk.CTkLabel(self.frame_square_options, text="Outline style :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=120)
        ctk.CTkLabel(self.frame_square_options, text="Fill color :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=200)
        ctk.CTkLabel(self.frame_square_options, text="Fill pattern :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=240)
        self.slider_square_thickness = ctk.CTkSlider(self.frame_square_options, width=150, from_=0, to=20, number_of_steps=20, button_color=self.action_color, button_hover_color=self.hover_action_color, progress_color=self.action_color, fg_color=self.background_color, command=lambda value: self.tooltip_square_thickness.configure(message=str(int(value))))
        self.tooltip_square_thickness = CTkToolTip(self.slider_square_thickness, message="5", bg_color=self.background_color, corner_radius=10)
        self.button_square_outline_color = ctk.CTkButton(self.frame_square_options, 30, 30, 100, text="", fg_color="#000000", hover_color="#000000", command=lambda: self.change_button_color(self.button_square_outline_color))
        self.option_menu_square_outline_style = ctk.CTkOptionMenu(self.frame_square_options, values=["Normal", "Dashed"], font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.switch_square_fill = ctk.CTkSwitch(self.frame_square_options, text="Fill", font=(self.font_name, 14), text_color=self.text_color, fg_color=self.background_color, progress_color=self.action_color, switch_height=20, switch_width=40)
        self.button_square_fill_color = ctk.CTkButton(self.frame_square_options, 30, 30, 100, text="", fg_color="#000000", hover_color="#000000", command=lambda: self.change_button_color(self.button_square_fill_color))
        self.option_menu_square_pattern = ctk.CTkOptionMenu(self.frame_square_options, values=list(self.patterns_dict.keys()), font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.switch_square_keep_ratio = ctk.CTkSwitch(self.frame_square_options, text="Keep 1:1 aspect ratio", font=(self.font_name, 14), text_color=self.text_color, fg_color=self.background_color, progress_color=self.action_color, switch_height=20, switch_width=40)
        self.slider_square_thickness.set(5)
        self.slider_square_thickness.place(x=125, y=47)
        self.button_square_outline_color.place(x=100, y=80)
        self.option_menu_square_outline_style.place(x=100, y=120)
        self.switch_square_fill.place(x=10, y=160)
        self.button_square_fill_color.place(x=75, y=200)
        self.option_menu_square_pattern.place(x=90, y=240)
        self.switch_square_keep_ratio.place(x=10, y=280)

        #? Circle Options Widgets
        self.frame_circle_options = ctk.CTkFrame(self, 300, 280, fg_color=self.highlight_color)
        ctk.CTkLabel(self.frame_circle_options, text="Circle Options", font=(self.font_name, 20), text_color=self.text_color).place(relx=0.5, y=10, anchor="n")
        ctk.CTkLabel(self.frame_circle_options, text="Outline thickness :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=40)
        ctk.CTkLabel(self.frame_circle_options, text="Outline color :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=80)
        ctk.CTkLabel(self.frame_circle_options, text="Outline style :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=120)
        ctk.CTkLabel(self.frame_circle_options, text="Fill color :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=200)
        self.slider_circle_thickness = ctk.CTkSlider(self.frame_circle_options, width=150, from_=0, to=20, number_of_steps=20, button_color=self.action_color, button_hover_color=self.hover_action_color, progress_color=self.action_color, fg_color=self.background_color, command=lambda value: self.tooltip_circle_thickness.configure(message=str(int(value))))
        self.tooltip_circle_thickness = CTkToolTip(self.slider_circle_thickness, message="5", bg_color=self.background_color, corner_radius=10)
        self.button_circle_outline_color = ctk.CTkButton(self.frame_circle_options, 30, 30, 100, text="", fg_color="#000000", hover_color="#000000", command=lambda: self.change_button_color(self.button_circle_outline_color))
        self.option_menu_circle_outline_style = ctk.CTkOptionMenu(self.frame_circle_options, values=["Normal", "Dashed"], font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.switch_circle_fill = ctk.CTkSwitch(self.frame_circle_options, text="Fill", font=(self.font_name, 14), text_color=self.text_color, fg_color=self.background_color, progress_color=self.action_color, switch_height=20, switch_width=40)
        self.button_circle_fill_color = ctk.CTkButton(self.frame_circle_options, 30, 30, 100, text="", fg_color="#000000", hover_color="#000000", command=lambda: self.change_button_color(self.button_circle_fill_color))
        self.switch_circle_keep_ratio = ctk.CTkSwitch(self.frame_circle_options, text="Keep 1:1 aspect ratio", font=(self.font_name, 14), text_color=self.text_color, fg_color=self.background_color, progress_color=self.action_color, switch_height=20, switch_width=40)
        self.slider_circle_thickness.set(5)
        self.slider_circle_thickness.place(x=125, y=47)
        self.button_circle_outline_color.place(x=100, y=80)
        self.option_menu_circle_outline_style.place(x=100, y=120)
        self.switch_circle_fill.place(x=10, y=160)
        self.button_circle_fill_color.place(x=75, y=200)
        self.switch_circle_keep_ratio.place(x=10, y=240)

        #? Polygon Options Widgets
        self.frame_polygon_options = ctk.CTkFrame(self, 300, 320, fg_color=self.highlight_color)
        ctk.CTkLabel(self.frame_polygon_options, text="Polygon Options", font=(self.font_name, 20), text_color=self.text_color).place(relx=0.5, y=10, anchor="n")
        ctk.CTkLabel(self.frame_polygon_options, text="Outline thickness :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=40)
        ctk.CTkLabel(self.frame_polygon_options, text="Outline color :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=80)
        ctk.CTkLabel(self.frame_polygon_options, text="Outline style :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=120)
        ctk.CTkLabel(self.frame_polygon_options, text="Fill color :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=200)
        ctk.CTkLabel(self.frame_polygon_options, text="Fill pattern :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=240)
        self.slider_polygon_thickness = ctk.CTkSlider(self.frame_polygon_options, width=150, from_=0, to=20, number_of_steps=20, button_color=self.action_color, button_hover_color=self.hover_action_color, progress_color=self.action_color, fg_color=self.background_color, command=lambda value: self.tooltip_polygon_thickness.configure(message=str(int(value))))
        self.tooltip_polygon_thickness = CTkToolTip(self.slider_polygon_thickness, message="5", bg_color=self.background_color, corner_radius=10)
        self.button_polygon_outline_color = ctk.CTkButton(self.frame_polygon_options, 30, 30, 100, text="", fg_color="#000000", hover_color="#000000", command=lambda: self.change_button_color(self.button_polygon_outline_color))
        self.option_menu_polygon_outline_style = ctk.CTkOptionMenu(self.frame_polygon_options, values=["Normal", "Dashed"], font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.switch_polygon_fill = ctk.CTkSwitch(self.frame_polygon_options, text="Fill", font=(self.font_name, 14), text_color=self.text_color, fg_color=self.background_color, progress_color=self.action_color, switch_height=20, switch_width=40)
        self.button_polygon_fill_color = ctk.CTkButton(self.frame_polygon_options, 30, 30, 100, text="", fg_color="#000000", hover_color="#000000", command=lambda: self.change_button_color(self.button_polygon_fill_color))
        self.option_menu_polygon_pattern = ctk.CTkOptionMenu(self.frame_polygon_options, values=list(self.patterns_dict.keys()), font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.switch_polygon_smooth = ctk.CTkSwitch(self.frame_polygon_options, text="Smooth", font=(self.font_name, 14), text_color=self.text_color, fg_color=self.background_color, progress_color=self.action_color, switch_height=20, switch_width=40)
        self.slider_polygon_thickness.set(5)
        self.slider_polygon_thickness.place(x=125, y=47)
        self.button_polygon_outline_color.place(x=100, y=80)
        self.option_menu_polygon_outline_style.place(x=100, y=120)
        self.switch_polygon_fill.place(x=10, y=160)
        self.button_polygon_fill_color.place(x=75, y=200)
        self.option_menu_polygon_pattern.place(x=90, y=240)
        self.switch_polygon_smooth.place(x=10, y=280)

        #? Pencil Options Widgets
        self.frame_pencil_options = ctk.CTkFrame(self, 300, 120, fg_color=self.highlight_color)
        ctk.CTkLabel(self.frame_pencil_options, text="Pencil Options", font=(self.font_name, 20), text_color=self.text_color).place(relx=0.5, y=10, anchor="n")
        ctk.CTkLabel(self.frame_pencil_options, text="Pencil thickness :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=40)
        ctk.CTkLabel(self.frame_pencil_options, text="Pencil color :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=80)
        self.slider_pencil_thickness = ctk.CTkSlider(self.frame_pencil_options, width=150, from_=1, to=20, number_of_steps=19, button_color=self.action_color, button_hover_color=self.hover_action_color, progress_color=self.action_color, fg_color=self.background_color, command=lambda value: self.tooltip_pencil_thickness.configure(message=str(int(value))))
        self.tooltip_pencil_thickness = CTkToolTip(self.slider_pencil_thickness, message="5", bg_color=self.background_color, corner_radius=10)
        self.button_pencil_color = ctk.CTkButton(self.frame_pencil_options, 30, 30, 100, text="", fg_color="#000000", hover_color="#000000", command=lambda: self.change_button_color(self.button_pencil_color))
        self.slider_pencil_thickness.set(5)
        self.slider_pencil_thickness.place(x=120, y=47)
        self.button_pencil_color.place(x=95, y=80)

        #? Eraser Options Widgets
        self.frame_eraser_options = ctk.CTkFrame(self, 300, 426, fg_color=self.highlight_color)
        ctk.CTkLabel(self.frame_eraser_options, text="Eraser Options", font=(self.font_name, 20), text_color=self.text_color).place(relx=0.5, y=10, anchor="n")

        #? Text Options Widgets
        self.frame_text_options = ctk.CTkFrame(self, 300, 240, fg_color=self.highlight_color)
        ctk.CTkLabel(self.frame_text_options, text="Text Options", font=(self.font_name, 20), text_color=self.text_color).place(relx=0.5, y=10, anchor="n")
        ctk.CTkLabel(self.frame_text_options, text="Text :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=40)
        ctk.CTkLabel(self.frame_text_options, text="Font :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=80)
        ctk.CTkLabel(self.frame_text_options, text="Font size :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=120)
        ctk.CTkLabel(self.frame_text_options, text="Text color :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=160)
        ctk.CTkLabel(self.frame_text_options, text="Anchor :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=200)
        self.entry_text = ctk.CTkEntry(self.frame_text_options, font=(self.font_name, 14), width=230, border_color=self.hover_action_color, fg_color=self.action_color, text_color=self.text_color)
        self.option_menu_text_font = ctk.CTkOptionMenu(self.frame_text_options, values=["Arial Black","Comic Sans MS","Cooper Black","Courier New","Rockwell","Times New Roman","Trebuchet MS","Ubuntu","Wide Latin"], font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.slider_text_size = ctk.CTkSlider(self.frame_text_options, width=200, from_=10, to=70, number_of_steps=60, button_color=self.action_color, button_hover_color=self.hover_action_color, progress_color=self.action_color, fg_color=self.background_color, command=lambda value: self.tooltip_text_size.configure(message=str(int(value))))
        self.tooltip_text_size = CTkToolTip(self.slider_text_size, message="20", bg_color=self.background_color, corner_radius=10)
        self.button_text_color = ctk.CTkButton(self.frame_text_options, 30, 30, 100, text="", fg_color="#000000", hover_color="#000000", command=lambda: self.change_button_color(self.button_text_color))
        self.option_menu_text_anchor = ctk.CTkOptionMenu(self.frame_text_options, values=list(self.anchors_dict.keys()), font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.entry_text.place(x=50, y=40)
        self.option_menu_text_font.place(x=50, y=80)
        self.slider_text_size.set(20)
        self.slider_text_size.place(x=80, y=127)
        self.button_text_color.place(x=85, y=160)
        self.option_menu_text_anchor.place(x=70, y=200)

        #? Image Options Widgets
        self.frame_image_options = ctk.CTkFrame(self, 300, 200, fg_color=self.highlight_color)
        ctk.CTkLabel(self.frame_image_options, text="Image Options", font=(self.font_name, 20), text_color=self.text_color).place(relx=0.5, y=10, anchor="n")
        ctk.CTkLabel(self.frame_image_options, text="Image width :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=40)
        ctk.CTkLabel(self.frame_image_options, text="Image height :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=80)
        ctk.CTkLabel(self.frame_image_options, text="Image path :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=120)
        ctk.CTkLabel(self.frame_image_options, text="Image anchor :", font=(self.font_name, 14), text_color=self.text_color).place(x=10, y=160)
        self.entry_image_width = ctk.CTkEntry(self.frame_image_options, font=(self.font_name, 14), width=80, border_color=self.hover_action_color, fg_color=self.action_color, text_color=self.text_color)
        self.entry_image_height = ctk.CTkEntry(self.frame_image_options, font=(self.font_name, 14), width=80, border_color=self.hover_action_color, fg_color=self.action_color, text_color=self.text_color)
        self.button_image_path = ctk.CTkButton(self.frame_image_options, text="No path", font=(self.font_name, 14), fg_color=self.action_color, hover_color=self.hover_action_color, text_color=self.text_color, command=self.change_image_path)
        self.option_menu_image_anchor = ctk.CTkOptionMenu(self.frame_image_options, values=list(self.anchors_dict.keys()), font=(self.font_name, 14), fg_color=self.action_color, button_color=self.action_color, button_hover_color=self.hover_action_color, text_color=self.text_color)
        self.entry_image_width.insert(0, "100")
        self.entry_image_height.insert(0, "100")
        self.entry_image_width.place(x=95, y=40)
        self.entry_image_height.place(x=100, y=80)
        self.button_image_path.place(x=95, y=120)
        self.option_menu_image_anchor.place(x=110, y=160)

        #? Tabview Settings Widgets
        self.tabview_settings.add("Canvas Settings")
        self.entry_canvas_name = ctk.CTkEntry(self.tabview_settings.tab("Canvas Settings"), font=(self.font_name, 14), width=170, placeholder_text="Canvas Name", border_color=self.hover_action_color, fg_color=self.action_color, text_color=self.text_color, placeholder_text_color=self.text_color)
        ctk.CTkButton(self.tabview_settings.tab("Canvas Settings"), font=(self.font_name, 14), text="Add", width=40, fg_color=self.action_color, hover_color=self.hover_action_color, text_color=self.text_color, command=self.add_canvas).place(relx=0.9, y=10, anchor="ne")
        ctk.CTkButton(self.tabview_settings.tab("Canvas Settings"), font=(self.font_name, 14), text="Delete current canvas", fg_color=self.action_color, hover_color=self.hover_action_color, text_color=self.text_color, command=self.delete_canvas).place(relx=0.5,y=50,anchor="n")
        ctk.CTkButton(self.tabview_settings.tab("Canvas Settings"), font=(self.font_name, 14), text="Change current canvas color", fg_color=self.action_color, hover_color=self.hover_action_color, text_color=self.text_color, command=self.change_canvas_color).place(relx=0.5, y=90, anchor="n")
        ctk.CTkButton(self.tabview_settings.tab("Canvas Settings"), font=(self.font_name, 14), text="Clear current canvas color", fg_color=self.action_color, hover_color=self.hover_action_color, text_color=self.text_color, command=self.clear_canvas).place(relx=0.5, y=130, anchor="n")
        ctk.CTkButton(self.tabview_settings.tab("Canvas Settings"), font=(self.font_name, 14), text="Reset current canvas view", fg_color=self.action_color, hover_color=self.hover_action_color, text_color=self.text_color, command=self.reset_canvas).place(relx=0.5, y=170, anchor="n")
        self.entry_canvas_name.place(relx=0.1, y=10)

        self.tabview_settings.add("Settings")

        #? Binding
        self.bind("<Escape>", lambda _:self.quit()) #! To remove

        self.bind("<Button-1>", self.lmb_click)
        self.bind("<Button-3>", self.rmb_click)
        self.bind("<B1-Motion>", self.lmb_motion)
        self.bind("<Motion>", self.motion)
        self.bind("<ButtonRelease-1>", self.lmb_release)
        self.bind("<ButtonRelease-3>", self.rmb_release)
        self.bind("<KeyPress>", self.key_press)
        self.bind("<KeyRelease>", self.key_release)
        self.bind("<Alt-c>", lambda _: self.radiobutton_circle.invoke())
        self.bind("<Alt-e>", lambda _: self.radiobutton_eraser.invoke())
        self.bind("<Alt-h>", lambda _: self.radiobutton_hand.invoke())
        self.bind("<Alt-l>", lambda _: self.radiobutton_line.invoke())
        self.bind("<Alt-m>", lambda _: self.radiobutton_move.invoke())
        self.bind("<Alt-p>", lambda _: self.radiobutton_pencil.invoke())
        self.bind("<Alt-s>", lambda _: self.radiobutton_square.invoke())
        self.bind("<Alt-t>", lambda _: self.radiobutton_text.invoke())
        self.bind("<Alt-z>", lambda _: self.radiobutton_zoom.invoke())
        self.bind("<Alt-Key-BackSpace>", lambda _: self.radiobutton_cursor.invoke())
        self.bind("<Control-z>", lambda _: self.crtl_z())

        self.entry_canvas_name.bind("<Return>", lambda _: self.add_canvas())
        self.entry_canvas_name.bind("<KeyRelease>", lambda _: self.cap_entry(self.entry_canvas_name, 10))
        self.entry_text.bind("<Return>", lambda _: self.focus_set())
        self.entry_image_width.bind("<Return>", lambda _: self.focus_set())
        self.entry_image_height.bind("<Return>", lambda _: self.focus_set())
        self.entry_image_width.bind("<KeyRelease>", lambda _: self.cap_entry_to_int(self.entry_image_width, 4))
        self.entry_image_height.bind("<KeyRelease>", lambda _: self.cap_entry_to_int(self.entry_image_height, 4))

        #? Mainloop
        self.mainloop()

    def lmb_click(self, event)-> None:
        if self.tabview_canvas.get() != '':
            current_canvas = self.tabview_canvas.tab(self.tabview_canvas.get()).children.get("!canvas")
            if current_canvas == event.widget:
                self.start_x, self.start_y = current_canvas.canvasx(event.x), current_canvas.canvasy(event.y)
                if self.selected_tool.get() == MOVE:
                    current_canvas.scan_mark(event.x, event.y)
                elif self.selected_tool.get() == ZOOM:
                    factor = 1.1
                    current_canvas.scale("all", self.start_x, self.start_y, factor, factor)
                elif self.selected_tool.get() == HAND:
                    selected = current_canvas.find_overlapping(self.start_x - 1, self.start_y - 1, self.start_x + 1, self.start_y + 1)
                    if selected and not any([True for tag in current_canvas.gettags(selected[-1]) if "line" in tag]):
                        self.selected_canvas_item = selected[-1]
                    elif selected:
                        self.selected_canvas_item = current_canvas.find_withtag(current_canvas.gettags(selected[-1]))
                    else:
                        self.selected_canvas_item = None
                elif self.selected_tool.get() == LINE:
                    self.line_points.append(self.start_x)
                    self.line_points.append(self.start_y)
                elif self.selected_tool.get() == POLYGON:
                    self.polygon_points.append(self.start_x)
                    self.polygon_points.append(self.start_y)
                    self.draw_polygon(current_canvas, self.polygon_points, True)
                elif self.selected_tool.get() == ERASER:
                    selected = current_canvas.find_overlapping(self.start_x - 1, self.start_y - 1, self.start_x + 1, self.start_y + 1)
                    if selected and not any([True for tag in current_canvas.gettags(selected[-1]) if "line" in tag]):
                        current_canvas.delete(selected[-1])
                    elif selected:
                        current_canvas.delete(current_canvas.gettags(selected[-1])[0])
                elif self.selected_tool.get() == TEXT:
                    self.draw_text(current_canvas)
                elif self.selected_tool.get() == IMAGE:
                    self.draw_image(current_canvas)

    def rmb_click(self, event)-> None:
        if self.tabview_canvas.get() != '':
            current_canvas = self.tabview_canvas.tab(self.tabview_canvas.get()).children.get("!canvas")
            if current_canvas == event.widget:
                self.start_x, self.start_y = current_canvas.canvasx(event.x), current_canvas.canvasy(event.y)
                if self.selected_tool.get() == ZOOM:
                    factor = 0.9
                    current_canvas.scale("all", self.start_x, self.start_y, factor, factor)

    def lmb_motion(self, event)-> None:
        if self.tabview_canvas.get() != '':
            current_canvas = self.tabview_canvas.tab(self.tabview_canvas.get()).children.get("!canvas")
            if current_canvas == event.widget:
                x, y = current_canvas.canvasx(event.x), current_canvas.canvasy(event.y)
                current_canvas.delete("delete")
                if self.selected_tool.get() == MOVE:
                    current_canvas.scan_dragto(event.x, event.y, gain=1)
                elif self.selected_tool.get() == HAND:
                    if self.selected_canvas_item != -1 and isinstance(self.selected_canvas_item, int):
                        dx, dy = x - self.start_x, y - self.start_y
                        current_canvas.move(self.selected_canvas_item, dx, dy)
                        self.lmb_click(event)
                    elif isinstance(self.selected_canvas_item, (tuple, list)):
                        dx, dy = x - self.start_x, y - self.start_y
                        for item in self.selected_canvas_item:
                            current_canvas.move(item, dx, dy)
                        self.lmb_click(event)
                elif self.selected_tool.get() == SQUARE:
                    self.draw_square(current_canvas, x, y, True)
                elif self.selected_tool.get() == CIRCLE:
                    self.draw_circle(current_canvas, x, y, True)
                elif self.selected_tool.get() == PENCIL:
                    current_canvas.create_line((self.start_x, self.start_y, x, y), width=self.slider_pencil_thickness.get(), capstyle="round", smooth=True, fill=self.button_pencil_color.cget("fg_color"), tags=(self.current_line_number))
                    self.lmb_click(event)

    def lmb_release(self, event)-> None:
        if self.tabview_canvas.get() != '':
            current_canvas = self.tabview_canvas.tab(self.tabview_canvas.get()).children.get("!canvas")
            if current_canvas == event.widget:
                x, y = current_canvas.canvasx(event.x), current_canvas.canvasy(event.y)
                if self.selected_tool.get() == SQUARE:
                    self.draw_square(current_canvas, x, y)
                elif self.selected_tool.get() == CIRCLE:
                    self.draw_circle(current_canvas, x, y)
                elif self.selected_tool.get() == PENCIL:
                    self.crtl_z_items.append(self.current_line_number)
                    self.current_line_number = "line_" + str(int(self.current_line_number[-1]) + 1)

    def rmb_release(self, event)-> None:
        if self.tabview_canvas.get() != '':
            current_canvas = self.tabview_canvas.tab(self.tabview_canvas.get()).children.get("!canvas")
            if current_canvas == event.widget:
                x, y = current_canvas.canvasx(event.x), current_canvas.canvasy(event.y)
                current_canvas.delete("delete")
                if self.selected_tool.get() == LINE:
                    self.draw_line(current_canvas, self.line_points + [x, y])
                    self.line_points = []
                if self.selected_tool.get() == POLYGON:
                    self.draw_polygon(current_canvas, self.polygon_points + [x, y])
                    self.polygon_points = []

    def motion(self, event)-> None:
        if self.tabview_canvas.get() != '':
            current_canvas = self.tabview_canvas.tab(self.tabview_canvas.get()).children.get("!canvas")
            if current_canvas == event.widget:
                x, y = current_canvas.canvasx(event.x), current_canvas.canvasy(event.y)
                current_canvas.delete("delete")
                if self.selected_tool.get() == LINE and len(self.line_points) > 0:
                    self.draw_line(current_canvas, self.line_points + [x, y], True)
                elif self.selected_tool.get() == POLYGON and len(self.polygon_points) > 0:
                    self.draw_polygon(current_canvas, self.polygon_points + [x, y], True)

    def draw_line(self, canvas, points:list, delete:bool=False)-> None:
        dash = (3, 5) if self.option_menu_line_style.get() == "Dashed" else ()
        capstyle = "projecting" if self.option_menu_line_style.get() == "Dashed" else "round"
        arrow = "last" if self.option_menu_line_head.get() == "Arrow" else "both" if self.option_menu_line_head.get() == "Double arrow" else ""
        pattern = self.patterns_dict.get(self.option_menu_line_pattern.get())
        tag = ("delete") if delete else ("")
        l = canvas.create_line(points, fill=self.button_line_color.cget("fg_color"), width=self.slider_line_thickness.get(), capstyle=capstyle, smooth=self.switch_line_smooth.get(), dash=dash, arrow=arrow, arrowshape=(12, 15, 4.5), stipple=pattern, offset=tk.NW, tags=tag)
        if not delete:
            self.crtl_z_items.append(l)

    def draw_square(self, canvas, x:int, y:int, delete:bool=False)-> None:
        dash = (3, 5) if self.option_menu_square_outline_style.get() == "Dashed" else ()
        fill = self.button_square_fill_color.cget("fg_color") if self.switch_square_fill.get() else ""
        pattern = self.patterns_dict.get(self.option_menu_square_pattern.get())
        tag = ("delete") if delete else ("")
        if self.switch_square_keep_ratio.get():
            width = max(abs(x - self.start_x), abs(y - self.start_y))
            x = self.start_x + width if x > self.start_x else self.start_x - width
            y = self.start_y + width if y > self.start_y else self.start_y - width
        r = canvas.create_rectangle((self.start_x, self.start_y, x, y), outline=self.button_square_outline_color.cget("fg_color"), width=self.slider_square_thickness.get(), dash=dash, fill=fill, stipple=pattern, offset=tk.NW, tags=tag)
        if not delete:
            self.crtl_z_items.append(r)

    def draw_circle(self, canvas, x:int, y:int, delete:bool=False)-> None:
        dash = (3, 5) if self.option_menu_circle_outline_style.get() == "Dashed" else ()
        fill = self.button_circle_fill_color.cget("fg_color") if self.switch_circle_fill.get() else ""
        tag = ("delete") if delete else ("")
        if self.switch_circle_keep_ratio.get():
            width = max(abs(x - self.start_x), abs(y - self.start_y))
            x = self.start_x + width if x > self.start_x else self.start_x - width
            y = self.start_y + width if y > self.start_y else self.start_y - width
        c = canvas.create_oval(self.start_x, self.start_y, x, y, outline=self.button_circle_outline_color.cget("fg_color"), width=self.slider_circle_thickness.get(), dash=dash, fill=fill, tags=tag)
        if not delete:
            self.crtl_z_items.append(c)

    def draw_polygon(self, canvas, points:list, delete:bool=False)-> None:
        dash = (3, 5) if self.option_menu_polygon_outline_style.get() == "Dashed" else ()
        fill = self.button_polygon_fill_color.cget("fg_color") if self.switch_polygon_fill.get() else ""
        pattern = self.patterns_dict.get(self.option_menu_polygon_pattern.get())
        tag = ("delete") if delete else ("")
        p = canvas.create_polygon(points, outline=self.button_polygon_outline_color.cget("fg_color"), smooth=self.switch_polygon_smooth.get(), width=self.slider_polygon_thickness.get(), dash=dash, fill=fill, stipple=pattern, tags=tag)
        if not delete:
            self.crtl_z_items.append(p)

    def draw_text(self, canvas)-> None:
        t = canvas.create_text(self.start_x, self.start_y, text=self.entry_text.get(), font=(self.option_menu_text_font.get(), int(self.slider_text_size.get())), fill=self.button_text_color.cget("fg_color"), anchor=self.anchors_dict.get(self.option_menu_text_anchor.get()))
        self.crtl_z_items.append(t)

    def draw_image(self, canvas)-> None:
        if len(self.images) > 0:
            anchor = self.anchors_dict.get(self.option_menu_image_anchor.get())
            i = canvas.create_image(self.start_x, self.start_y, image=self.images[self.current_image_index], anchor=anchor)
            self.crtl_z_items.append(i)

    def crtl_z(self)-> None:
        if len(self.crtl_z_items) > 0 and self.tabview_canvas.get() != '':
            current_canvas = self.tabview_canvas.tab(self.tabview_canvas.get()).children.get("!canvas")
            current_canvas.delete(self.crtl_z_items.pop(-1))

    def key_press(self, event)-> None:
        self.pressed_special_keys.add(event.keysym)
        if self.pressed_special_keys == {"Control_L"} or self.pressed_special_keys == {"Control_R"}:
            if self.selected_tool.get() == ZOOM:
                self.switch_zoom_dezoom.select()
            elif self.selected_tool.get() == SQUARE:
                self.switch_square_keep_ratio.select()
            elif self.selected_tool.get() == CIRCLE:
                self.switch_circle_keep_ratio.select()

    def key_release(self, event)-> None:
        if self.pressed_special_keys == {"Control_L"} or self.pressed_special_keys == {"Control_R"}:
            if self.selected_tool.get() == ZOOM:
                self.switch_zoom_dezoom.deselect()
            elif self.selected_tool.get() == SQUARE:
                self.switch_square_keep_ratio.deselect()
            elif self.selected_tool.get() == CIRCLE:
                self.switch_circle_keep_ratio.deselect()
        self.pressed_special_keys.discard(event.keysym)

    def change_button_color(self, button)-> None:
        color = askcolor(color=button.cget("fg_color"), title=self.title_name)[1]
        if color:
            button.configure(fg_color=color, hover_color=color)

    def change_image_path(self)-> None:
        path = askopenfilename(title=self.title_name, filetypes=[("Image files", "*.png;*.jpg;*.jpeg;")])
        if path and self.entry_image_width.get() and self.entry_image_height.get():
            if int(self.entry_image_width.get()) > 0 and int(self.entry_image_height.get()) > 0:
                self.button_image_path.configure(text=path.split("/")[-1])
                self.images.append(ImageTk.PhotoImage(image=Image.open(path).resize((int(self.entry_image_width.get()), int(self.entry_image_height.get())))))
                self.current_image_index = len(self.images) - 1

    def place_options(self, frame=None)-> None:
        self.frame_line_options.place_forget()
        self.frame_square_options.place_forget()
        self.frame_circle_options.place_forget()
        self.frame_polygon_options.place_forget()
        self.frame_pencil_options.place_forget()
        self.frame_eraser_options.place_forget()
        self.frame_text_options.place_forget()
        self.frame_image_options.place_forget()

        self.polygon_points = []

        if frame:
            frame.place(x=5, y=193)

    def show_error(self, message:str)-> None:
        topelevel_error = ctk.CTkToplevel(self, fg_color=self.highlight_color)
        topelevel_error.title(self.title_name)
        topelevel_error.geometry("350x100+100+100")
        topelevel_error.attributes('-topmost', True)
        ctk.CTkLabel(topelevel_error, font=(self.font_name, 14), text=message, text_color=self.text_color).place(relx=0.5,y=20,anchor="n")
        ctk.CTkButton(topelevel_error, font=(self.font_name, 14), text="Ok", fg_color=self.action_color, hover_color=self.hover_action_color, text_color=self.text_color, command=lambda: topelevel_error.destroy(), width=50).place(relx=0.5,y=60,anchor="n")
        self.bind("<Return>", lambda _: topelevel_error.destroy())

    def ask_yes_no(self, message:str)-> bool:
        self.response = None

        def yes()-> None:
            self.response = True
            topelevel_yes_no.destroy()

        def no()-> None:
            self.response = False
            topelevel_yes_no.destroy()

        topelevel_yes_no = ctk.CTkToplevel(self, fg_color=self.highlight_color)
        topelevel_yes_no.title(self.title_name)
        topelevel_yes_no.geometry("350x100+100+100")
        topelevel_yes_no.attributes('-topmost', True)
        ctk.CTkLabel(topelevel_yes_no, font=(self.font_name, 14), text=message, text_color=self.text_color).place(relx=0.5,y=20,anchor="n")
        ctk.CTkButton(topelevel_yes_no, font=(self.font_name, 14), text="Yes", fg_color=self.action_color, hover_color=self.hover_action_color, text_color=self.text_color, command=yes, width=50).place(relx=0.3,y=60)
        ctk.CTkButton(topelevel_yes_no, font=(self.font_name, 14), text="No", fg_color=self.action_color, hover_color=self.hover_action_color, text_color=self.text_color, command=no, width=50).place(relx=0.7,y=60,anchor="ne")

        self.bind("<Return>", lambda _: yes())
        self.wait_window(topelevel_yes_no)
        return self.response

    def cap_entry(self, widget, lenght:int)-> None:
        if len(widget.get()) > lenght:
            widget.delete(lenght, "end")

    def cap_entry_to_int(self, widget, lenght:int)-> None:
        if len(widget.get()) > lenght:
            widget.delete(lenght, "end")
        for char in widget.get():
            if not char.isdigit():
                widget.delete(len(widget.get()) - 1, "end")

    def add_canvas(self)-> None:
        canvas_name = self.entry_canvas_name.get()
        if canvas_name != "" and 1 < len(canvas_name) < 21 and self.canvas_number < 8:
            try:
                self.tabview_canvas.add(canvas_name)
                new_canvas = tk.Canvas(self.tabview_canvas.tab(canvas_name), width=950, height=810, highlightthickness=0, background="#FFFFFF")
                new_canvas.place(relx=0.5, y=-5, anchor="n")
                self.tabview_canvas.set(canvas_name)
                self.canvas_number += 1
                self.entry_canvas_name.delete("0", "end")
                self.focus_set()
            except ValueError:
                self.entry_canvas_name.delete("0", "end")
                self.focus_set()
                self.show_error(message="There is already a canvas with that name")
        elif canvas_name != "" and 1 < len(canvas_name) < 21:
            self.entry_canvas_name.delete("0", "end")
            self.focus_set()
            self.show_error(message="There is a limit of 8 canvas")
        elif canvas_name != "":
            self.entry_canvas_name.delete("0", "end")
            self.focus_set()
            self.show_error(message="The canvas name needs to be\nbetween 2 and 10 characters long")
        else:
            self.entry_canvas_name.delete("0", "end")
            self.focus_set()
            self.show_error(message="You need to insert a name before adding it")

    def delete_canvas(self)-> None:
        if self.canvas_number == 0:
            self.show_error("There is no canvas to delete")
            return

        if self.ask_yes_no("Are you sure you want to delete this canvas ?"):
            self.tabview_canvas.delete(self.tabview_canvas.get())
            self.canvas_number -= 1

    def change_canvas_color(self)-> None:
        if self.canvas_number == 0:
            self.show_error("There is no canvas to change color")
            return
        
        current_canvas = self.tabview_canvas.tab(self.tabview_canvas.get()).children.get("!canvas")
        current_canvas.configure(background=askcolor(color=current_canvas.cget("background"), title=self.title_name)[1])

    def clear_canvas(self)-> None:
        if self.canvas_number == 0:
            self.show_error("There is no canvas to clear")
            return
        
        if self.ask_yes_no("Are you sure you want to clear this canvas ?"):
            self.tabview_canvas.tab(self.tabview_canvas.get()).children.get("!canvas").delete("all")

    def reset_canvas(self)-> None:
        if self.canvas_number == 0:
            self.show_error("There is no canvas to reset")
            return
        
        if self.ask_yes_no("Are you sure you want to reset the view of\nthis canvas ?"):
            current_canvas = self.tabview_canvas.tab(self.tabview_canvas.get()).children.get("!canvas")
            current_canvas.xview_moveto(0.0)
            current_canvas.yview_moveto(0.0)

#? Main
if __name__ == "__main__":
    App()