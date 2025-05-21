# Yamlex

<p>
  <a href="https://pypi.org/pypi/yamlex"><img alt="Package version" src="https://img.shields.io/pypi/v/yamlex?logo=python&logoColor=white&color=blue"></a>
  <a href="https://pypi.org/pypi/yamlex"><img alt="Supported python versions" src="https://img.shields.io/pypi/pyversions/yamlex?logo=python&logoColor=white"></a>
</p>

The `yamlex` command-line tool is here to assist you in development of
an large Dynatrace Extensions.

It can assemble one giant `extension.yaml` from individual parts placed
in the `source/` folder.

## Benefits of using Yamlex

* It's much easier to find and modify a specific file than to scroll through
  thousands of lines in one big `extension.yaml`.
* Atomic predictable edits: modify just one small file.
* Flexibility in organization: organize the parts of your extension
  into the hierarchy you like: folders, nesting, and so on.

## How you would use it 99% of the time

Imagine you have an extension, with the individual YAML parts sitting in the
`src/source/` folder and the assembled `extension.yaml` stored in
`src/extension/extension.yaml`.

1. You modify a few parts inside the `src/source/` to implement new changes.
2. You then run `yamlex diff` to see what would change if you join:

   ```shell
   yamlex diff -s src/extension/extension.yaml -t src/source/
   ```

3. If you are satisfied with the diff, run `yamlex join`:

   ```shell   
   yamlex join
   ```

**🆕 New in Yamlex 1.3:** The way final `extension.yaml` is assembled has
changed in Yamlex 1.3.0. To preserve the old behavior such as line length
being limited to 80 chars you can invoke `yamlex join` with additional
flags:

```shell
yamlex join --line-length 80 --sort-paths --remove-comments
```

## There is more to it

It can `split` your original `extension.yaml` into carefully structured 
parts, which are easier to work with. It can then assembe the
`extension.yaml` back from the individual parts using the `join` command.

**Warning:** just be careful with split. You only need to do it once and
only for the extensions that were not already manually or automatically
split into individual parts.

## Why this works

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

**Important**: you don't need `yamlex` to develop Dynatrace Extensions.
It's only here to simplify the work when it comes to really
big extensions.

## Installation

Yamlex needs Python 3.9 or higher to run.

```shell
pip install yamlex
```

*You need to have Python installed on your system.*

### Excuse me, is there a no hussle way to install Python on my system?

Why, yes, of course! Here are some recommended ways for non-professionals to install Python.

However, here is one golden advice I would give to everyone:

> Don't use the Python version that comes with your system. You might irreparably break your OS
> if you do that. Use a separate Python installation instead, like described below. This mostly
> applies to Linux and older MacOS versions.

#### Windows

