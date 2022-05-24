# kindle2Readwise

解决中文 `My Clippings.txt` 上传到 Readwise 有误的问题

使用 CSV 文件导入可以解决中文字符的问题


## 使用方法：

复制 `My Clippings.txt` 到目标路径
```
cd "含有 My Clippings.txt 的路径"
python3 kindle2Readwise.py
```

## 说明：

`Old-Clippings.txt` 用于和新的 `My Clippings.txt` 对比，只上传之前没有导入的数据

`Old-Clippings.txt` 将被移动到 Clippings 文件夹用于备份

`My Clippings.txt` 文件将被重命名为 `Old-Clippings.txt`

生成的 CSV 文件保存在 KindleCSV 文件夹中，再将 csv 文件导入到 Readwise

`log.txt` 文件用于记录导入数据的信息

其他：
---

例图

![image](https://user-images.githubusercontent.com/42215787/122644924-344a4600-d14a-11eb-849e-fd48531b7611.png)

注意执行 `python3 kindle2Readwise.py` 后 `My Clippings.txt` 将不会显示（已被改为 `Old-Clippings.txt`)，需要重新添加 `My Clippings.txt`

---

直接从 Kindle 中复制文件到目标文件夹
取消注释，更改对应路径
![image](https://user-images.githubusercontent.com/42215787/170085682-5e75c0ba-55b3-4a8f-ac32-2f9d0b9392cb.png)

