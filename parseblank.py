#!/usr/bin/env python
# -*- coding: utf-8 -*-

# encoding=utf8

import sqlite3 as sql
import sys

from bs4 import BeautifulSoup
from datetime import datetime
import urllib
import threading
from mail import send_multiple_mailgun

reload(sys)
sys.setdefaultencoding('utf8')
DATABASE_PATH = './database.db'


def fetch_emails_and_tokens():
    conn = sql.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM emails')
    all_rows = c.fetchall()
    c.close()
    return all_rows


def fetch_previous_blank_posts():
    conn = sql.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM posts')
    all_rows = c.fetchall()
    c.close()
    return [row[0] for row in all_rows]


def add_post(post):
    con = sql.connect(DATABASE_PATH)
    c = con.cursor()
    c.execute("INSERT INTO posts (post) VALUES (?)", (post,))
    con.commit()
    con.close()


class Post:
    def get_type(self, article):
        link = article.find("a")
        href = link["href"]

        if article.find("div", class_="nrk-video"):
            return("video")
        if article.find("iframe", class_="instagram-media"):
            return "instagram-post"
        if article.find("div", class_="nrk-chatlog-header-element"):
            return("chat")
        else:
            return("post")

    def convert_time(self, norwegian):
        norwegian = norwegian.split(" ", 1)[1].strip()
        return datetime.strptime(norwegian, '%d.%m.%y kl %H.%M')

    def __init__(self, article):
        self.article = article
        self.img = article.find("img")["src"]
        self.link = article.find("a")
        self.href = self.link["href"]
        self.original_time = self.link.get_text()
        self.original_time = self.original_time.replace("ø", "o")
        self.time = datetime.now().strftime("%d.%m.%y kl %H.%M")
        self.type = self.get_type(self.article)
        try:
            self.title = ' '.join(self.href.split("/")[-2].split('-')).capitalize()
        except:
            self.title = ' '


def blank():
    emails_and_tokens = fetch_emails_and_tokens()
    r = urllib.urlopen('http://blank.p3.no').read()
    soup = BeautifulSoup(r, "html.parser")
    articles = soup.find_all("article", class_="post")
    posts = [Post(article) for article in articles]

    if not posts or len(posts) == 0:
        print("EMPTY POSTS")
    else:
        last = posts[0]
        _id = last.href

        if not _id in fetch_previous_blank_posts():
            add_post(_id)

            send_multiple_mailgun(emails_and_tokens, last.title, last.href, last.time, last.type)
            print("EMAILS SENDT!")

            print(last.__dict__)
        else:
            print("Allerede sendt: " + last.href)
    threading.Timer(30.0, blank).start()

blank()