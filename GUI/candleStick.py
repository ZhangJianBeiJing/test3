# coding=utf-8
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use('TkAgg')
import matplotlib.finance as mpf
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as nps
import GUI.CassandraStoreParser as cs
import datetime
from matplotlib.pylab import date2num
from pylab import np
from matplotlib.ticker import Locator
from matplotlib.patches import Ellipse
from matplotlib.widgets import Button as MplButton
from matplotlib.widgets import RadioButtons
import time
from tkinter import Button as TKButton
from tkinter import Label
from tkinter import Tk

# 计时工具
import timeit

'''
candleStickGraph的设计流程：
1 画出基本的candleStickGraph
2 添加事件：
        - 十字准线
        - OCHL提示框
        - volume提示框
3 tkinter设计：
        - button(2个，选择股票)
        - 滑动条/下拉框(选择时间周期)
        -
4 matplotlib的result内嵌到tkinter中


'''

'''
开盘价格和收盘价格之间有矩体组成，如果当天开盘加大于收盘价，则为阴线，
如果开盘价小于收盘价，则为阳线。
最高价和实体之间的线被称为上影线，最低价和实体间的线称为下影线。
当天上涨，用绿色表示，当天下跌，用红色表示。
'''
# 设置主题
# 常用主题：fivethirtyeight||ggplot||dark_background||bmh
# plt.style.use('bmh')
############
# 准备数据
############
# connectiong cassandra作为数据源
cluster = '54.191.204.210'
namespace = 'quote'
table = 'historical_data'
cassandraStoreParser = cs.CassandraStoreParser(cluster, namespace, table)
# quotes = cassandraStoreParser.GetDailyFromCassandra2('AAPL','2017-01-10','2017-01-16')
quotes2 = cassandraStoreParser.GetDailyFromCassandra2('AAPL', '2017-03-09', '2017-07-20')
# quotes=pd.read_csv('data.csv')
# 加载csv文件作为数据源
# 数据转换成candlestick_ohlc()方法可读取的格式
data_list = []
annocation_data_list = []
data_map = {}
volume_list = []
up_volume_list = []
down_volume_list = []
dates_list = []
open_list = []
close_list = []
high_list = []
low_list = []
bar_color_list = []
i_first = 0
up_bar_index = []
down_bar_index = []
for row in quotes2.iterrows():
    # 将时间转换为数字
    date_time = datetime.datetime.strptime(str(row[1][0]), '%Y-%m-%d')
    t = date2num(date_time)
    open = float(row[1][2])
    close = float(row[1][3])
    high = float(row[1][4])
    low = float(row[1][5])
    volume = int(row[1][6])
    print('date:%s' % t)
    print(open)
    print(close)
    print(high)
    print(low)
    print(volume)
    datas = (t, open, close, high, low)
    annocation_datas = (str(row[1][0]), open, close, high, low, volume)
    data_map[str(t)] = datas
    print(datas)
    for key in data_map:
        print('key:%s,value:%s' % (key, data_map[key]))

    # compute bar color list for ax2,if open<close,set 'green',else set 'red'
    if (close - open) > 0:
        bar_color_list.append('g')
        up_volume_list.append(volume)
        up_bar_index.append(i_first)
    else:
        bar_color_list.append('r')
        down_volume_list.append(volume)
        down_bar_index.append(i_first)

    i_first += 1
    data_list.append(datas)
    dates_list.append(str(row[1][0]))
    open_list.append(open)
    close_list.append(close)
    high_list.append(high)
    low_list.append(low)
    volume_list.append(volume)
    annocation_data_list.append(annocation_datas)
# Candlebar numbers
tickNum = len(dates_list)


############
# 绘制OCHL
############
# 自定义locator
class MyLocator(Locator):
    # 重写call方法
    def __call__(self, *args, **kwargs):
        return np.arange(tickNum - 1)


