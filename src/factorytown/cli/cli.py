#!/usr/bin/env python3

# Copyright (c) 2024 Samuel J. McKelvie
#
# MIT License - See LICENSE file accompanying this package.
#

"""
factorytown CLI tool
"""
from __future__ import annotations

import os
import sys
import argparse
import json
import logging
import re
import subprocess

from ..common import *
from ..version import __version__
from ..proj_dir import get_project_dir
from ..version import __version__ as pkg_version
from ..model_scrape import (
    scrape_model, FactoryTownModel
)

PROGNAME = "factorytown"

class CmdExitError(RuntimeError):
    exit_code: int

    def __init__(self, exit_code: int, msg: Optional[str]=None):
        if msg is None:
            msg = f"Command exited with return code {exit_code}"
        super().__init__(msg)
        self.exit_code = exit_code

class ArgparseExitError(CmdExitError):
    pass

class NoExitArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)
        raise ArgparseExitError(status, message)

class CommandHandler:
    _parser: argparse.ArgumentParser
    _argv: Optional[List[str]]
    _args: argparse.Namespace
    _provide_traceback: bool = True
    _project_dir: Optional[str] = None

    def __init__(self, argv: Optional[Sequence[str]]=None):
        self._argv = None if argv is None else list(argv)

    def get_project_dir(self) -> str:
        if self._project_dir is None:
            self._project_dir = get_project_dir()
        return self._project_dir
    
    def get_build_dir(self) -> str:
        return os.path.join(self.get_project_dir(), "build")

    def cmd_bare(self) -> int:
        print("Error: A command is required\n", file=sys.stderr)
        self._args.subparser.print_help(sys.stderr)
        return 1
    
    def cmd_get_md(self) -> int:
        from ..raw_scrape import get_page_markdown
        page_name: str = self._args.page_name
        force: bool = self._args.force, bool
        md = get_page_markdown(page_name, force)
        print(md, end='')
        return 0
    
    def cmd_get_html(self) -> int:
        from ..raw_scrape import get_page_html
        page_name: str = self._args.page_name
        force: bool = self._args.force, bool
        html = get_page_html(page_name, force)
        print(html, end='')
        return 0

    def cmd_scrape(self) -> int:
        from ..model_scrape import scrape_model, FactoryTownModel
        force: bool = self._args.force, bool
        model = scrape_model(force=force)
        print(model)
        return 0

    def cmd_version(self) -> int:
        print(pkg_version)
        return 0
    
    def cmd_test(self) -> int:
        from ..test import do_test
        #do_test()
        #return 0
        return self.cmd_scrape()

    def run(self) -> int:
        """Run the command-line tool with provided arguments

        Args:
            argv (Optional[Sequence[str]], optional):
                A list of commandline arguments (NOT including the program as argv[0]!),
                or None to use sys.argv[1:]. Defaults to None.

        Returns:
            int: The exit code that would be returned if this were run as a standalone command.
        """
        import argparse

        parser = argparse.ArgumentParser(
            prog=PROGNAME,
            description="factorytown metatool."
          )


        # ======================= Main command

        self._parser = parser
        parser.add_argument('--traceback', "--tb", action='store_true', default=False,
                            help='Display detailed exception information')
        parser.add_argument('--log-level', '-l', type=str.lower, dest='log_level', default='warning',
                            choices=['debug', 'infos', 'warning', 'error', 'critical'],
                            help='''The logging level to use. Default: warning''')
        parser.set_defaults(func=self.cmd_bare, subparser=parser)

        subparsers = parser.add_subparsers(
                            title='Commands',
                            description='Valid commands',
                            help=f'Additional help available with "{PROGNAME} <command-name> -h"')

        # ======================= get-md

        sp = subparsers.add_parser('get-md',
                                description='''fetch the wkitext markdown for a Factory Town wki page.''')
        sp.add_argument("--force", "-f", action="store_true",
                            help="Force refresh of cache")
        sp.add_argument("page_name",
                            help="The Wiki page name")
        sp.set_defaults(func=self.cmd_get_md, subparser=sp)

        # ======================= get-html

        sp = subparsers.add_parser('get-html',
                                description='''fetch the HTML for a Factory Town wki page.''')
        sp.add_argument("--force", "-f", action="store_true",
                            help="Force refresh of cache")
        sp.add_argument("page_name",
                            help="The Wiki page name")
        sp.set_defaults(func=self.cmd_get_html, subparser=sp)

        # ======================= scrape

        sp = subparsers.add_parser('scrape',
                                description='''Scrape the Factory Tow wiki for the entire model.''')
        sp.add_argument("--force", "-f", action="store_true",
                            help="Force refresh of cache")
        sp.set_defaults(func=self.cmd_scrape, subparser=sp)

        # ======================= test

        sp = subparsers.add_parser('test',
                                description='''Run a temporary test command.''')
        sp.add_argument("--force", "-f", action="store_true",
                            help="Force refresh of cache")
        sp.set_defaults(func=self.cmd_test, subparser=sp)

        # ======================= version

        sp = subparsers.add_parser('version',
                                description='''Display version information.''')
        sp.set_defaults(func=self.cmd_version, subparser=sp)

        # =========================================================

        try:
            args = parser.parse_args(self._argv)
        except ArgparseExitError as ex:
            return ex.exit_code
        traceback: bool = args.traceback
        self._provide_traceback = traceback

        try:
            try:
                log_level = getattr(logging, args.log_level.upper())
            except AttributeError:
                raise ValueError(f"Invalid log level: {args.log_level}")
            logging.basicConfig(
                
                level=log_level,
            )
            self._args = args
            func: Callable[[], int] = args.func
            logging.debug(f"Running command {func.__name__}, tb = {traceback}")
            rc = func()
            logging.debug(f"Command {func.__name__} returned {rc}")
        except Exception as ex:
            is_exit_error = isinstance(ex, CmdExitError)
            if is_exit_error:
                rc = ex.exit_code
            else:
                rc = 1
            ex_desc = str(ex)
            ex_classname = ex.__class__.__name__
            if len(ex_desc) == 0:
                print(f"{PROGNAME}: error: {ex_classname}", file=sys.stderr)
            else:
                print(f"{PROGNAME}: error ({ex_classname}): {ex_desc}", file=sys.stderr)
            if traceback:
                raise
        except BaseException as ex:
            print(f"{PROGNAME}: Unhandled exception {ex.__class__.__name__}: {ex}", file=sys.stderr)
            raise

        return rc

def run(argv: Optional[Sequence[str]]=None) -> int:
    rc = CommandHandler(argv).run()
    return rc
