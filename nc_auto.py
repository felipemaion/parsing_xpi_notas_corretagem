import pyautogui
import os
import time

dir_path = os.path.dirname(os.path.realpath(__file__))

while True:
    pyautogui.PAUSE = 2.5
    local = pyautogui.locateOnScreen(os.path.join(dir_path,"imgs","combobox.png"))
    print(local)
    pyautogui.moveTo(local.left + 20, local.top + 20)
    pyautogui.click()
    pyautogui.PAUSE = 1

    time.sleep(1)

    local = pyautogui.locateOnScreen(os.path.join(dir_path,"imgs","atual_sel.png"),confidence=0.8, grayscale=True)
    pyautogui.moveTo(local.left+35, local.top + 15)
    pyautogui.click()

    local = pyautogui.locateOnScreen(os.path.join(dir_path,"imgs","gerar_pdf.png"),confidence=0.8, grayscale=True)
    pyautogui.moveTo(local.left+35, local.top + 15)
    pyautogui.click()
    
    local = None
    while not local:
        try:
            local = pyautogui.locateOnScreen(os.path.join(dir_path,"imgs","download.png"),confidence=0.8, grayscale=True)
            pyautogui.moveTo(local.left+35, local.top + 15)
            pyautogui.click()
        except:
            local = None
            
    local = pyautogui.locateOnScreen(os.path.join(dir_path,"imgs","salvar.png"),confidence=0.8, grayscale=True)
    pyautogui.moveTo(local.left+35, local.top + 15)
    pyautogui.click()