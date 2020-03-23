import feedparser
from datetime import datetime, timedelta, timezone
import dateparser
from json import dumps 
from dateutil import tz
import csv

def newscrawler(rss_links_name, hour_offset, filter_by, file_to_write, output_type='csv'):
	"""
	Crawls through the RSS links specified to get news, filtering by hour_offset (how old do you want the news) and
	by keywords (filter_by)

	Inputs: 
		rss_links_name: {string} name of a file containing RSS links to crawl.
		hour_offset: 	{int} number of hours old an article can be
		filter_by:		{[string]} list of keywords. Article title or summary must have at least one keyword to be included
		file_to_write:	{string} name of file to write .json/csv output to. NOTE: overriding data in file given. 
		output_type: {string} "csv" for csv or "json" for json. (anything else will default to csv)
	Out:
		.json file with news or .csv file with news 
	"""
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

	# sort by date
	news_articles['news'] = sorted(news_articles['news'], key = lambda i: (datetime.strptime(i['date'],'%d %B %Y') , datetime.strptime(i['time'],'%I:%M%p')))
	news_articles['news'].reverse()

	if output_type == 'json':
		json_string =  dumps(news_articles, indent=4)
		out_json = open(file_to_write, 'w')
		out_json.write(json_string)

		out_json.close()
	else:	#csv
		out_csv = open(file_to_write, 'w')
		header_list = list(news_articles['news'][0].keys())
		writer = csv.DictWriter(out_csv, fieldnames=header_list)
		writer.writerow({'url': 'Last Updated', 'title': news_articles['updateTime'][0]['time'], 'source': '', 'date': '', 'time': ''})

		writer.writeheader()

		for diction in news_articles['news']:
			writer.writerow(diction)

	rss_file.close()

if __name__ == '__main__':
	### default constants ###

	#number of hours to look back
	HOUR_OFFSET = 4
	# keywords to filter tags by
	FILTER_BY = ['coronavirus', 'virus', 'corona', 'covid', 'covid-19', 'pandemic', 'self-isolation', 'lockdown', 'schools', 'Australia']

	# rss feeds link file
	FNAME = 'rss_feeds.md'
	FTOWRITE = 'scraped_news.csv'
	json_string = newscrawler(FNAME, HOUR_OFFSET, FILTER_BY, FTOWRITE, output_type='csv')