#############
# datacursor
#############
class DataCursor_annotation(object):
    text_template = 'x: %0.2f\ny: %0.2f'
    x, y = 0.0, 0.0
    xoffset, yoffset = 0, 0
    text_template = 'Date:%s'

    def __init__(self, ax):
        self.ax = ax
        self.annotation = self.ax.annotate(self.text_template,
                                           xy=(0, 0),
                                           xycoords='data',
                                           xytext=(30, -10),
                                           textcoords='offset points',
                                           size=8,
                                           ha='right', va='bottom',
                                           bbox=dict(boxstyle="round",
                                                     fc=(1.0, 0.7, 0.7),
                                                     alpha=0.8,
                                                     ec="none"),
                                           arrowprops=dict(arrowstyle="wedge,tail_width=1.",
                                                           fc=(1.0, 0.6, 0.5),
                                                           ec="none",
                                                           patchA=None,
                                                           patchB=el,
                                                           relpos=(0.2, 0.5)
                                                           )
                                           )
        self.annotation.set_visible(False)

    def __call__(self, event):
        self.event = event
        # xdata, ydata = event.artist.get_data()
        # self.x, self.y = xdata[event.ind], ydata[event.ind]
        if event.xdata is not None and event.ydata is not None:
            self.x, self.y = event.xdata, event.ydata
            print(self.x)
            print(self.y)
            x = round(self.x)
            x = int(x)
            date_label = dates_list[x]
            if self.x is not None:
                self.annotation.xy = self.x, self.ax.get_ylim()[0]
                self.annotation.set_text(self.text_template % (date_label))
                self.annotation.set_visible(True)
                event.canvas.draw()
        else:
            return


################################
# date text display using cursor
################################
class DataCursor_text(object):
    # 属性
    x, y = 0, 0

    # 构造方法
    def __init__(self, ax):
        self.ax = ax
        self.date_text = self.ax.text(0, 0, ' ')

    # callback
    def __call__(self, event):
        self.event = event
        if event.xdata is not None and event.ydata is not None:
            self.x = event.xdata
            self.y = event.ydata
            print(self.x)
            print(self.y)
            x = round(self.x)
            x = int(x)
            if x > 0 and self.ax.xaxis.get_ticklocs().__contains__(x):
                print('x:%s' % x)
                print(len(dates_list))
                date_label = dates_list[x]
                if self.x is not None:
                    self.date_text.set_x(self.x)
                    self.date_text.set_y(self.ax.get_ylim()[0])
                    self.date_text.set_text(date_label)
                else:
                    print(x)
            else:
                print(x)
        else:
            print('~~~~')


fig = plt.figure()
# candle Graph
# 设置figure总标题
fig.suptitle('AAPL')
ax1 = fig.add_axes([0.15, 0.3, 0.75, 0.6])
# volume Graph
ax2 = fig.add_axes([0.15, 0.1, 0.75, 0.1])

# 多图微调
fig.subplots_adjust(bottom=0.03, hspace=0.25)

# 获取x轴对象
xaxis = ax1.xaxis
# 获取y轴对象
yaxis = ax1.yaxis
# 设置x轴标签
OHCL_text = ax1.text(0, 0, ' ')
DATE_text = ax2.text(0, 0, ' ')
PRICE_text = ax1.text(0, 0, ' ')
VOLUME_text = ax2.text(0, 0, ' ')
# 左侧y轴
ax1.set_ylabel('Price($)')
ax1.set_xlim(left=0, right=tickNum - 1)
# 动态设置左侧y轴range，充分利用视图空间
ymin = min(low_list)
ymax = max(high_list)
ax1.set_ylim(bottom=ymin - 1.0, top=ymax + 1.0)
# 右侧y轴
# ax1_=ax1.twinx()
# ax1_.set_ylim(bottom=0,top=10)
# ax1_.set_ylabel('ZhangJian')

# mutipleLocator
mutipleLocator = ticker.MultipleLocator()
# ax1 set major locator using MaxNLocator
ax1.xaxis.set_major_locator(ticker.MaxNLocator(tickNum - 1))
# ax1.xaxis.set_major_locator(MyLocator())
ax1.xaxis_date()
ax1.autoscale_view()


def mydate(x, pos):
    try:
        return dates_list[int(x)]
    except IndexError:
        return ''


ax1.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))

# 设置x轴刻度标识
# ax1.set_xticklabels(dates_list)
# 设置x轴刻度标识属性
candle_x_ticklabels = ax1.get_xticklabels()
for i in candle_x_ticklabels:
    print(i)
    i.set_rotation(45)
    i.set_fontsize(5)
    i.set_color('black')
# 绘画candleGraph

# start time
# candlestick_graph_draw_start_time=str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
candlestick_graph_draw_start_time = time.time()
# candlestick()方法返回的是line2D列表和Rectangle列表,根据debug知道，
# candlestick_container的结构为：tuple(list[line2D,line2D,...],list[rectangle,rectangle,...])
# candlestick_container=mpf.candlestick_ochl(ax1, data_list,width=0.3,colorup='r', colordown='g',alpha=0.8)
# 此处，candlestick2_ochl()方法内部调用的是candlestick2_ohlc()方法，而前者在接收返回值时会报“NoneType”，即拿不到返回值，所以
# 此处用后者，后者可以成功接收返回值，方便后续给candle line加marker
candlestick_container = mpf.candlestick2_ohlc(ax1, open_list, high_list, low_list, close_list, width=0.3, alpha=0.8,
                                              colorup='g',
                                              colordown='r')
