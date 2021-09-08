# NamuWiki Regex Test

import re
import unittest

from NamuWiki.NamuParser import RE_ROW_SPLIT, RE_OLD_COL_SPAN, RE_NEW_COL_SPAN, RE_NEW_ROW_SPAN, RE_EMPTY_CELL
from NamuWiki.NamuParser import RE_TEXT_FORM, CONV_TEXT_FORM, RE_SUB_SCRIPT, CONV_SUB_SCRIPT, RE_TEXT_COLOR, CONV_TEXT_COLOR
from NamuWiki.NamuParser import RE_BR_TAG, RE_BG_COLOR, CONV_BG_COLOR, RE_TBG_COLOR, CONV_TBG_COLOR
from NamuWiki.NamuParser import RE_COL_BG_COLOR, CONV_COL_BG_COLOR, RE_ROW_BG_COLOR, CONV_ROW_BG_COLOR, RE_CELL_COLOR, CONV_CELL_COLOR
from NamuWiki.NamuParser import RE_COL_COLOR, CONV_COL_COLOR, RE_ROW_COLOR, CONV_ROW_COLOR, RE_LITERAL, RE_TEXT_SIZE_FRONT
from NamuWiki.NamuParser import RE_PARENT_ARTICLE_LINK, RE_CHILD_ARTICLIE_LINK, RE_EXTERNAL_LINK, RE_IMAGE_FILE, RE_IMAGE_PARAM
from NamuWiki.NamuParser import RE_IMAGE_ALIGN, RE_YOUTUBE, RE_KAKAO_TV, RE_NICO_VIDEO, RE_NAVER_VIDEO, RE_VIDEO_PARAM
from NamuWiki.NamuParser import RE_HTML_VIDEO, RE_ADD_LIST, RE_FOOT_NOTE, RE_AGE_FORM, RE_DATE_TIME_FORM, RE_DDAY_FORM
from NamuWiki.NamuParser import RE_TABLE_ALIGN, RE_TABLE_WIDTH, RE_CELL_WIDTH, RE_CELL_HEIGHT, RE_CELL_H_ALIGN, RE_CELL_V_ALIGN
from NamuWiki.NamuParser import RE_FOLDING, RE_MACRO_RUBY, RE_RUBY_FRONT

