import sys
from datetime import datetime
import os
import numpy as np
from camera import camera
from arduino import arduino
from errors import errors
from tkinter import ttk
from ttkthemes import ThemedStyle
import cv2
import tkinter as tk
from pathlib import Path
import toml

use_arduino = False


class main(tk.Frame):
    def __init__(self):
        # application paths
        self.application_path = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(Path(self.application_path).parents[0], "data")
        self.application_path_temp = self.application_path
        # main window
        self.parent = root
        # theme
        self.style = ThemedStyle(self.parent)
        self.initialization()
        # prevent closing window with x
        self.parent.protocol("WM_DELETE_WINDOW", self.__callback)
        self.parent.title("LBN Stop Motion")
        self.win_width = 800
        self.win_height = 800
        self.parent.geometry(f"{self.win_width}x{self.win_height}+10+10")
        self.parent.resizable(False, False)
        # GUI / start
        self.create_gui()
        self.camera.start()
        self.loop()

    @staticmethod
    def __callback():
        """Prevent closing the window with x"""
        return

    #########################
    ##          GUI        ##
    #########################

    def create_gui(self):
        """Create GUI"""
        # GUI general widgets customization
        self.style.configure("TCheckbutton", font=self.tk_font)
        self.style.configure("TButton", font=self.tk_font)
        self.style.configure("TLabel", font=self.tk_font)
        ################################
        # settings display
        settings_frame = ttk.Frame(self.parent, relief=tk.SUNKEN, borderwidth=1)
        settings_frame.grid(column=0, row=0, padx=10, pady=10)
        # scale
        scale_frame = ttk.Frame(settings_frame)
        scale_frame.grid(column=0, row=0, padx=5, pady=5)
        scale_text = ttk.Label(scale_frame, text="Displays scale")
        scale_text.grid(column=0, row=0, rowspan=2, padx=5, pady=5)
        self.scale_scale = ttk.Scale(
            scale_frame,
            from_=2,
            to=10,
            orient=tk.HORIZONTAL,
            command=self.change_scale,
            value=self.scale,
        )
        self.scale_scale.grid(column=1, row=0, padx=5, pady=5)
        self.scale_value_text = ttk.Label(
            scale_frame, text=str(self.scale_scale.get() * 10) + "%"
        )
        self.scale_value_text.grid(column=1, row=1, padx=5, pady=5)
        # exposure
        exposure_frame = ttk.Frame(settings_frame)
        exposure_frame.grid(column=0, row=2, columnspan=2, pady=5)
        exposure_text = ttk.Label(exposure_frame, text="Exposure")
        exposure_text.grid(column=0, row=0, padx=5, pady=5)
        # self.auto_expo_var = tk.BooleanVar(value=False)
        exposure_auto_chk = ttk.Checkbutton(
            exposure_frame,
            variable=self.auto_exp_var,
            command=lambda: self.set_value("auto_exp"),
            text="auto",
        )
        self.auto_exp_var.set(self.camera.auto_exp)
        exposure_auto_chk.grid(column=0, row=1, padx=5, pady=5)
        self.exposure_var = tk.IntVar(value=self.camera.exposure)
        set_exposure_spin = ttk.Spinbox(
            exposure_frame,
            from_=-13,
            to=-1,
            increment=1,
            textvariable=self.exposure_var,
            command=lambda: self.set_value("exp"),
            font=self.tk_font,
        )
        set_exposure_spin.grid(column=0, row=2, padx=5, pady=5)
        # onion
        onion_frame = ttk.Frame(settings_frame)
        onion_frame.grid(column=0, row=3, columnspan=2, pady=5)
        onion_text = ttk.Label(onion_frame, text="Onion skin")
        onion_text.grid(column=0, row=0, padx=5, pady=5)
        self.enable_onion = tk.BooleanVar(value=True)
        onion_chk = ttk.Checkbutton(
            onion_frame,
            variable=self.enable_onion,
            command=lambda: self.set_value("onion"),
            text="enabled",
        )
        onion_chk.grid(column=0, row=1, padx=5, pady=5)
        self.opacity_var = tk.IntVar(value=50)
        set_opacity_spin = ttk.Spinbox(
            onion_frame,
            from_=0,
            to=100,
            increment=1,
            textvariable=self.opacity_var,
            command=lambda: self.set_value("opacity"),
            font=self.tk_font,
        )
        set_opacity_spin.grid(column=0, row=3, padx=5, pady=5)
        # sequence
        seq_frame = ttk.Frame(settings_frame)
        seq_frame.grid(column=0, row=4, columnspan=2, pady=10)
        seq_text = ttk.Label(seq_frame, text="Sequence")
        seq_text.grid(column=0, row=0, columnspan=2, padx=5, pady=5)
        seq_name_text = ttk.Label(seq_frame, text="Seq. name" + ": ")
        seq_name_text.grid(column=0, row=1, padx=5, pady=5)
        self.set_seq_name_entry = ttk.Entry(seq_frame)
        self.set_seq_name_entry.grid(column=1, row=1, padx=5, pady=5)
        seq_name_btn = ttk.Button(
            seq_frame, text="Set", command=lambda: self.set_value("seq_name")
        )
        seq_name_btn.grid(column=0, row=2, columnspan=2, padx=5, pady=5)
        # buttons
        btn_frame = ttk.Frame(self.parent)
        btn_frame.grid(column=1, row=0, pady=10)
        acq_btn = ttk.Button(
            btn_frame, text="Acquisition [a]", command=self.capture_frame
        )
        r = 0
        acq_btn.grid(column=0, row=r, columnspan=2, padx=5, pady=5)
        r += 1
        delete_btn = ttk.Button(btn_frame, text="Delete [d]", command=self.delete_frame)
        delete_btn.grid(column=0, row=r, columnspan=2, padx=5, pady=5)
        r += 1
        prev_btn = ttk.Button(
            btn_frame, text=" Seq. prev [<]", command=lambda: self.set_value("seq_prev")
        )
        prev_btn.grid(column=0, row=r, padx=5, pady=5)
        next_btn = ttk.Button(
            btn_frame, text=" Seq. next [>]", command=lambda: self.set_value("seq_next")
        )
        next_btn.grid(column=1, row=r, padx=5, pady=5)
        r += 1
        prev_btn = ttk.Button(
            btn_frame,
            text=" Strip prev [n]",
            command=lambda: self.set_value("strip_prev"),
        )
        prev_btn.grid(column=0, row=r, padx=5, pady=5)
        next_btn = ttk.Button(
            btn_frame,
            text=" Strip next [m]",
            command=lambda: self.set_value("strip_next"),
        )
        next_btn.grid(column=1, row=r, padx=5, pady=5)
        r += 1
        # quit button
        self.style.configure("quit.TButton", font=("Helvetica", 20), foreground="red")
        self.quit_btn = ttk.Button(
            btn_frame, text="Quit", command=self.quit, style="quit.TButton"
        )
        self.quit_btn.grid(column=0, row=r, columnspan=2, padx=5, pady=5)
        # scales
        scales_frame = ttk.Frame(self.parent, relief=tk.SUNKEN, borderwidth=1)
        scales_frame.grid(column=2, row=0, pady=10)
        r = 0
        scale_text = ttk.Label(scales_frame, text="Scales")
        scale_text.grid(column=0, row=r, columnspan=2, padx=5, pady=5)
        r += 1
        del_last_btn = ttk.Button(
            scales_frame,
            text="Delete last [x]",
            command=lambda: self.set_value("del_last"),
        )
        del_last_btn.grid(column=0, row=r, columnspan=2, padx=5, pady=5)
        r += 1
        clear_btn = ttk.Button(
            scales_frame, text="Clear [c]", command=lambda: self.set_value("clear")
        )
        clear_btn.grid(column=0, row=r, columnspan=2, padx=5, pady=5)
        r += 1
        scale_length_text = ttk.Label(scales_frame, text="Number:")
        scale_length_text.grid(column=0, row=r, padx=5, pady=5)
        # self.scale_length_var = tk.IntVar(value=5)
        set_scale_length_spin = ttk.Spinbox(
            scales_frame,
            from_=1,
            to=100,
            increment=1,
            textvariable=self.scale_length_var,
            command=lambda: self.set_value("scale_length"),
            font=self.tk_font,
            width=6,
        )
        set_scale_length_spin.grid(column=1, row=r, padx=5, pady=5)
        r += 1
        scale_init_length_text = ttk.Label(scales_frame, text="Initial (px):")
        scale_init_length_text.grid(column=0, row=r, padx=5, pady=5)
        # self.scale_init_length_var = tk.IntVar(value=2)
        set_scale_init_length_spin = ttk.Spinbox(
            scales_frame,
            from_=1,
            to=50,
            increment=1,
            textvariable=self.scale_init_length_var,
            command=lambda: self.set_value("scale_init_length"),
            font=self.tk_font,
            width=6,
        )
        set_scale_init_length_spin.grid(column=1, row=r, padx=5, pady=5)
        r += 1
        scale_ratio_text = ttk.Label(scales_frame, text="Ratio:")
        scale_ratio_text.grid(column=0, row=r, padx=5, pady=5)
        # self.scale_ratio_var = tk.DoubleVar(value=1.2)
        set_scale_ratio_spin = ttk.Spinbox(
            scales_frame,
            from_=1,
            to=10,
            increment=0.1,
            textvariable=self.scale_ratio_var,
            command=lambda: self.set_value("scale_ratio"),
            font=self.tk_font,
            width=6,
        )
        set_scale_ratio_spin.grid(column=1, row=r, padx=5, pady=5)
        r += 1
        # self.scale_inverted_var = tk.BooleanVar(value=False)
        scale_inverted_chk = ttk.Checkbutton(
            scales_frame,
            variable=self.scale_inverted_var,
            command=lambda: self.set_value("invert"),
            text="Inverted",
        )
        scale_inverted_chk.grid(column=0, row=r, columnspan=2, padx=5, pady=5)
        r += 1
        color_scale_frame = ttk.Frame(scales_frame, relief=tk.SUNKEN, borderwidth=1)
        color_scale_frame.grid(column=0, row=r, columnspan=2, padx=10, pady=5)
        rgb = self.rgbtohex(self.color_scale)
        self.color_scale_canvas = tk.Canvas(
            color_scale_frame, bg=rgb, width=100, height=50
        )
        self.color_scale_canvas.grid(column=0, row=0, rowspan=3, padx=5, pady=2)
        color_scale_R_label = ttk.Label(color_scale_frame, text="R")
        color_scale_R_label.grid(column=1, row=0, padx=5, pady=2)
        self.color_scale_var = []
        self.color_scale_var.append(tk.IntVar())
        color_scale_R_spin = ttk.Spinbox(
            color_scale_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.color_scale_var[0],
            command=lambda: self.set_value("color_scale"),
            font=self.tk_font,
        )
        color_scale_R_spin.grid(column=2, row=0, padx=5, pady=2)
        self.color_scale_var[0].set(self.color_scale[0])
        color_scale_G_label = ttk.Label(color_scale_frame, text="G")
        color_scale_G_label.grid(column=1, row=1, padx=5, pady=2)
        self.color_scale_var.append(tk.IntVar())
        color_scale_G_spin = ttk.Spinbox(
            color_scale_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.color_scale_var[1],
            command=lambda: self.set_value("color_scale"),
            font=self.tk_font,
        )
        color_scale_G_spin.grid(column=2, row=1, padx=5, pady=2)
        self.color_scale_var[1].set(self.color_scale[1])
        color_scale_B_label = ttk.Label(color_scale_frame, text="B")
        color_scale_B_label.grid(column=1, row=2, padx=5, pady=2)
        self.color_scale_var.append(tk.IntVar())
        color_scale_B_spin = ttk.Spinbox(
            color_scale_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.color_scale_var[2],
            command=lambda: self.set_value("color_scale"),
            font=self.tk_font,
        )
        color_scale_B_spin.grid(column=2, row=2, padx=5, pady=2)
        self.color_scale_var[2].set(self.color_scale[2])
        # selected scale
        selected_scale_frame = ttk.Frame(self.parent, relief=tk.SUNKEN, borderwidth=1)
        selected_scale_frame.grid(column=2, row=1, pady=10)
        r = 0
        selected_scale_text = ttk.Label(selected_scale_frame, text="Selected Scale")
        selected_scale_text.grid(column=0, row=r, columnspan=2, padx=5, pady=5)
        r += 1
        self.selected_scale_var = tk.IntVar(value=0)
        self.set_selected_scale_spin = ttk.Spinbox(
            selected_scale_frame,
            from_=0,
            to=0,
            increment=1,
            textvariable=self.selected_scale_var,
            command=lambda: self.set_value("selected_scale"),
            font=self.tk_font,
            width=6,
        )
        self.set_selected_scale_spin.grid(column=0, row=r, columnspan=2, padx=5, pady=5)
        r += 1
        selected_scale_length_text = ttk.Label(selected_scale_frame, text="Number:")
        selected_scale_length_text.grid(column=0, row=r, padx=5, pady=5)
        self.selected_scale_length_var = tk.IntVar(value=0)
        set_selected_scale_length_spin = ttk.Spinbox(
            selected_scale_frame,
            from_=0,
            to=100,
            increment=1,
            textvariable=self.selected_scale_length_var,
            command=lambda: self.set_value("selected_scale_length"),
            font=self.tk_font,
            width=6,
        )
        set_selected_scale_length_spin.grid(column=1, row=r, padx=5, pady=5)
        r += 1
        selected_scale_init_length_text = ttk.Label(
            selected_scale_frame, text="Initial (px):"
        )
        selected_scale_init_length_text.grid(column=0, row=r, padx=5, pady=5)
        self.selected_scale_init_length_var = tk.IntVar(value=0)
        set_selected_scale_init_length_spin = ttk.Spinbox(
            selected_scale_frame,
            from_=1,
            to=50,
            increment=1,
            textvariable=self.selected_scale_init_length_var,
            command=lambda: self.set_value("selected_scale_init_length"),
            font=self.tk_font,
            width=6,
        )
        set_selected_scale_init_length_spin.grid(column=1, row=r, padx=5, pady=5)
        r += 1
        selected_scale_ratio_text = ttk.Label(selected_scale_frame, text="Ratio:")
        selected_scale_ratio_text.grid(column=0, row=r, padx=5, pady=5)
        self.selected_scale_ratio_var = tk.DoubleVar(value=1)
        set_selected_scale_ratio_spin = ttk.Spinbox(
            selected_scale_frame,
            from_=1,
            to=10,
            increment=0.1,
            textvariable=self.selected_scale_ratio_var,
            command=lambda: self.set_value("selected_scale_ratio"),
            font=self.tk_font,
            width=6,
        )
        set_selected_scale_ratio_spin.grid(column=1, row=r, padx=5, pady=5)
        r += 1
        self.selected_scale_inverted_var = tk.BooleanVar(value=False)
        selected_scale_inverted_chk = ttk.Checkbutton(
            selected_scale_frame,
            variable=self.selected_scale_inverted_var,
            command=lambda: self.set_value("selected_invert"),
            text="Inverted",
        )
        selected_scale_inverted_chk.grid(column=0, row=r, columnspan=2, padx=5, pady=5)
        r += 1
        color_selected_scale_frame = ttk.Frame(
            selected_scale_frame, relief=tk.SUNKEN, borderwidth=1
        )
        color_selected_scale_frame.grid(column=0, row=r, columnspan=2, padx=10, pady=5)
        rgb = self.rgbtohex(self.color_selected_scale)
        self.color_selected_scale_canvas = tk.Canvas(
            color_selected_scale_frame, bg=rgb, width=100, height=50
        )
        self.color_selected_scale_canvas.grid(
            column=0, row=0, rowspan=3, padx=5, pady=2
        )
        color_selected_scale_R_label = ttk.Label(color_selected_scale_frame, text="R")
        color_selected_scale_R_label.grid(column=1, row=0, padx=5, pady=2)
        self.color_selected_scale_var = []
        self.color_selected_scale_var.append(tk.IntVar())
        color_selected_scale_R_spin = ttk.Spinbox(
            color_selected_scale_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.color_selected_scale_var[0],
            command=lambda: self.set_value("color_selected_scale"),
            font=self.tk_font,
        )
        color_selected_scale_R_spin.grid(column=2, row=0, padx=5, pady=2)
        self.color_selected_scale_var[0].set(self.color_selected_scale[0])
        color_selected_scale_G_label = ttk.Label(color_selected_scale_frame, text="G")
        color_selected_scale_G_label.grid(column=1, row=1, padx=5, pady=2)
        self.color_selected_scale_var.append(tk.IntVar())
        color_selected_scale_G_spin = ttk.Spinbox(
            color_selected_scale_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.color_selected_scale_var[1],
            command=lambda: self.set_value("color_selected_scale"),
            font=self.tk_font,
        )
        color_selected_scale_G_spin.grid(column=2, row=1, padx=5, pady=2)
        self.color_selected_scale_var[1].set(self.color_selected_scale[1])
        color_selected_scale_B_label = ttk.Label(color_selected_scale_frame, text="B")
        color_selected_scale_B_label.grid(column=1, row=2, padx=5, pady=2)
        self.color_selected_scale_var.append(tk.IntVar())
        color_selected_scale_B_spin = ttk.Spinbox(
            color_selected_scale_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.color_selected_scale_var[2],
            command=lambda: self.set_value("color_selected_scale"),
            font=self.tk_font,
        )
        color_selected_scale_B_spin.grid(column=2, row=2, padx=5, pady=2)
        self.color_selected_scale_var[2].set(self.color_selected_scale[2])
        self.set_selected_scale_spin.configure(state="disable")

    #########################
    ## Program main methods##
    #########################

    def initialization(self):
        """Initializations"""
        # opencv font
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        # tkinter font
        self.tk_font = ("Helvetica", 12)
        # other
        self.sequence = []
        self.current_seq_frame = 0
        self.seq_name = ""
        self.d_folder = self.data_path
        self.shift_strip = 0
        self.scales = []
        self.current_scale = []
        self.new_scale = True
        self.mouse_coords = []
        self.color_selected_scale = [255, 255, 255]
        self.selected_scale = 0
        self.scale_settings = []
        self.set_settings = False
        self.read_config()
        # self.camera = camera.Camera(w=self.width, h=self.height)
        self.camera.start_stream(0)
        cv2.namedWindow("Monitoring", cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback("Monitoring", self.mouse_click)
        if use_arduino:
            self.arduino = arduino.Arduino("COM14")
        # cv2.imshow("strip", np.zeros((10, 10, 3), dtype=np.uint8))

    def quit(self):
        """Quit"""
        cv2.destroyAllWindows()
        self.camera.stop()
        # self.parent.after_cancel(self.after_id)
        self.parent.destroy()

    def loop(self):
        """Main loop"""
        """loop on camera(stream/processing)"""
        try:
            # (grabbed, self.frame) = self.camera.get_frame()
            self.frame, err = self.camera.read()
            if err:
                # if not grabbed:
                raise Exception("Camera error!")
        except:
            sys.exit()
        else:
            if self.camera.new:  # only if actually new frame
                # if grabbed:
                self.camera.new = False
                if self.frame is None:
                    raise Exception("No frame captured!")
                else:
                    self.update_scales()
                    self.display_capture()
            if use_arduino:
                if self.arduino.check_capture():
                    self.capture_frame()
            self.display_sequence()
            self.display_sequence_strip()
            # Wait for command
            k = cv2.waitKey(1)
            if k == 27:  # escape/quit
                self.quit()
            elif k == ord("a"):  # capture
                self.capture_frame()
            elif k == ord(">"):  # next frame
                self.current_seq_frame += 1
                if self.current_seq_frame >= len(self.sequence):
                    self.current_seq_frame = len(self.sequence) - 1
            elif k == ord("<"):  # next frame
                self.current_seq_frame -= 1
                if self.current_seq_frame < 0:
                    self.current_seq_frame = 0
            elif k == ord("m"):  # shift strip
                self.shift_strip -= 1
            elif k == ord("n"):  # shift strip
                self.shift_strip += 1
            elif k == ord("d"):  # delete frame
                self.delete_frame()
            elif k == ord("x"):  # delete last point
                if len(self.scales) > 0:
                    self.scales.pop(-1)
                    self.scale_settings.pop(-1)
                if len(self.scales) > 0:
                    if self.selected_scale == len(self.scale_settings):
                        self.selected_scale -= 1
                        self.selected_scale_var.set(self.selected_scale)
                        self.set_value("selected_scale")
                else:
                    self.selected_scale = 0
                    self.selected_scale_var.set(self.selected_scale)
                    self.set_selected_scale_spin.config(state="disable")
            elif k == ord("c"):  # clear points
                self.scales = []
                self.set_selected_scale_spin.config(state="disable")
                self.scale_settings = []
                self.selected_scale = 0
                self.selected_scale_var.set(self.selected_scale)
            elif k == ord("o"):  # double click
                self.new_scale = True
                self.mouse_coords = []
                self.scales.append(self.current_scale)
                self.scale_settings.append(
                    [
                        self.scale_ratio_var.get(),
                        self.scale_init_length_var.get(),
                        self.scale_length_var.get(),
                        self.color_scale.copy(),
                    ]
                )
                self.current_scale = []
            # continue loop
            self.parent.after(2, self.loop)

    def update_scales(self):
        self.set_selected_scale_spin.config(to=len(self.scales) - 1)
        if self.set_settings:
            if len(self.scales) > 0:
                self.set_selected_scale_spin.config(state="normal")
            self.set_settings = False
            self.scale_settings.append(
                [
                    self.scale_ratio_var.get(),
                    self.scale_init_length_var.get(),
                    self.scale_length_var.get(),
                    self.color_scale.copy(),
                    self.scale_inverted_var.get(),
                ]
            )
            self.set_value("selected_scale")

    #########################
    ##   Program helpers   ##
    #########################

    def read_config(self):
        """
        Read config file.
        """
        conf_path = os.path.join(self.application_path, "config.toml")
        try:
            if os.path.exists(conf_path):
                with open(conf_path, "r", encoding="utf-8") as f:
                    try:
                        try:
                            try:
                                config = toml.load(f)
                            except UnicodeDecodeError as ex:
                                raise errors.TomlDecodeError() from ex
                        except errors.TomlDecodeError:
                            pass
                        except toml.TomlDecodeError as ex:
                            raise errors.TomlDecodeError() from ex
                    except errors.TomlDecodeError:
                        pass
                    else:
                        # theme
                        self.theme = config.get("version", {}).get("theme")
                        match self.theme:
                            case "":
                                pass
                            case _:
                                try:
                                    try:
                                        self.style.set_theme(self.theme)
                                    except Exception as ex:
                                        raise errors.UnknownTheme() from ex
                                except errors.UnknownTheme:
                                    self.theme = ""
                        # display
                        self.width = config.get("display", {}).get("width")
                        self.height = config.get("display", {}).get("height")
                        self.camera = camera.Camera(w=self.width, h=self.height)
                        self.scale = config.get("display", {}).get("scale")
                        # camera
                        camera_source = config.get("camera", {}).get("source")
                        self.camera.start_stream(camera_source)
                        self.auto_exp_var = tk.BooleanVar(value=False)
                        self.auto_exp_var.set(config.get("camera", {}).get("auto_exp"))
                        self.exposure_var = tk.IntVar(value=-7)
                        self.exposure_var.set(config.get("camera", {}).get("exposure"))
                        self.camera.set_exposure(self.exposure_var.get())
                        self.camera.auto_exp = self.auto_exp_var.get()
                        self.camera.exposure_auto()
                        # scales
                        self.scale_ratio_var = tk.DoubleVar(value=1)
                        self.scale_ratio_var.set(config.get("scales", {}).get("ratio"))
                        self.scale_init_length_var = tk.IntVar(value=10)
                        self.scale_init_length_var.set(
                            config.get("scales", {}).get("l_init")
                        )
                        self.scale_length_var = tk.IntVar(value=5)
                        self.scale_length_var.set(config.get("scales", {}).get("n"))
                        self.scale_inverted_var = tk.BooleanVar(value=False)
                        self.scale_inverted_var.set(
                            config.get("scales", {}).get("invert")
                        )
                        self.color_scale = config.get("scales", {}).get("color")
                        # arduino
                        self.use_arduino_var = tk.BooleanVar(value=True)
                        self.use_arduino_var.set(config.get("arduino", {}).get("use"))
                        self.port = config.get("arduino", {}).get("port")
                        # save
                        data_folder = config.get("save", {}).get("data_folder")
                        if not os.path.exists(data_folder):
                            data_folder = "data"
                        if data_folder == "data" or data_folder == "":
                            self.data_folder = os.path.join(
                                self.application_path, "data"
                            )
                            if not os.path.exists(self.data_folder):
                                os.makedirs(self.data_folder)
                        else:
                            self.data_folder = data_folder
            else:
                raise errors.NoConfig()
        except errors.NoConfig:
            pass

    def save_config(self):
        """
        Save config file.
        """
        config = {}
        config["title"] = "Configuration file"
        # version
        config["version"] = {}
        config["version"]["theme"] = self.theme
        # display
        config["display"] = {}
        config["display"]["width"] = self.width
        config["display"]["height"] = self.height
        config["display"]["scale"] = int(self.scale_scale.get())
        # scales
        config["scales"] = {}
        config["scales"]["ratio"] = self.scale_ratio_var.get()
        config["scales"]["l_init"] = self.scale_init_length_var.get()
        config["scales"]["n"] = self.scale_length_var.get()
        config["scales"]["color"] = [
            self.color_scale_var[0],
            self.color_scale_var[1],
            self.color_scale_var[2],
        ]
        config["scales"]["invert"] = self.scale_inverted_var.get()
        # camera
        config["camera"] = {}
        config["camera"]["exposure"] = self.exposure_var.get()
        config["camera"]["auto_exp"] = self.auto_exp_var.get()
        # arduino
        config["arduino"] = {}
        config["arduino"]["use"] = self.use_arduino_var.get()
        if self.use_arduino_var.get():
            config["arduino"]["port"] = self.arduino.port
        else:
            config["arduino"]["port"] = self.port
        # save
        config["save"] = {}
        config["save"]["data_folder"] = self.data_folder
        # save config
        save_path = os.path.join(self.application_path, "config.toml")
        with open(save_path, "w", encoding="utf-8") as configfile:
            toml.dump(config, configfile)

    def rgbtohex(self, rgb):
        """convert RGB to tkinter color"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.new_scale:
                self.new_scale = False
                self.current_scale.append(
                    [int(x * 10 / self.scale), int(y * 10 / self.scale)]
                )
            else:
                self.current_scale.append(
                    [int(x * 10 / self.scale), int(y * 10 / self.scale)]
                )
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            self.new_scale = True
            self.mouse_coords = []
            self.scales.append(self.current_scale)
            self.set_settings = True
            self.current_scale = []
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.new_scale = True
            self.mouse_coords = []
            self.scales.append(self.current_scale)
            self.set_settings = True
            self.current_scale = []
        elif event == cv2.EVENT_MOUSEMOVE:
            if not self.new_scale:
                self.mouse_coords = [int(x * 10 / self.scale), int(y * 10 / self.scale)]

    def display_camera(self):
        frame_copy = self.frame.copy()
        cv2.imshow(
            "Monitoring",
            cv2.resize(
                frame_copy,
                (
                    int(self.width * self.scale_scale.get() / 10),
                    int(self.height * self.scale_scale.get() / 10),
                ),
            ),
        )

    def capture_frame(self):
        if self.seq_name == "":
            now = datetime.now()
            date_time = now.strftime("%Y%m%d_%H%M%S")
            self.seq_name = date_time
        # insert or append
        if len(self.sequence) > 0:
            if self.current_seq_frame == len(self.sequence) - 1:
                self.sequence.append(self.frame.copy())
                self.current_seq_frame += 1
                filename = self.seq_name + "_" + str(len(self.sequence) - 1) + ".png"
                cv2.imwrite(os.path.join(self.d_folder, filename), self.sequence[-1])
            else:
                self.current_seq_frame += 1
                self.sequence.insert(self.current_seq_frame, self.frame.copy())
                for i in range(len(self.sequence) - 2, self.current_seq_frame - 1, -1):
                    filename = os.path.join(
                        self.d_folder, self.seq_name + "_" + str(i) + ".png"
                    )
                    if os.path.isfile(filename):
                        filename_new = os.path.join(
                            self.d_folder,
                            self.seq_name + "_" + str(i + 1) + ".png",
                        )
                        os.rename(filename, filename_new)
                filename = os.path.join(
                    self.d_folder,
                    self.seq_name + "_" + str(self.current_seq_frame) + ".png",
                )
                cv2.imwrite(
                    os.path.join(self.d_folder, filename),
                    self.sequence[self.current_seq_frame],
                )
        else:
            self.sequence.append(self.frame.copy())
            filename = self.seq_name + "_" + str(len(self.sequence) - 1) + ".png"
            cv2.imwrite(os.path.join(self.d_folder, filename), self.sequence[-1])

    def delete_frame(self):
        if len(self.sequence) > 0:
            filename = os.path.join(
                self.d_folder,
                self.seq_name + "_" + str(self.current_seq_frame) + ".png",
            )
            if os.path.isfile(filename):
                l = len(self.sequence)
                os.remove(filename)
                self.sequence.pop(self.current_seq_frame)
                if len(self.sequence) > 0:
                    if self.current_seq_frame >= len(self.sequence):
                        self.current_seq_frame = len(self.sequence) - 1
                    else:
                        for i in range(self.current_seq_frame + 1, l):
                            filename = os.path.join(
                                self.d_folder, self.seq_name + "_" + str(i) + ".png"
                            )
                            if os.path.isfile(filename):
                                filename_new = os.path.join(
                                    self.d_folder,
                                    self.seq_name + "_" + str(i - 1) + ".png",
                                )
                                os.rename(filename, filename_new)

    def display_capture(self):
        if len(self.sequence) > 0:
            if self.enable_onion.get():
                alpha = self.opacity_var.get() / 100
                output = cv2.addWeighted(
                    self.frame, 1 - alpha, self.sequence[-1], alpha, 0
                )
            else:
                output = self.frame.copy()
        else:
            output = self.frame.copy()
        output = self.display_scale_line(self.current_scale, output)
        if len(self.scales) > 0:
            for i, s in enumerate(self.scales):
                if self.scale_settings[i][0] == 1:
                    output = self.display_scale_multiple(
                        s, output, self.scale_settings[i]
                    )
                else:
                    output = self.display_scale_multiple_ratio(
                        s, output, self.scale_settings[i]
                    )
        cv2.imshow(
            "Monitoring",
            cv2.resize(
                output,
                (
                    int(self.width * self.scale_scale.get() / 10),
                    int(self.height * self.scale_scale.get() / 10),
                ),
            ),
        )

    def display_scale(self, pos_xy, img):
        col = (self.color_scale[2], self.color_scale[1], self.color_scale[0])
        if len(pos_xy) >= 2:
            d = 5
            n = self.scale_length_var.get()
            for i in range(len(pos_xy) - 1):
                if pos_xy[i][0] == pos_xy[i + 1][0]:
                    x = pos_xy[i][0]
                    if pos_xy[i][1] < pos_xy[i + 1][1]:
                        pA = (x, pos_xy[i][1])
                        pB = (x, pos_xy[i + 1][1])
                    else:
                        pB = (x, pos_xy[i][1])
                        pA = (x, pos_xy[i + 1][1])
                    cv2.line(img, pA, pB, col, 2)
                    le = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l = int(le / n)
                    for i in range(n + 1):
                        p1 = (x - d, pA[1] + i * l)
                        p2 = (x + d, pA[1] + i * l)
                        cv2.line(img, p1, p2, col, 2)
                elif pos_xy[i][1] == pos_xy[i + 1][1]:
                    y = pos_xy[i][1]
                    if pos_xy[i][0] < pos_xy[i + 1][0]:
                        pA = (pos_xy[i][0], y)
                        pB = (pos_xy[i + 1][0], y)
                    else:
                        pB = (pos_xy[i][0], y)
                        pA = (pos_xy[i + 1][0], y)
                    cv2.line(img, pA, pB, col, 2)
                    le = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l = int(le / n)
                    for i in range(n + 1):
                        p1 = (pA[0] + i * l, y - d)
                        p2 = (pA[0] + i * l, y + d)
                        cv2.line(img, p1, p2, (255, 255, 255), 2)
                else:
                    if pos_xy[i][0] < pos_xy[i + 1][0]:
                        pA = (pos_xy[i][0], pos_xy[i][1])
                        pB = (pos_xy[i + 1][0], pos_xy[i + 1][1])
                    else:
                        pB = (pos_xy[i][0], pos_xy[i][1])
                        pA = (pos_xy[i + 1][0], pos_xy[i + 1][1])
                    a = (pA[1] - pB[1]) / (pA[0] - pB[0])
                    b = pA[1] - a * pA[0]
                    b1 = b + d * np.sqrt(1 + a * a)
                    b2 = b - d * np.sqrt(1 + a * a)
                    cv2.line(img, pA, pB, col, 2)
                    le = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l = int(le / n)
                    for i in range(n + 1):
                        x = pA[0] + l * i / np.sqrt(1 + a * a)
                        y = a * x + b
                        b3 = y + 1 / a * x
                        x1 = (b3 - b1) * a / (1 + a * a)
                        x2 = (b3 - b2) * a / (1 + a * a)
                        y1 = a * x1 + b1
                        y2 = a * x2 + b2
                        p1 = (int(x1), int(y1))
                        p2 = (int(x2), int(y2))
                        cv2.line(img, p1, p2, col, 2)
        return img

    def display_scale_line(self, pos_xy, img):
        col = (self.color_scale[2], self.color_scale[1], self.color_scale[0])
        if len(pos_xy) >= 2:
            for i in range(len(pos_xy) - 1):
                pA = (pos_xy[i][0], pos_xy[i][1])
                pB = (pos_xy[i + 1][0], pos_xy[i + 1][1])
                cv2.line(img, pA, pB, col, 2)
        if len(pos_xy) > 0:
            if (
                len(self.current_scale) > 0
                and not self.new_scale
                and len(self.mouse_coords) > 0
            ):
                cv2.line(
                    img,
                    pos_xy[-1],
                    self.mouse_coords,
                    list(reversed(self.color_scale)),
                    2,
                )
        return img

    def display_scale_multiple(self, pos_xy, img, settings):
        col = (settings[3][2], settings[3][1], settings[3][0])
        if len(pos_xy) >= 2:
            d = 5
            # n = self.scale_length_var.get()
            n = settings[2]
            le = 0
            for i in range(len(pos_xy) - 1):
                pA = (pos_xy[i][0], pos_xy[i][1])
                pB = (pos_xy[i + 1][0], pos_xy[i + 1][1])
                le += np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
            l = int(le / n)
            l0 = 0
            for i in range(len(pos_xy) - 1):
                if pos_xy[i][0] == pos_xy[i + 1][0]:
                    x = pos_xy[i][0]
                    pA = (x, pos_xy[i][1])
                    pB = (x, pos_xy[i + 1][1])
                    if pos_xy[i][1] < pos_xy[i + 1][1]:
                        inc = 1
                    else:
                        inc = -1
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    nl = int((ls - l0) / l)
                    for k in range(nl + 1):
                        p1 = (x - d, pA[1] + inc * (k * l + l0))
                        p2 = (x + d, pA[1] + inc * (k * l + l0))
                        cv2.line(img, p1, p2, col, 2)
                    y = pA[1] + inc * ((nl + 1) * l + l0)
                    l0 = int(np.sqrt((pA[0] - x) ** 2 + (pA[1] - y) ** 2) - ls)
                elif pos_xy[i][1] == pos_xy[i + 1][1]:
                    y = pos_xy[i][1]
                    pA = (pos_xy[i][0], y)
                    pB = (pos_xy[i + 1][0], y)
                    if pos_xy[i][0] < pos_xy[i + 1][0]:
                        inc = 1
                    else:
                        inc = -1
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    nl = int((ls - l0) / l)
                    for k in range(nl + 1):
                        p1 = (pA[0] + inc * (k * l + l0), y - d)
                        p2 = (pA[0] + inc * (k * l + l0), y + d)
                        cv2.line(img, p1, p2, col, 2)
                    x = pA[0] + inc * ((nl + 1) * l + l0)
                    l0 = int(np.sqrt((pA[0] - x) ** 2 + (pA[1] - y) ** 2) - ls)
                else:
                    pA = (pos_xy[i][0], pos_xy[i][1])
                    pB = (pos_xy[i + 1][0], pos_xy[i + 1][1])
                    if pos_xy[i][0] < pos_xy[i + 1][0]:
                        inc = 1
                    else:
                        inc = -1
                    a = (pA[1] - pB[1]) / (pA[0] - pB[0])
                    b = pA[1] - a * pA[0]
                    b1 = b + d * np.sqrt(1 + a * a)
                    b2 = b - d * np.sqrt(1 + a * a)
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    nl = int((ls - l0) / l)
                    for k in range(nl + 1):
                        x = pA[0] + inc * (l * k + l0) / np.sqrt(1 + a * a)
                        y = a * x + b
                        b3 = y + 1 / a * x
                        x1 = (b3 - b1) * a / (1 + a * a)
                        x2 = (b3 - b2) * a / (1 + a * a)
                        y1 = a * x1 + b1
                        y2 = a * x2 + b2
                        p1 = (int(x1), int(y1))
                        p2 = (int(x2), int(y2))
                        cv2.line(img, p1, p2, col, 2)
                    x = pA[0] + inc * (l * (nl + 1) + l0) / np.sqrt(1 + a * a)
                    y = a * x + b
                    l0 = int(np.sqrt((pA[0] - x) ** 2 + (pA[1] - y) ** 2) - ls)
        return img

    def display_scale_multiple_ratio(self, pos_xy, img, settings):
        col = (settings[3][2], settings[3][1], settings[3][0])
        r = settings[0]
        li = settings[1]
        if len(pos_xy) >= 2:
            d = 5
            n = settings[2]
            le = 0
            for i in range(len(pos_xy) - 1):
                pA = (pos_xy[i][0], pos_xy[i][1])
                pB = (pos_xy[i + 1][0], pos_xy[i + 1][1])
                le += np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
            l = int(le / n)
            l0 = 0
            k = 0
            if settings[4]:
                s = len(pos_xy) - 1
                e = 0
                dir = -1
            else:
                s = 0
                e = len(pos_xy) - 1
                dir = 1
            for i in range(s, e, dir):
                # for i in range(len(pos_xy) - 1, 0, -1): for reverse with i-1
                if pos_xy[i][0] == pos_xy[i + dir][0]:
                    x = pos_xy[i][0]
                    pA = (x, pos_xy[i][1])
                    pB = (x, pos_xy[i + dir][1])
                    if pos_xy[i][1] < pos_xy[i + dir][1]:
                        inc = 1
                    else:
                        inc = -1
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l_current = 0
                    l = 0
                    while l_current <= ls:
                        l_current = l + l0
                        if l_current <= ls:
                            p1 = (x - d, int(pA[1] + inc * int(l_current)))
                            p2 = (x + d, int(pA[1] + inc * int(l_current)))
                            cv2.line(img, p1, p2, col, 2)
                            k += 1
                            l += li * r**k
                        else:
                            l0 = l_current - ls
                elif pos_xy[i][1] == pos_xy[i + dir][1]:
                    y = pos_xy[i][1]
                    pA = (pos_xy[i][0], y)
                    pB = (pos_xy[i + dir][0], y)
                    if pos_xy[i][0] < pos_xy[i + dir][0]:
                        inc = 1
                    else:
                        inc = -1
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l_current = 0
                    l = 0
                    while l_current <= ls:
                        l_current = l + l0
                        if l_current <= ls:
                            p1 = (int(pA[0] + inc * int(l_current)), y - d)
                            p2 = (int(pA[0] + inc * int(l_current)), y + d)
                            cv2.line(img, p1, p2, col, 2)
                            k += 1
                            l += li * r**k
                        else:
                            l0 = l_current - ls
                else:
                    pA = (pos_xy[i][0], pos_xy[i][1])
                    pB = (pos_xy[i + dir][0], pos_xy[i + dir][1])
                    if pos_xy[i][0] < pos_xy[i + dir][0]:
                        inc = 1
                    else:
                        inc = -1
                    a = (pA[1] - pB[1]) / (pA[0] - pB[0])
                    b = pA[1] - a * pA[0]
                    b1 = b + d * np.sqrt(1 + a * a)
                    b2 = b - d * np.sqrt(1 + a * a)
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l_current = 0
                    l = 0
                    while l_current <= ls:
                        x = pA[0] + inc * (l + l0) / np.sqrt(1 + a * a)
                        y = a * x + b
                        l_current = np.sqrt((pA[0] - x) ** 2 + (pA[1] - y) ** 2)
                        if l_current <= ls:
                            b3 = y + 1 / a * x
                            x1 = (b3 - b1) * a / (1 + a * a)
                            x2 = (b3 - b2) * a / (1 + a * a)
                            y1 = a * x1 + b1
                            y2 = a * x2 + b2
                            p1 = (int(x1), int(y1))
                            p2 = (int(x2), int(y2))
                            cv2.line(img, p1, p2, col, 2)
                            k += 1
                            l += li * r**k
                        else:
                            l0 = l_current - ls
        return img

    def display_scale_ratio(self, pos_xy, img):
        r = self.scale_ratio_var.get()
        l0 = self.scale_init_length_var.get()
        col = (self.color_scale[2], self.color_scale[1], self.color_scale[0])
        if len(pos_xy) >= 2:
            d = 5
            n = self.scale_length_var.get()
            for i in range(len(pos_xy) - 1):
                if pos_xy[i][0] == pos_xy[i + 1][0]:
                    x = pos_xy[i][0]
                    if pos_xy[i][1] < pos_xy[i + 1][1]:
                        pA = (x, pos_xy[i][1])
                        pB = (x, pos_xy[i + 1][1])
                    else:
                        pB = (x, pos_xy[i][1])
                        pA = (x, pos_xy[i + 1][1])
                    cv2.line(img, pA, pB, col, 2)
                    le = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l = int(le / n)
                    for i in range(n + 1):
                        p1 = (x - d, pA[1] + i * l)
                        p2 = (x + d, pA[1] + i * l)
                        cv2.line(img, p1, p2, col, 2)
                elif pos_xy[i][1] == pos_xy[i + 1][1]:
                    y = pos_xy[i][1]
                    if pos_xy[i][0] < pos_xy[i + 1][0]:
                        pA = (pos_xy[i][0], y)
                        pB = (pos_xy[i + 1][0], y)
                    else:
                        pB = (pos_xy[i][0], y)
                        pA = (pos_xy[i + 1][0], y)
                    cv2.line(img, pA, pB, col, 2)
                    le = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l = int(le / n)
                    for i in range(n + 1):
                        p1 = (pA[0] + i * l, y - d)
                        p2 = (pA[0] + i * l, y + d)
                        cv2.line(img, p1, p2, (255, 255, 255), 2)
                else:
                    pA = (pos_xy[i][0], pos_xy[i][1])
                    pB = (pos_xy[i + 1][0], pos_xy[i + 1][1])
                    if pos_xy[i][0] < pos_xy[i + 1][0]:
                        inc = 1
                    else:
                        inc = -1
                    a = (pA[1] - pB[1]) / (pA[0] - pB[0])
                    b = pA[1] - a * pA[0]
                    b1 = b + d * np.sqrt(1 + a * a)
                    b2 = b - d * np.sqrt(1 + a * a)
                    cv2.line(img, pA, pB, col, 2)
                    le = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    if r == 1:
                        l = int(le / n)
                        for i in range(n + 1):
                            x = pA[0] + l * i / np.sqrt(1 + a * a)
                            y = a * x + b
                            b3 = y + 1 / a * x
                            x1 = (b3 - b1) * a / (1 + a * a)
                            x2 = (b3 - b2) * a / (1 + a * a)
                            y1 = a * x1 + b1
                            y2 = a * x2 + b2
                            p1 = (int(x1), int(y1))
                            p2 = (int(x2), int(y2))
                            cv2.line(img, p1, p2, col, 2)
                    else:
                        ls = 0
                        i = 0
                        while ls <= le:
                            l = l0 * r**i
                            x = pA[0] + inc * l * i / np.sqrt(1 + a * a)
                            y = a * x + b
                            ls = np.sqrt((pA[0] - x) ** 2 + (pA[1] - y) ** 2)
                            if ls <= le:
                                b3 = y + 1 / a * x
                                x1 = (b3 - b1) * a / (1 + a * a)
                                x2 = (b3 - b2) * a / (1 + a * a)
                                y1 = a * x1 + b1
                                y2 = a * x2 + b2
                                p1 = (int(x1), int(y1))
                                p2 = (int(x2), int(y2))
                                cv2.line(img, p1, p2, col, 2)
                                i += 1

        return img

    def display_sequence(self):
        if len(self.sequence) > 0:
            output = self.sequence[self.current_seq_frame].copy()
            output = cv2.putText(
                output,
                str(self.current_seq_frame + 1) + "/" + str(len(self.sequence)),
                (10, 30),
                self.font,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow(
                "Sequence",
                cv2.resize(
                    output,
                    (
                        int(self.width * self.scale_scale.get() / 10),
                        int(self.height * self.scale_scale.get() / 10),
                    ),
                ),
            )

    def display_sequence_strip(self):
        center = len(self.sequence) - self.shift_strip - 1
        if len(self.sequence) > 0:
            half_w = 2
            w = int(self.width * 2 / 10)
            h = int(self.height * 2 / 10)
            blank = np.zeros((h, w, 3), dtype=np.uint8)
            f_resized = []
            for i in range(center - half_w, center + half_w + 1):
                if i < 0:
                    f_resized.append(blank)
                elif i >= len(self.sequence):
                    f_resized.append(blank)
                else:
                    output = cv2.putText(
                        self.sequence[i].copy(),
                        str(i + 1),
                        (10, 80),
                        self.font,
                        3,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )
                    f_resized.append(
                        cv2.resize(
                            output,
                            (
                                w,
                                h,
                            ),
                        )
                    )
            hcon = cv2.hconcat(f_resized)
            cv2.imshow("strip", hcon)

    #########################
    ##   GUI interactions  ##
    #########################

    def change_scale(self, val):
        """Change the size of displays (zoom)"""
        self.scale_value_text.configure(text=str(int(float(val)) * 10) + "%")

    def set_value(self, name):
        """Set values (general method for widgets)"""
        match name:
            case "color_scale":
                for i in range(3):
                    self.color_scale[i] = self.color_scale_var[i].get()
                rgb = self.rgbtohex(self.color_scale)
                self.color_scale_canvas.config(bg=rgb)
            case "exp":
                self.auto_expo.set(False)
                self.camera.set_exposure(self.exposure_var.get())
            case "auto_exp":
                self.camera.auto_exp = self.auto_expo.get()
                self.camera.exposure_auto()
            case "seq_name":
                self.sequence = []
                self.current_seq_frame = 0
                self.shift_strip = 0
                self.seq_name = self.set_seq_name_entry.get()
                if self.seq_name == "":
                    now = datetime.now()
                    date_time = now.strftime("%Y%m%d_%H%M%S")
                    self.seq_name = date_time
                self.d_folder = os.path.join(self.data_path, self.seq_name)
                if not os.path.exists(self.d_folder):
                    os.makedirs(self.d_folder)
            case "seq_next":
                self.current_seq_frame += 1
                if self.current_seq_frame >= len(self.sequence):
                    self.current_seq_frame = len(self.sequence) - 1
            case "seq_prev":
                self.current_seq_frame -= 1
                if self.current_seq_frame < 0:
                    self.current_seq_frame = 0
            case "strip_next":
                self.shift_strip -= 1
            case "strip_prev":
                self.shift_strip += 1
            case "del_last":  # delete last point
                if len(self.scales) > 0:
                    self.scales.pop(-1)
                    self.scale_settings.pop(-1)
                if len(self.scales) > 0:
                    if self.selected_scale == len(self.scale_settings):
                        self.selected_scale -= 1
                        self.selected_scale_var.set(self.selected_scale)
                        self.set_value("selected_scale")
                else:
                    self.selected_scale = 0
                    self.selected_scale_var.set(self.selected_scale)
                    self.set_selected_scale_spin.config(state="disable")
            case "clear":  # clear points
                self.scales = []
                self.set_selected_scale_spin.config(state="disable")
                self.scale_settings = []
                self.selected_scale = 0
                self.selected_scale_var.set(self.selected_scale)
            case "selected_scale":
                self.selected_scale = self.selected_scale_var.get()
                self.selected_scale_ratio_var.set(
                    self.scale_settings[self.selected_scale][0]
                )
                self.selected_scale_init_length_var.set(
                    self.scale_settings[self.selected_scale][1]
                )
                self.selected_scale_length_var.set(
                    self.scale_settings[self.selected_scale][2]
                )
                self.color_selected_scale_var[0].set(
                    self.scale_settings[self.selected_scale][3][0]
                )
                self.color_selected_scale_var[1].set(
                    self.scale_settings[self.selected_scale][3][1]
                )
                self.color_selected_scale_var[2].set(
                    self.scale_settings[self.selected_scale][3][2]
                )
                for i in range(3):
                    self.color_selected_scale[i] = self.color_selected_scale_var[
                        i
                    ].get()
                rgb = self.rgbtohex(self.color_selected_scale)
                self.color_selected_scale_canvas.config(bg=rgb)
                self.selected_scale_inverted_var.set(
                    self.scale_settings[self.selected_scale][4]
                )
            case "selected_scale_length":
                self.scale_settings[self.selected_scale][
                    2
                ] = self.selected_scale_length_var.get()
            case "selected_scale_init_length":
                self.scale_settings[self.selected_scale][
                    1
                ] = self.selected_scale_init_length_var.get()
            case "selected_scale_ratio":
                self.scale_settings[self.selected_scale][
                    0
                ] = self.selected_scale_ratio_var.get()
            case "selected_invert":
                self.scale_settings[self.selected_scale][
                    4
                ] = self.selected_scale_inverted_var.get()
            case "color_selected_scale":
                for i in range(3):
                    self.color_selected_scale[i] = self.color_selected_scale_var[
                        i
                    ].get()
                rgb = self.rgbtohex(self.color_selected_scale)
                self.color_selected_scale_canvas.config(bg=rgb)
                self.scale_settings[self.selected_scale][3] = self.color_selected_scale


root = tk.Tk()
main()
root.mainloop()
