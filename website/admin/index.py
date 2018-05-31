#!/usr/bin/python3.6
import os
import datetime

from simplerr.web import web
from common.models.main import *

def prod_check():
    """Check if we are in production environment."""
    if 'DEVBOX' in os.environ:
        if os.environ['DEVBOX'] == 'PROD': return False
    return True

@web('/admin', '/admin/templates/admin.html')
def admin(request):
    if not prod_check(): return

    if request.form.get('link'):
        Article.create(link=request.form.get('link')).save()
        # To do: redirect

    if request.args.get('delete'):
        article = Article.get(Article.link == request.args.get('delete'))
        article.delete_instance()

    return {'title': 'admin', 'articles': Article.select()}

@web('/admin/edit_article/<article_id>', '/admin/templates/edit_article.html')
def edit_article(request, article_id):
    if not prod_check(): return

    article = Article.get(Article.id == article_id)

    if request.form.get('action') == 'save':
        article.link      = request.form.get('link', '')
        article.title     = request.form.get('title', '')
        article.date      = request.form.get('date', datetime.datetime.now())
        article.category  = request.form.get('category', '')
        article.content   = request.form.get('content', '')
        article.thumbnail = request.form.get('thumbnail', '')
        article.tags      = request.form.get('tags', '')

        article.save()

    if request.form.get('action') == 'publish':
        article.wip  = 'no'
        article.date = datetime.datetime.now()

        article.save()

    return {'title': 'edit article', 'article': article}

@web('/admin/view_article/<link>', '/article/templates/article_layout.html')
def view_article(request, link):
    if not prod_check(): return

    article = Article.get(Article.link == link)

    previous_article = Article.select().where(Article.date < article.date, Article.wip == 'no') or [{'title': '', 'link': '#'}]
    next_article     = Article.select().where(Article.date > article.date, Article.wip == 'no') or [{'title': '', 'link': '#'}]

    return {
        'title'    : f'Preview: {article.title}',
        'article'  : article, 
        'previous' : previous_article[-1:][0],
        'next'     : next_article[0]
    }

@web('/admin/static/<path:file>', file=True)
def files(request, file):
    return './admin/static/' + file