candlestick_graph_draw_end_time = time.time()
print(candlestick_container)
print('candlestickgraph draw using:%s s' % (candlestick_graph_draw_end_time - candlestick_graph_draw_start_time))
# candlestick_container=mpf.plot_day_summary2_ochl(ax1,open_list,close_list,high_list,low_list)
# candlestick2_ochl return tuple(lineCollection,barCollection)
# line2D加marker很好加，既可以：lines.set_marker('v'),也可以：plt.setp(lines,marker='v')，但是linecollection不好加
# 所以此处，自己手动画三角形来代替marker;
# argecho.py

##################################
# candlestick set triangle marker
##################################
xlocationlist = ax1.xaxis.get_ticklocs()
# 计算high和low的差向量的均值
high_array = np.array(high_list)
low_array = np.array(low_list)
# 差向量
diff_array = high_array - low_array
# 求均值
d = diff_array.mean()
print('平均值d:%f' % d)
#########
# FlagArray is used to confirm the location of triangle what we want to draw on the candlestick
#########
# SWING SPAN
SWS = 6
# 数据结构：swing_point_dict={'SWP':dict={index:number},'':dict={index:number}}
swing_point_dict = {}
swl = {}
swh = {}
# swl swh初始化
for i in range(len(dates_list) - 1):
    swh[i] = 0
    swl[i] = 0
print(swh)
print(swl)
swp = {}
sw = {}
pswl = ''
pswh = ''
# flag_array 初始化 length:len(dates_list) items:0
for i in range(len(dates_list)):
    print('')
pswh_index = 0
pswl_index = 0
# last_swh,last_swl初始化
last_swh = 0
last_swl = 0
###############
# low swing point
###############
tmp_index = pswl_index + SWS
print('pswl_index初始值：%s' % pswl_index)
while tmp_index <= len(dates_list) - 1:
    low_tmp_list = low_list[pswl_index:pswl_index + SWS + 1]
    print('low_tmp_list%s' % low_tmp_list)
    low_min = min(low_tmp_list)
    print('low_min:%s' % low_min)
    low_min_index = low_tmp_list.index(low_min)
    print('low_min_index:%s' % low_min_index)
    if low_min_index == 0:
        # swl 装填
        swl[pswl_index] = 1
        while tmp_index <= len(dates_list) - 1 and low_list[tmp_index] > low_list[tmp_index - 1]:
            print('tmp_index内层while循环%s' % tmp_index)
            # tmp_index从6开始
            tmp_index = tmp_index + 1
            print('tmp_index内层while循环+1%s' % tmp_index)
        print('tmp_index内层while循环终值:%s' % tmp_index)
        if tmp_index <= len(dates_list) - 1:
            pswl_index = tmp_index
            tmp_index = pswl_index + SWS
            print('pswl_index循环内的if值%s:' % pswl_index)
    else:
        pswl_index = pswl_index + low_min_index
        tmp_index = pswl_index + SWS
    print('pswl_index循环值：%s' % pswl_index)
    print('tmp_index while循环入口值%s' % tmp_index)
if pswl_index < len(dates_list) - 1:
    low_tmp_list_2 = dates_list[pswl_index:]
    low_min_2 = min(low_tmp_list_2)
    print('low_min_2%s' % low_min_2)
    # index()方法会抛异常，需要try-catch
    low_min_index_2 = low_tmp_list_2.index(low_min_2)
    print('low_min_index_2%s' % low_min_index_2)
    pswl_index = pswl_index + low_min_index_2
    print('pswl_index%s' % pswl_index)
# the last swing point low CANDIDATE（候选人）
print('最终pswl_index:%s' % pswl_index)
pswl = dates_list[pswl_index]
# 装填
sw['SWL'] = swl
swing_point_dict['PSWL'] = pswl
# 遍历swl
print('遍历swl')
swl_key = swl.keys()
for i in swl_key:
    print('value:%s' % swl[i])
print('pswl值:%s' % pswl)
# 此时,尚不能装填sw
# swing_point_dict['SWP']=sw
##############
# high swing point
##############
tmp_index = pswh_index + SWS
while tmp_index <= len(dates_list) - 1:
    high_tmp_list = high_list[pswh_index:pswh_index + SWS + 1]
    high_max = max(high_tmp_list)
    high_max_index = high_tmp_list.index(high_max)
    if high_max_index == 0:
        # swh 装填
        swh[pswh_index] = 1
        while tmp_index == len(dates_list) and high_list[tmp_index] < high_list[tmp_index - 1]:
            tmp_index = tmp_index + 1
        if tmp_index <= len(dates_list) - 1:
            pswh_index = tmp_index
            tmp_index = pswh_index + SWS
    else:
        pswh_index = pswh_index + high_max_index
        tmp_index = pswh_index + SWS
