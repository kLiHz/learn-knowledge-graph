from typing import List
# import fool
import jieba
from ltp import LTP
import jiagu
import thulac
from snownlp import SnowNLP
import hanlp

# Initialize Jieba
jieba.initialize()

# Initialize HIT LTP
ltp = LTP()

# Initialize Jiagu
jiagu.init()

# Initialize THULAC
thu1 = thulac.thulac(seg_only=True)

# Fix THULAC for Python 3.8+
# See https://github.com/thunlp/THULAC-Python/issues/100#issuecomment-903049502
import time
if not hasattr(time, 'clock'):  
    setattr(time,'clock',time.perf_counter)

# Initialize HanLP
tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)

class Seg:

    def jiagu(s: str) -> List[str]:
        return jiagu.seg(s)

    def jieba(s: str) -> List[str]:
        return list(jieba.cut(s))
    
    def hit_ltp(s: str) -> List[str]:
        return ltp.seg([s])[0][0]

    def thulac(s: str) -> List[str]:
        return [pair[0] for pair in thu1.cut(s)]

#    def fool_nltk(s: str) -> List[str]:
#        return fool.cut(s)

    def snownlp(s: str) -> List[str]:
        return SnowNLP(s).words

    def hanlp(s: str) -> List[str]:
        return tok(s)


tools = {
    'jieba':    Seg.jieba,  
    'hanlp':    Seg.hanlp,  
    'snownlp':  Seg.snownlp,
#    'foolnltk': Seg.fool_nltk,
    'jiagu':    Seg.jiagu,
    'hit_ltp':  Seg.hit_ltp,
    'thulac':   Seg.thulac,
}