# 2.1 Text Form
class UnitTestSet(unittest.TestCase):
    '''
        Test - Text Form Convert
    '''
    def test_ConvertTextForm(self):
        textFormStr_1 = "''' 안녕하세요 '''"
        textFormStr_2 = "'' 안녕하세요 ''"
        textFormStr_3 = "''' '' 안녕하세요 '' '''"
        textFormStr_4 = "__ 안녕하세요 __"
        textFormStr_5 = "~~ 안녕하세요 __"
        textFormStr_6 = "-- 안녕하세요 --"
        textFormStr_7 = "안녕하세요^^위첨자^^"
        textFormStr_8 = "안녕하세요,,아래첨자,,"

        textFormAns_1 = '<tf> 안녕하세요 <tf>'
        textFormAns_2 = '안녕하세요 위첨자 '
        textFormAns_3 = '안녕하세요 아래첨자 '

        re_textForm_1 = re.sub(RE_TEXT_FORM, CONV_TEXT_FORM, textFormStr_1)
        re_textForm_2 = re.sub(RE_TEXT_FORM, CONV_TEXT_FORM, textFormStr_2)
        re_textForm_3 = re.sub(RE_TEXT_FORM, CONV_TEXT_FORM, textFormStr_3)
        re_textForm_4 = re.sub(RE_TEXT_FORM, CONV_TEXT_FORM, textFormStr_4)
        re_textForm_5 = re.sub(RE_TEXT_FORM, CONV_TEXT_FORM, textFormStr_5)
        re_textForm_6 = re.sub(RE_TEXT_FORM, CONV_TEXT_FORM, textFormStr_6)

        re_textForm_7 = re.sub(RE_SUB_SCRIPT, CONV_SUB_SCRIPT, textFormStr_7)
        re_textForm_8 = re.sub(RE_SUB_SCRIPT, CONV_SUB_SCRIPT, textFormStr_8)

        self.assertEqual(textFormAns_1, re_textForm_1)
        self.assertEqual(textFormAns_1, re_textForm_2)
        self.assertEqual(textFormAns_1, re_textForm_3)
        self.assertEqual(textFormAns_1, re_textForm_4)
        self.assertEqual(textFormAns_1, re_textForm_5)
        self.assertEqual(textFormAns_1, re_textForm_6)
        self.assertEqual(textFormAns_2, re_textForm_7)
        self.assertEqual(textFormAns_3, re_textForm_8)

    '''
        Test - Text Color Convert
    '''
    def test_ConvertTextColor(self):
        textColorStr_1 = "{{{#ff0000 텍스트}}}"
        textColorStr_2 = "{{{#f00 텍스트}}}"
        textColorStr_3 = "{{{#800080 text}}}"
        textColorStr_4 = "{{{#purple text}}}"
        textColorStr_5 = "{{{#888,#ff0 다크테스트}}}"
        textColorStr_6 = "{{{#grey, #yellow 다크테스트}}}"
        textColorStr_7 = "{{{#red __밑줄 포함__}}}"
        textColorStr_8 = "__{{{#red 밑줄 제외}}}__"

        re_tc_1 = re.sub(RE_TEXT_COLOR, CONV_TEXT_COLOR, textColorStr_1)
        re_tc_2 = re.sub(RE_TEXT_COLOR, CONV_TEXT_COLOR, textColorStr_2)
        re_tc_3 = re.sub(RE_TEXT_COLOR, CONV_TEXT_COLOR, textColorStr_3)
        re_tc_4 = re.sub(RE_TEXT_COLOR, CONV_TEXT_COLOR, textColorStr_4)
        re_tc_5 = re.sub(RE_TEXT_COLOR, CONV_TEXT_COLOR, textColorStr_5)
        re_tc_6 = re.sub(RE_TEXT_COLOR, CONV_TEXT_COLOR, textColorStr_6)

        re_tc_7 = re.sub(RE_TEXT_FORM, CONV_TEXT_FORM, textColorStr_7)
        re_tc_7 = re.sub(RE_TEXT_COLOR, CONV_TEXT_COLOR, re_tc_7)

        re_tc_8 = re.sub(RE_TEXT_FORM, CONV_TEXT_FORM, textColorStr_8)
        re_tc_8 = re.sub(RE_TEXT_COLOR, CONV_TEXT_COLOR, re_tc_8)

        ans_1 = "<tc>텍스트}}}"
        ans_2 = "<tc>text}}}"
        ans_3 = "<tc>다크테스트}}}"
        ans_4 = "<tc><tf>밑줄 포함<tf>}}}"
        ans_5 = "<tf><tc>밑줄 제외}}}<tf>"

        self.assertEqual(ans_1, re_tc_1)
        self.assertEqual(ans_1, re_tc_2)

        self.assertEqual(ans_2, re_tc_3)
        self.assertEqual(ans_2, re_tc_4)

        self.assertEqual(ans_3, re_tc_5)
        self.assertEqual(ans_3, re_tc_6)

        self.assertEqual(ans_4, re_tc_7)
        self.assertEqual(ans_5, re_tc_8)

    '''
        Test - Convert Background Color
    '''
    def test_ConvertBackgroundColor(self):
        answer = CONV_BG_COLOR

        testStr_1 = "<bgcolor=white>"
        re_bgc_1 = re.sub(RE_BG_COLOR, CONV_BG_COLOR, testStr_1)
        self.assertEqual(answer, re_bgc_1)

        testStr_2 = "<bgcolor=#RRGGBB>"
        re_bgc_2 = re.sub(RE_BG_COLOR, CONV_BG_COLOR, testStr_2)
        self.assertEqual(answer, re_bgc_2)

        testStr_3 = "<bgcolor=#RRGGBB,#RRGGBB>"
        re_bgc_3 = re.sub(RE_BG_COLOR, CONV_BG_COLOR, testStr_3)
        self.assertEqual(answer, re_bgc_3)

        testStr_4 = "<bgcolor=#00a495, #2d2f34>"
        re_bgc_4 = re.sub(RE_BG_COLOR, CONV_BG_COLOR, testStr_4)
        self.assertEqual(answer, re_bgc_4)


    '''
        Test - Convert Table Background Color
    '''
    def test_ConvertTableBackgroundColor(self):
        answer = CONV_TBG_COLOR

        testStr_1 = "<tablecolor=white>"
        re_tbg_1 = re.sub(RE_TBG_COLOR, CONV_TBG_COLOR, testStr_1)
        self.assertEqual(answer, re_tbg_1)

        testStr_2 = "<tablecolor=#RRGGBB>"
        re_tbg_2 = re.sub(RE_TBG_COLOR, CONV_TBG_COLOR, testStr_2)
        self.assertEqual(answer, re_tbg_2)

        testStr_3 = "<tablecolor=#RRGGBB,#RRGGBB>"
        re_tbg_3 = re.sub(RE_TBG_COLOR, CONV_TBG_COLOR, testStr_3)
        self.assertEqual(answer, re_tbg_3)

        testStr_4 = "<tablecolor=#00a495, #2d2f34>"
        re_tbg_4 = re.sub(RE_TBG_COLOR, CONV_TBG_COLOR, testStr_4)
        self.assertEqual(answer, re_tbg_4)

    '''
        Test - Convert Column Background Color
    '''
    def test_ConvertColBackgroundColor(self):
        answer = CONV_COL_BG_COLOR

        testStr_1 = "<colbgcolor=#RRGGBB>"
        re_cbg_1 = re.sub(RE_COL_BG_COLOR, CONV_COL_BG_COLOR, testStr_1)
        self.assertEqual(answer, re_cbg_1)

        testStr_2 = "<colbgcolor=#FFF,#000>"
        re_cbg_2 = re.sub(RE_COL_BG_COLOR, CONV_COL_BG_COLOR, testStr_2)
        self.assertEqual(answer, re_cbg_2)

        testStr_3 = "<colbgcolor=#00a495, #2d2f34>"
        re_cbg_3 = re.sub(RE_COL_BG_COLOR, CONV_COL_BG_COLOR, testStr_3)
        self.assertEqual(answer, re_cbg_3)

    '''
        Test - Convert Row Background Color
    '''
    def test_ConvertRowBackgroundColor(self):
        answer = CONV_ROW_BG_COLOR

        testStr_1 = "<rowbgcolor=#RRGGBB>"
        re_rbg_1 = re.sub(RE_ROW_BG_COLOR, CONV_ROW_BG_COLOR, testStr_1)
        self.assertEqual(answer, re_rbg_1)

        testStr_2 = "<rowbgcolor=#FFF,#000>"
        re_rbg_2 = re.sub(RE_ROW_BG_COLOR, CONV_ROW_BG_COLOR, testStr_2)
        self.assertEqual(answer, re_rbg_2)

        testStr_3 = "<rowbgcolor=#00a495, #2d2f34>"
        re_rbg_3 = re.sub(RE_ROW_BG_COLOR, CONV_ROW_BG_COLOR, testStr_3)
        self.assertEqual(answer, re_rbg_3)

    '''
        Test - Convert Cell Color
    '''
    def test_ConvertCellColor(self):
        answer = CONV_CELL_COLOR

        testStr_1 = "<color=#RRGGBB>"
        re_cell_color_1 = re.sub(RE_CELL_COLOR, CONV_CELL_COLOR, testStr_1)

        testStr_2 = "<color=#FFF,#000>"
        re_cell_color_2 = re.sub(RE_CELL_COLOR, CONV_CELL_COLOR, testStr_2)

        testStr_3 = "<color=#00a495, #2d2f34>"
        re_cell_color_3 = re.sub(RE_CELL_COLOR, CONV_CELL_COLOR, testStr_3)

    '''
        Test - Convert Column Color
    '''
    def test_ConvertColColor(self):
        answer = CONV_COL_COLOR

        testStr_1 = "<colcolor=#RRGGBB>"
        re_col_color_1 = re.sub(RE_COL_COLOR, CONV_COL_COLOR, testStr_1)

        testStr_2 = "<colcolor=#FFF,#000>"
        re_col_color_2 = re.sub(RE_COL_COLOR, CONV_COL_COLOR, testStr_2)

        testStr_3 = "<colcolor=#00a495, #2d2f34>"
        re_col_color_3 = re.sub(RE_COL_COLOR, CONV_COL_COLOR, testStr_3)

    '''
        Test - Convert Row Color
    '''
    def test_ConvertRowColor(self):
        answer = CONV_ROW_COLOR

        testStr_1 = "<rowcolor=#RRGGBB>"
        re_row_color_1 = re.sub(RE_ROW_COLOR, CONV_ROW_COLOR, testStr_1)

        testStr_2 = "<rowcolor=#FFF,#000>"
        re_row_color_2 = re.sub(RE_ROW_COLOR, CONV_ROW_COLOR, testStr_2)

        testStr_3 = "<rowcolor=#00a495, #2d2f34>"
        re_row_color_3 = re.sub(RE_ROW_COLOR, CONV_ROW_COLOR, testStr_3)
