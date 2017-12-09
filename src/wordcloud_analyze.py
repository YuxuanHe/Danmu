# 抓取弹幕后保存为text文档，然后词云分析,此部分是词云部分

import jieba
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import os
import PIL.Image as Image
import numpy as np

result_dir = '../result/danmu/'
print('--------弹幕收集结果---------')
for f in os.listdir(result_dir):
    print(f)
print('--------弹幕收集结果---------')

room_id = input('输入房间号: ')
with open(result_dir + room_id, 'r', encoding='utf-8') as f:
    text = f.read()
    f.close()
cut_text = " ".join(jieba.cut(text))

d = os.path.dirname(__file__)
color_mask = np.array(Image.open(os.path.join(d, 'img_round.jpg')))
my_wordcloud = WordCloud(
    background_color='white',  # 背景颜色
    font_path="FZLTKHK--GBK1-0.ttf",  # 使用特殊字体可以显示中文
    max_words=200,
    font_step=20,  # 步调太大，显示的词语就少了
    mask=color_mask,
    random_state=15,  # 设置有多少种随机生成状态，即有多少种配色方案
    min_font_size=15,
    max_font_size=202,
    collocations=False,
)
my_wordcloud.generate(cut_text)
image_colors = ImageColorGenerator(color_mask)
plt.show(my_wordcloud.recolor(color_func=image_colors))
plt.imshow(my_wordcloud)  # 以图片的形式显示词云
plt.axis('off')  # 关闭坐标轴
plt.show()  # 展示图片

my_wordcloud.to_file(os.path.join(d, '../result/wordcloud/' + room_id + '.jpg'))
