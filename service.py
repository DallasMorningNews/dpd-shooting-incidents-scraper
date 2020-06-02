import scraper

def handler(event, context):
    print('service started')
    # Call the function from your imported file
    scraper.perform_scrape()

# just calling the main handler function
if __name__ == '__main__':
    handler(1, 2)
