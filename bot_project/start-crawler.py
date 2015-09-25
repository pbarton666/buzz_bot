# Load libraries
import buzzbot.crawler

# Instantiate objects and start service
crawler = buzzbot.crawler.Crawler(items_completed=True)
crawler.start()
