from utils import tools

from calc import Calc

s = '商品和服务'
truth = ['商品', '和', '服务']

for name in tools.keys():
    result = tools[name](s)
    print(f'{name}:\t{result}')
    
    hits = Calc.calc_hits(truth, result)
    
    P, R, F = Calc.calc_PRF(hits, len(truth), len(result))

    print("准确率 (P): {:.5f} %".format(100 * P))
    print("回归率 (R): {:.5f} %".format(100 * R))
    print("F 值为：{}".format(F))

