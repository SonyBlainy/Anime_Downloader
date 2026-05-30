from playwright.async_api import async_playwright

async def cookies():
    async with async_playwright() as p:
        navegador = await p.chromium.launch(executable_path='chrome-win64\\chrome.exe',headless=False)
        context = await navegador.new_context()
        pagina = await context.new_page()
        await pagina.goto('https://www.erai-raws.info/account-login/?redirect_to=https://www.erai-raws.info/')
        await pagina.wait_for_url('https://www.erai-raws.info', timeout=0)
        cookies = await context.cookies()
        await context.close()
        await navegador.close()
        return cookies
