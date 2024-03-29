# Yamlex

<p>
    <a href="https://pypi.org/pypi/yamlex"><img alt="Package version" src="https://img.shields.io/pypi/v/yamlex?logo=python&logoColor=white&color=blue"></a>
    <a href="https://pypi.org/pypi/yamlex"><img alt="Supported python versions" src="https://img.shields.io/pypi/pyversions/yamlex?logo=python&logoColor=white"></a>
</p>

The `yamlex` command-line tool is here to assist you in development of
an oversized `extension.yaml`, when working with Dynatrace 2.0 Extensions.

It can `split` your original `extension.yaml` into carefully structured 
parts, which are easier to work with. It can then assembe the
`extension.yaml` back from the individual parts using the `join` command.

The Extension Framework only cares about the final assembled
`extension.yaml`. Any extension would be considered invalid without it.
However, it is recommended to commit both the individual parts and
the assembled `extension.yaml` file into the code repository of your
extension, because individual parts are your "code" and the assembled 
file is your artifact. 

With `yamlex`, your development workflow changes in such a way that
you only modify the individual parts and never really touch the artificial 
`extension.yaml`. Before you build the extension, you run `yamlex join`
to assemble the parts into the main file.

*Important: you don't need `yamlex` to develop Dynatrace Extensions.
It's only here to simplify the work when it comes to really
big extensions.*

## Installation

```shell
pip install yamlex
```

## Usage

### Assemble `extension.yaml` from parts

```shell
# Normal call
$ yamlex join

# Shorthand
$ yamlex j

# More options
$ yamlex join --source extension/src --target extension/extension.yaml --force

# Create "dev" version of extension.yaml with 'custom:' prefix in its name
$ yamlex j --dev

# Join yaml and bump version in version.properties before assembling final file
$ yamles j --bump

# Help message
$ yamlex join --help
 Usage: yamlex join [OPTIONS]                                                          
                                                                                       
 Join YAML files into a single file.                                                   
                                                                                       
╭─ Options ───────────────────────────────────────────────────────────────────────────╮
│ --source     -s    DIRECTORY  Path to directory where split YAML source files are   │
│                               stored. [default: source or src/source]               │
│ --target     -t    FILE       Path for target extension.yaml file that will be      │
│                               assembled from parts. [default:                       │
│                               extension/extension.yaml or                           │
│                               src/extension/extension.yaml]                         │
│ --dev        -d               Prefix extension name with 'custom:' and use explicit │
│                               version.                                              │
│ --bump       -b               Bump version in the version.properties file.          │
│ --multiline  -m               Non YAML files are embedded as multiline strings.     │
│                               [default: True]                                       │
│ --version    -v    TEXT       Explicitly set the version to use during assembly or  │
│                               bump process. [default: None]                         │
│ --force      -f               Overwrite the files even if they were created         │
│                               manually.                                             │
│ --comment    -c    TEXT       Comment to add at the top of the YAML. [default:      │
│                               This file was generated by yamlex]                    │
│ --verbose                     Enable verbose output.                                │
│ --quiet                       Disable any informational output. Only errors.        │
│ --help                        Show this message and exit.                           │
╰─────────────────────────────────────────────────────────────────────────────────────╯
```

When assembling, the `join` command will avoid overwriting a manually
created `extension.yaml` file. The way it detects that the file is
manually created is by checking whether the file contains the following
comment: *generated by yamlex*.

In order to overwrite this safety check, you can launch the `join`
command with the `--force` flag.

#### Folder structure

The way `yamlex` assembles the `extension.yaml` from parts is by
parsing the `--source` directory.

*Example structure of an extension:*

```text
my-extension/
├── extension/
│   └── extension.yaml
├── source/
│   ├── metrics/
│   │   ├── +account_metrics/
│   │   │   ├── -my.account.storage.yaml
│   │   │   └── -my.account.size.yaml
│   │   └── my.availability.yaml
│   ├── sqlOracle/
│   │   └── index.yaml
│   └── index.yaml
└── activation.json
```

Here:
- `my-extension/source/` is a `--source` directory.
- `my-extension/extension/extension.yaml` is a `--target` file.

