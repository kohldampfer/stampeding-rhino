import feedparser
import bs4
import requests
import urllib.request
import os
import os.path
import zipfile
import shutil
import glob
import re
import getopt
import sys

RSS_URL="https://wordpress.org/plugins/rss/browse/new/"
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TARGET_DIR = "{0}/downloads".format(CURRENT_DIR)

def parse_command_line_arguments(arguments):
  try:
    opts, args = getopt.getopt(arguments, "t:", ["targetdir="])
  except getopt.GetoptError:
    print("Use one of the following commands: ")
    print(arguments[0] + " -t <targetdir>")
    print(arguments[0] + " --targetdir=<targetdir>")
    sys.exit(-1)
  
  for opt, arg in opts:
    if opt in ("-t", "--targetdir"):
      TARGET_DIR = arg

def parse_rss():
	print("Start parsing {0}".format(RSS_URL))
	d = feedparser.parse(RSS_URL)
	links = []
	for e in d.entries:
		links.append(e.link)

	return links

def get_zip_link(link):
	# use requests to get the contents
	r = requests.get(link)

	# get the text of the contents
	html_content = r.text

	# find all links in the url
	soup = bs4.BeautifulSoup(html_content, "html.parser")
	links = soup.findAll('a')
	return_links = []
	for l in links:
		if l is not None:
			href = l.get('href')
			if href is not None and href.endswith(".zip"):
				print(" - Found zip link: {0}".format(href))
				return_links.append(href)

	# return all zip links
	return return_links

def download_zip(zip_url):
	last_slash = zip_url.rfind('/')
	# get filename of zip which needs to be downloaded
	zip_file=zip_url[last_slash+1:len(zip_url)]

	# remove file if it exists
	if os.path.isfile(zip_file):
		print(" - Deleting file {0}".format(zip_file))
		os.remove(zip_file)

	# retrieve zip
	print(" - Download file {0}".format(zip_file))
	urllib.request.urlretrieve(zip_url, "{0}/{1}".format(TARGET_DIR, zip_file))

	return "{0}/{1}".format(TARGET_DIR, zip_file)

def unzip_file(zip_file):
	dir_of_zip = zip_file[0:len(zip_file)-4]

	if os.path.isdir(dir_of_zip):
		shutil.rmtree(dir_of_zip)

	zip_ref = zipfile.ZipFile(zip_file, 'r')
	zip_ref.extractall(".")
	zip_ref.close()

# parse command line arguments
parse_command_line_arguments(sys.argv)
print("Target dir is '{0}'".format(TARGET_DIR))

# download plugins and extract files
urls = parse_rss()
for z in urls:
	zip_urls = get_zip_link(z)
	for u in zip_urls:
		zip_file = download_zip(u)
		unzip_file(zip_file)
		os.remove(zip_file)

exit(0)
