import psutil
import flet as ft
from flet_core import KeyboardEvent

# TODO: How to save and load window position?
# TODO: Window resizes on startup
# TODO: Display shortcuts in background


class Killer:
    p_dict = dict()
    p_keys = list()

    p_text = None
    p_list = None

    page = None

    list_processes = None

    def __init__(self, page: ft.Page):
        self.page = page
        self.get_processes()

        self.p_text = ft.TextField(label="Process name:", on_change=self.textbox_changed, autofocus=True)
        self.p_list = ft.ListView(expand=1, spacing=10, padding=20)

        self.page.window_width = 600
        self.page.window_height = 490
        self.page.title = "Process-Killer"
        self.page.on_keyboard_event = self.on_keyboard
        self.page.add(self.p_text, self.p_list)

    def get_processes(self):
        self.p_dict.clear()
        self.p_keys.clear()

        for process in psutil.process_iter():
            self.p_dict[process.name()] = process
            self.p_keys.append(process.name())

        self.get_list_processes()

    def get_list_processes(self):
        self.list_processes = {
            name: ft.ListTile(
                title=ft.Text(name),
                leading=ft.Icon(ft.icons.DELETE),
                on_click=self.kill_process
            )
            for name in self.p_keys
        }

    def kill_process(self, e):
        if e.control in self.p_list.controls:
            p_name = e.control.title.value

            if p_name in self.p_keys:
                try:
                    self.p_dict[p_name].kill()
                    del self.p_dict[p_name]
                    self.p_keys.remove(p_name)
                    self.p_list.controls.remove(e.control)
                except psutil.NoSuchProcess:
                    del self.p_dict[p_name]
                    self.p_keys.remove(p_name)
                    self.p_list.controls.remove(e.control)
                except psutil.AccessDenied:
                    e.control.leading = ft.Icon(ft.icons.ERROR)

            self.p_text.focus()
            self.page.update()

    def textbox_changed(self, string):
        str_lower = string.control.value.lower()

        self.p_list.controls = [
            self.list_processes.get(n) for n in self.p_keys if str_lower in n.lower()
        ] if str_lower else []

        self.page.update()

    def on_keyboard(self, e: KeyboardEvent):
        # ESC - Clear input field
        if e.key == "Escape":
            self.p_text.value = None
            self.p_list.controls = None
            self.page.update()

        # CTRL + K - Multi kill
        elif e.key == "K" and e.control:
            tmp_list = list()

            for entry in self.p_list.controls:
                tmp_list.append(entry)

            for entry in tmp_list:
                p_name = entry.title.value

                if p_name in self.p_keys:
                    try:
                        self.p_dict[p_name].kill()
                        del self.p_dict[p_name]
                        self.p_keys.remove(p_name)
                        self.p_list.controls.remove(entry)
                    except psutil.NoSuchProcess:
                        del self.p_dict[p_name]
                        self.p_keys.remove(p_name)
                        self.p_list.controls.remove(entry)
                    except psutil.AccessDenied:
                        entry.leading = ft.Icon(ft.icons.ERROR)

            if not self.p_list.controls:
                self.p_text.value = None

            self.p_text.focus()
            self.page.update()

        # CTRL + R - Refresh process list
        elif e.key == "R" and e.control:
            self.p_text.value = None
            self.p_list.controls = None

            self.p_dict.clear()
            for process in psutil.process_iter():
                self.p_dict[process.name()] = process

            self.p_keys = list(self.p_dict.keys())

        # CTRL + Q - Exit app
        elif e.key == "Q" and e.control:
            self.page.window_destroy()


ft.app(target=Killer)
