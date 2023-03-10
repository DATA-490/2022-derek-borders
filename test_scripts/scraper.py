#! /usr/bin/python3

# Example from: 
# https://github.com/NotYourGuy/scraperr/blob/master/scrapper.py

import argparse
import sys
import praw
import prawcore
import shutil
import subprocess
import os
import errno

# Initialize reddit using your credentials:
# http://www.storybench.org/how-to-scrape-reddit-with-python/

# Example
# reddit = praw.Reddit("scraperr")

# My Personal REddit App
reddit = praw.Reddit(client_id='VZDFQR1wT8giqAVcq09UmQ', \
                     client_secret='27AnuMqvvV6CbxekJspgAyxD4UYThw ', \
                     user_agent='nms-screenshot-scraper', \
                     username='nms_cartographer ', \
                     password='FITV4g63420@')

# nmsce = reddit.subreddit('NMSCoordinateExchange')

# Argument parsing
parser = argparse.ArgumentParser()

# Argument help messages
subredditArgHelp = 'The subreddit from which you wish to download the pictures'
limitArgHelp = 'Limit the number of posts to download (default: 10)'
periodArgHelp = ("The period from when to download the pictures (default: day) -- options: day, month, year, all")
directoryArgHelp = ('The directory for the pictures to be downloaded into (default: reddit-wallpapers/)')

# Arguments
# Example usage: scrapper.py [-l LIMIT] [-p PERIOD] [-d DIRECTORY] subreddit
parser.add_argument('subreddit', default='NMSCoordinateExchange' help=subredditArgHelp, action='store')
parser.add_argument('-l', '--limit', default=100, help=limitArgHelp, type=int, action='store')
parser.add_argument('-p', '--period', default='day', help=periodArgHelp, action='store')
parser.add_argument('-d', '--directory', default='../img/scraped', help=directoryArgHelp, action='store')

args = parser.parse_args()

hot_subreddit = reddit.subreddit(args.subreddit).top(args.period, limit=args.limit)

try:
    url = [post.url for post in hot_subreddit]
except prawcore.ResponseException:
    print('An error occurred during authorisation. Please check that'
          'your Reddit app credentials are set correctly and try again.')
    sys.exit(-1)
except prawcore.OAuthException:
    print('An error occurred during authorisation. Please check that'
          'your Reddit account credentials are set correctly and try again.')
    sys.exit(-2)
except prawcore.NotFound:
    print('Failed to find a subreddit called "{}". Please check that'
          'the subreddit exists and try again.'.format(args.subreddit))
    sys.exit(-3)

# https://stackoverflow.com/a/3173388


def main():
    # check if gallery-dl is installed on the system
    if shutil.which("gallery-dl") is None:
        print('gallery-dl not found on system')
        sys.exit(-4)
    download_urls()


def download_urls():
    cmd = ["gallery-dl"]
    cmd.append("--dest")
    cmd.append(args.directory)
    cmd.append("--verbose")
    cmd.append("--write-log")
    cmd.append(os.path.join(args.directory, "gallery-dl.log"))
    cmd.append("--write-unsupported")
    cmd.append(os.path.join(args.directory,"gallery-dl-unsupported.log"))
    cmd.append("-i-")

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for value in url:
        try:
            p.stdin.write((value+'\n').encode())
        except IOError as e:
            if e.errno == errno.EPIPE or e.errno == errno.EINVAL:
                break
            else:
                raise

    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()