import asyncio
from pyppeteer import launch
import csv


async def open_webpage():
    # browser = await launch(headless=False)
    browser = await launch()

    page = await browser.newPage()
    await page.goto('https://judicialrecords.wilco.org/PublicAccess/default.aspx')

    # Wait for the page to load (optional)
    await page.waitForSelector('a')

# Execute JavaScript code to click on the hyperlink
    await page.evaluate('''() => {
        const href = "javascript:LaunchSearch('Search.aspx?ID=100', false, true, sbxControlID2)";
        const hyperlink = document.querySelector(`a[href="${href}"]`);
        if (hyperlink) {
            hyperlink.click();
        }
    }''')

    # Wait for the page to load (optional)
    await page.waitForSelector('label')

    # Find a specific label based on its text or attributes
    label = await page.querySelector('label[for="DateFiled"]')

    if label:
        # Click on the label
        await label.click()
        await asyncio.sleep(5)  # Wait for 5 seconds (optional)

    # Wait for the page to load (optional)
    await page.waitForSelector('input[type="text"]')

    # Find the input field by its id
    inputFieldAfter = await page.querySelector('#DateFiledOnAfter')
    inputFieldBefore = await page.querySelector('#DateFiledOnBefore')

    if inputFieldAfter:
        # Input a date into the field
        await inputFieldAfter.click()  # Click the field to ensure it's focused
        await page.type('#DateFiledOnAfter', '06/01/2023')  # Input the date

    if inputFieldBefore:
        # Input a date into the field
        await inputFieldBefore.click()  # Click the field to ensure it's focused
        await page.type('#DateFiledOnBefore', '07/01/2023')  # Input the date

    # Wait for the page to load (optional)
    await page.waitForSelector('input[type="submit"]')

    # Find the submit button by its attributes
    submitButton = await page.querySelector('input[type="submit"]')

    if submitButton:
        # Click on the submit button
        await submitButton.click()
        await asyncio.sleep(5)  # Wait for 5 seconds (optional)

    with open('output.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row if present
        count = 1
        valueoflink = []
        for row in reader:
            # Assuming the link is in the last column of the CSV
            link = row[-1]
            await page.goto(link)
            # Get the <span> element within the <div> by class name
            span_element = await page.querySelector('div.ssCaseDetailCaseNbr span')

            span_text = await page.evaluate('(element) => element.textContent', span_element)
            cdisp_element = await page.querySelector('#CDisp')

            # Get the text contents of the children elements within the tbody using XPath
            text_contents = await page.evaluate('''() => {
                                                    let items = document.querySelector('body > table:nth-child(9) > tbody')
                                                    let item_children = items.childNodes
                                                    let a = []
                                                    item_children.forEach(x=> a.push(x.textContent))
                                                    text = a.join(" , ")
                                                    return text

    }''')

            text_contents = ' '.join(
                text_contents.split()).replace('\xa0', ' ')

            if cdisp_element:
                valueoflink.append([span_text, text_contents])
            else:
                valueoflink.append([span_text, 'No Information'])

            count += 1
            if count == 1000:
                break

    # Save the rows to a CSV file
    with open('output2.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Case number', 'Informations'])
        for row in valueoflink:
            writer.writerow(row)

    await browser.close()


asyncio.get_event_loop().run_until_complete(open_webpage())
asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))
