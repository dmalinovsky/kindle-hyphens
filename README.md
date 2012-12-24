fb2-hyphens
===========

Soft hyphens for FB2 ebook format, TeX hyphenation algorithm is used.

Processed e-books can be converted to Kindle [KF8](http://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000729511)
format using [calibre](http://calibre-ebook.com/).  You can use `fb2mobi.sh.example` script to do it, after
renaming it to `fb2mobi.sh` and adapting to your needs.  To transfer ready e-books into Kindle you can use 
`send2kindle.sh.example` template.

The hyphens will work in Kindle Keyboard and newer readers 
[with the lastest software updates](http://www.amazon.com/gp/help/customer/display.html/ref=hp_200127470_software?nodeId=200529680).
Search and dictionary lookup will look correctly.

Russian, Ukranian, English and German hyphenation patters are supported.

You can also check out `append_series.py` script, which appends FB2 series
number and title to Kindle book title.

Инструкция по-русски
====================

Расстановка [«мягких» переносов](http://ru.wikipedia.org/wiki/%D0%9F%D0%B5%D1%80%D0%B5%D0%BD%D0%BE%D1%81_%28%D1%82%D0%B8%D0%BF%D0%BE%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D0%BA%D0%B0%29#.D0.9C.D1.8F.D0.B3.D0.BA.D0.B8.D0.B9_.D0.BF.D0.B5.D1.80.D0.B5.D0.BD.D0.BE.D1.81)
в FB2-файлах электронных книг.
Используется алгоритм расстановки переносов из TeX.

Обработанные таким образом книги можно конвертировать в формат Kindle [KF8](http://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000729511) 
с помощью [calibre](http://calibre-ebook.com/). С этой целью можно использовать
bash-скрипт `fb2mobi.sh.example`.  Его следует переименовать в `fb2mobi.sh`
и подправить под своё окружение. Для переноса готовых книг на Kindle можно
использовать шаблон `send2kindle.sh.example`.

Переносы будут видны в Kindle Keyboard и новее с [последними версиями
прошивки](http://www.amazon.com/gp/help/customer/display.html/ref=hp_200127470_software?nodeId=200529680).
Поиск и использование словаря будут продолжать нормально работать.

Поддерживаются правила переносов для русского, украинского, английского и немецкого языков.

Также может быть полезен скрипт `append_series.py`, который добавляет номер
книги в серии и саму серию в заголовок файла для Kindle.
