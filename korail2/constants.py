# -*- coding: utf-8 -*-
"""ikrail.item.Decoder 에서 발췌"""

__author__ = 'sng2c'


class EnumItem(str):
    """EnumItem : str상속, desc로 상세설명조회"""

    def __init__(self, code):
        super(EnumItem, self).__init__(code)
        self.desc = None


class Enum:
    def __init__(self, kv):
        assert isinstance(kv, dict)
        self.kv = {}
        for k, v in kv.items():
            self.kv[k] = EnumItem(k)
            self.kv[k].desc = v

    def __getitem__(self, key):
        """조회해서 있으면 EnumItem을 출력하고 없으면 key를 그대로 리턴"""
        return self.kv.get(str(key), key)


enum_h_jrny_tp_cd = Enum(
    {
        10: "열차상품",
        11: "편도",
        12: "왕편",
        13: "복편",
        14: "환승편도",
        15: "왕편환승",
        16: "복편환승",
        20: "병합",
        21: "병합선행",
        22: "병합후행",
        50: "열차외상품",
        51: "숙박",
        52: "렌터카",
        53: "선박",
        54: "이벤트",
        55: "항공",
    })

enum_h_psg_tp_cd = Enum(
    {
        1: "어른",
        2: "unknown",
        3: "어린이",
    })

enum_h_psrm_cl_cd = Enum(
    {
        1: "일반실",
        2: "특실",
        3: "침대실",
        4: "가족실",
        5: "별실",
        6: "비승용",
        7: "우등실",
    })

enum_h_rsv_tp_cd = Enum(
    {
        0: "unknown",
        1: "특단",
        2: "전세",
        3: "일반",
        4: "대납",
        5: "Open",
        6: "T-Less",
        7: "OVER",
        8: "대기",
        9: "단체",
        10: "열전",
        11: "군수송",
        12: "우편배송",
    })

enum_h_seat_att_cd_2 = Enum(
    {
        9: "순방",
        10: "역방",
    })

enum_h_seat_att_cd_3 = Enum(
    {
        11: "1인",
        12: "창측",
        13: "내측",
    })

enum_h_trn_clsf_cd = Enum(
    {
        "00": "KTX, KTX-산천",
        "01": "새마을호",
        "02": "무궁화호",
        "03": "통근열차",
        "04": "누리로",
        "05": "전체",
        "06": "공학직통",
        "KTX-07": "KTX-산천",
        "ITX-08": "ITX-새마을",
        "ITX-09": "ITX-청춘",
    })