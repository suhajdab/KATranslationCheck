#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2015 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief Crowdin .po file filter
#
# Usecase:
#    Remove translated entries from the .po file
#
# Example:
#    Extract non-translated entries
#       ./pofilter.py -i sample.po -o sample.po.txt
#
#    Extract non-translated entries with context line
#    (Note: context is always output, means translated lines still outputs the context.)
#       ./pofilter.py --keep_context -i sample.po -o sample.po.txt
#


import argparse, sys, re, codecs

class Pofilter(object):
    """Crowdin .po file filter"""

    def __init__(self, opt_dict):
        """constructor
        """
        self.__opt_dict      = opt_dict
        self.__infile        = None
        self.__outfile       = None
        self.__cur_line      = 0
        self.__is_keep_context = opt_dict['keep_context']
        self.__parsing_kind  = None    # 'msgid' | 'msgstr' | None

        self.__re_context    = re.compile(r"^#.*$") # context line
        self.__re_msgid      = re.compile(r"^msgid .*") # msgid line
        self.__re_msgstr     = re.compile(r"^msgstr .*") # msgid line
        self.__re_dequote    = re.compile(r'^".*') # double quote started line

        self.__re_empty      = re.compile(r"^$")   # empty line

    def __is_line_context(self, line):
        """Is the line context line?
        """
        mat = self.__re_context.fullmatch(line)
        # print('This is entry. {0}:'.format(line))
        if (mat != None):
            # print('context')
            return True
        else:
            # print('not context')
            return False


    def __get_msg(self, proc_lines, msg_re):
        """get msg{id,str} chank as a list
        \param[in] proc_lines all readed lines, has been processed for context
        \param[in] msg_re matching regex (msg{id,str})
        \return list of the msg{id,str}
        """
        # look for msg{id,str} from the current line
        nb_line = len(proc_lines)

        # find msg{id,str} line
        msg_cont_str = []
        while True:
            if (self.__cur_line >= nb_line):
                # reach to the end
                return msg_cont_str

            line = proc_lines[self.__cur_line].rstrip()
            # print('line:{0}: {1}'.format(self.__cur_line, line).encode('utf-8', 'ignore'))

            ma = msg_re.match(line)
            if (ma != None):
                # Note: ma.group(1) doesn't work when '\n' is in the string (mutiple lines)
                # print('found msgid/msgstr line:{0}'.format(self.__cur_line))
                msg_cont_str.append(line)
                self.__cur_line += 1
                break

            # print('not found msgid/msgstr line:{0}, lookup continue'.format(self.__cur_line))
            self.__cur_line += 1
            # when keep context, output this line
            if (self.__is_keep_context == True):
                self.__outfile.write(line + '\n')


        # continue the following msgid strings (continue as long as "" lines)
        while True:
            if (self.__cur_line >= nb_line):
                # reach to the end
                return msg_cont_str

            line = proc_lines[self.__cur_line].rstrip()
            # print('line:{0}: {1}'.format(self.__cur_line, line).encode('utf-8', 'ignore'))
            ma = self.__re_dequote.match(line)
            if (ma != None):
                # Note: ma.group(1) doesn't work when '\n' is in the string (mutiple lines)
                msg_cont_str.append(line)
                # print('double quote found at {0}'.format(self.__cur_line))
                self.__cur_line += 1
            else:
                # print('double quote not found at {0}'.format(self.__cur_line))
                break

        # print('finished chank process at {0}: {1}'.format(self.__cur_line, proc_lines[self.__cur_line]).encode('utf-8', 'replace'))
        return msg_cont_str


    def __comp_msg(self, msgid_str, msgstr_str):
        """value equality comparison between msgid_str and msgstr_str.
        Remove the tag msg{id,str} and compare the rest.
        \return True when equal, False otherwise
        """
        msgid_list_len  = len(msgid_str)
        msgstr_list_len = len(msgstr_str)
        if (msgid_list_len == 0):
            raise RuntimeError('empty msgid_str.')

        if (msgstr_list_len == 0):
            raise RuntimeError('empty msgstr_str.')

        if (msgid_list_len != msgstr_list_len):
            return False        # there is a difference

        assert(msgid_str[0][0:6]  == "msgid ")
        assert(msgstr_str[0][0:7] == "msgstr ")

        # first line has the tag, msg{id,str}
        assert(msgid_str[0][0:6]  == "msgid ")
        assert(msgstr_str[0][0:7] == "msgstr ")
        if (msgid_str[0][6:]  != msgstr_str[0][7:]):
            return False

        for i in range(1, len(msgid_str)):
            if (msgid_str[i] != msgstr_str[i]):
                return False

        # all equal
        return True


    def __write_list(self, str_list, outfile):
        """write a list to the outfile
        """
        for line in str_list:
            outfile.write(line +'\n')


    def __apply_filter(self):
        """apply the filter function for the po file.
        """
        assert(self.__infile  != None)
        assert(self.__outfile != None)

        self.__is_parsing_str = None # init to msgid
        msgid_str  = []
        msgstr_str = []

        # read all lines
        all_lines = self.__infile.readlines()

        # handle context
        proc_context_line = []
        if (self.__is_keep_context == True):
            # print('keep context')
            proc_context_line = all_lines
        else:
            # print('remove context')
            for raw_line in all_lines:
                # check the context
                line = raw_line.rstrip()
                if (self.__is_line_context(line) == False):
                    proc_context_line.append(raw_line)

        # for line in proc_context_line:
        #     self.__outfile.write(line)

        # process pair of (msgid, msgstr)
        nb_lines = len(proc_context_line)
        self.__cur_line = 0
        while (self.__cur_line < nb_lines):
            msgid_str  = []
            msgstr_str = []
            msgid_str   = self.__get_msg(proc_context_line, self.__re_msgid)
            msgstr_str  = self.__get_msg(proc_context_line, self.__re_msgstr)
            if (len(msgid_str) == 0):
                # print('no more msgid')
                return

            if (self.__comp_msg(msgid_str, msgstr_str) == True):
                # print(msgid_str)
                self.__write_list(msgid_str,  self.__outfile)
                self.__write_list(msgstr_str, self.__outfile)
                self.__outfile.write('\n')


    def filter(self):
        """perform filter action
        """
        with open(self.__opt_dict['infile'], encoding='utf-8', mode='r') as self.__infile:
            with open(self.__opt_dict['outfile'], encoding='utf-8', mode='w') as self.__outfile:
                self.__apply_filter()


def main():
    """process a srt file."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="verbose output.")

    parser.add_argument("-i", "--infile", type=str,
                        default='',
                        help="input srt filename.")

    parser.add_argument("-o", "--outfile", type=str,
                        default='',
                        help="output filename.")

    parser.add_argument("--keep_context", action='store_true',
                        help="keep the context line.")

    args = parser.parse_args()

    opt_dict = {
        'infile':       args.infile,
        'outfile':      args.outfile,
        'keep_context': args.keep_context,
        'verbose':      args.verbose
    }

    if (args.verbose == True):
        for opt in opt_dict:
            print('verb: {0}: {1}'.format(opt, opt_dict[opt]))

    if (args.infile == ''):
        raise RuntimeError('No input file. Use -i to specify the input file.')

    if (args.outfile == ''):
        raise RuntimeError('No output file. Use -o to specify the output file.')

    pf = Pofilter(opt_dict)
    pf.filter()


if __name__ == "__main__":
    try:
        main()
        # sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))
