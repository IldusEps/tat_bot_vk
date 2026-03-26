from types import SimpleNamespace
from database.word import *
import sys
sys.path.append(r"../")


def test_translation_replace():
    result = translation_replace(
        "с\n<tr>агач</tr><eml><w>хвойные деревья</w> ылыслы агачлар</eml>")
    assert result == (
        'с\n<u>агач</u>\n    <i><b>хвойные деревья</b> ылыслы агачлар</i>', ['хвойные деревья'])


def test_get_word():
    result = get_word("дерево", 215001844, 1)
    assert result == [{'translation': 'с\n<tr>агач</tr>\n<eml><w>хвойные деревья</w> ылыслы агачлар</eml>', 'order': '', 'word': 'дерево'}, {'translation': 'бот. <tr>хин агачы</tr>', 'order': '',
                                                                                                                                             'word': 'хинное дерево'}, {'translation': '<tr>кызыл агач</tr> (кыйммәтле агач)', 'order': '', 'word': 'красное дерево'}, {'translation': 'ж\n<tr>агач эшкәртү</tr>', 'order': '', 'word': 'деревообработка'}]


def test_get_word_tat():
    result = get_word("сэлэм", 215001844)
    assert result == [{'translation': '<ml0>1.\nсущ.\n<tr>соло́ма</tr>\n<eml><w>бодай саламы</w> пшени́чная соло́ма</eml>\n<eml><w>салам эскерте</w> скирда́ соло́мы</eml>\n<ml0>2.\nприл.\n<tr>соло́менный</tr>\n<eml><w>салам эшләпә</w> соло́менная шля́па</eml>\n<eml><w>салам түбә</w> соло́менная кры́ша</eml>\n- <word>салам аергыч</word>\n- <word>салам биргеч</word>\n\n<br/>- <word>салам бөртеге</word>\n\n<br/>- <word>салам ишкеч</word>\n\n<br/>- <word>салам кискеч</word>\n\n<br/>- <word>салам турагыч</word>\n\n<br/>- <word>салам турау машинасы</word>\n\n<br/>- <word>салам күтәргеч</word>\n\n<br/>- <word>салам өйгеч</word>\n<ml0>••\n<eml><w>салам торхан</w> воро́на в павли́ньих пе́рьях</eml>\n<eml><w>саламга ябышу</w> хвата́ться за соло́минку</eml>\n- <word>салам сыйрак</word>', 'order': 'сущ.|прил.', 'word': 'салам'}, {'translation': 'сущ.\n<ml0>1) <tr>приве́т</tr>; <tr>приве́тствие</tr>, <tr>покло́н</tr>\n<eml><w>сәлам, сәлам соңында каләм</w> (погов.) снача́ла приве́т, пото́м\xa0-\xa0разгово́р</eml>\n<ml0>2) в знач. межд. <tr>здра́вствуйте! приве́т! здоро́во</tr>!\n<ml0>•\n- <word>сәлам алу</word>\n- <word>сәлам кайтару</word>\n\n<br/>- <word>сәлам әйтү</word>\n\n<br/>- <word>сәлам бирдек!</word>\n\n<br/>- <word>сәлам бирү</word>', 'order': 'сущ.|межд.|ч.', 'word': 'сәлам'}, {'translation': 'прил.\n<ml0>1) <tr>рва́ный</tr>, <tr>дра́ный</tr>, <tr>истрёпанный</tr>, <tr>худо́й</tr> (одежда); <tr>излохма́ченный</tr> || <tr>рваньё</tr>, <tr>отре́пья</tr>; <tr>лохмо́тья</tr>, <tr>ру́бище</tr>; <tr>ло́хмы</tr>\n<eml><w>сәләмәләрен киеп</w> оде́вшись в лохмо́тья</eml>\n<ml0>2) <tr>оде́тый в рвань</tr> (лохмотья, отрепье)', 'order': 'прил.', 'word': 'сәләмә'}, {
        'translation': 'прил.\n<tr>здоро́вый</tr> (не больно́й); <tr>здра́вый</tr>\n<eml><w>сәламәт тәндә сәламәт җан</w> в здоро́вом те́ле\xa0-\xa0здоро́вый дух</eml>\n- <word>сәламәт бул</word>', 'order': 'прил.', 'word': 'сәламәт'}]


def test_get_by_id():
    result = get_by_id(1, 1090)
    assert result == [{'translation': 'ж\n<tr>аэрофототөшерү</tr>',
                       'order': '', 'word': 'аэрофотосъёмка'}]


def test_get_by_id_tat():
    result = get_by_id(0, 1488)
    assert result == [
        {'translation': 'бот. <tr>кувши́нка бе́лая</tr>', 'order': '', 'word': 'ак төнбоек'}]


def test_get_lang():
    result = get_lang(SimpleNamespace(
        **{'chat': SimpleNamespace(**{'id': 215001844, 'username': 'ilduseps'})}))
    assert result == 0 or result == 1
