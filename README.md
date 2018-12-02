SublimeLinter-contrib-rustc
================================

[![Build Status](https://travis-ci.org/oschwald/SublimeLinter-contrib-rustc.svg?branch=master)](https://travis-ci.org/oschwald/SublimeLinter-contrib-rustc)

This linter plugin for [SublimeLinter][docs]
provides an interface to [rustc and cargo](http://www.rust-lang.org/).
It will be used with files using the Rust syntax.

By default, `cargo` will be run for saved files only,
assuming your project defines a `Cargo.toml` file in its root.
`rustc` is available as a fallback
and may also be used to lint files in background mode, if desired.
See the [settings](#settings) for more.

## Installation
SublimeLinter must be installed in order to use this plugin.
If SublimeLinter is not installed,
please follow the instructions [here][installation].

### Linter installation
Before using this plugin,
you must ensure that `rustc` and `cargo` are installed on your system.
To install `rustc`,
install Rust as directed in the [Rust tutorial](https://static.rust-lang.org/doc/master/book/getting-started.html).

### Linter configuration
In order for `rustc` and `cargo` to be executed by SublimeLinter,
you must ensure that its path is available to SublimeLinter.
Before going any further,
please read and follow the steps in ["Finding a linter executable"](http://sublimelinter.readthedocs.org/en/latest/troubleshooting.html#finding-a-linter-executable)
through “Validating your PATH” in the documentation.

Once you have installed and configured `rustc`, you can proceed to install the SublimeLinter-contrib-rustc plugin if it is not yet installed.

### Plugin installation
Please use [Package Control][pc] to install the linter plugin.
This will ensure that the plugin will be updated
when new versions are available.
If you want to install from source so you can modify the source code,
you probably know what you are doing.

To install via Package Control, do the following:

1. Within Sublime Text, bring up the [Command Palette][cmd] and type `install`.
Among the commands you should see `Package Control: Install Package`.
If that command is not highlighted,
use the keyboard or mouse to select it.
There will be a pause of a few seconds
while Package Control fetches the list of available plugins.

1. When the plugin list appears, type `rustc`.
Among the entries you should see `SublimeLinter-contrib-rustc`.
If that entry is not highlighted,
use the keyboard or mouse to select it.

## Settings
For general information on how SublimeLinter works with settings,
please see [Settings][settings].
For information on generic linter settings,
please see [Linter Settings][linter-settings].

In addition to the standard SublimeLinter settings,
SublimeLinter-contrib-rustc provides its own settings.

|Setting|Description|
|:------|:----------|
|`cargo_command`|The command to run with cargo. Examples: `check all`, `test all`, `clippy` or `build`. Default: `"check"`|
|`rustc_live`|Since `cargo` only operates on entire projects, you may elect to run `rustc` on the current file only. This can quickly fail because of imports, however. Default: `false`|
|`rustc_fallback`|When a `Cargo.toml` file cannot be found, use just `rustc` as a fallback. This allows linting stand-alone files. Default: `true`|


[docs]: http://sublimelinter.readthedocs.org
[installation]: http://sublimelinter.readthedocs.org/en/latest/installation.html
[locating-executables]: http://sublimelinter.readthedocs.org/en/latest/usage.html#how-linter-executables-are-located
[pc]: https://packagecontrol.io/installation
[cmd]: http://docs.sublimetext.info/en/sublime-text-3/extensibility/command_palette.html
[settings]: http://sublimelinter.readthedocs.org/en/latest/settings.html
[linter-settings]: http://sublimelinter.readthedocs.org/en/latest/linter_settings.html
[inline-settings]: http://sublimelinter.readthedocs.org/en/latest/settings.html#inline-settings
