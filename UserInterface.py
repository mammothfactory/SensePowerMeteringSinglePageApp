from nicegui import ui, app

from fastapi import FastAPI

def init(fastApiApp: FastAPI) -> None:
    @ui.page('init_setting')
    def init_setting():
        ui.label('Dollar General Energy Cost at 3521 Russel Road')

    token = '3' #load_dotenv()
    ui.run_with(fastApiApp, storage_secret=token)
    
def set_background(color: str) -> None:
    ui.query('body').style(f'background-color: {color}')
    
def build_svg_graph() -> str:
    """ Create an 1920 x 1080 graph in HTML / SVG

    Args:
        NONE

    Returns:
        str: Valid HTML to create a time vs Wh line graph
    """
    now = db.get_date_time()
    return f'''
    <svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
    <circle cx="200" cy="200" r="180" stroke="black" stroke-width="4" fill="white" />
    <line x1="200" y1="200" x2="200" y2="50" stroke="black" stroke-width="6" transform="rotate({now.minute / 60 * 360} 200 200)" />
    <line x1="200" y1="200" x2="200" y2="100" stroke="black" stroke-width="6" transform="rotate({now.hour / 12 * 360} 200 200)" />
    <circle cx="200" cy="200" r="20" fill="black" />
    
    <!-- Hour marks -->
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(0 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(30 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(60 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(90 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(120 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(150 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(180 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(210 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(240 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(270 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(300 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(330 200 200)" />
    </svg>
    '''


async def update_graph(direction: int, sanitizedID: str):
    """ Perform database insert

    Args:
        direction (CONSTANT int):Define function as clock IN or clock OUT method
        sanitizedID (str): Global sanitized number entered into Number text  box
    """

    if invalidIdLabel.visible == False and len(sanitizedID) == GC.VALID_EMPLOYEE_ID_LENGTH:
        if direction == GC.CLOCK_IN:
            clockedInLabel.set_text(f'{sanitizedID} - REGISTRO EN (CLOCKED IN)')
            clockedInLabel.visible = True
            db.insert_check_in_table(sanitizedID)
            #set_background('grey')
            await ui.run_javascript(f'getElement({inputBox.id}).focus()', respond=False)
        
        elif direction == GC.CLOCK_OUT:
            clockedOutLabel.set_text(f'{sanitizedID} - RELOJ DE SALIDA (CLOCK OUT)')
            clockedOutLabel.visible = True
            db.insert_check_out_table(sanitizedID)
            #set_background('grey')
            await ui.run_javascript(f'getElement({inputBox.id}).focus()', respond=False)

    else:
       tryAgainLabel.visible = True
       set_background('grey')

    inputBox.set_value(None)                          # Clear user input box. Note set_value('') doesn't work :)


def sanitize_search(inputText: str) -> str:
    """ Convert all bad user input to valid ouput and update GUI label visibility to control datatbase writes

    Args:
        inputText (str): Raw user input with possible errors

    Returns:
        str: A string with all blank spaces and non-digit characters removed
    """
    global sanitizedID

    if int(inputText) > 9999 or int(inputText) < 0:
        invalidIdLabel.visible = True
        set_background('grey')
        return 'ID DE EMPLEADO NO VÁLIDO (INVALID EMPLOYEE ID)'
    else:
       invalidIdLabel.visible = False

    if inputText == None:
        sanitizedID = ''
    else:
        sanitizedID = str(int(inputText))

    return sanitizedID


if __name__ == "__main__":
    print("1")
    app = FastAPI()
    init(app)
    print("2")