if pswh_index < len(dates_list) - 1:
    high_tmp_list_2 = high_list[pswh_index:pswh_index + SWS + 1]
    high_max_2 = max(high_tmp_list_2)

    high_max_index_2 = high_tmp_list_2.index(high_max_2)
    pswh_index = pswh_index + high_max_index_2
# the last swing point high Candidate; potential swing point high
pswh = dates_list[pswh_index]
sw['SWH'] = swh
print(swh)
# 装填
swing_point_dict['PSWH'] = pswh
swing_point_dict['SWP'] = sw
# 入参个数==2


#############
# swh,swl绘制
#############
SWH = swing_point_dict.get('SWP').get('SWH')
SWL = swing_point_dict.get('SWP').get('SWL')
for index in range(len(dates_list) - 1):
    # console error:    if SWH[i]==1: TypeError: list indices must be integers or slices, not Text
    # range()生成的是数组元素是text type,要转换成integer
    index = int(index)
    # 此处SWH,SWL的元素是不一定是互补关系，相同位置，一方为1，则另一方可能为0，可能为1，所以用if-else不合适，要用多if；
    if SWH[index] == 1:
        ax1.plot([index, index], [high_list[index] + d / 3, high_list[index] + d / 3],
                 alpha=0.8, marker='v', markerEdgeColor='b', markerFaceColor='b')
        last_swh = index
    if SWL[index] == 1:
        ax1.plot([index, index], [low_list[index] - d / 3, low_list[index] - d / 3],
                 alpha=0.8, marker='^', markerEdgeColor='k', markerFaceColor='k')
        last_swl = index
# pswh,pswl值在dates_list的下标
pswh_index_ = dates_list.index(swing_point_dict.get('PSWH'))
pswl_index_ = dates_list.index(swing_point_dict.get('PSWL'))
print('pswh_index_:%s' % pswh_index_)
print('pswl_index_:%s' % pswl_index_)

print('pswh:%s' % pswh)
print('pswl:%s' % pswl)
print('last_swh:%s' % last_swh)
print('lst_swl:%s' % last_swl)
##############
# pswh,pswl绘制
##############
if pswh_index_ != last_swh:
    ax1.plot([pswh_index_, pswh_index_], [high_list[pswh_index_] + d / 3, high_list[pswh_index_] + d / 3],
             color='blue', alpha=0.8, marker='v', markerEdgeColor='b', markerFaceColor='w')
if pswl_index_ != last_swl:
    ax1.plot([pswl_index_, pswl_index_], [low_list[pswl_index_] - d / 3, low_list[pswl_index_] - d / 3],
             color='blue', alpha=0.8, marker='v', markerEdgeColor='k', markerFaceColor='w')
# 复写bar_color_list
for key in swh.keys():
    if swh[key] == 1:
        bar_color_list[key] = 'b'
for key in swl.keys():
    if swl[key] == 1:
        bar_color_list[key] = 'k'

# for i in xlocationlist:
#     i = int(i)
#     ###########
#     # 上行
#     ###########
#     # 三角形的三顶点坐标
#     A_UP = [i, high_list[i] + 0.4]
#     B_UP = [i - 0.3, high_list[i] + 0.7]
#     C_UP = [i + 0.3, high_list[i] + 0.7]
#     triangle_up = plt.Polygon([A_UP, B_UP, C_UP], color='blue', alpha=1)
#     ###########
#     # 下行
#     ###########
#     A_DOWN = [i, low_list[i] - 0.4]
#     B_DOWN = [i - 0.3, low_list[i] - 0.7]
#     C_DOWN = [i + 0.3, low_list[i] - 0.7]
#     triangle_down = plt.Polygon([A_DOWN, B_DOWN, C_DOWN], color='black', alpha=1)
#     # 此句是必须的，因为必须将polygon对象纳入到axes的patchlist property中，才会有效
#     ax1.add_patch(triangle_up)
#     ax1.add_patch(triangle_down)

# 设置网格属性
# ax1.grid(linestyle='--', color='k', alpha=0.2, linewidth=0.8)
# 此处x轴的grid不是水平的网格，而是垂直的网格，因为其x坐标都在x轴上，隶属于xaxis；
ax1.xaxis.grid(linestyle=':', color='black', alpha=0.2, linewidth=0.8)

