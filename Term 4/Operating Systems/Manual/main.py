#!/usr/bin/python3
"""
This script parses BMSTU IU9 Operating Systems course's manual.
It takes 36 pages from press.bmstu.ru and combines them into manual.pdf
"""
import weasyprint
import sys
from datetime import datetime


def get_url(ind: int) -> str:
    """
    Return an url in a right format
    :param ind: Number of the page
    :return: url do download
    """
    if ind <= 0 or ind >= 37:
        return ""
    if ind < 10:
        return f"https://press.bmstu.ru/ebooks/2024/06/16/169de298de71ec859ae19b5c7a963936/OEBPS/mybook000{ind}.xhtml"
    else:
        return f"https://press.bmstu.ru/ebooks/2024/06/16/169de298de71ec859ae19b5c7a963936/OEBPS/mybook00{ind}.xhtml"

# Actually the verbose mode scares me
# I think weasyprint could lose some content
# Saving some errors anyway
sys.stderr = open("errors.txt", "w")

print("Building pdf")
# Make a remark page
today = datetime.today().strftime('%d.%m.%y')
remark = f"<i style=\"display:inline-block;width:100%;text-align:right;\">By {today}</i><h1 style=\"text-align: center;\">This file is the compilation from press.bmstu.ru</h1><b>The book's formatting could probably be corrupted</b>"
doc = weasyprint.HTML(string=remark).render()

# Iterate the book
for i in range(1, 37):
    print(f"\rCurrent page: {i}", end="")
    doc.pages.extend(weasyprint.HTML(url=get_url(i)).render().pages)

comb_name = "manual.pdf"
print(f"\nSaving into {comb_name}")
doc.write_pdf(comb_name)