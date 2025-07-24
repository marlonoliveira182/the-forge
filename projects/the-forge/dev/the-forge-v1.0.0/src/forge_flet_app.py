import flet as ft


def main(page: ft.Page):
    page.title = "The Forge - Schema to Excel"
    page.window_width = 500
    page.window_height = 350
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    input_file_picker = ft.FilePicker()
    output_file_picker = ft.FilePicker()

    input_file_text = ft.TextField(label="Input Schema File", read_only=True, width=350)
    output_file_text = ft.TextField(label="Output Schema File", read_only=True, width=350)

    def pick_input_file(e):
        page.show_dialog(input_file_picker)

    def pick_output_file(e):
        page.show_dialog(output_file_picker)

    def on_input_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            input_file_text.value = e.files[0].path
            page.update()

    def on_output_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            output_file_text.value = e.files[0].path
            page.update()

    input_file_picker.on_result = on_input_file_result
    output_file_picker.on_result = on_output_file_result

    input_row = ft.Row([
        input_file_text,
        ft.IconButton(icon=ft.icons.FOLDER_OPEN, on_click=pick_input_file)
    ], alignment=ft.MainAxisAlignment.CENTER)

    output_row = ft.Row([
        output_file_text,
        ft.IconButton(icon=ft.icons.FOLDER_OPEN, on_click=pick_output_file)
    ], alignment=ft.MainAxisAlignment.CENTER)

    generate_btn = ft.ElevatedButton("Generate Excel", icon=ft.icons.DOWNLOAD, disabled=True)

    page.add(
        ft.Column([
            ft.Text("The Forge", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            input_row,
            output_row,
            generate_btn
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30)
    )

ft.app(target=main) 