ax1.yaxis.grid(b=False)
# # 开启网格显示
# ax1.grid(True)
# 绘制日期间隔
# 定义最小间隔标准,单位：秒
DAY_INTERVAL = 60 * 60 * 24
MINUTE_INTERVAL = 60 * 60
WEEKLY_INTERVAL = DAY_INTERVAL * 7
MOUTH_INTERVAL = DAY_INTERVAL * 30
YEAR_INTERVAL = DAY_INTERVAL * 365
# 存储绘制间隔线位置的容器
interval_index_list = []
# 找出间隔点
# 索引遍历
'''
str = '0123456789'
str='2017-08-25 00:00:00'
print str[0:3]    #截取第一位到第三位的字符
print str[:]      #截取字符串的全部字符
print str[6:]     #截取第七个字符到结尾
print str[:-3]    #截取从头开始到倒数第三个字符之前
print str[2]      #截取第三个字符
print str[-1]     #截取倒数第一个字符
print str[::-1]   #创造一个与原字符串顺序相反的字符串
print str[-3:-1]  #截取倒数第三位与倒数第一位之前的字符
print str[-3:]    #截取倒数第三位到结尾
print str[:-5:-3] #逆向截取，倒数第一位与倒数第五位之间的字符，步长为3
'''
for index in range(len(dates_list)):
    print(dates_list[index])
    # 非首个元素
    if index > 0:
        # current point
        current = time.strptime(dates_list[index], '%Y-%m-%d')
        # 单位是秒
        current_seconds = int(time.mktime(current))
        print('loop_current_seconds:%d' % current_seconds)
        # pre point
        pre = time.strptime(dates_list[index - 1], '%Y-%m-%d')
        # 单位是秒
        pre_seconds = int(time.mktime(pre))
        print('loop_pre_seconds:%d' % pre_seconds)
        # 有间隔
        if (current_seconds - pre_seconds) > DAY_INTERVAL:
            print('############出现间隔！############，index:%s' % index)
            print('min:%f' % ax1.get_ylim()[0])
            print('max:%f' % ax1.get_ylim()[1])
            # 在画间隔线时，plt.vlines()，还是ax1.axvline()均不管用，plt.plot()也不管用，只能用ax1.plot()了；
            # ax1.axvline((index + index - 1) / 2.0, ax1.get_ylim()[0], ax1.get_ylim()[1])
            ax1.plot([(index + index - 1) / 2.0, (index + index - 1) / 2.0], [ax1.get_ylim()[0], ax1.get_ylim()[1]],
                     color='black', linestyle=':', alpha=0.2, linewidth=0.8)
            # 间隔点标识
            ax1.plot([(index + index - 1) / 2.0, (index + index - 1) / 2.0], [ax1.get_ylim()[0], ax1.get_ylim()[0]],
                     color='green', alpha=1, marker='.')

        else:
            # do nothing
            print('')
    else:
        # do nothing
        print('')
# #check time unit
# print(1497283200-1497196800)
# print(60*60*24)

# line_zj=ax2.axvline()
# line_zj.set_data([20,20], [ax2.get_ylim()[0], ax2.get_ylim()[1]])
# line_zj.set_linewidth(4)
# line_zj.set_linestyle('--')
# line_zj.set_color('red')
# candlestick_ochl return tuple(line_list,rectangle_list)
# for line in candlestick_container[0]:
#     print('low:%f,high:%f'%(line.get_ydata()[0],line.get_ydata()[1]))
#     plt.setp(line,marker='v',visible=True)
#     print('')
# for rectangle in candlestick_container[1]:
#     print('rec:x,y,width,height'+str((rectangle.get_bbox().bounds)))
#     print('open:%f,close:%f,'%(rectangle.get_y(),rectangle.get_y()+rectangle.get_height()))
#     plt.setp(rectangle,visible=True)

# candlestick2_ochl
# linecollection=candlestick_container[0]
# barcollection=candlestick_container[1]




# 打印ax1的x轴的locator
print(ax1.xaxis.get_ticklocs())
fig.autofmt_xdate()

vline_1 = ax2.axvline()
hline_1 = ax2.axhline()
vline_2 = ax1.axvline()
hline_2 = ax1.axhline()

# ax1_.plot()

el = Ellipse((2, 155), 0.5, 0.5)


