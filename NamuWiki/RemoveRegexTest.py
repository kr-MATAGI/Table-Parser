# NamuWiki Regex Test

import re
import unittest

from NamuWiki.NamuParser import RE_LITERAL, RE_TEXT_SIZE_FRONT, RE_BR_TAG
from NamuWiki.NamuParser import RE_PARENT_ARTICLE_LINK, RE_CHILD_ARTICLIE_LINK, RE_EXTERNAL_LINK, RE_IMAGE_FILE, RE_IMAGE_PARAM
from NamuWiki.NamuParser import RE_IMAGE_ALIGN, RE_YOUTUBE, RE_KAKAO_TV, RE_NICO_VIDEO, RE_NAVER_VIDEO, RE_VIDEO_PARAM
from NamuWiki.NamuParser import RE_HTML_VIDEO, RE_ADD_LIST, RE_FOOT_NOTE, RE_AGE_FORM, RE_DATE_TIME_FORM, RE_DDAY_FORM
from NamuWiki.NamuParser import RE_TABLE_ALIGN, RE_TABLE_WIDTH, RE_CELL_WIDTH, RE_CELL_HEIGHT, RE_CELL_H_ALIGN, RE_CELL_V_ALIGN
from NamuWiki.NamuParser import RE_FOLDING, RE_MACRO_RUBY, RE_RUBY_FRONT


class RemoveRegexTest(unittest.TestCase):
    '''

    '''