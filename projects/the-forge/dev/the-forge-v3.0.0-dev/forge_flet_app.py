import flet as ft
import os
from schema_parser import flatten_xsd_schema, flatten_json_schema
from excel_exporter import export_paths_to_excel


def is_xsd(path):
    return path and path.lower().endswith('.xsd')

def is_json(path):
    return path and path.lower().endswith('.json')


def main(page: ft.Page):
    page.title = "The Forge - Schema to Excel"
    page.window_width = 500
    page.window_height = 350
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    input_file_picker = ft.FilePicker()
    output_file_picker = ft.FilePicker()
    save_file_picker = ft.FilePicker()

    # Add FilePickers to page overlay as required by Flet
    page.overlay.append(input_file_picker)
    page.overlay.append(output_file_picker)
    page.overlay.append(save_file_picker)

    input_file_text = ft.TextField(label="Input Schema File", read_only=True, width=350)
    output_file_text = ft.TextField(label="Output Schema File", read_only=True, width=350)

    generate_btn = ft.ElevatedButton("Generate Excel", icon="download", disabled=True)

    snackbar = ft.SnackBar(content=ft.Text(""))

    def show_message(msg, error=False):
        snackbar.content.value = msg
        snackbar.bgcolor = ft.Colors.ERROR if error else ft.Colors.SECONDARY_CONTAINER
        page.snack_bar = snackbar
        snackbar.open = True
        page.update()

    def update_generate_btn():
        generate_btn.disabled = not (input_file_text.value and output_file_text.value)
        page.update()

    def pick_input_file(e):
        input_file_picker.pick_files(allow_multiple=False)

    def pick_output_file(e):
        output_file_picker.pick_files(allow_multiple=False)

    def on_input_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            input_file_text.value = e.files[0].path
            update_generate_btn()

    def on_output_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            output_file_text.value = e.files[0].path
            update_generate_btn()

    input_file_picker.on_result = on_input_file_result
    output_file_picker.on_result = on_output_file_result

    def on_generate_click(e):
        print("[DEBUG] Generate Excel clicked")
        input_path = input_file_text.value
        output_path = output_file_text.value
        print(f"[DEBUG] Input path: {input_path}")
        print(f"[DEBUG] Output path: {output_path}")
        if not (input_path and output_path and os.path.isfile(input_path) and os.path.isfile(output_path)):
            print("[DEBUG] Invalid file paths")
            show_message("Please select valid files.", error=True)
            return
        try:
            # Only flatten the output schema for Excel
            if is_xsd(output_path):
                print("[DEBUG] Output is XSD")
                paths = flatten_xsd_schema(output_path)
            elif is_json(output_path):
                print("[DEBUG] Output is JSON Schema")
                paths = flatten_json_schema(output_path)
            else:
                print("[DEBUG] Output schema is not .xsd or .json")
                raise ValueError("Output schema must be .xsd or .json")
            def on_save_result(ev: ft.FilePickerResultEvent):
                print(f"[DEBUG] Save dialog result: {ev.path}")
                if ev.path:
                    try:
                        export_paths_to_excel(paths, ev.path)
                        print(f"[DEBUG] Excel exported to: {ev.path}")
                        show_message(f"Excel exported to: {ev.path}")
                    except Exception as ex:
                        print(f"[DEBUG] Export Error: {ex}")
                        show_message(f"Export Error: {ex}", error=True)
            save_file_picker.on_result = on_save_result
            print("[DEBUG] Opening save file dialog...")
            save_file_picker.save_file(file_name="mapping.xlsx")
        except Exception as ex:
            print(f"[DEBUG] Exception: {ex}")
            show_message(f"Error: {ex}", error=True)

    generate_btn.on_click = on_generate_click

    input_row = ft.Row([
        input_file_text,
        ft.IconButton(icon="folder_open", on_click=pick_input_file)
    ], alignment=ft.MainAxisAlignment.CENTER)

    output_row = ft.Row([
        output_file_text,
        ft.IconButton(icon="folder_open", on_click=pick_output_file)
    ], alignment=ft.MainAxisAlignment.CENTER)

    page.add(
        ft.Column([
            ft.Text("The Forge", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            input_row,
            output_row,
            generate_btn
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30)
    )

ft.app(target=main) 