# #annocation
# _annotation_ = ax2.annotate('',
#                           xy=(0,0),
#                           xycoords='data',
#                           xytext=(0, 0),
#                           textcoords='offset points',
#                           size=8,
#                           va="bottom",
#                           bbox=dict(boxstyle="round",
#                                     fc=(1.0, 0.7, 0.7),
#                                     ec="none"),
#                           arrowprops=dict(arrowstyle="wedge,tail_width=1.",
#                                           fc=(1.0, 0.7, 0.7),
#                                           ec="none",
#                                           patchA=None,
#                                           patchB=el,
#                                           relpos=(0.2, 0.5))
#                                   )
# _annotation_.set_visible(False)


# click event

# 回调函数
def on_mouse_move(event):
    time_1 = time.time()
    try:
        x_data = event.xdata
        y_data = event.ydata
        x_pixel = event.x
        y_pixel = event.y
        if event.xdata == None and event.ydata == None:
            return

        print('DATA_X_Y:x:%s,y:%s' % (x_data, y_data))
        print('PIXEL_X_Y:x:%s,y:%s' % (x_pixel, y_pixel))
        x = round(x_data)
        x = int(x)
        print(list(ax1.xaxis.get_ticklocs()).__contains__(x))
        if list(ax1.xaxis.get_ticklocs()).__contains__(x):

            # line2D
            # 离散处理 xvline是必须离散化处理的，yhline可选；
            x_vline = int(round(x_data))
            # y_hline=int(round(y_data))
            y_hline = y_data
            # set new xy for vline and hline
            vline_1.set_data([x_vline, x_vline], [0, ax2.get_ylim()[1]])
            vline_1.set_linewidth(1)
            vline_1.set_linestyle('--')
            vline_1.set_color('black')

            hline_1.set_data([0, ax2.get_xlim()[1]], [y_hline, y_hline])
            hline_1.set_linewidth(1)
            hline_1.set_linestyle('--')
            hline_1.set_color('black')

            vline_2.set_data([x_vline, x_vline], [0, ax1.get_ylim()[1]])
            vline_2.set_linewidth(1)
            vline_2.set_linestyle('--')
            vline_2.set_color('black')

            hline_2.set_data([0, ax1.get_xlim()[1]], [y_hline, y_hline])
            hline_2.set_linewidth(1)
            hline_2.set_linestyle('--')
            hline_2.set_color('black')

            # time_2=time.time()
            # print('########################################>>v||h line using time:%s'%(time_2-time_1))
            OCHL = annocation_data_list[x]
            annocation_text = 'Open:%0.2f Close:%0.2f High:%0.2f Low:%0.2f' % (OCHL[1], OCHL[2], OCHL[3], OCHL[4])
            annocation_date = OCHL[0]
            annocation_price = 'Price:%.2f' % float(y_data)
            annocation_volume = OCHL[5]
            print(annocation_text)
            # print('vline.get_cursor_data%s'%(vline.get_cursor_data))
            # Vline重新定位
            # vline.set_offset_position('data')
            # ax1.set_title(annocation_text)

            OHCL_text.set_text(annocation_text)
            OHCL_text.set_x(0)
            OHCL_text.set_y(ax1.get_ylim()[1])
            # annotation = ax2.annotate('',
            #                           xy=(x_data, 0),
            #                           xycoords='data',
            #                           xytext=(x_data, 0),
            #                           textcoords='offset points',
            #                           size=8,
            #                           va="bottom",
            #                           bbox=dict(boxstyle="round",
            #                                     fc=(1.0, 0.7, 0.7),
            #                                     ec="none"),
            #                           arrowprops=dict(arrowstyle="wedge,tail_width=1.",
            #                                           fc=(1.0, 0.7, 0.7),
            #                                           ec="none",
            #                                           patchA=None,
            #                                           patchB=el,
            #                                           relpos=(0.2, 0.5))
            #                           )
            # 更新日期文本框
            DATE_text.set_x(x_data)
            DATE_text.set_y(ax2.get_ylim()[1])
            DATE_text.set_text(annocation_date)
            # 更新价格文本框
            PRICE_text.set_x(ax1.get_xlim()[1])
            PRICE_text.set_y(y_data)
            PRICE_text.set_text(annocation_price)
            # 更新成交量文本框
            VOLUME_text.set_x(ax2.get_xlim()[1])
            VOLUME_text.set_y(y_data)
            VOLUME_text.set_text('Volume:%s' % annocation_volume)

            # linecollection
            # vline_1.set_offset_position('data')
            # vline_2.set_offset_position('data')
            # hline_1.set_offset_position('data')
            # hline_2.set_offset_position('data')
            #
            # vline_1.set_offsets((x_data,x_data,0,ax1.get_ylim()[1]))
            # hline_1.set_offsets((0,ax1.get_xlim()[1],y_data,y_data))
            # vline_2.set_offsets((x_data,x_data,0,ax2.get_ylim()[1]))
            # hline_2.set_offsets((0,ax2.get_xlim()[1],y_data,y_data))
            # 此句很重要，否则不会动态加载
            # event.canvas.draw()
            # 此句虽然也能实现draw,但鼠标动的多了会造成stack over flow
            # plt.show()
            plt.draw()
        else:
            print('非法区域！')
    except Exception as e:
        print(e)


