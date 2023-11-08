import psutil
import flet as ft
from flet_core import KeyboardEvent

# TODO: How to save and load window position?
# TODO: Window resizes on startup
# TODO: Display shortcuts in background

processes = dict()

for proc in psutil.process_iter():
    processes[proc.name()] = proc

p_keys = list(processes.keys())


def main(page: ft.Page):
    global p_keys

    def kill_process(e):
        if e.control in list_view.controls:
            p_name = e.control.title.value

            if p_name in p_keys:
                try:
                    processes[p_name].kill()
                    del processes[p_name]
                    p_keys.remove(p_name)
                    list_view.controls.remove(e.control)
                except psutil.NoSuchProcess:
                    del processes[p_name]
                    p_keys.remove(p_name)
                    list_view.controls.remove(e.control)
                except psutil.AccessDenied:
                    e.control.leading = ft.Icon(ft.icons.ERROR)

            text_field.focus()
            page.update()

    list_processes = {
        name: ft.ListTile(
            title=ft.Text(name),
            leading=ft.Icon(ft.icons.DELETE),
            on_click=kill_process
        )
        for name in p_keys
    }

    def textbox_changed(string):
        str_lower = string.control.value.lower()
        list_view.controls = [
            list_processes.get(n) for n in p_keys if str_lower in n.lower()
        ] if str_lower else []
        page.update()

    text_field = ft.TextField(label="Process name:", on_change=textbox_changed, autofocus=True)
    list_view = ft.ListView(expand=1, spacing=10, padding=20)

    def on_keyboard(e: KeyboardEvent):
        global p_keys

        # ESC - Clear input field
        if e.key == "Escape":
            text_field.value = None
            list_view.controls = None
            page.update()

        # CTRL + K - Multi kill
        elif e.key == "K" and e.control:
            tmp_list = list()

            for entry in list_view.controls:
                tmp_list.append(entry)

            for entry in tmp_list:
                p_name = entry.title.value

                if p_name in p_keys:
                    try:
                        processes[p_name].kill()
                        del processes[p_name]
                        p_keys.remove(p_name)
                        list_view.controls.remove(entry)
                    except psutil.NoSuchProcess:
                        del processes[p_name]
                        p_keys.remove(p_name)
                        list_view.controls.remove(entry)
                    except psutil.AccessDenied:
                        entry.leading = ft.Icon(ft.icons.ERROR)

            if not list_view.controls:
                text_field.value = None

            text_field.focus()
            page.update()

        # CTRL + R - Refresh process list
        elif e.key == "R" and e.control:
            text_field.value = None
            list_view.controls = None

            processes.clear()
            for process in psutil.process_iter():
                processes[process.name()] = process

            p_keys = list(processes.keys())

        # CTRL + Q - Exit app
        elif e.key == "Q" and e.control:
            page.window_destroy()

    page.window_width = 600
    page.window_height = 490
    page.title = "Process-Killer"
    page.on_keyboard_event = on_keyboard
    page.add(text_field, list_view)


ft.app(target=main)