1. Download the latest Python installer from the [Python website](https://www.python.org/downloads/windows/).
   1. Look in the "Stable Releases" section.
   1. Choose the latest version of Python 3.x. It's usually somewhere at the top of the list. For example: Python 3.13.3.
   1. Download the installer compatible with your system. Most common is: "Windows installer (64-bit)".
1. Run the installer and make sure to check the box that says "Add Python to PATH".
1. Follow the installation instructions.
1. Open the command prompt and run `pip install yamlex`.

#### MacOS

1. Download the latest Python installer from the [Python website](https://www.python.org/downloads/macos/).
   1. Look in the "Stable Releases" section.
   1. Choose the latest version of Python 3.x. It's usually somewhere at the top of the list. For example: Python 3.13.3.
   1. Download the installer compatible with your system. Most common is: "macOS 64-bit universal2 installer".
      It will work on both Intel and Apple Silicon Macs.
1. Run the installer and follow the installation instructions.
1. Open the terminal and run `pip install yamlex`.

#### Linux

Linux doesn't have a downloadable installer for Python. But if you are using Linux you probably know the best way
install Python on your specific distribution. Here are some common ways:

1. **Debian/Ubuntu**:

   ```shell
   sudo apt install software-properties-common
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt install python3.9
   ```

1. **Fedora**: Python is already preinstalled on Fedora and is safe to use!

## Full instructions

**TL;DR:**

When you work with an extension that was already split into parts:

1. Modify whichever part you want.
1. Assemble the `extension.yaml` file from parts using `yamlex join`.
1. Repeat the last two steps as you continue developing the extension.

*Congratulations! You rock!*

In a very rare case you **start with an already big `extension.yaml`** that will take
to long to split into parts manually, you can use `yamlex split` to do it for you:

1. Go into the directory of your extension.
1. Run `yamlex split` to split your `extension.yaml` into individual parts.
1. Back up the original `extension.yaml` by renaming it to `extension.yaml.bckp` or something.
1. Run `yamlex join` to assemble `extension.yaml` back from split parts.

*Done!*

```
$ yamlex --help
                                                                                
 Usage: yamlex [OPTIONS] COMMAND [ARGS]...                                      
                                                                                
 How assembling works:                                                          
                                                                                
 - Hierarchy preserved                                                          
                                                                                
   Any folder or file within the --source directory is considered to be         
   a field within the final extension.yaml. For example, a file called          
   name.yaml will become a field called name: and its content                   
   will be put into that field.                                                 
                                                                                
   Example 1:                                                                   
   ┌───────────────────────────────────┬───────────────────────────────────┐    
   │ Source folder structure:          │ Contents of the file:             │    
   │ source/                           │                                   │    
   │ └── author.yaml                   │ name: John Doe                    │    
   ├───────────────────────────────────┼───────────────────────────────────┤    
   │ Resulting extension.yaml:         │                                   │    
   │ author:                           │                                   │    
   │   name: John Doe                  │                                   │    
   └───────────────────────────────────┴───────────────────────────────────┘    
                                                                                
 - Arrays with '-' symbol                                                       
                                                                                
   The minus sign '-' in front of a file or directory inside a parent           
   folder means that the parent folder is an array. Every item within           
   that folder will become an array item and the folder itself will             
   be added as an array to the final yaml.                                      
                                                                                
   Example 2:                                                                   
                                                                                
   ┌───────────────────────────────────┬───────────────────────────────────┐    
   │ Source folder structure:          │ Contents of the file:             │    
   │ source/                           │                                   │    
   │ ├── metrics/                      │                                   │    
   │ │   └── -metric_1.yaml            │ key: metric_1                     │    
   │ └── +index.yaml                   │ name: com.example.extension.test  │    
   ├───────────────────────────────────┼───────────────────────────────────┤    
   │ Resulting extension.yaml:         │                                   │    
   │ name: com.example.extension.test  │                                   │    
   │ metrics:                          │                                   │    
   │   - key: metric_1                 │                                   │    
   └───────────────────────────────────┴───────────────────────────────────┘    
                                                                                
   Example 3 (same result, using different structure):                          
                                                                                
   ┌───────────────────────────────────┬───────────────────────────────────┐    
   │ Source folder structure:          │ Contents of the file:             │    
   │ source/                           │                                   │    
   │ ├── metrics/                      │                                   │    
   │ │   └── -metric_1/                │                                   │    
   │ │       └── index.yaml            │ key: metric_1                     │    
   │ └── +index.yaml                   │ name: com.example.extension.test  │    
   ├───────────────────────────────────┼───────────────────────────────────┤    
   │ Resulting extension.yaml:         │                                   │    
   │ name: com.example.extension.test  │                                   │    
   │ metrics:                          │                                   │    
   │   - key: metric_1                 │                                   │    
   └───────────────────────────────────┴───────────────────────────────────┘    
                                                                                
 - Groupers with '+' symbol                                                     
                                                                                
   If the name of a folder or file starts with a + symbol, then the             
   content of that file or folder is added on the same level as the folder      
   itself.                                                                      
                                                                                
   The folder itself is ignored, but everything inside it is used.              
   With the + in front, the folder or file become a "virtual"                   
   hierarchy, which doesn't add a new nesting level in the final yaml.          
   However, anything inside such folder or file will be added on the same       
   level as the parent. Almost as if the +folder/ or +file.yaml do not          
   exist at all and their content just gets added to the parent.                
                                                                                
   Example 4:                                                                   
                                                                                
   ┌───────────────────────────────────┬───────────────────────────────────┐    
   │ Source folder structure:          │ Contents of the file:             │    
   │ source/                           │                                   │    
   │ ├── author.yaml                   │ name: John Doe                    │    
   │ └── +index.yaml                   │ name: com.example.extension.test  │    
   │                                   │ minDynatraceVersion: 1.295.0      │    
   ├───────────────────────────────────┼───────────────────────────────────┤    
   │ Resulting extension.yaml:         │                                   │    
   │ name: com.example.extension.test  │                                   │    
   │ minDynatraceVersion: 1.295.0      │                                   │    
   │ author:                           │                                   │    
   │   name: John Doe                  │                                   │    
   └───────────────────────────────────┴───────────────────────────────────┘    
                                                                                
   Example 5:                                                                   
                                                                                
   ┌───────────────────────────────────┬───────────────────────────────────┐    
   │ Source folder structure:          │ Contents of the file:             │    
   │ source/                           │                                   │    
   │ ├── author.yaml                   │ name: John Doe                    │    
   │ └── +grouper.yaml                 │ name: com.example.extension.test  │    
   │                                   │ minDynatraceVersion: 1.295.0      │    
   ├───────────────────────────────────┼───────────────────────────────────┤    
   │ Resulting extension.yaml:         │                                   │    
   │ name: com.example.extension.test  │                                   │    
   │ minDynatraceVersion: 1.295.0      │                                   │    
   │ author:                           │                                   │    
   │   name: John Doe                  │                                   │    
   └───────────────────────────────────┴───────────────────────────────────┘    
                                                                                
   Example 6:                                                                   
                                                                                
   ┌───────────────────────────────────┬───────────────────────────────────┐    
   │ Source folder structure:          │ Contents of the file:             │    
   │ source/                           │                                   │    
   │ ├── metrics/                      │                                   │    
   │ │   └── +group_of_metrics.yaml    │ - key: metric_1                   │    
   │ └── +index.yaml                   │ name: com.example.extension.test  │    
   ├───────────────────────────────────┼───────────────────────────────────┤    
   │ Resulting extension.yaml:         │                                   │    
   │ name: com.example.extension.test  │                                   │    
   │ metrics:                          │                                   │    
   │   - key: metric_1                 │                                   │    
   └───────────────────────────────────┴───────────────────────────────────┘    
                                                                                
   Example 7:                                                                   
                                                                                
   ┌───────────────────────────────────┬───────────────────────────────────┐    
   │ Source folder structure:          │ Contents of the file:             │    
   │ source/                           │                                   │    
   │ ├── metrics/                      │                                   │    
   │ │   └── +group_of_metrics/        │                                   │    
   │ │       └── -metric_1.yaml        │ key: metric_1                     │    
   │ └── +index.yaml                   │ name: com.example.extension.test  │    
   ├───────────────────────────────────┼───────────────────────────────────┤    
   │ Resulting extension.yaml:         │                                   │    
   │ name: com.example.extension.test  │                                   │    
   │ metrics:                          │                                   │    
   │   - key: metric_1                 │                                   │    
   └───────────────────────────────────┴───────────────────────────────────┘    
                                                                                
 - Ignoring with '!' symbol                                                     
                                                                                
   If a folder or a file starts with the exclamation mark symbol '!', then      
   it will be ignored, as if it doesn't exist at all, including all its         
   content. This is useful for excluding files or folders from the final        
   yaml.                                                                        
                                                                                
   Example 8:                                                                   
                                                                                
   ┌───────────────────────────────────┬───────────────────────────────────┐    
   │ Source folder structure:          │ Contents of the file:             │    
   │ source/                           │                                   │    
   │ ├── !metrics/                     │                                   │    
   │ │   └── -metric_1.yaml            │ key: metric_1                     │    
   │ └── +index.yaml                   │ name: com.example.extension.test  │    
   ├───────────────────────────────────┼───────────────────────────────────┤    
   │ Resulting extension.yaml:         │                                   │    
   │ name: com.example.extension.test  │                                   │    
   └───────────────────────────────────┴───────────────────────────────────┘    
                                                                                
 - Scalar files                                                                 
                                                                                
   Any plain text file (not yaml) will be added as a scalar value. With         
   the formatting preserved.                                                    
                                                                                
   Example 9:                                                                   
                                                                                
   ┌───────────────────────────────────┬───────────────────────────────────┐    
   │ Source folder structure:          │ Contents of the file:             │    
   │ source/                           │                                   │    
   │ └── vars/                         │                                   │    
   │     └── -timeout/                 │                                   │    
   │         ├── description.txt       │ Custom timeout.                   │    
   │         └── +index.yaml           │ id: timeout                       │    
   │                                   │ type: text                        │    
   │                                   │ defaultValue: "120"               │    
   ├───────────────────────────────────┼───────────────────────────────────┤    
   │ Resulting extension.yaml:         │                                   │    
   │ vars:                             │                                   │    
   │   - id: timeout                   │                                   │    
   │     description: Custom timeout.  │                                   │    
   │     type: text                    │                                   │    
   │     defaultValue: "120"           │                                   │    
   └───────────────────────────────────┴───────────────────────────────────┘    
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --version  -v                                                                │
│ --help     -h        Show this message and exit.                             │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ map     Map JSON schema to YAML files in VS Code settings.                   │
│ split   Split extension.yaml file into individual components.                │
│ join    Join individual components into a single extension.yaml file.        │
│ diff    Compare --source YAML file or directory to --target and print the    │
│         differences.                                                         │
╰──────────────────────────────────────────────────────────────────────────────╯

```

### Join

Assemble `extension.yaml` from parts

**Usage**

```shell
# Normal call
$ yamlex join

# Shorthand: Yamlex will automatically find your source and target paths if the
# are located in the usual places: inside the current dir or inside src/ folder.
$ yamlex j

# More options: specify where the parts are and where the assembled file should be
# and if there is already an extension.yaml there, written manually, overwrite it
$ yamlex join --source extension/src --target extension/extension.yaml --force

# Limit line length of the assembled file to 80 characters
$ yamlex j --line-length 80

# Sort all paths in the source folder before assembling (this affects the order
# of the keys in the assembled file)
$ yamlex j --sort-paths

# Remove any YAML comments form the generated file
$ yamlex j --remove-comments

# Generate the "dev" version of the extension with 'custom:' prefix in its name
# and the version explicitly specified in the generated extension.yaml
$ yamlex j --dev

# Specify the version of the extension
$ yamlex j --version 1.0.0

# Enable verbose output for troubleshooting. Will show exactly what yamlex is doing
$ yamlex j --verbose
```

**Help**

```
$ yamlex join --help
                                                                                
 Usage: yamlex join [OPTIONS]                                                   
                                                                                
 Join individual components into a single extension.yaml file.                  
                                                                                
 Assembles all files from the --source directory in a hierarchical order.       
 As if the folder structure of the --source directory represents a YAML         
 structure.                                                                     
                                                                                
 Overwriting existing extension.yaml (--no-file-header and --force)             
                                                                                
 Yamlex tries to be cautious not to accidentally overwrite a manually           
 created extension.yaml. If that file contains the "Generated with              
 yamlex" header in it, then yamlex overwrites it without hesitation.            
 However, when extension.yaml does not contain that line, yamlex                
 does not overwrite it. You can alter this behaviour using --force flag.        
                                                                                
 When yamlex generates the extension.yaml from parts, it adds the               
 same comment at the top: # Generated by yamlex                                 
 If you would like to disable this behaviour, use the                           
 --no-file-header flag.                                                         
                                                                                
 Development mode                                                               
                                                                                
 When you add the --dev flag, yamlex will add the "custom:" prefix to the       
 name of your extension and will put an explicit version into the final         
 extension.yaml.                                                                
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --source           -s      DIRECTORY  Path to the directory where individual │
│                                       source component files are stored.     │
│                                       [default: (source or src/source)]      │
│ --target           -t      FILE       Path to the target extension.yaml file │
│                                       that will be assembled from parts.     │
│                                       [default: (extension/extension.yaml or │
│                                       src/extension/extension.yaml)]         │
│ --dev              -d                 Add the 'custom:' prefix and embed     │
│                                       version into extension.yaml.           │
│ --keep             -k                 Keep formatting and indentation when   │
│                                       embedding non-yaml files.              │
│                                       [default: True]                        │
│ --version          -v      TEXT       Explicitly set the version in the      │
│                                       extension.yaml.                        │
│ --sort-paths                          Sort paths alphabetically when         │
│                                       traversing source directory before     │
│                                       join.                                  │
│ --line-length              INTEGER    Maximum line length in the generated   │
│                                       extension.yaml.                        │
│                                       [default: (not limited)]               │
│ --dry-run                             Test run without any files being       │
│                                       created.                               │
│ --remove-comments                     Remove any YAML comments from the      │
│                                       created files.                         │
│ --no-file-header   -H                 Do not add the 'generated by yamlex'   │
│                                       comment header at the top of the file. │
│ --force            -f                 Overwrite target files even if they    │
│                                       were created manually.                 │
│ --verbose                             Enable verbose output.                 │
│ --quiet                               Disable any informational output. Only │
│                                       errors.                                │
│ --help             -h                 Show this message and exit.            │
╰──────────────────────────────────────────────────────────────────────────────╯

```

### `diff`

Compare two YAML files or source dirrectories and show the differences.

This is an **extremely useful command** when you are dealing with a very big
set of changes in the `extension.yaml` file and need to verify what exactly changed.

The power of `yamlex diff` is that it can compare the actual content of the YAML,
not the line number or the order of the keys. It recursively compares the source 
and target and shows exactly what has changed and where, irrespective
of how the keys are ordered or how long the lines are.

Use cases:

* Someone manually changed the `extension.yaml` and it is out of sync
  with the split parts.
* You have changed the `--line-length` and the git diff is too big to
  see what changed.
* You have changed the `--sort-paths` and the git diff completely our of
  order.

This is useful when you want to see what changed in the `extension.yaml`
between two versions of the extension. It can also be used to compare
the `extension.yaml` with the split parts to see if they are in sync.

**ℹ️ Note:** The `--source` will be marked as "old" in the diff and the
`--target` will be marked as "new".

**Usage**

```shell
# Compare a new version of the extension.yaml to the old one
yamlex diff --source src/extension/extension.yaml --target src/extension/new-extension.yaml

# Compare the contents of the source directory to the existing extension.yaml
# to see what would change if you run join
yamlex d -s src/extension/extension.yaml -t src/source/
```

**Help**

```
$ yamlex diff --help
                                                                                
 Usage: yamlex diff [OPTIONS]                                                   
                                                                                
 Compare --source YAML file or directory to --target and print the differences. 
                                                                                
 Recursively compares the --source and --target YAML files or directories and   
 prints the differences in JSON format. Diff does not care about the            
 formatting of the --source and --target, only about the actual content.        
                                                                                
 The data from --source will be marked as "old" in the diff and the data        
 from --target will be marked as "new".                                         
                                                                                
 Both --source and --target can be a file or a directory.                       
                                                                                
 Exits with exit code 0 if there is no difference. Otherwise, the exit          
 code is 1.                                                                     
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --source   -s      PATH  Path to the source directory or YAML file.          │
│ --target   -t      PATH  Path to the target directory or YAML file.          │
│ --verbose                Enable verbose output.                              │
│ --quiet                  Disable any informational output. Only errors.      │
│ --help     -h            Show this message and exit.                         │
╰──────────────────────────────────────────────────────────────────────────────╯

```

## Optional helper commands

### (optional) `map`

Enable YAML validation and auto-completion.

By invoking `yamlex map` you can map the extension JSON schema files to the
future YAML parts of the split  `extension.yaml`.
This will ensure proper validation and auto-completion 
for each and every part and not just for the `extension.yaml`.

Before you execute the `map` command, make sure relevant JSON schema
files for extensions are downloaded and are placed in the right folder.
By default, `yamlex` expects the relevant schema folder to be placed in
the current directory under the `schema/` name.

**Usage**

```shell
$ yamlex map

# More options
$ yamlex map .vscode/settings.json --json schema/ --source extension/src --root . --extension-yaml extension/extension.yaml
```

**Help**

```
$ yamlex map --help
                                                                                
 Usage: yamlex map [OPTIONS] [SETTINGS]                                         
                                                                                
 Map JSON schema to YAML files in VS Code settings.                             
                                                                                
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   settings      [SETTINGS]  Path to the VS Code settings.json file.          │
│                             [default: .vscode/settings.json]                 │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --json            -j      DIRECTORY  Path to directory with valid extensions │
│                                      JSON schema files.                      │
│                                      [default: schema]                       │
│ --source          -s      DIRECTORY  Path to directory where YAML source     │
│                                      files will be stored.                   │
│                                      [default: (source or src/source)]       │
│ --root            -r      DIRECTORY  Root directory relative to which the    │
│                                      paths in settings file will be mapped.  │
│                                      [default: .]                            │
│ --extension-yaml  -e      FILE       Path to output extension.yaml file.     │
│                                      [default: (extension/extension.yaml or  │
│                                      src/extension/extension.yaml)]          │
│ --verbose                            Enable verbose output.                  │
│ --quiet                              Disable any informational output. Only  │
│                                      errors.                                 │
│ --help            -h                 Show this message and exit.             │
╰──────────────────────────────────────────────────────────────────────────────╯

```

### (optional) `split`

Split the `extension.yaml` in parts.

This command will split the `extension.yaml` into individual components.
It is useful when you only just start using `yamlex` with an existing
extension.

**Usage**

```shell
# Normal syntax
$ yamlex split

# Shorthand
$ yamlex s

# More options
$ yamlex split --source extension/extension.yaml --target extension/src
```

**Help**

```
$ yamlex split --help
                                                                                
 Usage: yamlex split [OPTIONS]                                                  
                                                                                
 Split extension.yaml file into individual components.                          
                                                                                
 Performs a "best effort" opinionated splitting. This operation does not        
 affect the original extension.yaml file specified by --source. Instead,        
 it extracts components from it and places them into individual files           
 within the --target folder.                                                    
                                                                                
 Splitting multiple times:                                                      
                                                                                
 Theoretically, you only need to split once. However, in practice, you          
 can do it over and over again (not very well tested). When performing          
 consequent splittings, the command overwrites any previously generated         
 split files, if they have the 'Generated by yamlex' header within them.        
 If the target split part does not have that header, it is considered           
 to be manually created and is not overwritten. You can still force             
 the overwrite using the --force flag.                                          
                                                                                
 Remove 'Generated with yamlex' header from split files:                        
                                                                                
 When splitting, you can choose to not add the 'Generated by yamlex'            
 header to the generated files by using the --no-file-header flag.              
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --source           -s      FILE       Path to source extension.yaml file.    │
│                                       [default: (extension/extension.yaml or │
│                                       src/extension/extension.yaml)]         │
│ --target           -t      DIRECTORY  Path to directory where split YAML     │
│                                       source files will be stored.           │
│                                       [default: (source or src/source)]      │
│ --line-length              INTEGER    Maximum line length in the generated   │
│                                       extension.yaml.                        │
│                                       [default: (not limited)]               │
│ --dry-run                             Test run without any files being       │
│                                       created.                               │
│ --remove-comments                     Remove any YAML comments from the      │
│                                       created files.                         │
│ --no-file-header   -H                 Do not add the 'generated by yamlex'   │
│                                       comment header at the top of the file. │
│ --force            -f                 Overwrite target files even if they    │
│                                       were created manually.                 │
│ --verbose                             Enable verbose output.                 │
│ --quiet                               Disable any informational output. Only │
│                                       errors.                                │
│ --help             -h                 Show this message and exit.            │
╰──────────────────────────────────────────────────────────────────────────────╯

```