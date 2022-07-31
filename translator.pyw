import sys
from threading import Thread

import cv2
import numpy
from contextlib import suppress
import time
from mytools.common.files import INI
from mytools.common.keyboard import Keyboard
from mytools.common.mouse import Mouse
from mytools.common.tesseract import *
from mytools.templates.selenium_ import *

import PySimpleGUI as sg
from googletrans import Translator
from PIL import ImageGrab
from googlesearch import search


class Dictionary:
    def __init__(self, activation_key, exit_key):
        self.activate = activation_key
        self.exit = exit_key
        self.keyboard = Keyboard()
        self.mouse = Mouse()

    def show_output(self, text):
        try:
            translation = Translator().translate(text, src='en', dest='ur').text
        except Exception as e:
            sg.theme('defaultNoMoreNagging')
            sg.popup_error(f"{e}\nPlease try again!", title='Translator error', text_color='red')
            return

        def get_explanation(window):
            driver = Selenium('chrome', start=True, load_full=True, args=['--headless'])
            driver.get(f"https://www.google.com/search?q={text.replace(' ', '+') + '+meaning'}")
            try:
                byte = driver.driver.find_element(By.XPATH, '//div[@class="vmod"]').screenshot_as_png
            except:
                byte = None
            driver.quit()
            if not window.was_closed():
                window['EXPLAIN'](data=byte) if byte is not None else window['EXPLAIN'](data='')
                window['EXPLAIN_SPACE']('') if byte is not None else window['EXPLAIN_SPACE'](
                    ' ' * 40 + 'No information found!')

        def get_links(window):
            LINKS = [j for j in search(text, tld="co.in", num=no_of_links, stop=no_of_links, pause=2)]
            if not window.was_closed():
                window['LINK_TEXT']('Links Found') if LINKS else window['LINK-TEXT']('No useful link found')
                window['LINKS']('\n'.join(LINKS)) if LINKS else window['LINKS']('')

        sg.theme("defaultNoMoreNagging")
        layout = [
            [sg.T(f'Translation in {language}', font=('Ariel', 20))],
            [sg.T(" " * 40),
             sg.T(text, font=("Ariel", '12')),
             sg.T("→", font=('Ariel', 30)), sg.T(translation, font=("Ariel", '12'))],
            [sg.T("Explanation", font=('Ariel', 15))],
            [sg.T(" " * 50, key="EXPLAIN_SPACE"),
             sg.Image(
                 data="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"
                      "Mc8EAnxUNsGWyFI08/3o+IOklVZaaaWVFv8FqDxu92FOoxEAAAAldEVYdGRhdGU6Y3JlYXRlADIwMjItMDctMzFUMDc6MTQ6MDkrMDA6MDC1jtIdAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDIyLTA3LTMxVDA3OjE0OjA5KzAwOjAwxNNqoQAAAABJRU5ErkJggg==",
                 key="EXPLAIN")],
            [sg.T("Finding useful links...", font=("Ariel", '12'), key="LINK_TEXT")],
            [sg.T('', key="LINKS")],
            [sg.B('Translate', size=(10, 1)), sg.T(' ' * 90), sg.Exit(size=(10, 1))],
        ]
        window = sg.Window('Translator®', layout=layout, finalize=True)
        window.move(300, 200)
        explain = True
        links = True
        while True:
            event, value = window.read(timeout=100)
            if event in (sg.WINDOW_CLOSED, 'Exit'):
                window.close()
                return False
            elif explain:
                Thread(target=get_explanation, args=[window]).start()
                explain = False
            elif links:
                Thread(target=get_links, args=[window]).start()
                links = False
            elif event == 'Translate':
                window.close()
                break
        self.make_window()

    def make_window(self):
        layout = [[sg.Graph((1920, 1080), (0, 1080), (1920, 0), background_color="white", key="graph")]]
        window = sg.Window("", layout=layout, keep_on_top=True,
                           finalize=True, no_titlebar=True, background_color="white", alpha_channel=0.1)
        window.maximize()
        check = False
        while True:
            event, values = window.read(timeout=10)
            graph = window["graph"]
            if event == sg.WINDOW_CLOSED or self.keyboard.multi_pressed(self.activate):
                window.close()
                return True
            elif self.mouse.is_pressed("left") and not check:
                check = True
                pos = self.mouse.get_location()
                starting_pos = (pos[0] - 14, pos[1] - 7)
            elif self.mouse.is_pressed("left"):
                current_pos = self.mouse.get_location()
                graph.erase()
                graph.draw_rectangle(starting_pos, current_pos, line_color="#FF0000", line_width=3)
            elif self.mouse.not_pressed("left") and check:
                rect = ImageGrab.grab(
                    (starting_pos[0] + 15, starting_pos[1] + 5, current_pos[0] + 12, current_pos[1] + 8))
                window.close()
                break
        if rect:
            rect = numpy.array(rect.convert('RGB'))
            _, binary = cv2.threshold(cv2.cvtColor(rect, cv2.COLOR_RGB2GRAY), 125, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            text = image_to_string(binary).strip("\n")
            self.show_output(text)

    def run(self):
        while True:
            if self.keyboard.multi_pressed(self.activate):
                time.sleep(1)
                self.make_window()
                time.sleep(1)
            elif self.keyboard.multi_pressed(self.exit):
                sys.exit()
            time.sleep(0.01)


if __name__ == '__main__':
    con = INI("config.ini").read()
    language = con['DEFAULT']['translate']
    activate = con['DEFAULT']['activation_key']
    no_of_links = int(con['DEFAULT']['no_of_links'])
    activate = [x.strip() for x in activate.split('+')]
    exit_ = con['DEFAULT']['exit_key']
    exit_ = [x.strip() for x in exit_.split('+')]
    translator = Dictionary(activate, exit_)
    print(f"Translator started!\nPress {' + '.join(activate)} to activate translator"
          f"\nPress {' + '.join(exit_)} to exit translator")
    translator.run()
