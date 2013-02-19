#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from operator import attrgetter
from itertools import chain
from urllib import unquote

from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from endless_pagination.decorators import page_template

from .models import Post
from .models import Tag
from .models import Like
from .models import Follow
from account.models import UserProfile
from .utils import random_queryset


@login_required(login_url=reverse_lazy('login'))
def like(request, post_id):
    referer = request.META.get('HTTP_REFERER')
    post = Post.objects.get(id=post_id)
    user = request.user

    if user != post.author:
        Like.objects.get_or_create(author=user, post=post)

    return HttpResponseRedirect(referer or '/')


@login_required(login_url=reverse_lazy('login'))
def unlike(request, post_id):
    referer = request.META.get('HTTP_REFERER')
    post = Post.objects.get(id=post_id)
    user = request.user

    try:
        Like.objects.get(author=user, post=post).delete()
    except ObjectDoesNotExist:
        pass

    return HttpResponseRedirect(referer or '/')


@login_required(login_url=reverse_lazy('login'))
def reblog(request, post_id):
    referer = request.META.get('HTTP_REFERER')
    post = Post.objects.get(id=post_id)
    user = request.user
    src_post = deepcopy(Post.objects.get(id=post_id))
    tags = src_post.tags.all()

    if user != src_post.author:
        try:
            Post.objects.get(author=user, reblog=src_post)
        except ObjectDoesNotExist:
            post.reblog = src_post
            post.id = None
            post.author = user
            post.created_at = None
            post.save()
            post.tags.add(*tags)

    return HttpResponseRedirect(referer or '/')


@login_required(login_url=reverse_lazy('login'))
def follow(request, user_slug):
    referer = request.META.get('HTTP_REFERER')
    follower = request.user
    following = UserProfile.objects.get(slug=user_slug).user
    if follower != following:
        Follow.objects.get_or_create(follower=follower, following=following)

    return HttpResponseRedirect(referer or '/')


@login_required(login_url=reverse_lazy('login'))
def unfollow(request, user_slug):
    referer = request.META.get('HTTP_REFERER')
    follower = request.user
    following = UserProfile.objects.get(slug=user_slug).user
    follow = Follow.objects.get(follower=follower, following=following)
    follow.delete()

    return HttpResponseRedirect(referer or '/')


@page_template('post/index_page.html')
def user_index(request, user_slug, tag_slug=None,
               template='post/index.html', extra_context=None):
    userprofile = UserProfile.objects.get(slug=user_slug)
    user = blog_author = userprofile.user
    posts = Post.objects.filter(author=user).order_by('-created_at')
    if tag_slug:
        posts = posts.filter(tags__slug__iexact=tag_slug)
        tag_name = Tag.objects.get(slug=tag_slug)
    else:
        tag_name = None

    context = {
        'blog_author': blog_author,
        'tag_name': tag_name,
        'posts': posts,
    }
    if extra_context:
        context.update(extra_context)
    return render_to_response(template, context,
                              context_instance=RequestContext(request))


def user_search(request, user_slug):
    referer = request.META.get('HTTP_REFERER',
                               reverse_lazy('user_index', user_slug))
    keyword = request.GET.get('q')
    if not keyword:
        return HttpResponseRedirect(referer)
    else:
        return HttpResponseRedirect(reverse_lazy('user_search_result',
                                                 kwargs={
                                                     'user_slug': user_slug,
                                                     'keyword': keyword,
                                                 }))


def user_search_result(request, user_slug, keyword):
    keyword = unquote(keyword)
    if not keyword:
        return HttpResponseRedirect(reverse_lazy('user_index', user_slug))

    userprofile = UserProfile.objects.get(slug=user_slug)
    user = blog_author = userprofile.user
    posts = Post.objects.filter(Q(author=user) & Q(tags__name__iexact=keyword))
    posts = posts.order_by('-created_at')

    context = {
        'blog_author': blog_author,
        'posts': posts,
        'keyword': keyword,
    }
    return render_to_response('post/search.html', context,
                              context_instance=RequestContext(request))


def detail(request, user_slug, post_id, post_slug=None):
    userprofile = UserProfile.objects.get(slug=user_slug)
    blog_author = userprofile.user
    post = Post.objects.get(id=post_id)
    likes = Like.objects.filter(post=post)
    reblogs = Post.objects.filter(reblog=post)
    # if likes and (not reblogs):
        # notes = likes
    # elif reblogs and (not likes):
        # notes = reblogs
    # elif likes and reblogs:
    notes = sorted(chain(likes, reblogs), key=attrgetter('created_at'),
                   reverse=True)
    # else:
        # notes = None

    if post_slug and post_slug != post.slug:
        return HttpResponseNotFound()
    else:
        context = {
            'blog_author': blog_author,
            'post': post,
            'notes': notes,
        }
        return render_to_response('post/detail.html', context,
                                  context_instance=RequestContext(request))


def random_post(request, user_slug):
    author = UserProfile.objects.get(slug=user_slug).user
    post_id = random_queryset(Post, number=1, author=author)
    print post_id
    post_id = post_id[0].id

    return HttpResponseRedirect(reverse_lazy('post_detail',
                                             kwargs={
                                                 'user_slug': user_slug,
                                                 'post_id': post_id,
                                             }))
