import asyncio
from pyppeteer import launch
import csv


async def open_webpage():
    browser = await launch(headless=False)
    page = await browser.newPage()
    await page.goto('https://judicialrecords.wilco.org/PublicAccess/default.aspx')

    # Wait for the page to load
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

    await page.waitForSelector('tbody')

    # Specify the tbody element using XPath
    # Adjust the XPath expression as needed
    tbody_element = await page.xpath('/html/body/table[4]/tbody')

    if tbody_element:
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

        # Save the rows to a CSV file
        with open('output.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Case number', 'Citation number',
                             'Defendant info', 'Field/location', 'Type/Status', 'Charges'])
            for row in values:
                writer.writerow(row)


asyncio.get_event_loop().run_until_complete(open_webpage())

# Delay added to keep the browser open for 10 seconds before exiting
# asyncio.get_event_loop().run_until_complete(asyncio.sleep(20))
