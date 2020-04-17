import re
text = '<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">text\ntext\n336\nABI绝对广量指标\n分类：大盘指标\n\n指标说明\n1.ABI绝对广量主要用于扫瞄瞬间极端的多头或空头力道；\n2.ABI值数据只会在0～100之间波动，数据越高代表市场立即转折的概率越大；ABI值高于95以上时，市场行情将极容易产生短期转折点；\n3.越高的数据代表市场转向的机会越大；\n4.随著上市公司家数递增，ABI的极限数据须伴随修正；\n5.本指标可设参考线,对ABI作了归一化处理以减少误差。\n\n代码\n\n\x08\n\n\x0f\x03\x02\n\x03\x02// ADVANCE 上涨家数\n// DECLINE 下跌家数\nM:=10  // min 2 max 100\nABI:100*ABS(ADVANCE-DECLINE)/(ADVANCE+DECLINE);\nMAABI:EMA(ABI,M);\n\x03\n\nattribs\ntext\n210\n*0+9*1*2+1*2+3*0+4*3*2+2*2+4*4*2+1*0+s*5*0+1*0+1'
text = "".join(text.split("\n"))
print(text)
print(re.findall(r'text(.*)attribs', text))
