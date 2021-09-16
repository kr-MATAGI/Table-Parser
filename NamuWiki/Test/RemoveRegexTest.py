# NamuWiki Regex Test

import re
import unittest

from NamuWiki.NamuParser import RE_LITERAL, RE_TEXT_SIZE_FRONT, RE_BR_TAG, RE_CLEARFIX
from NamuWiki.NamuParser import RE_PARENT_ARTICLE_LINK, RE_EXTERNAL_LINK, RE_IMAGE_FILE
from NamuWiki.NamuParser import RE_YOUTUBE, RE_KAKAO_TV, RE_NICO_VIDEO, RE_NAVER_VIDEO
from NamuWiki.NamuParser import RE_HTML_VIDEO, RE_ADD_LIST, RE_FOOT_NOTE, RE_AGE_FORM, RE_DATE_TIME_FORM, RE_DDAY_FORM
from NamuWiki.NamuParser import RE_TABLE_ALIGN, RE_TABLE_WIDTH, RE_CELL_SIZE, RE_CELL_H_ALIGN, RE_CELL_V_ALIGN
from NamuWiki.NamuParser import RE_FOLDING, RE_TABLE_BORDER_COLOR, RE_BG_COLOR


class RemoveRegexTest(unittest.TestCase):
    '''
        Test - Remove Literal
    '''
    def test_RemoveLiteral(self):
        answer = "리터럴"

        testStr = "{{{[[리터럴]]}}}"
        re_literal = re.sub(RE_LITERAL, '', testStr)
        self.assertEqual(answer, re_literal)

    '''
        Test - Remove Text Size (Front)
    '''
    def test_RemoveTextSizeAttr(self):
        testStr_1 = "{{{+1 텍스트}}}"
        answer_1 = "텍스트}}}"
        re_textSize_1 = re.sub(RE_TEXT_SIZE_FRONT, '', testStr_1)
        self.assertEqual(answer_1, re_textSize_1)

        testStr_2 = "{{{+2 Te2xt3}}}"
        answer_2 = "Te2xt3}}}"
        re_textSize_2 = re.sub(RE_TEXT_SIZE_FRONT, '', testStr_2)
        self.assertEqual(answer_2, re_textSize_2)

        testStr_3 = "{{{+2 323231243}}}"
        answer_3 = "323231243}}}"
        re_textSize_3 = re.sub(RE_TEXT_SIZE_FRONT, '', testStr_3)
        self.assertEqual(answer_3, re_textSize_3)

    '''
        Test - Remove article link
    '''
    def test_RemoveArticleLink(self):
        testStr_1 = "[[../]]"
        re_artiLink_1 = re.sub(RE_PARENT_ARTICLE_LINK, '', testStr_1)
        self.assertEqual('', re_artiLink_1)

        testStr_2 = "[[https://goo.gl]]"
        re_artiLink_2 = re.sub(RE_EXTERNAL_LINK, '', testStr_2)
        self.assertEqual('', re_artiLink_2)

        testStr_3 = "[[https://goo.gl/|출력]]"
        re_artiLink_3 = re.sub(RE_EXTERNAL_LINK, '', testStr_3)
        self.assertEqual('', re_artiLink_3)

        testStr_4 = "[[https://goo.gl/|[[파일:홈페이지 아이콘.svg]]]] test"
        re_artiLink_4 = re.sub(RE_EXTERNAL_LINK, '', testStr_4)
        self.assertEqual(' test', re_artiLink_4)

        testStr_5 = "[[http://goo.gl/|출력]]"
        re_artiLink_5 = re.sub(RE_EXTERNAL_LINK, '', testStr_5)
        self.assertEqual('', re_artiLink_5)

    '''
        Test - Remove Image File
    '''
    def test_RemoveImageAttributes(self):
        testStr_1 = "[[파일:example.png]] 1test"
        re_imageFile_1 = re.sub(RE_IMAGE_FILE, '', testStr_1)
        self.assertEqual(' 1test', re_imageFile_1)

        testStr_2 = "[[파일:example.png|width=100]] image"
        re_imageFile_2 = re.sub(RE_IMAGE_FILE, '', testStr_2)
        self.assertEqual(' image', re_imageFile_2)

        testStr_3 = "[[파일:example.png|width=15%]] image"
        re_imageFile_3 = re.sub(RE_IMAGE_FILE, '', testStr_3)
        self.assertEqual(' image', re_imageFile_3)

        testStr_4 = "[[파일:example.png|width=22%&align=center&height=300&bgcolor=#RRGGBB]] image"
        re_imageFile_4 = re.sub(RE_IMAGE_FILE, '', testStr_4)
        self.assertEqual(' image', re_imageFile_4)

    '''
        Test - Remove Video
    '''
    def test_RemoveVideoLinks(self):
        testStr_1 = "[youtube(jNQXAC9IVRw, start=1,height=200)] !youtube"
        re_youtube_1 = re.sub(RE_YOUTUBE, '', testStr_1)
        self.assertEqual(' !youtube', re_youtube_1)

        testStr_2 = "[kakaotv(405064748)]1 ~kakao"
        re_kakao = re.sub(RE_KAKAO_TV, '', testStr_2)
        self.assertEqual('1 ~kakao', re_kakao)

        testStr_3 = "[nicovideo(sm8628149)]nicovideo"
        re_nico = re.sub(RE_NICO_VIDEO, '', testStr_3)
        self.assertEqual('nicovideo', re_nico)

        testStr_4 = "[include(틀:navertv, i=1369799)]NAVER"
        re_naver_1 = re.sub(RE_NAVER_VIDEO, '', testStr_4)
        self.assertEqual('NAVER', re_naver_1)

        testStr_5 = "[include(틀:navervid, vid=123123324, outkey=dd832818s)]...nav...."
        re_naver_2 = re.sub(RE_NAVER_VIDEO, '', testStr_5)
        self.assertEqual("...nav....", re_naver_2)

        testStr_6 = "{{{#!html <video src='https://www.youtube.com/watch?v=_NDf8AdqOhA'></video>}}}, dd'd'"
        re_html_video_1 = re.sub(RE_HTML_VIDEO, '', testStr_6)
        self.assertEqual(", dd'd'", re_html_video_1)

        testStr_7 = "{{{#!html 'https://www.youtube.com/watch?v=_NDf8AdqOhA'}}}srcTest"
        re_html_video_2 = re.sub(RE_HTML_VIDEO, '', testStr_7)
        self.assertEqual('srcTest', re_html_video_2)

    '''
        Test - Remove List
    '''
    def test_RemoveAddList(self):
        testStr_1 = "v*v리스트 1"
        re_list_1 = re.sub(RE_ADD_LIST, '', testStr_1)
        self.assertEqual('리스트 1', re_list_1)

        testStr_2 = "vv*v리스트 1.1"
        re_list_2 = re.sub(RE_ADD_LIST, '', testStr_2)
        self.assertEqual('리스트 1.1', re_list_2)

        testStr_3 = "vvv*v리스트 2.1.1"
        re_list_3 = re.sub(RE_ADD_LIST, '', testStr_3)
        self.assertEqual('리스트 2.1.1', re_list_3)

        testStr_4 = "v1.v리스트 1"
        re_list_4 = re.sub(RE_ADD_LIST, '', testStr_4)
        self.assertEqual('리스트 1', re_list_4)

        testStr_5 = "vv1.v리스트 1.1"
        re_list_5 = re.sub(RE_ADD_LIST, '', testStr_5)
        self.assertEqual("리스트 1.1", re_list_5)

        testStr_6 = "vA.v리스트 1"
        re_list_6 = re.sub(RE_ADD_LIST, '', testStr_6)
        self.assertEqual("리스트 1", re_list_6)

        testStr_7 = "vvA.v리스트 2.1"
        re_list_7 = re.sub(RE_ADD_LIST, '', testStr_7)
        self.assertEqual("리스트 2.1", re_list_7)

        testStr_8 = "va.v리스트 1"
        re_list_8 = re.sub(RE_ADD_LIST, '', testStr_8)
        self.assertEqual("리스트 1", re_list_8)

        testStr_9 = "vva.v리스트 2.1"
        re_list_9 = re.sub(RE_ADD_LIST, '', testStr_9)
        self.assertEqual("리스트 2.1", re_list_9)

        testStr_10 = "vI.v리스트 1"
        re_list_10 = re.sub(RE_ADD_LIST, '', testStr_10)
        self.assertEqual("리스트 1", re_list_10)

        testStr_11 = "vvI.v리스트 2.1"
        re_list_11 = re.sub(RE_ADD_LIST, '', testStr_11)
        self.assertEqual("리스트 2.1", re_list_11)

        testStr_12 = "v*v리스트 1"
        re_list_12 = re.sub(RE_ADD_LIST, '', testStr_12)
        self.assertEqual("리스트 1", re_list_12)

        testStr_13 = "vv*v리스트 1.1"
        re_list_13 = re.sub(RE_ADD_LIST, '', testStr_13)
        self.assertEqual("리스트 1.1", re_list_13)

        testStr_14 = "vvv*v리스트 2.1"
        re_list_14 = re.sub(RE_ADD_LIST, '', testStr_14)
        self.assertEqual("리스트 2.1", re_list_14)

        testStr_15 = "v1.v리스트 1"
        re_list_15 = re.sub(RE_ADD_LIST, '', testStr_15)
        self.assertEqual("리스트 1", re_list_15)

    '''
        Test - Remove Foot Note
    '''
    def test_RemoveFootNote(self):
        testStr_1 = "[*v텍스트 1] test"
        re_footNote_1 = re.sub(RE_FOOT_NOTE, '', testStr_1)
        self.assertEqual(' test', re_footNote_1)

        testStr_2 = "[*Av텍스트 2] test"
        re_footNote_2 = re.sub(RE_FOOT_NOTE, '', testStr_2)
        self.assertEqual(' test', re_footNote_2)

        testStr_3 = "[*A]"
        re_footNote_3 = re.sub(RE_FOOT_NOTE, '', testStr_3)
        self.assertEqual('', re_footNote_3)

    '''
        Test - Remove Age, Date, d-day
    '''
    def test_RemoveAgeDateDday(self):
        ageStr_1 = "[age(1994-12-09)]"
        re_age_1 = re.sub(RE_AGE_FORM, '', ageStr_1)
        self.assertEqual('', re_age_1)

        ageStr_2 = "[age(1994-9-2)]"
        re_age_2 = re.sub(RE_AGE_FORM, '', ageStr_2)
        self.assertEqual('', re_age_2)

        dateStr = "[date]"
        re_date = re.sub(RE_DATE_TIME_FORM, '', dateStr)
        self.assertEqual('', re_date)

        dateTimeStr = "[datetime]"
        re_dateTime = re.sub(RE_DATE_TIME_FORM, '', dateTimeStr)
        self.assertEqual('', re_dateTime)

        ddayStr_1 = "[dday(1994-12-09)]"
        re_dday_1 = re.sub(RE_DDAY_FORM, '', ddayStr_1)
        self.assertEqual('', re_dday_1)

        ddayStr_2 = "[dday(1994-02-01)]"
        re_dday_2 = re.sub(RE_DDAY_FORM, '', ddayStr_2)
        self.assertEqual('', re_dday_2)

    '''
        Test - Remove [br], [clearfix] tags
    '''
    def test_RemoveBrAndClearfixTags(self):
        answer = "나는  마타기  입니다."

        brStr = "나는 [br] 마타기 [br] 입니다."
        re_br = re.sub(RE_BR_TAG, '', brStr)
        self.assertEqual(answer, re_br)

        clearfixStr = "나는 [clearfix] 마타기 [clearfix] 입니다."
        re_clearfix = re.sub(RE_CLEARFIX, '', clearfixStr)
        self.assertEqual(answer, re_clearfix)

    '''
        Test - Remove Table Attributes
    '''
    def test_RemoveTableAttributes(self):
        answer = ".!3text"

        alignStr_1 = "<tablealign=left>" + answer
        re_align_1 = re.sub(RE_TABLE_ALIGN, '', alignStr_1)
        self.assertEqual(answer, re_align_1)

        alignStr_2 = "<table align=center>" + answer
        re_align_2 = re.sub(RE_TABLE_ALIGN, '', alignStr_2)
        self.assertEqual(answer, re_align_2)

        tableWidthStr_1 = "<tablewidth=100px>" + answer
        re_tableWidth_1 = re.sub(RE_TABLE_WIDTH, '', tableWidthStr_1)
        self.assertEqual(answer, re_tableWidth_1)

        tableWidthStr_2 = "<table width=100px>" + answer
        re_tableWidth_2 = re.sub(RE_TABLE_WIDTH, '', tableWidthStr_2)
        self.assertEqual(answer, re_tableWidth_2)

        tableBorderColorStr_1 = "<tablebordercolor=#RRGGBB>" + answer
        re_tableBorder_1 = re.sub(RE_TABLE_BORDER_COLOR, '', tableBorderColorStr_1)
        self.assertEqual(answer, re_tableBorder_1)

        tableBorderColorStr_2 = "<table bordercolor=#RRGGBB>" + answer
        re_tableBorder_2 = re.sub(RE_TABLE_BORDER_COLOR, '', tableBorderColorStr_2)
        self.assertEqual(answer, re_tableBorder_2)

        cellWidthStr = "<width=100px>" + answer
        re_cellWidth = re.sub(RE_CELL_SIZE, '', cellWidthStr)
        self.assertEqual(answer, re_cellWidth)

        cellWidthHeight = "<width=100%>" + answer + "<height=50px>"
        re_cellWHSize = re.sub(RE_CELL_SIZE, '', cellWidthHeight)
        self.assertEqual(answer, re_cellWHSize)

        cellHAlignStr = "<(>" + answer + "<:>" + "<)>" + answer
        re_cellHAlign = re.sub(RE_CELL_H_ALIGN, '', cellHAlignStr)
        self.assertEqual(answer+answer, re_cellHAlign)

        cellVAlignStr = "<^|31>" + answer + "<v|1>" + answer
        re_cellVAlign = re.sub(RE_CELL_V_ALIGN, '', cellVAlignStr)
        self.assertEqual(answer+answer, re_cellVAlign)

    '''
        Test - Remove Folding
    '''
    def test_RemoveFolding(self):
        answer = "[ 내용 1 ][ '''내용 2''' ]}}}"
        foldingStr = "{{{#!folding [ ''접기'' 링크 텍스트 ][ 내용 1 ][ '''내용 2''' ]}}}"
        re_folding = re.sub(RE_FOLDING, '', foldingStr)
        self.assertEqual(answer, re_folding)


    '''
        Test - Real Dataset Exception
    '''
    def test_RealDatasetException(self):
        ans_1 = "마스코트 '에너지보이'"
        test_1 = "[[파일:한전 캐릭터.jpg|width=70]]마스코트 '에너지보이'"
        re_test_1 = re.sub(RE_IMAGE_FILE, '', test_1)
        self.assertEqual(ans_1, re_test_1)

        ans_2 = "마스코트 '에너지보이' 각주 테스트"
        test_2 = "마스코트 '에너지보이'[* 메인 마스코트와는 별개로 서비스 쪽 캐릭터인 ] 각주 테스트"
        re_test_2 = re.sub(RE_FOOT_NOTE, '', test_2)
        self.assertEqual(ans_2, re_test_2)

        ans_3 = '[* 메인 마스코트와는 별개로 서비스 쪽 캐릭터인 ]'
        test_3 = "[* 메인 마스코트와는 별개로 서비스 쪽 캐릭터인 [[https://pbs.twing.com/media/DQvgTnHUQAEbaru.jpg|케피, 우피, 해피도 있다.]]]"
        reg_3 = re.sub(RE_EXTERNAL_LINK, '', test_3)
        self.assertEqual(ans_3, reg_3)

        ans_4 = '[br]'
        test_4 = "[br][[https://www.instagram.com/iamkepco| [[파일:인스타그램 아이콘.svg|width=15]]"
        reg_4 = re.sub(RE_EXTERNAL_LINK, '', test_4)
        self.assertEqual(ans_4, reg_4)
