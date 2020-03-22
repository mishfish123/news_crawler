import feedparser
from datetime import datetime, timedelta, timezone
import dateparser
from json import dumps 
from dateutil import tz

### constants ###

#number of days to look back
HOUR_OFFSET = 3
# keywords to filter tags by
FILTER_BY = ['coronavirus', 'virus', 'corona', 'covid', 'covid-19', 'pandemic', 'self-isolation', 'lockdown', 'schools']

# rss feeds link file
FNAME = 'rss_feeds.md'
def newscrawler(rss_links_name, hour_offset, filter_by, file_to_write):

	##### read link file #####
	rss_file = open(rss_links_name, 'r')
	rss_feeds = rss_file.readlines()
	rss_feeds = [x.strip() for x in rss_feeds] #strip whiteline
	

	local_zone = tz.tzlocal()
	now = datetime.now().astimezone(local_zone)

	##### Get the current news related to the filters ####
	news_articles = {'updateTime': [{'time': now.strftime('%I:%M%p %d %B %Y')}], 'news': []}; # create json object 

	for url in rss_feeds:
		d = feedparser.parse(url)
		try: 
			author = d.feed.author
		except:
			author = url
		for entry in d.entries:
			# filter by date
			article_date = dateparser.parse(entry.updated).astimezone(local_zone)
			if now - timedelta(hours=hour_offset) < article_date:

				# filter by keywords
				if (any(x in entry.title.lower() for x in filter_by) or any(x in entry.summary.lower() for x in filter_by)):
					print_date = article_date.strftime('%d %B %Y')
					print_time = article_date.time().strftime('%I:%M%p')
					news_articles['news'].append({'url': entry.link, 'title': entry.title, 'source': author, 'date': print_date, 'time': print_time})


	json_string =  dumps(news_articles, indent=4)
	out_json = open(file_to_write, 'w')
	out_json.write(json_string)

	out_json.close()
	rss_file.close()

if __name__ == '__main__':
	### default constants ###

	#number of days to look back
	HOUR_OFFSET = 4
	# keywords to filter tags by
	FILTER_BY = ['coronavirus', 'virus', 'corona', 'covid', 'covid-19', 'pandemic', 'self-isolation', 'lockdown', 'schools']

	# rss feeds link file
	FNAME = 'rss_feeds.md'
	FTOWRITE = 'scraped_news.json'
	json_string = newscrawler(FNAME, HOUR_OFFSET, FILTER_BY, FTOWRITE)

