import asyncio
from pyppeteer import launch
import csv


async def new_website():

    browser = await launch(headless=False)
    page = await browser.newPage()
    await page.goto('https://justice1.dentoncounty.gov/PublicAccess/default.aspx')

    hyperlink = '''a[href="javascript:LaunchSearch('../PublicAccessDC/Search.aspx?ID=200', false, true, sbxControlID2)"]'''
    await page.waitForSelector(hyperlink)
    await page.click(hyperlink)

    hyperlink = '''a[href="javascript:LaunchSearch('Search.aspx?ID=100', false, true, sbxControlID2)"]'''
    await page.waitForSelector(hyperlink)
    await page.click(hyperlink)

    dateFieldLabel = '''label[for = "DateFiled"]'''
    await page.waitForSelector(dateFieldLabel)
    await page.click(dateFieldLabel)

    inputDateAfter = await page.querySelector('#DateFiledOnAfter')
    await inputDateAfter.click()
    await page.type('#DateFiledOnAfter', '06/01/2023')

    inputDateBefore = await page.querySelector('#DateFiledOnBefore')
    await inputDateBefore.click()
    await page.type('#DateFiledOnBefore', '07/01/2023')

    submitButton = await page.querySelector('input[type="submit"]')
    await submitButton.click()

    await page.waitForSelector('tbody')
    tbody_element = await page.xpath('/html/body/table[4]/tbody')
    await asyncio.sleep(5)

    tbody = tbody_element[0]  # Get the first matching tbody element
    # Extract the values within tr elements of the specified tbody
    values = await page.evaluate('''(tbody) => {
            const rows = Array.from(tbody.getElementsByTagName('tr'));
            const result = rows.filter(row => {
                let parent = row.parentElement;
                while (parent) {
                    if (parent.tagName === 'TR') {
                        return false;
                    }
                    parent = parent.parentElement;
                }
                return true;
            }).map(row => {
                const outerCells = Array.from(row.getElementsByTagName('td')).filter(td => !td.querySelector('td')).map(td => td.textContent.trim());
                const link = row.querySelector('td:first-child a');
                if (link) {
                    outerCells.push(link.href);
                } else {
                    outerCells.push('');
                }
                return outerCells;
            });
            return result;
        }''', tbody)
    values = values[2:]
    # print(values)

    xpath = '/html/body/table[4]/tbody/tr[1]/th'
    headers = await page.xpath(xpath)
    header_texts = []
    for header in headers:
        header_text = await page.evaluate('(element) => element.textContent', header)
        header_texts.append(header_text.strip())

    # print(header_texts)
    # print(values)

    with open('output4.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header_texts)
        for row in values:
            writer.writerow(row)


asyncio.get_event_loop().run_until_complete(new_website())
asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))