For each level of directories within the given `--source` folder:
- If `index.yaml` is found, its content is taken as-is into the
  current level.
- If any other `<name>.yaml` is found, its content is placed as-is
  into the <name> field of the current level.
- If `<folder>` is found, we parse its content and place it in the
  field called <folder>.

Couple of additional details:
- If any file or folder on some inside a directory has a name that
  starts with `-`, then this whole directory is considered to be
  an array field.
- Folders that start with `+` symbol
  are considered to be meta-grouping folders and files from them are
  treated as if they are not in those folder bur rather exist on the
  current level.

### (optional) Enable YAML validation and auto-completion 

By invoking `yamlex map` you can map the extension JSON schema files to the
future YAML parts of the split  `extension.yaml`.
This will ensure proper validation and auto-completion 
for each and every part and not just for the `extension.yaml`.

Before you execute the `map` command, make sure relevant JSON schema
files for extensions are downloaded and are placed in the right folder.
By default, `yamlex` expects the relevant schema folder to be placed in
the current directory under the `schema/` name.

```shell
# Normal help
$ yamlex map

# More options
$ yamlex map .vscode/settings.json --json schema/ --source extension/src --root . --extension-yaml extension/extension.yaml

# Help message
$ yamlex map --help

 Usage: yamlex map [OPTIONS] [SETTINGS]                                                
                                                                                       
 Map JSON schema to YAML files in VS Code settings                                     
                                                                                       
╭─ Arguments ─────────────────────────────────────────────────────────────────────────╮
│   settings      [SETTINGS]  Path to the VS Code settings.json file.                 │
│                             [default: .vscode/settings.json]                        │
╰─────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────╮
│ --json            -j      DIRECTORY  Path to directory with valid extensions JSON   │
│                                      schema files.                                  │
│                                      [default: schema]                              │
│ --source          -s      DIRECTORY  Path to directory where YAML source files will │
│                                      be stored. [default: source or src/source]     │
│ --root            -r      DIRECTORY  Root directory relative to which the paths in  │
│                                      settings file will be mapped. [default: .]     │
│ --extension-yaml  -e      FILE       Path to output extension.yaml file. [default:  │
│                                      extension/extension.yaml or                    │
│                                      src/extension/extension.yaml]                  │
│ --verbose                            Enable verbose output.                         │
│ --quiet                              Disable any informational output. Only errors. │
│ --help                               Show this message and exit.                    │
╰─────────────────────────────────────────────────────────────────────────────────────╯
```

### (optional) Split the `extension.yaml`

This command will split the `extension.yaml` into individual parts.
It is useful when you only just start using `yamlex` with an existing
extension.

```shell
# Normal syntax
$ yamlex split

# Shorthand
$ yamlex s

# More options
$ yamlex split --source extension/extension.yaml --target extension/src

# Help message
$ yamlex split --help

 Usage: yamlex split [OPTIONS]                                                         
                                                                                       
 Split central YAML file into parts.                                                   
                                                                                       
╭─ Options ───────────────────────────────────────────────────────────────────────────╮
│ --source   -s      FILE       Path to source extension.yaml file. [default:         │
│                               extension/extension.yaml or                           │
│                               src/extension/extension.yaml]                         │
│ --target   -t      DIRECTORY  Path to directory where split YAML source files will  │
│                               be stored. [default: source or src/source]            │
│ --force    -f                 Overwrite the files even if they were created         │
│                               manually.                                             │
│ --comment    -c    TEXT       Comment to add at the top of the YAML. [default:      │
│                               This file was generated by yamlex]                    │
│ --verbose                     Enable verbose output.                                │
│ --quiet                       Disable any informational output. Only errors.        │
│ --help                        Show this message and exit.                           │
╰─────────────────────────────────────────────────────────────────────────────────────╯
```

It tries to split YAML in a way that makes sense. It also preserves all
comments and formatting.

Any part created by `split` will have a *generated by yamlex* line at the top
of it. When you run the `split` command again, it won't overwrite the files
that do not have this line, considering them to be manually created.
You can overwrite this behavior by adding the `--force` flag.
