#
# SublimeLinter-contrib-rustc/linter.py
# Linter plugin for SublimeLinter,
# a code checking framework for Sublime Text 3.
#
# Copyright (c) 2018 FichteFoll
#
# License: MIT
#
"""Exports the Rustc SublimeLinter plugin class."""

import getpass
import json
import logging
import os
import shutil
import tempfile

from SublimeLinter.lint import util
from SublimeLinter.lint import Linter
from SublimeLinter.lint.linter import LintMatch


USER = getpass.getuser()
TMPDIR_PREFIX = "SublimeLinter-contrib-rustc-%s" % USER

logger = logging.getLogger("SublimeLinter.plugin.mypy")

# Mapping for our created temporary directories (for rustc output)
if 'tmpdirs' not in globals():
    tmpdirs = {}


class Rust(Linter):
    """Provides an interface to Rust (rustc and cargo)."""

    use_cargo = True
    cargo_command = "check"
    defaults = {
        'selector': "source.rust",
        # Examples: 'check', 'check all', 'test all', 'clippy', 'build'
        'cargo_command': cargo_command,
        # Whether to use rustc for live linting of unsaved files.
        'rustc_live': False,
        # Whether to fall back to rustc if file isn't in a cargo project.
        'rustc_fallback': True,
    }
    # tempfile_suffix = 'rs'
    tempfile_suffix = '-'
    line_col_base = (1, 0)
    error_stream = util.STREAM_STDERR

    def should_lint(self, reason=None):
        """Only allow background mode when rustc_live is is enabled."""
        # TOCHECK is this sensitive to races?
        v_settings = self.get_view_settings()
        rustc_live = v_settings.get('rustc_live')
        self.tempfile_suffix = "rs" if rustc_live and not self.cargo else "-"

        return super().should_lint(reason=reason)

    def cmd(self):
        """Build command used to lint.

        The command chosen is resolved as follows:

        - Check if the current project has a `Cargo.toml` file
          and lint using `cargo <cargo_command>`.
        - Otherwise lint the current file with `rustc`.
        """
        v_settings = self.get_view_settings()
        self.working_dir = self.get_working_dir(v_settings)
        self.cargo = os.path.exists(os.path.join(self.working_dir, 'Cargo.toml'))

        if self.cargo:
            cargo_command = v_settings.get('cargo_command', self.cargo_command).split()
            return ['cargo'] + cargo_command

        elif v_settings.get('rustc_fallback') or v_settings.get('rustc_live'):
            if self.working_dir in tmpdirs:
                cache_dir = tmpdirs[self.working_dir].name
            else:
                tmp_dir = tempfile.TemporaryDirectory(prefix=TMPDIR_PREFIX)
                tmpdirs[self.working_dir] = tmp_dir
                cache_dir = tmp_dir.name
                logger.info("Created temporary cache dir at: %s", cache_dir)

            file = '$file_on_disk' if self.tempfile_suffix == '-' else '$temp_file'

            return ['rustc', '${args}',
                    '--error-format=json',
                    '--out-dir', cache_dir,
                    file]
        else:
            return None

    def finalize_cmd(self, *args, **kwargs):
        """Never auto-append (cargo runs on the working dir)."""
        if kwargs.get('auto_append'):
            kwargs['auto_append'] = False
        return super().finalize_cmd(*args, **kwargs)

    def get_environment(self, settings):
        """Ensure --error-format is in RUSTFLAGS."""
        env = super().get_environment(settings)
        env['RUSTFLAGS'] = env.get('RUSTFLAGS', '') + ' --error-format=json'
        return env

    @staticmethod
    def _parse_output_line(line):
        """Filter out frequent/normal non-JSON lines."""
        stripped = line.strip()
        valid_words = ("Checking", "Finished", "Downloading", "Compiling")
        if any(stripped.startswith(word) for word in valid_words):
            return None
        return json.loads(line)

    def find_errors(self, output):
        """Return the components of the match.

        We override this because Cargo lints all referenced files,
        and we only want errors from the linted file.
        Of course when linting a single file only,
        all the errors will be from that file.
        """
        for line in output.splitlines():
            try:
                data = self._parse_output_line(line)
            except ValueError as e:
                logger.warning("Invalid JSON from executable %s; %r", e, line)
                self.notify_failure()
                return None

            if not data or not data['spans']:
                continue
            span = data['spans'][0]

            if self.cargo:
                matched_file = span['file_name']
                matched_file = os.path.join(self.working_dir, matched_file)
                if matched_file != self.filename:
                    continue

            if span['text'] and span['line_start'] == span['line_end']:
                text = span['text'][0]
                near = text['text'][text['highlight_start']:text['highlight_end']]
            else:
                near = None

            code = data.get('code')
            code = code.get('code', True) if code else True
            if data['level'].endswith("error"):
                error = code
                warning = False
            else:
                error = False
                warning = code

            yield LintMatch(
                match=span,
                line=span['line_start'] - 1,
                col=span['column_start'] - 1,
                error=error,
                warning=warning,
                message=data['message'],
                near=near,
            )

    def reposition_match(self, line, col, m, vv):
        """Apply region positions as reported by rustc."""
        match = m.match
        if (
            col is None
            or 'line_end' not in match
            or 'column_end' not in match
        ):
            return super().reposition_match(line, col, m, vv)

        # apply line_col_base manually
        end_line = match['line_end'] - 1
        end_column = match['column_end'] - 1

        # add line lenths of all lines inbetween
        for _line in range(line, end_line):
            text = vv.select_line(_line)
            end_column += len(text)

        return line, col, end_column


def _cleanup_tmpdirs():
    def _onerror(function, path, exc_info):
        logger.exception("Unable to delete '%s' while cleaning up temporary directory",
                         path, exc_info=exc_info)
    tmpdir = tempfile.gettempdir()
    for dirname in os.listdir(tmpdir):
        if dirname.startswith(TMPDIR_PREFIX):
            shutil.rmtree(os.path.join(tmpdir, dirname), onerror=_onerror)


def plugin_loaded():
    """Attempt to clean up temporary directories from previous runs."""
    _cleanup_tmpdirs()


def plugin_unloaded():
    """Clear references to TemporaryDirectory instances.

    They should then be removed automatically.
    """
    tmpdirs.clear()
