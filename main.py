##from uu import Error
from io import StringIO
import time
from playwright.sync_api import sync_playwright
import pytesseract      
from PIL import Image  
import pandas as pd
from tabulate import tabulate
import mail

def iterator(locator):
    lst =[]
    for info in range(locator.count() ):
        raw_text = locator.nth(info).text_content() 
        text = raw_text.replace("\n", "")
        text = text.replace("\t", "")

        lst.append(text)
    return lst



def image_to_string(image):
                
    img = Image.open(image)                               
    pytesseract.pytesseract.tesseract_cmd ='C:/Program Files/Tesseract-OCR/tesseract.exe'   
    result = pytesseract.image_to_string(img)
    eqn = result
    char_remov = ["?", "="]
    for i in char_remov:
        eqn = eqn.replace(i, "") 
    
    for i in ["B"]:
        eqn = eqn.replace(i, "8")
    try:
        solved = eval(eqn)
        print(solved)
        return(solved)
    except SyntaxError:
        return SyntaxError

def EvalError(ans, page):
    while(ans == SyntaxError):
        print("Captcha Error..Retrying")
        page.locator("#refreshCaptcha").click(force = True)
        time.sleep(0.2)
        page.locator("#CaptchaImgID").screenshot(path="screenshot.png")
        ans = image_to_string("screenshot.png")

def main(pnr, name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.indianrail.gov.in/enquiry/PNR/PnrEnquiry.html?locale=en")
        page.fill("#inputPnrNo", str(pnr))
        page.locator("#modal1").click()
        time.sleep(1)
        page.locator("#CaptchaImgID").screenshot(path="screenshot.png")
        ans = image_to_string("screenshot.png")

        EvalError(ans, page)
        page.fill("#inputCaptcha", str(ans))
        page.locator("#submitPnrNo").click()

        while(page.locator("#errorMessagemodal").text_content() != "") :
            print("Captcha Errror..Retrying")
            page.locator("#CaptchaImgID").screenshot(path="screenshot.png")
            ans = image_to_string("screenshot.png")

            EvalError(ans, page)
            
            page.fill("#inputCaptcha", str(ans))
            page.locator("#submitPnrNo").click()
            
        passenger_records = iterator(page.locator("#psgnDetailsTable>>tbody >>tr >>td"))
        i = 0
        # passenger_records = []
        while(passenger_records == []):
            time.sleep(1)
            passenger_records = iterator(page.locator("#psgnDetailsTable>>tbody >>tr >>td"))
            # passenger_records = []
            i+= 1
            if(i> 10):
                page.screenshot(path="Debug.png")
                print("Critical Error")
                page.close()
                browser.close()
                p.stop()                
                main(pnr, name)

        page.locator("#pnrOutputDiv").screenshot(path = f"{name}.png")
        lst = []
        for i in range(len(passenger_records)):
            if(passenger_records[i] == ''):
                lst.append(passenger_records[i-1])
        g = ' '.join([str(elem) for elem in lst])
        print("Current Status:- ", g)

        all_tables = pd.read_html(StringIO(page.inner_html("#pnrOutputDiv")))
        all_tables.pop()
        html = ""

        for i in all_tables:
            df1 = pd.DataFrame(i)
            html += tabulate(df1,headers='keys', tablefmt='html',)

        html = f"""
        <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>html title</title>
        </head>
        <html><body>
        <p> Current Status of {name}:- <b>{g}</b> </p>
        <br>
        <table border = '1' style="border: black 0.5px;"> 
            {html}
        </table>

        </body></html>
        """
        mail.send_mail(name = name, html = html, TO_ADDRESS='sudipta01.dutta@gmail.com')
        print(f"Sent {name}")
        browser.close()

if __name__ == "__main__":
        main("6129155548", "ID & SD")
        main("6629158599", "Arka")