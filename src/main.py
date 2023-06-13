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
from paths import paths
from annotations import annotations
from enums import Mode, PathMotion, PathType


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
        self.win_height = 900
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
        columns = []
        for i in range(3):
            columns.append(ttk.Frame(self.parent, relief=tk.SUNKEN, borderwidth=1))
            columns[-1].grid(column=i, row=0, padx=2, pady=2)
        # settings display
        settings_frame = ttk.Frame(columns[0])
        settings_frame.grid(column=0, row=0, padx=2, pady=2)
        # scale
        scale_frame = ttk.Frame(settings_frame)
        scale_frame.grid(column=0, row=0, padx=2, pady=2)
        scale_text = ttk.Label(scale_frame, text="Displays scale")
        scale_text.grid(column=0, row=0, rowspan=2, padx=2, pady=2)
        self.scale_scale = ttk.Scale(
            scale_frame,
            from_=2,
            to=10,
            orient=tk.HORIZONTAL,
            command=self.change_scale,
            value=self.scale,
        )
        self.scale_scale.grid(column=1, row=0, padx=2, pady=2)
        self.scale_value_text = ttk.Label(
            scale_frame, text=str(self.scale_scale.get() * 10) + "%"
        )
        self.scale_value_text.grid(column=1, row=1, padx=2, pady=2)
        # exposure
        exposure_frame = ttk.Frame(settings_frame)
        exposure_frame.grid(column=0, row=2, columnspan=2, pady=2)
        exposure_text = ttk.Label(exposure_frame, text="Exposure")
        exposure_text.grid(column=0, row=0, padx=2, pady=2)
        # self.auto_expo_var = tk.BooleanVar(value=False)
        exposure_auto_chk = ttk.Checkbutton(
            exposure_frame,
            variable=self.auto_exp_var,
            command=lambda: self.set_value("auto_exp"),
            text="auto",
        )
        self.auto_exp_var.set(self.camera.auto_exp)
        exposure_auto_chk.grid(column=0, row=1, padx=2, pady=2)
        self.exposure_var = tk.IntVar(value=self.camera.exposure)
        set_exposure_spin = ttk.Spinbox(
            exposure_frame,
            from_=-13,
            to=-1,
            increment=1,
            textvariable=self.exposure_var,
            command=lambda: self.set_value("exp"),
            font=self.tk_font,
            width=5,
        )
        set_exposure_spin.grid(column=0, row=2, padx=2, pady=2)
        # onion
        onion_frame = ttk.Frame(settings_frame)
        onion_frame.grid(column=0, row=3, columnspan=2, pady=2)
        r = 0
        onion_text = ttk.Label(onion_frame, text="Onion skin")
        onion_text.grid(column=0, row=r, columnspan=2, padx=2, pady=2)
        r += 1
        # self.enable_onion_var = tk.BooleanVar(value=True)
        onion_chk = ttk.Checkbutton(
            onion_frame,
            variable=self.enable_onion_var,
            command=lambda: self.set_value("enable_onion"),
            text="enabled",
        )
        onion_chk.grid(column=0, row=r, columnspan=2, padx=2, pady=2)
        r += 1
        # self.opacity_var = tk.IntVar(value=50)
        opacity_text = ttk.Label(onion_frame, text="opacity")
        opacity_text.grid(column=0, row=r, padx=2, pady=2)
        set_opacity_spin = ttk.Spinbox(
            onion_frame,
            from_=0,
            to=100,
            increment=1,
            textvariable=self.opacity_var,
            command=lambda: self.set_value("opacity"),
            font=self.tk_font,
            width=5,
        )
        set_opacity_spin.grid(column=1, row=r, padx=2, pady=2)
        r += 1
        # self.n_onion_var = tk.IntVar(value=2)
        n_onion_text = ttk.Label(onion_frame, text="n")
        n_onion_text.grid(column=0, row=r, padx=2, pady=2)
        set_n_onion_spin = ttk.Spinbox(
            onion_frame,
            from_=1,
            to=10,
            increment=1,
            textvariable=self.n_onion_var,
            command=lambda: self.set_value("n_onion"),
            font=self.tk_font,
            width=5,
        )
        set_n_onion_spin.grid(column=1, row=r, padx=2, pady=2)
        # sequence
        seq_frame = ttk.Frame(settings_frame)
        seq_frame.grid(column=0, row=4, columnspan=2, pady=2)
        seq_text = ttk.Label(seq_frame, text="Sequence")
        seq_text.grid(column=0, row=0, columnspan=2, padx=2, pady=2)
        seq_name_text = ttk.Label(seq_frame, text="Seq. name" + ": ")
        seq_name_text.grid(column=0, row=1, padx=2, pady=2)
        self.set_seq_name_entry = ttk.Entry(seq_frame)
        self.set_seq_name_entry.grid(column=1, row=1, padx=2, pady=2)
        seq_name_btn = ttk.Button(
            seq_frame, text="Set", command=lambda: self.set_value("seq_name")
        )
        seq_name_btn.grid(column=0, row=2, columnspan=2, padx=2, pady=2)
        # arduino
        arduino_use_chk = ttk.Checkbutton(
            settings_frame,
            variable=self.use_arduino_var,
            command=lambda: self.set_value("use_arduino"),
            text="arduino",
        )
        arduino_use_chk.grid(column=0, row=5, padx=2, pady=2)
        # buttons
        btn_frame = ttk.Frame(columns[0])
        btn_frame.grid(column=0, row=1, pady=2)
        acq_btn = ttk.Button(
            btn_frame, text="Acquisition [a]", command=self.capture_frame
        )
        r = 0
        acq_btn.grid(column=0, row=r, columnspan=2, padx=2, pady=2)
        r += 1
        delete_btn = ttk.Button(btn_frame, text="Delete [d]", command=self.delete_frame)
        delete_btn.grid(column=0, row=r, columnspan=2, padx=2, pady=2)
        r += 1
        prev_btn = ttk.Button(
            btn_frame, text=" Seq. prev [<]", command=lambda: self.set_value("seq_prev")
        )
        prev_btn.grid(column=0, row=r, padx=2, pady=2)
        next_btn = ttk.Button(
            btn_frame, text=" Seq. next [>]", command=lambda: self.set_value("seq_next")
        )
        next_btn.grid(column=1, row=r, padx=2, pady=2)
        r += 1
        prev_btn = ttk.Button(
            btn_frame,
            text=" Strip prev [n]",
            command=lambda: self.set_value("strip_prev"),
        )
        prev_btn.grid(column=0, row=r, padx=2, pady=2)
        next_btn = ttk.Button(
            btn_frame,
            text=" Strip next [m]",
            command=lambda: self.set_value("strip_next"),
        )
        next_btn.grid(column=1, row=r, padx=2, pady=2)
        r += 1
        # quit button
        self.style.configure("quit.TButton", font=("Helvetica", 20), foreground="red")
        self.quit_btn = ttk.Button(
            btn_frame, text="Quit", command=self.quit, style="quit.TButton"
        )
        self.quit_btn.grid(column=0, row=r, columnspan=2, padx=2, pady=2)
        # modes
        mode_frame = ttk.Frame(columns[1])
        mode_frame.grid(column=0, row=0, pady=2)
        self.mode_var = tk.IntVar(value=self.mode.value)
        mode_rdbtn = []
        txt = ["path", "Annotation"]
        for i in range(len(txt)):
            mode_rdbtn.append(
                ttk.Radiobutton(
                    mode_frame,
                    text=txt[i],
                    variable=self.mode_var,
                    value=i,
                    command=lambda: self.set_value("mode"),
                )
            )
            mode_rdbtn[-1].grid(column=0, row=i + 1, pady=2)
        r = len(txt) + 1
        del_last_btn = ttk.Button(
            mode_frame,
            text="Delete last [x]",
            command=lambda: self.set_value("del_last"),
        )
        del_last_btn.grid(column=0, row=r, padx=2, pady=2)
        r += 1
        clear_btn = ttk.Button(
            mode_frame, text="Clear [c]", command=lambda: self.set_value("clear")
        )
        clear_btn.grid(column=0, row=r, padx=2, pady=2)
        r += 1
        draw_color_frame = ttk.Frame(mode_frame, relief=tk.SUNKEN, borderwidth=1)
        draw_color_frame.grid(column=0, row=r, padx=10, pady=2)
        rgb = self.rgbtohex(self.draw_color)
        self.draw_color_canvas = tk.Canvas(
            draw_color_frame, bg=rgb, width=100, height=50
        )
        self.draw_color_canvas.grid(column=0, row=0, rowspan=3, padx=2, pady=2)
        draw_color_R_label = ttk.Label(draw_color_frame, text="R")
        draw_color_R_label.grid(column=1, row=0, padx=2, pady=2)
        self.draw_color_var = []
        self.draw_color_var.append(tk.IntVar())
        draw_color_R_spin = ttk.Spinbox(
            draw_color_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.draw_color_var[0],
            command=lambda: self.set_value("draw_color"),
            font=self.tk_font,
        )
        draw_color_R_spin.grid(column=2, row=0, padx=2, pady=2)
        self.draw_color_var[0].set(self.draw_color[0])
        draw_color_G_label = ttk.Label(draw_color_frame, text="G")
        draw_color_G_label.grid(column=1, row=1, padx=2, pady=2)
        self.draw_color_var.append(tk.IntVar())
        draw_color_G_spin = ttk.Spinbox(
            draw_color_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.draw_color_var[1],
            command=lambda: self.set_value("draw_color"),
            font=self.tk_font,
        )
        draw_color_G_spin.grid(column=2, row=1, padx=2, pady=2)
        self.draw_color_var[1].set(self.draw_color[1])
        draw_color_B_label = ttk.Label(draw_color_frame, text="B")
        draw_color_B_label.grid(column=1, row=2, padx=2, pady=2)
        self.draw_color_var.append(tk.IntVar())
        draw_color_B_spin = ttk.Spinbox(
            draw_color_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.draw_color_var[2],
            command=lambda: self.set_value("draw_color"),
            font=self.tk_font,
        )
        draw_color_B_spin.grid(column=2, row=2, padx=2, pady=2)
        self.draw_color_var[2].set(self.draw_color[2])
        # paths
        paths_frame = ttk.Frame(columns[1], relief=tk.SUNKEN, borderwidth=1)
        paths_frame.grid(column=0, row=1, pady=2)
        r = 0
        path_text = ttk.Label(paths_frame, text="paths")
        path_text.grid(column=0, row=r, columnspan=2, padx=2, pady=2)
        r += 1
        path_length_text = ttk.Label(paths_frame, text="Number:")
        path_length_text.grid(column=0, row=r, padx=2, pady=2)
        # self.path_segments_var = tk.IntVar(value=5)
        set_path_length_spin = ttk.Spinbox(
            paths_frame,
            from_=1,
            to=100,
            increment=1,
            textvariable=self.path_segments_var,
            command=lambda: self.set_value("path_length"),
            font=self.tk_font,
            width=6,
        )
        set_path_length_spin.grid(column=1, row=r, padx=2, pady=2)
        r += 1
        path_init_length_text = ttk.Label(paths_frame, text="Initial (px):")
        path_init_length_text.grid(column=0, row=r, padx=2, pady=2)
        # self.path_min_length_var = tk.IntVar(value=2)
        set_path_init_length_spin = ttk.Spinbox(
            paths_frame,
            from_=1,
            to=50,
            increment=1,
            textvariable=self.path_min_length_var,
            command=lambda: self.set_value("path_init_length"),
            font=self.tk_font,
            width=6,
        )
        set_path_init_length_spin.grid(column=1, row=r, padx=2, pady=2)
        r += 1
        path_ratio_text = ttk.Label(paths_frame, text="Ratio:")
        path_ratio_text.grid(column=0, row=r, padx=2, pady=2)
        # self.path_ratio_var = tk.DoubleVar(value=1.2)
        set_path_ratio_spin = ttk.Spinbox(
            paths_frame,
            from_=1,
            to=10,
            increment=0.1,
            textvariable=self.path_ratio_var,
            command=lambda: self.set_value("path_ratio"),
            font=self.tk_font,
            width=6,
        )
        set_path_ratio_spin.grid(column=1, row=r, padx=2, pady=2)
        r += 1
        # self.path_inverted_var = tk.BooleanVar(value=False)
        path_inverted_chk = ttk.Checkbutton(
            paths_frame,
            variable=self.path_inverted_var,
            command=lambda: self.set_value("invert"),
            text="Inverted",
        )
        path_inverted_chk.grid(column=0, row=r, columnspan=2, padx=2, pady=2)
        r += 1

        # selected path
        selected_path_frame = ttk.Frame(columns[1], relief=tk.SUNKEN, borderwidth=1)
        selected_path_frame.grid(column=0, row=2, pady=2)
        r = 0
        selected_path_text = ttk.Label(selected_path_frame, text="Selected path")
        selected_path_text.grid(column=0, row=r, columnspan=2, padx=2, pady=2)
        r += 1
        self.selected_path_var = tk.IntVar(value=0)
        self.set_selected_path_spin = ttk.Spinbox(
            selected_path_frame,
            from_=0,
            to=0,
            increment=1,
            textvariable=self.selected_path_var,
            command=lambda: self.set_value("selected_path"),
            font=self.tk_font,
            width=6,
        )
        self.set_selected_path_spin.grid(column=0, row=r, columnspan=2, padx=2, pady=2)
        r += 1
        selected_path_length_text = ttk.Label(selected_path_frame, text="Number:")
        selected_path_length_text.grid(column=0, row=r, padx=2, pady=2)
        self.selected_path_segments_var = tk.IntVar(value=0)
        set_selected_path_length_spin = ttk.Spinbox(
            selected_path_frame,
            from_=0,
            to=100,
            increment=1,
            textvariable=self.selected_path_segments_var,
            command=lambda: self.set_value("selected_path_segments"),
            font=self.tk_font,
            width=6,
        )
        set_selected_path_length_spin.grid(column=1, row=r, padx=2, pady=2)
        r += 1
        selected_path_init_length_text = ttk.Label(
            selected_path_frame, text="Initial (px):"
        )
        selected_path_init_length_text.grid(column=0, row=r, padx=2, pady=2)
        self.selected_path_min_length_var = tk.IntVar(value=0)
        set_selected_path_init_length_spin = ttk.Spinbox(
            selected_path_frame,
            from_=1,
            to=50,
            increment=1,
            textvariable=self.selected_path_min_length_var,
            command=lambda: self.set_value("selected_path_min_length"),
            font=self.tk_font,
            width=6,
        )
        set_selected_path_init_length_spin.grid(column=1, row=r, padx=2, pady=2)
        r += 1
        selected_path_ratio_text = ttk.Label(selected_path_frame, text="Ratio:")
        selected_path_ratio_text.grid(column=0, row=r, padx=2, pady=2)
        self.selected_path_ratio_var = tk.DoubleVar(value=1)
        set_selected_path_ratio_spin = ttk.Spinbox(
            selected_path_frame,
            from_=1,
            to=10,
            increment=0.1,
            textvariable=self.selected_path_ratio_var,
            command=lambda: self.set_value("selected_path_ratio"),
            font=self.tk_font,
            width=6,
        )
        set_selected_path_ratio_spin.grid(column=1, row=r, padx=2, pady=2)
        r += 1
        self.selected_path_inverted_var = tk.BooleanVar(value=False)
        selected_path_inverted_chk = ttk.Checkbutton(
            selected_path_frame,
            variable=self.selected_path_inverted_var,
            command=lambda: self.set_value("selected_invert"),
            text="Inverted",
        )
        selected_path_inverted_chk.grid(column=0, row=r, columnspan=2, padx=2, pady=2)
        r += 1
        color_selected_path_frame = ttk.Frame(
            selected_path_frame, relief=tk.SUNKEN, borderwidth=1
        )
        color_selected_path_frame.grid(column=0, row=r, columnspan=2, padx=10, pady=2)
        rgb = self.rgbtohex(self.color_selected_path)
        self.color_selected_path_canvas = tk.Canvas(
            color_selected_path_frame, bg=rgb, width=100, height=50
        )
        self.color_selected_path_canvas.grid(column=0, row=0, rowspan=3, padx=2, pady=2)
        color_selected_path_R_label = ttk.Label(color_selected_path_frame, text="R")
        color_selected_path_R_label.grid(column=1, row=0, padx=2, pady=2)
        self.color_selected_path_var = []
        self.color_selected_path_var.append(tk.IntVar())
        color_selected_path_R_spin = ttk.Spinbox(
            color_selected_path_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.color_selected_path_var[0],
            command=lambda: self.set_value("color_selected_path"),
            font=self.tk_font,
        )
        color_selected_path_R_spin.grid(column=2, row=0, padx=2, pady=2)
        self.color_selected_path_var[0].set(self.color_selected_path[0])
        color_selected_path_G_label = ttk.Label(color_selected_path_frame, text="G")
        color_selected_path_G_label.grid(column=1, row=1, padx=2, pady=2)
        self.color_selected_path_var.append(tk.IntVar())
        color_selected_path_G_spin = ttk.Spinbox(
            color_selected_path_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.color_selected_path_var[1],
            command=lambda: self.set_value("color_selected_path"),
            font=self.tk_font,
        )
        color_selected_path_G_spin.grid(column=2, row=1, padx=2, pady=2)
        self.color_selected_path_var[1].set(self.color_selected_path[1])
        color_selected_path_B_label = ttk.Label(color_selected_path_frame, text="B")
        color_selected_path_B_label.grid(column=1, row=2, padx=2, pady=2)
        self.color_selected_path_var.append(tk.IntVar())
        color_selected_path_B_spin = ttk.Spinbox(
            color_selected_path_frame,
            from_=0,
            to=255,
            increment=1,
            width=8,
            textvariable=self.color_selected_path_var[2],
            command=lambda: self.set_value("color_selected_path"),
            font=self.tk_font,
        )
        color_selected_path_B_spin.grid(column=2, row=2, padx=2, pady=2)
        self.color_selected_path_var[2].set(self.color_selected_path[2])
        self.set_selected_path_spin.configure(state="disable")

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
        self.paths = paths.Paths()
        self.annos = annotations.Annotations()
        self.new_path = False
        self.new_annotation = False
        self.mouse_coords = []
        self.mouse_coords_annotation = []
        self.mouse_coords_annotations = []
        self.color_selected_path = [255, 255, 255]
        self.selected_path = 0
        self.mode = Mode.PATH
        self.drawing = False
        self.path_end = False
        self.read_config()
        # self.camera = camera.Camera(w=self.width, h=self.height)
        self.camera.start_stream(0)
        cv2.namedWindow("Monitoring", cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback("Monitoring", self.mouse_click)
        if self.use_arduino_var.get():
            self.arduino = arduino.Arduino(self.port)
        # cv2.imshow("strip", np.zeros((10, 10, 3), dtype=np.uint8))

    def quit(self):
        """Quit"""
        self.save_config()
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
                    self.update_paths()
                    self.update_annotations()
                    self.display_capture()
            if self.use_arduino_var.get():
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
                if self.mode == 0:
                    if len(self.paths) > 0:
                        self.paths.pop(-1)
                        self.path_settings.pop(-1)
                    if len(self.paths) > 0:
                        if self.selected_path == len(self.path_settings):
                            self.selected_path -= 1
                            self.selected_path_var.set(self.selected_path)
                            self.set_value("selected_path")
                    else:
                        self.selected_path = 0
                        self.selected_path_var.set(self.selected_path)
                        self.set_selected_path_spin.config(state="disable")
                elif self.mode == 1:
                    if len(self.mouse_coords_annotations) > 0:
                        self.mouse_coords_annotations.pop(-1)
            elif k == ord("c"):  # clear points
                if self.mode == 0:
                    self.paths = []
                    self.set_selected_path_spin.config(state="disable")
                    self.path_settings = []
                    self.selected_path = 0
                    self.selected_path_var.set(self.selected_path)
                    self.current_path = []
                elif self.mode == 1:
                    self.mouse_coords_annotation = []
                    self.mouse_coords_annotations = []
            elif k == ord("o"):  # double click
                self.new_path = True
                self.mouse_coords = []
                self.paths.append(self.current_path)
                self.path_settings.append(
                    [
                        self.path_ratio_var.get(),
                        self.path_min_length_var.get(),
                        self.path_segments_var.get(),
                        self.draw_color.copy(),
                    ]
                )
                self.current_path = []
            # continue loop
            self.parent.after(2, self.loop)

    def update_paths(self):
        if self.mode == Mode.PATH:
            if self.path_end:
                self.path_end = False
                self.set_selected_path_spin.config(state="normal")
                self.selected_path_var.set(len(self.paths.paths) - 1)
                self.set_value("selected_path")
                self.set_selected_path_spin.config(to=len(self.paths.paths) - 1)
            if self.new_path:
                self.new_path = False
                r = self.path_ratio_var.get()
                if r == 1:
                    type = PathType.LINEAR
                    motion = PathMotion.CONST
                elif r == 2:
                    type = PathType.HALF
                    motion = PathMotion.ACC
                else:
                    type = PathType.RATIO
                    motion = PathMotion.ACC
                if type == PathType.RATIO or type == PathType.HALF:
                    if self.path_inverted_var.get():
                        motion = PathMotion.DEC
                self.paths.new_path(
                    r,
                    self.path_min_length_var.get(),
                    self.path_segments_var.get(),
                    self.draw_color.copy(),
                    type,
                    motion,
                )
                self.paths.append_pos(self.mouse_coords)

    def update_annotations(self):
        if self.mode == Mode.ANNO:
            if self.new_annotation:
                self.new_annotation = False
                self.annos.new_annotation(
                    self.draw_color.copy(),
                )
                self.annos.append_pos(self.mouse_coords)
                self.drawing = True

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
                        # parameters
                        mode = config.get("parameters", {}).get("mode")
                        match mode:
                            case 0:
                                self.mode = Mode.PATH
                            case 1:
                                self.mode = Mode.ANNO
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
                        # paths
                        self.path_ratio_var = tk.DoubleVar(value=1)
                        self.path_ratio_var.set(config.get("paths", {}).get("ratio"))
                        self.path_min_length_var = tk.IntVar(value=10)
                        self.path_min_length_var.set(
                            config.get("paths", {}).get("min_l")
                        )
                        self.path_segments_var = tk.IntVar(value=5)
                        self.path_segments_var.set(config.get("paths", {}).get("n"))
                        self.path_inverted_var = tk.BooleanVar(value=False)
                        self.path_inverted_var.set(
                            config.get("paths", {}).get("invert")
                        )
                        self.draw_color = config.get("paths", {}).get("color")
                        # onion
                        self.enable_onion_var = tk.BooleanVar(value=True)
                        self.enable_onion_var.set(config.get("onion", {}).get("enable"))
                        self.opacity_var = tk.IntVar(value=50)
                        self.opacity_var.set(config.get("onion", {}).get("opacity"))
                        self.n_onion_var = tk.IntVar(value=2)
                        self.n_onion_var.set(config.get("onion", {}).get("n"))
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
        # parameters
        config["parameters"] = {}
        config["parameters"]["mode"] = self.mode.value
        # paths
        config["paths"] = {}
        config["paths"]["ratio"] = self.path_ratio_var.get()
        config["paths"]["min_l"] = self.path_min_length_var.get()
        config["paths"]["n"] = self.path_segments_var.get()
        config["paths"]["color"] = [
            self.draw_color_var[0].get(),
            self.draw_color_var[1].get(),
            self.draw_color_var[2].get(),
        ]
        config["paths"]["invert"] = self.path_inverted_var.get()
        # onion
        config["onion"] = {}
        config["onion"]["n"] = self.n_onion_var.get()
        config["onion"]["opacity"] = self.opacity_var.get()
        config["onion"]["enable"] = self.enable_onion_var.get()
        # camera
        config["camera"] = {}
        config["camera"]["source"] = self.camera.source
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
            if self.mode == Mode.PATH:
                if self.paths.new:
                    self.new_path = True
                    self.mouse_coords = [
                        int(x * 10 / self.scale),
                        int(y * 10 / self.scale),
                    ]
                else:
                    self.paths.append_pos(
                        [int(x * 10 / self.scale), int(y * 10 / self.scale)]
                    )
            elif self.mode == Mode.ANNO:
                if self.annos.new:
                    self.new_annotation = True
                    self.mouse_coords = [
                        int(x * 10 / self.scale),
                        int(y * 10 / self.scale),
                    ]
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            if self.mode == Mode.PATH:
                self.paths.end_path()
                self.path_end = True
                self.mouse_coords = []
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.mode == Mode.PATH:
                if not self.paths.new:
                    self.mouse_coords = [
                        int(x * 10 / self.scale),
                        int(y * 10 / self.scale),
                    ]
            elif self.mode == Mode.ANNO:
                if self.drawing:
                    self.annos.append_pos(
                        [int(x * 10 / self.scale), int(y * 10 / self.scale)]
                    )
        elif event == cv2.EVENT_LBUTTONUP:
            if self.mode == Mode.ANNO:
                self.drawing = False
                self.annos.end_annotation()
                self.mouse_coords = []

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
        # onion skin
        if self.enable_onion_var.get():
            n_onion = self.n_onion_var.get()
            output = self.frame.copy()
            if len(self.sequence) > 0:
                n_onion = min(n_onion, len(self.sequence))
                alpha = self.opacity_var.get() / 100
                for i in range(n_onion):
                    output = cv2.addWeighted(
                        output,
                        1 - alpha ** (i + 1),
                        self.sequence[-(i + 1)],
                        alpha ** (i + 1),
                        0,
                    )
            else:
                output = self.frame.copy()
        else:
            output = self.frame.copy()
        # paths
        output = self.paths.display_current_path(output, self.mouse_coords)
        output = self.paths.display_paths(output)
        # annotations
        output = self.annos.display_current_annotation(output)
        output = self.annos.display_annotations(output)
        # resulting image
        cv2.imshow(
            "Monitoring",
            cv2.resize(
                output,
                (
                    int(self.width * self.scale / 10),
                    int(self.height * self.scale / 10),
                ),
            ),
        )

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
        self.scale = int(float(val))
        self.scale_value_text.configure(text=str(self.scale * 10) + "%")

    def set_value(self, name):
        """Set values (general method for widgets)"""
        match name:
            case "mode":
                mode = self.mode_var.get()
                match mode:
                    case 0:
                        self.mode = Mode.PATH
                    case 1:
                        self.mode = Mode.ANNO
            case "use_arduino":
                if self.use_arduino_var.get():
                    self.arduino = arduino.Arduino(self.port)
            case "draw_color":
                for i in range(3):
                    self.draw_color[i] = self.draw_color_var[i].get()
                rgb = self.rgbtohex(self.draw_color)
                self.draw_color_canvas.config(bg=rgb)
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
                if self.mode == Mode.PATH:
                    if len(self.paths.paths) > 0:
                        self.paths.paths.pop(-1)
                    if len(self.paths.paths) > 0:
                        if self.selected_path == len(self.paths.paths):
                            self.selected_path -= 1
                            self.selected_path_var.set(self.selected_path)
                            self.set_value("selected_path")
                    else:
                        self.selected_path = 0
                        self.selected_path_var.set(self.selected_path)
                        self.set_selected_path_spin.config(state="disable")
                elif self.mode == Mode.ANNO:
                    if len(self.annos.annos) > 0:
                        self.annos.annos.pop(-1)
            case "clear":  # clear points
                if self.mode == Mode.PATH:
                    self.paths.paths = []
                    self.set_selected_path_spin.config(state="disable")
                    self.selected_path = 0
                    self.selected_path_var.set(self.selected_path)
                elif self.mode == 1:
                    self.annos.annos = []
            case "selected_path":
                self.selected_path = self.selected_path_var.get()
                self.selected_path_ratio_var.set(
                    self.paths.paths[self.selected_path].ratio
                )
                self.selected_path_min_length_var.set(
                    self.paths.paths[self.selected_path].min_length
                )
                self.selected_path_segments_var.set(
                    self.paths.paths[self.selected_path].segments
                )
                self.color_selected_path_var[0].set(
                    self.paths.paths[self.selected_path].color[0]
                )
                self.color_selected_path_var[1].set(
                    self.paths.paths[self.selected_path].color[1]
                )
                self.color_selected_path_var[2].set(
                    self.paths.paths[self.selected_path].color[2]
                )
                for i in range(3):
                    self.color_selected_path[i] = self.color_selected_path_var[i].get()
                rgb = self.rgbtohex(self.color_selected_path)
                self.color_selected_path_canvas.config(bg=rgb)
                if self.paths.paths[self.selected_path].motion == PathMotion.DEC:
                    self.selected_path_inverted_var.set(True)
                else:
                    self.selected_path_inverted_var.set(False)
            case "selected_path_segments":
                self.paths.paths[
                    self.selected_path
                ].segments = self.selected_path_segments_var.get()
            case "selected_path_min_length":
                self.paths.paths[
                    self.selected_path
                ].min_length = self.selected_path_min_length_var.get()
            case "selected_path_ratio":
                r = self.selected_path_ratio_var.get()
                self.paths.paths[self.selected_path].ratio = r
                if r == 1:
                    self.paths.paths[self.selected_path].type = PathType.LINEAR
                elif r == 2:
                    self.paths.paths[self.selected_path].type = PathType.HALF
                else:
                    self.paths.paths[self.selected_path].type = PathType.RATIO
            case "selected_invert":
                if self.selected_path_inverted_var.get():
                    self.paths.paths[self.selected_path].motion = PathMotion.DEC
                else:
                    self.paths.paths[self.selected_path].motion = PathMotion.ACC
                if self.paths.paths[self.selected_path].ratio == 1:
                    self.paths.paths[self.selected_path].motion = PathMotion.CONST
            case "color_selected_path":
                for i in range(3):
                    self.color_selected_path[i] = self.color_selected_path_var[i].get()
                rgb = self.rgbtohex(self.color_selected_path)
                self.color_selected_path_canvas.config(bg=rgb)
                self.paths.paths[
                    self.selected_path
                ].color = self.color_selected_path.copy()


root = tk.Tk()
main()
root.mainloop()
