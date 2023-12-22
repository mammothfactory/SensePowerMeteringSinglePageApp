from nicegui import ui, app

from fastapi import FastAPI

def init(fastApiApp: FastAPI) -> None:
    @ui.page('init_setting')
    def init_setting():
        ui.label('Dollar General Energy Cost at 3521 Russel Road')

    token = '3' #load_dotenv()
    ui.run_with(fastApiApp, storage_secret=token)
