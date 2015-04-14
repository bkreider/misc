#!/opt/anaconda/bin/python
import re
import sys
import logging
import datetime

logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s:%(levelname)9s:%(name)20s: %(message)s")
handler.setFormatter(formatter)

#logger.addHandler(handler)



examples = """
DEBUG 2013-09-29 13:36:49,634 common 10529 140713088272128 command:ssh -t -t vzcontroller@prod-vz-10.wakari.io "sudo cp /user_home/private/w_jswfnal/ssh_config /vz/root/522/etc/ssh/ssh_config"
DEBUG 2013-09-29 13:36:49,899 common 10529 140713088272128 stdout:
DEBUG 2013-09-29 13:36:49,900 common 10529 140713088272128 stderr:tcgetattr: Invalid argument
"""

def is_valid(line):
    return line

def process(line):
    """Return False for any failures"""
    output = {}

    fields = line.split(" ")
    if len(fields) < 6:
        return False
    
    output["log_level"] = fields[0]
    
    # Convert date/time to object or reject line
    try:
        output["datetime"] = datetime.datetime.strptime(
            "%s %s" % (fields[1], fields[2]),
            "%Y-%m-%d %H:%M:%S,%f"
        )
    except ValueError:
        return False
    
    output["logger"] = fields[3]
    output["thread"] = fields[4]
    output["process"] = fields[5]
    output["message"] = " ".join(fields[6:])
    
    return output

def gen_parse_log(lines):
    
    current = {}
    
    try:
        for line in lines:
            
            line = line.strip()
            
            if line == "":
                logger.debug("Skipping empty line")
                continue
            
            logger.debug("checking line: %s" % (line,))
            
            # Fresh state
            if current == {}:
                
                # We are valid -- look to see if next line is valid
                output = process(line)
                if is_valid(output):
                    current = output
                    logger.debug("Looking at next line")
                    continue
                else:
                    logger.debug("Bad line: %s" % (line,))
                    continue
            else:
                
                # Already parsing lines
                output = process(line)
                if is_valid(output):
                    logger.debug("Line is valid so yielding current")
                    yield current
                    current = output
                else:
                    # keep collapsing invalid lines into message
                    logger.debug("invalid: %s, so collapsing" % (line,))
                    current["message"] = "%s\n%s" % (current["message"], line)
                    continue
    
    # Don't yield on other exceptions
    except StopIteration:
        yield current
    else:
        yield current
        

def gen_filter_standard(messages):
    
    standard_ignores = [
        re.compile(r"^success.*retries"),
        re.compile(r"^checking.*retries"),
        re.compile(r"^stderr:tcgetattr: Invalid argument"),
        re.compile(r"^stdout:$"),
        re.compile(r"^Public Data list length"),
        re.compile(r"^INFO: import publicdata succeeded.$"),
        re.compile(r"^Log Debug information can pass in variables"),
        re.compile(r"^Log info$")
    ]
    
    for message in messages:

        # Most likely garbage in
        if "message" not in message:
            continue
        
        reject = False
        for filter_ in standard_ignores:
            m = filter_.match(message["message"])
            if m:
                reject = True
                break
        
        if reject:
            continue
        
        yield message

def gen_filter_stopidle(messages):
    # 530     000d00h:07m:14s 4       260     6       6       23817128        w_avrba782
    ignores = [
        re.compile(r"sudo /srv/deploy/wakari/scripts/container_status.sh"),
        re.compile(r"\d\d\d\s+\d\d\dd\d\dh:\d\dm:\d\ds"),
    ]

    for message in messages:

        # Most likely garbage in
        if "message" not in message:
            continue
        
        reject = False
        for filter_ in ignores:
            m = filter_.search(message["message"])
            if m:
                reject = True
                break
        
        if reject:
            continue
        
        yield message


    
def main():
    import sys
    
    parsed_input = gen_parse_log(sys.stdin)
    stop_idle    = gen_filter_stopidle(parsed_input)
    filtered     = gen_filter_standard(stop_idle)

    for line in filtered: 
        print "%(log_level)s %(datetime)s %(logger)s %(thread)s %(message)s" % line
    
if __name__ == '__main__':
    main()
    

    
    

