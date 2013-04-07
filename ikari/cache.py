import random
import hashlib
from django.core.cache import cache

from . import settings


def format_key(key, value=None):
    if value is None:
        return settings.CACHE_KEY_PREFIX + key
    return settings.CACHE_KEY_PREFIX + hashlib.md5(key.format(value)).hexdigest()


def cache_thing(**kwargs):
    """ add an item to the cache """
    action = kwargs.get('action', None)
    # action is included for m2m_changed signal. Only cache on the post_*.
    if not action or action in ['post_add', 'post_remove', 'post_clear']:
        thing = kwargs.get('instance')
        key = format_key(settings.CACHE_KEY_ITEM, thing.get_slug())
        cache.add(key, thing)
        print "Cached {} with {}".format(thing, key)


def get_thing(**kwargs):
    """
        facet: search on all or just for one item?
                a search on all only tells you if the query is in the list
                a search on a unique key will return that item

        query: generally a hostname to check. ie:
            - subdomain.example.com
            - example.com
            - another.net

        update: A callable that will return data to update the cache key with.
    """
    facet = kwargs.get('facet', None)
    query = kwargs.get('query', None)
    update = kwargs.get('update', None)


    if facet:
        facet = facet.lower()
        if facet == 'all':
            key = format_key(settings.CACHE_KEY_ALL)
            # is the query in the list?
            result = cache.get(key)
            if result == None and callable(update):
                result = update()
                cache.add(key, result)
            print "Retrieving Cache Key {} result: {}".format(key, thing)
            return bool(query in result)

        elif facet == 'item':
            key = format_key(settings.CACHE_KEY_ITEM, query)
            # give me the item matching the query
            thing = cache.get(key)
            if thing == None and callable(update):
                thing = update()
                cache.add(key, thing)
            print "Retrieving Cache Key {} result: {}".format(key, thing)
            return thing


def uncache_thing(**kwargs):
    """ Simple scorched earth policy on cache items. """
    thing = kwargs.get('instance')
    data = {
        format_key(settings.CACHE_KEY_ITEM, thing.name): None,
        format_key(settings.CACHE_KEY_ALL): None
    }
    cache.set_many(data, 5)
