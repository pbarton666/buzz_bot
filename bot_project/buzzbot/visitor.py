import types

import buzzbot
from buzzbot import model
from buzzbot import bot
from datetime import datetime

myBotRoutines = bot.BotRoutines()

class Visitor(object):
    """
    Visits URLs and creates Content.
    """
    def __init__(self, search, url_records, delete_existing=False):
        """
        Instantiate.

        Keyword arguments:
        * `search`: A Search record
        * `url_records`: Either a URLS record or a list of them
        """
        self._search = search
        self._url_records = isinstance(url_records, types.ListType) and url_records or [url_records]
        self._delete_existing = delete_existing
    def __iter__(self):
        """
        Return Content records for these URLs.
        """
        for url_record in self._url_records:
            # TODO provide reasonable variable names 
            mydict = myBotRoutines.getContentWithFeedparser(url_record.urltext, self._search.targetword)
            snippets = mydict.get('cont')
            cleancont = myBotRoutines.applyContentLevelFilter(snippets, self._search.eliminationwords, self._search.searchstring)
            for c in cleancont:
                attributes = dict(
                    urlid = url_record.id,
                    cont = c,
                    urltext = url_record.urltext,
                    userid = self._search.userid,
                    dateaccessed = datetime.now(),
                    searchid = self._search.id,
                    deleteme = self._delete_existing
                )
                yield model.Content(**attributes)

    def visit(self):
        """
        Return list of Content records for these URLs.
        """
        return list(self)
