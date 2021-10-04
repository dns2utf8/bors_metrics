#!/usr/bin/env python3

from prometheus_client import start_http_server, write_to_textfile, Summary, Counter, Gauge, CollectorRegistry
from bs4 import BeautifulSoup
import requests

### Begin Config

OUTPUT_FILE = './htdocs/metrics'
NAMESPACE = "bors"
PROMETHEUS_LISTEN_PORT = 8000

URLS = [
    ('rust', 'https://bors.rust-lang.org/queue/rust'),
]

### End Config

registry = CollectorRegistry()

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request', registry=registry, namespace=NAMESPACE)
FETCH_TIME = Summary('fetch_processing_seconds', 'Time spent processing request', registry=registry, namespace=NAMESPACE)

### Fetching the interesting data
@FETCH_TIME.time()
def fetch(url):
    r = requests.get(url)
    if r.status_code != 200:
        print("failed to fetch", url, r.status_code)
        return ""
    
    soup = BeautifulSoup(r.text, features="html.parser")
    p = soup.body.findNext('p')
    p = p.findNextSibling('p')
    
    c = list(p.children)
    first = c[0].strip()
    
    return first

def parse_totals_string(queue_name, input):
    """
    Expecting something like this:
    '449 total, 59 approved, 12 rolled up, 9 failed\n            /'
    """
    l = input.splitlines()[0]
    parts = l.split(',')
    
    o = {}
    for part in parts:
        spaced = part.strip().split(" ", 1)
        if len(spaced) != 2:
            print("skipping spaced result", part)
            continue
        (num, kind) = spaced
        kind_underscored = kind.replace(" ", "_")
        g = Gauge('{}_{}'.format(queue_name, kind_underscored), '{} {}'.format(queue_name, kind), registry=registry, namespace=NAMESPACE)
        g.set(int(num))
    


@REQUEST_TIME.time()
def prepare_output():
    for (queue_name, url) in URLS:
        output = fetch(url)
        parse_totals_string(queue_name, output)

    #textfile = open(OUTPUT_FILE, "w")
    #a = textfile.write(output)
    #textfile.close()


### Distributing to prometheus

# Decorate function with metric.
#@REQUEST_TIME.time()
#def process_request(t):
#    """A dummy function that takes some time."""
#    time.sleep(t)

if __name__ == '__main__':
    prepare_output()
    
    # Start up the server to expose the metrics.
    start_http_server(PROMETHEUS_LISTEN_PORT)
    
    request_counter = Counter('number_requests_handled', 'The amount of request processed by this instance', registry=registry, namespace=NAMESPACE)
    #request_counter.set(0)
    request_counter.inc()
    # process the requests in sequence
    
    # Generate synthetic events
    #while True:
    #    request_counter.inc()
    #    process_request(random.random())
    write_to_textfile(OUTPUT_FILE, registry)
