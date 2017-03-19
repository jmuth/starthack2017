#! /usr/bin/env python
# coding=utf-8

# Copyright © 2016 Joachim Muth <joachim.henri.muth@gmail.com>
#
# Distributed under terms of the MIT license.

from os import listdir
from os.path import isfile, join

def except_already_existing():
    mypath = 'out/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    onlyfiles = [f for f in onlyfiles if f[0] is not '.']
    # print(onlyfiles)

    n = []
    for file in onlyfiles:
        n.append(int(file[5:-4]))

    # print(n)
    return n