'''
像素坐标转换为数据坐标，并且显示左右两侧y轴的值
'''


def make_format(current, other):
    # current and other are axes
    def format_coord(x, y):
        # x, y are data coordinates
        # convert to display coords
        display_coord = current.transData.transform((x, y))
        inv = other.transData.inverted()
        # convert back to data coords with respect to ax
        ax_coord = inv.transform(display_coord)
        coords = [ax_coord, (x, y)]
        return ('Left: {:<40}    Right: {:<}'
                .format(*['({:.3f}, {:.3f})'.format(x, y) for x, y in coords]))

    return format_coord


# 绘画volumeGraph
# bar数量
barNum = len(dates_list)
# range()和numpy.arange()的区别，前者带右边界，后者不带右边界
list_ = nps.arange(barNum)
# 绘制bar
# bar方法返回的是bar Container实例
# bar宽度：x/min(diff(swh)) diff():求差分，降1维
# 求swh,swl中有效标识1的索引
swh_1_index = []
swl_1_index = []
swh_volume_list = []
swl_volume_list = []
for key in SWH.keys():
    if SWH[key] == 1:
        key = int(key)
        swh_1_index.append(key)
        swh_volume_list.append(volume_list[key])
for key in SWL.keys():
    if SWL[key] == 1:
        key = int(key)
        swl_1_index.append(key)
        swl_volume_list.append(volume_list[key])
print('swh_1_index:%s' % swh_1_index)
print('swl_1_index:%s' % swl_1_index)
# 求差分
diff_swh = []
diff_swl = []
print(range(len(swh_1_index)))
for i in range(len(swh_1_index)):
    if i > 0:
        tmp = swh_1_index[i] - swh_1_index[i - 1]
        diff_swh.append(tmp)
    else:
        print('')

for i in range(len(swl_1_index)):
    if i > 0:
        tmp = swl_1_index[i] - swl_1_index[i - 1]
        diff_swl.append(tmp)
    else:
        print('')

print('diff_swh:%s' % diff_swh)
print('diff_swl:%s' % diff_swl)
# 画volume bar的第一种方式：统一绘制，使用同一颜色列表
# bar_container = ax2.bar(list_, volume_list, 0.6, None, tick_label=dates_list, color=bar_color_list)
# 画volume bar的第二种方式：分别绘制，使用不同的属性设置
ax2.bar(up_bar_index, up_volume_list, 0.6, color='g')
ax2.bar(down_bar_index, down_volume_list, 0.6, color='r')
ax2.bar(swh_1_index, swh_volume_list, 0.6, color='b')
ax2.bar(swl_1_index, swl_volume_list, 0.6, color='k')
# ax2.bar(swh_1_index,swh_volume_list,0.6/min(diff_swh),color='b')
# ax2.bar(swl_1_index,swl_volume_list,0.6/min(diff_swl),color='k')
volume_x_ticklabels = ax2.get_xticklabels()
for i in volume_x_ticklabels:
    i.set_rotation(45)
    i.set_color('black')
    i.set_fontsize(5)
ax2.set_xlabel('Date')
ax2.set_ylabel('Volume')
ax2.set_xlim(left=0, right=tickNum - 1)
print(ax2.xaxis.get_ticklocs())
ax2.xaxis.set_major_locator(ticker.MaxNLocator(tickNum - 1))
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
ax2.plot()
# cursor1=Cursor(ax1, horizOn=True, vertOn=True, useblit=True,linestyle='--',color='black',linewidth=1)
# cursor2=Cursor(ax2, horizOn=False, vertOn=True, useblit=True,linestyle='--',color='black',linewidth=1)
# cursor3=Cursor(ax1_,horizOn=False, vertOn=True, useblit=True,linestyle='--',color='black',linewidth=1)
# multi = MultiCursor(fig.canvas, (ax1, ax2), color='black', lw=1,horizOn=False, vertOn=True,linestyle='--')
fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
# fig.canvas.mpl_connect('motion_notify_event', DataCursor_annotation(ax1))
# fig.canvas.mpl_connect('motion_notify_event', DataCursor_annotation(ax2))
# fig.canvas.mpl_connect('motion_notify_event',DataCursor_text(ax1))
# fig.canvas.mpl_connect('motion_notify_event',DataCursor_text(ax2))

