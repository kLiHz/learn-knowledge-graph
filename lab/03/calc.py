# https://github.com/tsagaanbar/learn-nlp/blob/main/src/lab/03/calc.py

from typing import List

#包括部分特殊字符，在进行分词比对时将特殊字符排除，以免对结果产生一定的影响

class Calc:

    def __init__(self) -> None:
        self.special_characters = set(list(
            "()[]+-*/<>|\\;:\"\'\,.?!@#$%^&~`\{\}（）【】《》，。？“”‘’；：——「」『』〔〕"
        ))

    def clean(self, l: List[str]):
        return [item for item in l if item not in self.special_characters]

    def calc_hits(cut_truth: List[str], cut_result: List[str]):
        # 传入分词得到的结果（列表），以及“正确分词”结果
        i = 0       # 指向 truth 中的 token
        j = 0       # 指向 result 中的 token
        l1 = 0      # i 所指向词串，对应在原句中的长度
        l2 = 0      # j 所指向词串，对应在原句中的长度
        hits = 0
        while i < len(cut_truth) and j < len(cut_result):
            if l1 < l2:
                l1 += len(cut_truth[i])
                i += 1
            elif l1 > l2:
                l2 += len(cut_result[j])
                j += 1
            else: 
                if cut_truth[i] == cut_result[j]:
                    hits += 1
                l1 += len(cut_truth[i])
                i += 1
                l2 += len(cut_result[j])
                j += 1
        
        return hits


    def calc_PRF(hits: int, truth_len: int, result_len: int):
        P = hits / result_len       # precision
        R = hits / truth_len        # recall
        F = (2 * P * R) / (P + R)   # F_1
        return P, R, F
