"""
    RSS Parser:  Parse a RSS file for data and add to a CSV file
"""
import csv
import urllib2
import logging
import datetime

from xml.dom.minidom import parseString

logger = logging.getLogger()

HOST = "192.168.1.3"
TEST_FILE = "rss.xml"
OUTPUT_FILE = "rss_output.txt"

def get_rss(uri, local_file=False):
    """
    Gets the raw data from the RSS URL or a local test file
    
    Returns:  RSS document as a string
    """
    PATH = "/rss/rss.xml"
    
    if local_file:
        logger.debug("Using local test file for RSS parsing")
        rss_file = open(uri, 'rU')
    else:
        url = "http://%s/%s" % (uri, PATH)
        rss_file = urllib2.urlopen("http://%s" % (uri,))
    
    data = rss_file.read()
    rss_file.close()
    
    logger.debug("Read %d bytes" % (len(data),)) 
    return data

def parse_rss(data, host):
    
    def element_to_text(tag_name):
        """Get the text node out of the xml tag"""
        
        # Hackish using [0] but it shouldn't ever fail unless the RSS is broken
        # Each item has exactly one title and one description and one text node
        temp = item.getElementsByTagName(tag_name)[0].firstChild.data
        
        # remove leading/trailing whitespace and carrage returns
        return temp.strip()
        
    dom = parseString(data)
    
    # Get all of the "item" tags
    xmlTags = dom.getElementsByTagName('item')
    
    output = []
    for item in xmlTags:
        now = datetime.datetime.now()
        now_string =  now.strftime("%m/%d/%Y %H:%M:%S")
        
        title = element_to_text("title")
        title = clean_title(title)
        data_source = "%s-%s" % (host, title)
        
        description = element_to_text("description")
        description = clean_description(description)
        
        logger.debug("Data: now_string: (%s), data_source(%s), description(%s)" % \
                     (now_string, data_source, description))
        
        output.append([now_string, data_source, description])
        
    return output

def clean_title(title):
    """
    Extract the title string and format nicer
    Looks like: PC4, ID 02, CH1
    """
    output = []
    temp = title.split(",")
    for item in temp:
        t = item.strip()
        t2 = t.replace(" ", "") # remove spaces
        output.append(t2)
    
    return "_".join(output)

def clean_description(description):
    """Cleans off the first 15 chars of this: 'Current Value: ' """
    return description[15:]
    
def write_output(output, output_file):
    with open(output_file, 'ab') as f:
        csv_writer = csv.writer(f, delimiter=",")
        for row in output:
            csv_writer.writerow(row)
    
def main():
    """This is where the magic happens"""
    
    data = get_rss(TEST_FILE, local_file=True)
    output = parse_rss(data, "127.0.0.1")
    write_output(output, OUTPUT_FILE)
    
if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    logging.basicConfig()
    main()
    
