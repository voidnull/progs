#!/usr/bin/env python

import argparse
import os
import pprint
import subprocess
import sys
import time
import traceback

try:
    import git
except:
    print 'unable to find pkg [git for python] !!!'
    print 'Please install with `easy_install GitPython` or `pip install GitPython`'
    sys.exit(0)

class GitTool:

    def __init__(self, repodir='.'):
        self.repo = git.Repo(repodir)
        self.num_files = 0
        self.num_lines = 0
        
    # get the full author from a commit
    def get_commit_author(self, commit):
        return "{} <{}>".format(commit.author.name,commit.author.email)

    # get all the authors of a file
    def get_file_authors(self, filename):
        try:
            b = self.repo.blame(self.repo.head,filename)
        except:
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_tb(exc_traceback)
            #print 'unable to blame file:{}'.format(filename)
            return set()

        return set([self.get_commit_author(commit[0]) for commit in b])

    # get all the unique repo authors
    def get_repo_authors(self):
        files = self.get_files()
        authors = set()
        for f in files:
            authors.update(self.get_file_authors(f))
        return authors

    # get all the authors and the respective lines modified
    def get_author_lines(self,filename, specific_author=None):
        '''
        Returns a dict of author->[(from,to) ...]
        '''
        try:
            b = self.repo.blame(self.repo.head,filename)
        except:
            #print "Unexpected error:", sys.exc_info()[0]
            #print 'unable to blame file:{}'.format(filename)
            return {}

        # author to lines
        authors = {}
        line = 0
        for commit in b:
            from_line = line + 1
            line += len(commit[1])
            to_line = line
            author = self.get_commit_author(commit[0])
            if specific_author and author != specific_author:
                continue
            
            if author not in authors:
                authors[author] = []

            lines = authors[author]
            if len(lines) > 0 and lines[-1][1]+1 == from_line:
                # if they are continuous section, then merge
                lines[-1][1] = to_line
            else:
                lines.append([from_line, to_line])
            
        return authors

    # get all the files->lines modified by author
    def get_repo_lines_by_author(self, author):
        files = self.get_files()
        all_lines = {}
        for f in files:
            lines = self.get_author_lines(f, author)
            if len(lines) > 0:
                print lines
                all_lines[f] = lines[author]

        return all_lines

    def get_format_command(self, files, lines):
        cmd = ['clang-format', '-i']
        for line in lines:
            cmd.append('-lines={}:{}'.format(line[0],line[1]))

        if type(files) == type(''):
            files = [files]

        cmd.extend(files)
        return cmd

    # get the clang format cmd line for a specific author
    def get_format_cmd_author(self, author, files=None, execute=False):
        cmdlist = []
        if type(files) == type(''):
            if files == 'all':
                files = None
            else:
                files=[files]

        if files == None: files = self.get_files()
        
        for f in files:
            lines = self.get_author_lines(f, author)
            if len(lines) > 0:
                for l in lines[author]:
                    self.num_lines += l[1] - l[0] + 1

                cmd = self.get_format_cmd(f, lines[author])
                if execute:
                    self.num_files += 1
                    #print 'processing : {}'.format(f)
                    subprocess.call(cmd)
                cmdlist.append(' '.join(cmd))
                
        return cmdlist

    def commit_for_author(self, author):
        cmd = ['git','add','-A']
        subprocess.call(cmd)
        cmd = ['git','commit','-m','whitespace/formatting changes for : {}'.format(author), '--author="{}"'.format(author)]
        subprocess.call(cmd)
    
    def format_author_files(self, authors = None, files = None):
        if type(authors) == type(''):
            if authors == 'all':
                authors = None
            else:
                authors=[authors]

        if authors == None: authors = self.get_repo_authors()
        
        for a in authors:
            self.num_files = 0
            self.num_lines = 0
            st = time.time()
            print 'begin author:{} lines:{} files:{}'.format(a, self.num_lines, self.num_files)
            self.get_format_cmd_author(a, files, True)
            self.commit_for_author(a)
            print 'end   author:{} lines:{} files:{} time:{}'.format(a, self.num_lines, self.num_files, int(time.time()-st))
            
    # find all c/c++ files
    def get_files(self):
        files_all = []
        for root, dirs, files in os.walk(self.repo.working_dir):
            for f in files:
                fullpath = os.path.join(root, f)
                fullpath = os.path.relpath(fullpath, self.repo.working_dir)
                ext = os.path.splitext(fullpath)[1][1:]
                if ext in ['cc','cpp','h','hpp']:
                    files_all.append(fullpath)

        return files_all
    
    
if __name__ == "__main__" :

    parser = argparse.ArgumentParser(description='Format code for specific users')
    parser.add_argument('-f', '--file',default=None, help='file to be process, specify `all` for all files')
    parser.add_argument('-a', '--author',default=None, help='author to be process, specify `all` for all authors')
    parser.add_argument('-c',dest='command', choices=['list-authors',
                                                      'list-files',
                                                      'list-lines',
                                                      'show-format-command',
                                                      'do-format-command'],
                        help="do one of the specified")
    parser.add_argument('--yes', default=False, action='store_true', help="specify this to execute formatting")
    args = parser.parse_args()
    #print args

    gt = GitTool()
    
    if args.command == 'list-files':
        pprint.pprint( gt.get_files() )
    elif args.command == 'list-authors':
        if args.file:
            pprint.pprint( gt.get_file_authors(args.file) )
        else:
            pprint.pprint( gt.get_repo_authors() )
    elif args.command == 'list-lines':
        if args.file:
            pprint.pprint( gt.get_author_lines(args.file, args.author) )
        else:
            pprint.pprint( gt.get_repo_lines_by_author(args.author) )

    elif args.command == 'show-format-command':
        if args.author:
            pprint.pprint( gt.get_format_cmd_author(args.author, args.file) )
        else:
            print 'author needs to be specified'

    elif args.command == 'do-format-command':
        print '!!!!  About to apply formatting ...'
        if args.yes:
            st = time.time()
            gt.format_author_files(args.author, args.file)
            print 'total time : {}'.format(int(time.time()-st))
        else:
            print 'please specify --yes and re-run .. This is a sanity check'

    else:
        parser.print_help();
