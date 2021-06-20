import re
import os
import time
import shutil
import csv
from pathlib import Path

def main():
    # 从 Kindle 中直接复制
    # shutil.copyfile('/Volumes/Kindle/documents/My Clippings.txt', '/Volumes/File/KindleTXT2CSV/My Clippings.txt')
    f = open('./My Clippings.txt')
    # 生成 KindleCSV 和 Clippings 文件夹
    pathCsv = 'KindleCSV'
    mkdirPath(pathCsv)
    pathClip = 'Clippings'
    mkdirPath(pathClip)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    wrtpath = './' + pathCsv + '/' + timestr + '.csv'
    # wrtpath = './test.csv'
    # 跳过之前导入的
    num_lines_old = getLinesNum('./Old-Clippings.txt')
    for i in range(num_lines_old):
        f.readline()
    #
    analyseLine(f, wrtpath, timestr)
    f.close()
    shutil.move('./Old-Clippings.txt', './Clippings/' + timestr + '-Clippings.txt')
    os.rename('./My Clippings.txt', './Old-Clippings.txt')

def analyseLine(f, wrtpath, timestr):
    #保存高亮数,笔记数,书签数,重复数
    meta = open('log.txt', 'a')
    highlightNum = 0
    noteNum = 0
    bookmarkNum = 0
    repeatNum = 0
    # 初始配置，CSV 表头
    title = "Title"
    name = "Author"
    page = "Location"
    highlight = "Highlight"
    note = 'Note'
    noteType = 'highlight'
    # 读入第一条
    line = f.readline()
    # 循环处理
    while line:
        noteType = 'highlight'
        newtitle = getTitle(line)
        newname = getName(line)
        newpage, noteType, line = getPageAndType(f, noteType)
        newhighlight, line = getHighlightOrNote(f, noteType)
        # 跳过书签，不保存
        if noteType == 'bookmark':
            meta.write('Bookmark: ' + newtitle + newpage + '\n')
            bookmarkNum += 1
            continue
        # 有笔记的, 则不保存之前的, 在高亮后附加上笔记
        elif noteType == 'note':
            noteNum += 1
            note = newhighlight
            newhighlight = highlight
        # 重复高亮, 则不保存之前的, 页数相同，前几个字符相同
        elif newpage == page and highlight[:4] == newhighlight[:4]:
            repeatNum += 1
            meta.write(page + ': ' + highlight + '\n')
            meta.write(newpage + ': ' + newhighlight + '\n')
        else:
            highlightNum += 1
            datastr = [title, name, page, highlight, note]
            writerCsv(wrtpath, datastr)
            note = ''
        # 保存结果，和后一条对比，再进行判断
        title = newtitle
        name = newname
        page = newpage
        highlight = newhighlight
    # 跳出循环，最后一条处理
    if noteType != 'bookmark':
        datastr = [title, name, page, highlight, note]
        writerCsv(wrtpath, datastr)
    # 保存处理结果
    log(meta, noteNum, bookmarkNum, repeatNum, highlightNum, timestr)

def mkdirPath(path):
    if not os.path.exists(path):
        os.mkdir(path)

def writerCsv(wrtpath, datastr):
    with open(wrtpath, 'a', encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(datastr)

def log(meta, noteNum, bookmarkNum, repeatNum, highlightNum, timestr):
    meta.write('\n' + '---------------------' + '\n')
    meta.write('noteNum: ' + str(noteNum) + '\n')
    meta.write('bookmark: ' + str(bookmarkNum) + '\n')
    meta.write('repeatNum: ' + str(repeatNum) + '\n')
    meta.write('highlightNum: ' + str(highlightNum) + '\n')
    meta.write('---------------------' + timestr + '\n\n\n')

def getLinesNum(fileName):
    # 没有则新建
    oldTxt = open(fileName, 'a')
    oldTxt.close()
    num_lines = sum(1 for line in open(fileName))
    # num_lines = sum(1 for line in oldTxt)
    return num_lines

def getTitle(line):
    if line[:-1][-2:] != '))':
        t = line.rsplit('(', 1)[0]
    # 中英混名
    else:
        t = line.rsplit('(', 2)[0]
    return t
    
def getName(line):
    if line[:-1][-2:] != '))':
        name = line.rsplit('(', 1)[1]
        name = name.rsplit(')', 1)[0]
    # 中英混名
    else:
        name = line.rsplit('(', 2)[1] + line.rsplit('(', 2)[2]
        name = name[:-3]
    return name

def getPageAndType(f, noteType):
    # 空白行
    line = f.readline()
    page = re.split('#|-', line)[2]
    if len(page) > 6:
        page, noteType = page.split(' ', 1)
        noteType = noteType.split(' ', 1)[0]
    if noteType == '的笔记':
        noteType = 'note'
    if noteType == '的书签':
        noteType = 'bookmark'
    return page, noteType, line

def getHighlightOrNote(f, noteType):
    line = f.readline()
    line = f.readline()
    h = line[:-1]
    if noteType != 'note':
        line = f.readline()
        line = f.readline()
    # 笔记类型有多行的问题
    else:
        line = f.readline()
        while line[:2] != '==':
            h = h + '\n' + line[:-1]
            line = f.readline()
        line = f.readline()
    return h, line


if __name__ == '__main__':
    main()
