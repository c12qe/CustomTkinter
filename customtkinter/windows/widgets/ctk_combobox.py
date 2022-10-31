import tkinter
import sys
from typing import Union, Tuple, Callable, List

from .core_widget_classes.dropdown_menu import DropdownMenu
from .core_rendering.ctk_canvas import CTkCanvas
from .theme.theme_manager import ThemeManager
from .core_rendering.draw_engine import DrawEngine
from .core_widget_classes.widget_base_class import CTkBaseClass
from .font.ctk_font import CTkFont


class CTkComboBox(CTkBaseClass):
    """
    Combobox with dropdown menu, rounded corners, border, variable support.
    For detailed information check out the documentation.
    """

    def __init__(self,
                 master: any = None,
                 width: int = 140,
                 height: int = 28,
                 corner_radius: Union[int, str] = "default_theme",
                 border_width: Union[int, str] = "default_theme",

                 bg_color: Union[str, Tuple[str, str], None] = None,
                 fg_color: Union[str, Tuple[str, str]] = "default_theme",
                 border_color: Union[str, Tuple[str, str]] = "default_theme",
                 button_color: Union[str, Tuple[str, str]] = "default_theme",
                 button_hover_color: Union[str, Tuple[str, str]] = "default_theme",
                 dropdown_fg_color: Union[str, Tuple[str, str]] = "default_theme",
                 dropdown_hover_color: Union[str, Tuple[str, str]] = "default_theme",
                 dropdown_text_color: Union[str, Tuple[str, str]] = "default_theme",
                 text_color: Union[str, Tuple[str, str]] = "default_theme",
                 text_color_disabled: Union[str, Tuple[str, str]] = "default_theme",

                 font: Union[tuple, CTkFont] = "default_theme",
                 dropdown_font: Union[tuple, CTkFont] = "default_theme",
                 values: List[str] = None,
                 state: str = tkinter.NORMAL,
                 hover: bool = True,
                 variable: tkinter.Variable = None,
                 command: Callable = None,
                 justify: str = "left",
                 **kwargs):

        # transfer basic functionality (_bg_color, size, __appearance_mode, scaling) to CTkBaseClass
        super().__init__(master=master, bg_color=bg_color, width=width, height=height, **kwargs)

        # color variables
        self._fg_color = ThemeManager.theme["color"]["entry"] if fg_color == "default_theme" else fg_color
        self._border_color = ThemeManager.theme["color"]["combobox_border"] if border_color == "default_theme" else border_color
        self._button_color = ThemeManager.theme["color"]["combobox_border"] if button_color == "default_theme" else button_color
        self._button_hover_color = ThemeManager.theme["color"]["combobox_button_hover"] if button_hover_color == "default_theme" else button_hover_color

        # shape
        self._corner_radius = ThemeManager.theme["shape"]["button_corner_radius"] if corner_radius == "default_theme" else corner_radius
        self._border_width = ThemeManager.theme["shape"]["entry_border_width"] if border_width == "default_theme" else border_width

        # text and font
        self._text_color = ThemeManager.theme["color"]["text"] if text_color == "default_theme" else text_color
        self._text_color_disabled = ThemeManager.theme["color"]["text_disabled"] if text_color_disabled == "default_theme" else text_color_disabled

        # font
        self._font = CTkFont() if font == "default_theme" else self._check_font_type(font)
        if isinstance(self._font, CTkFont):
            self._font.add_size_configure_callback(self._update_font)

        # callback and hover functionality
        self._command = command
        self._variable = variable
        self._state = state
        self._hover = hover

        if values is None:
            self._values = ["CTkComboBox"]
        else:
            self._values = values

        self._dropdown_menu = DropdownMenu(master=self,
                                           values=self._values,
                                           command=self._dropdown_callback,
                                           fg_color=dropdown_fg_color,
                                           hover_color=dropdown_hover_color,
                                           text_color=dropdown_text_color,
                                           font=dropdown_font)

        # configure grid system (1x1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas = CTkCanvas(master=self,
                                 highlightthickness=0,
                                 width=self._apply_widget_scaling(self._desired_width),
                                 height=self._apply_widget_scaling(self._desired_height))
        self.draw_engine = DrawEngine(self._canvas)

        self._entry = tkinter.Entry(master=self,
                                    state=self._state,
                                    width=1,
                                    bd=0,
                                    justify=justify,
                                    highlightthickness=0,
                                    font=self._apply_font_scaling(self._font))

        self._create_grid()

        # insert default value
        if len(self._values) > 0:
            self._entry.insert(0, self._values[0])
        else:
            self._entry.insert(0, "CTkComboBox")

        self._draw()  # initial draw

        # event bindings
        self._canvas.tag_bind("right_parts", "<Enter>", self._on_enter)
        self._canvas.tag_bind("dropdown_arrow", "<Enter>", self._on_enter)
        self._canvas.tag_bind("right_parts", "<Leave>", self._on_leave)
        self._canvas.tag_bind("dropdown_arrow", "<Leave>", self._on_leave)
        self._canvas.tag_bind("right_parts", "<Button-1>", self._clicked)
        self._canvas.tag_bind("dropdown_arrow", "<Button-1>", self._clicked)

        if self._variable is not None:
            self._entry.configure(textvariable=self._variable)

    def _create_grid(self):
        self._canvas.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="nsew")

        left_section_width = self._current_width - self._current_height
        self._entry.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="ew",
                         padx=(max(self._apply_widget_scaling(self._corner_radius), self._apply_widget_scaling(3)),
                               max(self._apply_widget_scaling(self._current_width - left_section_width + 3), self._apply_widget_scaling(3))),
                         pady=self._apply_widget_scaling(self._border_width))

    def _set_scaling(self, *args, **kwargs):
        super()._set_scaling(*args, **kwargs)

        # change entry font size and grid padding
        self._entry.configure(font=self._apply_font_scaling(self._font))
        self._create_grid()

        self._canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                               height=self._apply_widget_scaling(self._desired_height))
        self._draw(no_color_updates=True)

    def _set_dimensions(self, width: int = None, height: int = None):
        super()._set_dimensions(width, height)

        self._canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                               height=self._apply_widget_scaling(self._desired_height))
        self._draw()

    def _update_font(self):
        """ pass font to tkinter widgets with applied font scaling and update grid with workaround """
        self._entry.configure(font=self._apply_font_scaling(self._font))

        # Workaround to force grid to be resized when text changes size.
        # Otherwise grid will lag and only resizes if other mouse action occurs.
        self._canvas.grid_forget()
        self._canvas.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="nsew")

    def destroy(self):
        if isinstance(self._font, CTkFont):
            self._font.remove_size_configure_callback(self._update_font)

        super().destroy()

    def _draw(self, no_color_updates=False):
        super()._draw(no_color_updates)

        left_section_width = self._current_width - self._current_height
        requires_recoloring = self.draw_engine.draw_rounded_rect_with_border_vertical_split(self._apply_widget_scaling(self._current_width),
                                                                                            self._apply_widget_scaling(self._current_height),
                                                                                            self._apply_widget_scaling(self._corner_radius),
                                                                                            self._apply_widget_scaling(self._border_width),
                                                                                            self._apply_widget_scaling(left_section_width))

        requires_recoloring_2 = self.draw_engine.draw_dropdown_arrow(self._apply_widget_scaling(self._current_width - (self._current_height / 2)),
                                                                     self._apply_widget_scaling(self._current_height / 2),
                                                                     self._apply_widget_scaling(self._current_height / 3))

        if no_color_updates is False or requires_recoloring or requires_recoloring_2:

            self._canvas.configure(bg=self._apply_appearance_mode(self._bg_color))

            self._canvas.itemconfig("inner_parts_left",
                                    outline=self._apply_appearance_mode(self._fg_color),
                                    fill=self._apply_appearance_mode(self._fg_color))
            self._canvas.itemconfig("border_parts_left",
                                    outline=self._apply_appearance_mode(self._border_color),
                                    fill=self._apply_appearance_mode(self._border_color))
            self._canvas.itemconfig("inner_parts_right",
                                    outline=self._apply_appearance_mode(self._border_color),
                                    fill=self._apply_appearance_mode(self._border_color))
            self._canvas.itemconfig("border_parts_right",
                                    outline=self._apply_appearance_mode(self._border_color),
                                    fill=self._apply_appearance_mode(self._border_color))

            self._entry.configure(bg=self._apply_appearance_mode(self._fg_color),
                                  fg=self._apply_appearance_mode(self._text_color),
                                  disabledbackground=self._apply_appearance_mode(self._fg_color),
                                  disabledforeground=self._apply_appearance_mode(self._text_color_disabled),
                                  highlightcolor=self._apply_appearance_mode(self._fg_color),
                                  insertbackground=self._apply_appearance_mode(self._text_color))

            if self._state == tkinter.DISABLED:
                self._canvas.itemconfig("dropdown_arrow",
                                        fill=self._apply_appearance_mode(self._text_color_disabled))
            else:
                self._canvas.itemconfig("dropdown_arrow",
                                        fill=self._apply_appearance_mode(self._text_color))

    def _open_dropdown_menu(self):
        self._dropdown_menu.open(self.winfo_rootx(),
                                 self.winfo_rooty() + self._apply_widget_scaling(self._current_height + 0))

    def configure(self, require_redraw=False, **kwargs):
        if "corner_radius" in kwargs:
            self._corner_radius = kwargs.pop("corner_radius")
            require_redraw = True

        if "border_width" in kwargs:
            self._border_width = kwargs.pop("border_width")
            self._create_grid()
            require_redraw = True

        if "fg_color" in kwargs:
            self._fg_color = kwargs.pop("fg_color")
            require_redraw = True

        if "border_color" in kwargs:
            self._border_color = kwargs.pop("border_color")
            require_redraw = True

        if "button_color" in kwargs:
            self._button_color = kwargs.pop("button_color")
            require_redraw = True

        if "button_hover_color" in kwargs:
            self._button_hover_color = kwargs.pop("button_hover_color")
            require_redraw = True

        if "dropdown_fg_color" in kwargs:
            self._dropdown_menu.configure(fg_color=kwargs.pop("dropdown_fg_color"))

        if "dropdown_hover_color" in kwargs:
            self._dropdown_menu.configure(hover_color=kwargs.pop("dropdown_hover_color"))

        if "dropdown_text_color" in kwargs:
            self._dropdown_menu.configure(text_color=kwargs.pop("dropdown_text_color"))

        if "text_color" in kwargs:
            self._text_color = kwargs.pop("text_color")
            require_redraw = True

        if "text_color_disabled" in kwargs:
            self._text_color_disabled = kwargs.pop("text_color_disabled")
            require_redraw = True

        if "font" in kwargs:
            if isinstance(self._font, CTkFont):
                self._font.remove_size_configure_callback(self._update_font)
            self._font = self._check_font_type(kwargs.pop("font"))
            if isinstance(self._font, CTkFont):
                self._font.add_size_configure_callback(self._update_font)

            self._update_font()

        if "dropdown_font" in kwargs:
            self._dropdown_menu.configure(font=kwargs.pop("dropdown_font"))

        if "values" in kwargs:
            self._values = kwargs.pop("values")
            self._dropdown_menu.configure(values=self._values)

        if "state" in kwargs:
            self._state = kwargs.pop("state")
            self._entry.configure(state=self._state)
            require_redraw = True

        if "hover" in kwargs:
            self._hover = kwargs.pop("hover")

        if "variable" in kwargs:
            self._variable = kwargs.pop("variable")
            self._entry.configure(textvariable=self._variable)

        if "command" in kwargs:
            self._command = kwargs.pop("command")

        if "justify" in kwargs:
            self._entry.configure(justify=kwargs.pop("justify"))

        super().configure(require_redraw=require_redraw, **kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "corner_radius":
            return self._corner_radius
        elif attribute_name == "border_width":
            return self._border_width

        elif attribute_name == "fg_color":
            return self._fg_color
        elif attribute_name == "border_color":
            return self._border_color
        elif attribute_name == "button_color":
            return self._button_color
        elif attribute_name == "button_hover_color":
            return self._button_hover_color
        elif attribute_name == "dropdown_fg_color":
            return self._dropdown_menu.cget("fg_color")
        elif attribute_name == "dropdown_hover_color":
            return self._dropdown_menu.cget("hover_color")
        elif attribute_name == "dropdown_text_color":
            return self._dropdown_menu.cget("text_color")
        elif attribute_name == "text_color":
            return self._text_color
        elif attribute_name == "text_color_disabled":
            return self._text_color_disabled

        elif attribute_name == "font":
            return self._font
        elif attribute_name == "dropdown_font":
            return self._dropdown_menu.cget("font")
        elif attribute_name == "values":
            return self._values
        elif attribute_name == "state":
            return self._state
        elif attribute_name == "hover":
            return self._hover
        elif attribute_name == "variable":
            return self._variable
        elif attribute_name == "command":
            return self._command
        elif attribute_name == "justify":
            return self._entry.cget("justify")
        else:
            return super().cget(attribute_name)

    def _on_enter(self, event=0):
        if self._hover is True and self._state == tkinter.NORMAL and len(self._values) > 0:
            if sys.platform == "darwin" and len(self._values) > 0 and self._cursor_manipulation_enabled:
                self._canvas.configure(cursor="pointinghand")
            elif sys.platform.startswith("win") and len(self._values) > 0 and self._cursor_manipulation_enabled:
                self._canvas.configure(cursor="hand2")

            # set color of inner button parts to hover color
            self._canvas.itemconfig("inner_parts_right",
                                    outline=self._apply_appearance_mode(self._button_hover_color),
                                    fill=self._apply_appearance_mode(self._button_hover_color))
            self._canvas.itemconfig("border_parts_right",
                                    outline=self._apply_appearance_mode(self._button_hover_color),
                                    fill=self._apply_appearance_mode(self._button_hover_color))

    def _on_leave(self, event=0):
        if sys.platform == "darwin" and len(self._values) > 0 and self._cursor_manipulation_enabled:
            self._canvas.configure(cursor="arrow")
        elif sys.platform.startswith("win") and len(self._values) > 0 and self._cursor_manipulation_enabled:
            self._canvas.configure(cursor="arrow")

        # set color of inner button parts
        self._canvas.itemconfig("inner_parts_right",
                                outline=self._apply_appearance_mode(self._button_color),
                                fill=self._apply_appearance_mode(self._button_color))
        self._canvas.itemconfig("border_parts_right",
                                outline=self._apply_appearance_mode(self._button_color),
                                fill=self._apply_appearance_mode(self._button_color))

    def _dropdown_callback(self, value: str):
        if self._state == "readonly":
            self._entry.configure(state="normal")
            self._entry.delete(0, tkinter.END)
            self._entry.insert(0, value)
            self._entry.configure(state="readonly")
        else:
            self._entry.delete(0, tkinter.END)
            self._entry.insert(0, value)

        if self._command is not None:
            self._command(value)

    def set(self, value: str):
        if self._state == "readonly":
            self._entry.configure(state="normal")
            self._entry.delete(0, tkinter.END)
            self._entry.insert(0, value)
            self._entry.configure(state="readonly")
        else:
            self._entry.delete(0, tkinter.END)
            self._entry.insert(0, value)

    def get(self) -> str:
        return self._entry.get()

    def _clicked(self, event=0):
        if self._state is not tkinter.DISABLED and len(self._values) > 0:
            self._open_dropdown_menu()

    def bind(self, sequence=None, command=None, add=None):
        """ called on the tkinter.Entry """
        return self._entry.bind(sequence, command, add)

    def unbind(self, sequence, funcid=None):
        """ called on the tkinter.Entry """
        return self._entry.unbind(sequence, funcid)

    def focus(self):
        return self._entry.focus()

    def focus_set(self):
        return self._entry.focus_set()

    def focus_force(self):
        return self._entry.focus_force()