#############
# toolbar draw
#############
# toolbar Graph
ax3 = fig.add_axes([0, 0, 0.1, 1.0])

freqs = np.arange(2, 20, 3)


class Index(object):
    def rsi(self, event):
        ax1.clear()

        event.canvas.draw()

    def prev(self, event):
        ##
        fig = plt.figure(3)
        ax = fig.add_subplot(111)
        ax.plot([3, 2, 1], [1, 2, 3])
        event.canvas.draw()


callback = Index()
axprev = plt.axes([0, 0.93, 0.05, 0.04])
axnext = plt.axes([0.05, 0.93, 0.05, 0.04])
# matplotlib.widget button
bnext = MplButton(axnext, 'RSI')
bnext.on_clicked(callback.rsi)
bprev = MplButton(axprev, 'Previous')
bprev.on_clicked(callback.prev)

# matplotlib.widget radio button
axcolor = 'white'
rax = plt.axes([0, 0.7, 0.1, 0.1], facecolor=axcolor)
radio = RadioButtons(rax, ('Daily', 'XXX', 'YYY'))


# button的回调函数
def hzfunc(label):
    hzdict = {'Daily': '0', 'XXX': '1', 'YYY': '2'}
    c_value = hzdict[label]
    print('MarkerValue:%s' % c_value)
    plt.draw()


# 给button注册点击事件的回调函数
radio.on_clicked(hzfunc)

# 数据相关的算法应该与plot分离开
# 计算RSI
'''
RS=N日内收盘价上涨数之和的平均值/N日内收盘价下跌数之和的平均值
RSI=100-(100/(1+RS))
短期RSI,N一般取7
长期RSI,N一般取14
'''
total_close_up = 0.0
total_close_down = 0.0
period = 14
tmp_list = []
rsi_dict = {}
rsi_list = []
# 最近十四天，日期往前推13，包含今天
for index in nps.arange(len(annocation_data_list)):
    if index >= 13:
        # 清零
        tmp_list.clear()
        # 重置
        total_close_up = 0
        total_close_down = 0
        # 截取最近14天的数据，并装载到列表中
        for i in nps.arange(14):
            tmp_list.append(annocation_data_list[index - i])
        # 计算这14天的RS值
        for t_index in nps.arange(len(tmp_list)):
            if t_index > 0:
                close = tmp_list[t_index][2]
                close_pre = tmp_list[t_index - 1][2]
                # 收盘价的涨幅或跌幅
                close_diff = close - close_pre
                if close_diff >= 0:
                    total_close_up += close_diff
                else:
                    # abs():取绝对值
                    total_close_down += abs(close_diff)
        rs = (total_close_up / 14 * 1.0) / (total_close_down / 14 * 1.0)
        # 计算rsi
        rsi = 100 - 100 / (1 + rs)
        # 装填rsi值 {date1:rs1,date2:rs2,...}
        rsi_dict[annocation_data_list[index][0]] = rsi
        rsi_list.append(rsi)
    else:
        print('')

print('rsi_list length:%s' % len(rsi_list))
print(rsi_list)
for i, element in enumerate(rsi_list):
    print('index:%s,rsi_value:%s' % (i, element))
print(len(dates_list))
print(nps.arange(len(rsi_list)))
print(rsi_list)
# 绘制RSI曲线
# 创建和ax1共享x轴的axes对象
# ax4=ax1.twinx()
# for i in nps.arange(13):
#     rsi_list.append(0)
# ax4.plot(nps.arange(29),rsi_list,linewidth=1,linestyle='--',color='black')
fig2 = plt.figure(2)
ax = fig2.add_axes([0.1, 0.1, 0.8, 0.8])
ax.set_title('AAPL_RSI')
ax.set_ylim(bottom=0, top=100)
ax.set_xlim(left=0, right=len(rsi_list))
ax.set_ylabel('%', verticalalignment='center', horizontalalignment='left')
ax.plot(nps.arange(len(rsi_list)), rsi_list, linewidth=0.6, linestyle='--', color='g')


def daily_candle():
    print('')


matplotlib.use('TKAgg')
# 创建主窗口
root = Tk()
# 设置主窗口大小
root.geometry('100x400')

# 指定渲染器
canvas = FigureCanvasTkAgg(fig, master=root)
label = Label(root, text="SHM Simulation").grid(column=0, row=0)
button = TKButton(root, text='Daily', command='daily_candle').grid(column=0, row=1)
plt.show()
plt.close()
