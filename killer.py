import psutil
import flet as ft
from flet_core import KeyboardEvent


def main(page: ft.Page):
    processes = dict()

    page.title = "Process-Killer"

    for proc in psutil.process_iter():
        processes[proc.name()] = proc

    p_keys = list(processes.keys())

    def kill_process(e):
        if e.control in list_view.controls:
            list_view.controls.remove(e.control)
            page.update()

            p_name = e.control.title.value

            if p_name in p_keys:
                p_keys.remove(p_name)
                del processes[p_name]

                processes[p_name].kill()

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

    text_field = ft.TextField(label="Search for process to kill:", on_change=textbox_changed, autofocus=True)
    list_view = ft.ListView(expand=1, spacing=10, padding=20)

    def on_keyboard(e: KeyboardEvent):
        if e.key == 'Escape':
            text_field.value = None
            list_view.controls = None
            page.update()

    page.on_keyboard_event = on_keyboard

    page.window_width = 600
    page.window_height = 490

    page.add(text_field, list_view)


ft.app(target=main)
