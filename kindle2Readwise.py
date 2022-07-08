import re
import os
import time
import shutil
import csv


def main():
    """
    :return:
    """
    # 从 Kindle 中直接复制
    # shutil.copyfile('/Volumes/Kindle/documents/My Clippings.txt', '/Volumes/File/KindleTXT2CSV/My Clippings.txt')
    try:
        with open('./My Clippings.txt', encoding='utf-8') as f:
            # 生成 KindleCSV 和 Clippings 文件夹
            path_csv = 'KindleCSV'
            mkdir_path(path_csv)
            path_clip = 'Clippings'
            mkdir_path(path_clip)
            time_str = time.strftime("%Y%m%d-%H%M%S")
            wrt_path = './' + path_csv + '/' + time_str + '.csv'
            # wrt_path = './test.csv'
            # 跳过之前导入的
            num_lines_old = get_lines_num('./Old-Clippings.txt')
            for _ in range(num_lines_old):
                f.readline()
            #
            analyse_line(f, wrt_path, time_str)
            f.close()
            shutil.move('./Old-Clippings.txt', './Clippings/' + time_str + '-Clippings.txt')
            os.rename('./My Clippings.txt', './Old-Clippings.txt')
    except IOError:
        print("Error: File does not appear to exist.")


def analyse_line(f, wrt_path, time_str):
    """
    :param f: file
    :param wrt_path: Written to the path
    :param time_str: Time format
    :return:
    """
    # 保存高亮数,笔记数,书签数,重复数
    meta = open('log.txt', 'a', encoding='utf-8')
    highlight_num = 0
    note_num = 0
    bookmark_num = 0
    repeat_num = 0
    null_highlight = 0
    # 初始配置，CSV 表头
    title = "Title"
    name = "Author"
    page = "Location"
    highlight = "Highlight"
    note = 'Note'
    note_type = 'highlight'
    # 读入第一条
    line = f.readline()
    # 循环处理
    while line:
        note_type = 'highlight'
        new_title = get_title(line)
        print('page', page)
        newname = get_name(line)
        new_page, note_type, line = get_page_and_type(f, note_type)
        new_highlight, line = get_highlight_or_note(f)
        # 跳过书签，不保存
        if note_type == 'bookmark':
            meta.write('Bookmark: ' + new_title + new_page + '\n')
            bookmark_num += 1
            continue
        # 有笔记的, 则不保存之前的, 在高亮后附加上笔记
        elif note_type == 'note':
            note_num += 1
            note = new_highlight
            new_highlight = highlight
        # 重复高亮, 则不保存之前的, 页数相同，前几个字符相同
        elif new_page == page and highlight[:4] == new_highlight[:4]:
            repeat_num += 1
            meta.write(page + ': ' + highlight + '\n')
            meta.write(new_page + ': ' + new_highlight + '\n')
        # 空白 highlight
        elif highlight == '':
            null_highlight += 1
            meta.write(page + ': nullHighlight' + '\n')
        else:
            highlight_num += 1
            data_str = [title, name, page, highlight, note]
            writer_csv(wrt_path, data_str)
            note = ''
        # 保存结果，和后一条对比，再进行判断
        title = new_title
        name = newname
        page = new_page
        highlight = new_highlight
    # 跳出循环，最后一条处理
    if note_type != 'bookmark':
        data_str = [title, name, page, highlight, note]
        writer_csv(wrt_path, data_str)
    # 保存处理结果
    log(meta, note_num, bookmark_num, repeat_num, null_highlight, highlight_num, time_str)


def mkdir_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def writer_csv(wrt_path, data_str):
    with open(wrt_path, 'a', encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_str)


def log(meta, note_num, bookmark_num, repeat_num, null_highlight, highlight_num, time_str):
    meta.write('\n' + '---------------------' + '\n')
    meta.write('noteNum: ' + str(note_num) + '\n')
    meta.write('bookmark: ' + str(bookmark_num) + '\n')
    meta.write('repeatNum: ' + str(repeat_num) + '\n')
    meta.write('nullHighlight: ' + str(null_highlight) + '\n')
    meta.write('highlightNum: ' + str(highlight_num) + '\n')
    meta.write('---------------------' + time_str + '\n\n\n')


def get_lines_num(file_name):
    # 没有则新建
    old_txt = open(file_name, 'a', encoding='utf-8')
    old_txt.close()
    try:
        with open(file_name, encoding='utf-8') as file:
            num_lines = sum(1 for _ in file)
    except IOError:
        print("Error: File does not appear to exist.")
        return 0
    return num_lines


def get_title(line):
    if line[:-1][-2:] != '))':
        t = line.rsplit('(', 1)[0]
    # 中英混名
    else:
        t = line.rsplit('(', 2)[0]
    return t


def get_name(line):
    if line[:-1][-2:] != '))':
        name = line.rsplit('(', 1)[1]
        name = name.rsplit(')', 1)[0]
    # 中英混名
    else:
        name = line.rsplit('(', 2)[1] + line.rsplit('(', 2)[2]
        name = name[:-3]
    return name


def get_page_and_type(f, note_type):
    # 空白行
    line = f.readline()
    a = line.split('#', 1)[1]
    print('a', a)
    if '-' in a:
        # - or #
        # page = re.split('#|-', line)[2]
        page = re.split('[#-]', line)[2]
        print('page', page)
    else:
        page, note_type = a.split('的', 1)
        note_type = note_type.split(' ', 1)[0]
    if note_type == '笔记':
        page = page[:-1]
        note_type = 'note'
    if note_type == '书签':
        page = page[:-1]
        note_type = 'bookmark'
    return page, note_type, line


def get_highlight_or_note(f):
    f.readline()
    line = f.readline()
    h = line[:-1]
    # highlight 也有多行问题
    # if note_type != 'note':
    #     line = f.readline()
    #     line = f.readline()
    # 笔记类型有多行的问题
    # else:
    line = f.readline()
    while line[:2] != '==':
        h = h + '\n' + line[:-1]
        line = f.readline()
    line = f.readline()
    return h, line


if __name__ == '__main__':
    main()
