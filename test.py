import asyncio
from pyppeteer import launch

async def test_pdf():
    browser = await launch(executablePath="C:/Program Files/Google/Chrome/Application/chrome.exe")
    page = await browser.newPage()
    await page.setContent("<h1>Hello PDF</h1>")
    await page.pdf({'path': 'test.pdf', 'format': 'A4'})
    await browser.close()

asyncio.get_event_loop().run_until_complete(test_pdf())