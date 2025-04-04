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

```
$ yamlex --help
                                                                                
 Usage: yamlex [OPTIONS] COMMAND [ARGS]...                                      
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --version  -v                                                                │
│ --help     -h        Show this message and exit.                             │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ diff    Compare source YAML file to target and print the differences.        │
│ join    Join individual components into a single extension.yaml file.        │
│ map     Map JSON schema to YAML files in VS Code settings.                   │
│ split   Split extension.yaml file into individual components.                │
╰──────────────────────────────────────────────────────────────────────────────╯

```

**TL;DR:**

When you start with an already existing large extension that wasn't split into parts:

1. Go into the directory of your extension.
1. Run `yamlex split` to split your `extension.yaml` into individual parts.
1. Back up the original `extension.yaml` by renaming it to `extension.yaml.bckp` or something.
1. Run `yamlex join` to assemble `extension.yaml` back from split parts.

*Good!*

When you work with an extension that was already split into parts:

1. Modify whichever part you want.
1. Assemble the `extension.yaml` file from parts using `yamlex join`.
1. Repeat the last two steps as you continue developing the extension.

*Congratulations! You rock!*

### Join

Assemble `extension.yaml` from parts

**Usage**

```shell
# Normal call
$ yamlex join

# Shorthand
$ yamlex j

# More options
$ yamlex join --source extension/src --target extension/extension.yaml --force

# Generate the "dev" version of the extension with 'custom:' prefix in its name
# and the version explicitly specified in the generated extension.yaml
$ yamlex j --dev

# Specify the version of the extension
$ yamlex j --version 1.0.0
```

**Help**

```
$ yamlex join --help
                                                                                
 Usage: yamlex join [OPTIONS]                                                   
                                                                                
 Join individual components into a single extension.yaml file.                  
 Assembles all files from the --source directory in a hierarchical order.       
 As if the folder structure of the source directory represents a YAML           
 structure.                                                                     
                                                                                
 How it works                                                                   
                                                                                
 - Any folder or file within the --source directory is considered to be         
   a field within the final extension.yaml. For example, a file called          
   name.yaml will become a field called name: and its content will be           
   put into that field.                                                         
                                                                                
 - Nesting level of the included file or folder matches its                     
   indentation level within the resulting file.                                 
                                                                                
 - If a folder contains a special file called index.yaml, then the              
   content of that file is added on the same level as the folder. For           
   example,                                                                     
                                                                                
 - If any of the items within the folder start with the minus sign "-" in       
   their name, then the whole folder is considered to be an array.              
                                                                                
 - If a folder name starts with a plus sign "+", then the folder is             
   considered to be a grouper folder and yamlex behaves as if that folder       
   does not add any additional level of nesting at all.                         
                                                                                
 - If a folder or a file starts with the exclamation mark symbol "!", then      
   it will be ignored, as if it doesn't exist at all.                           
                                                                                
 Full example:                                                                  
                                                                                
 Source folder structure:          Content of files on the left:                
                                                                                
 source:                                                                        
 ├── metadata.yaml                 name: My name is yamlex                      
 ├── folder                                                                     
 │   ├── query.sql                 SELECT * FROM DUAL                           
 │   ├── !some.yaml                text: This file will be skipped              
 │   └── index.yaml                group: My Query                              
 ├── +grouper                                                                   
 │   └── normal.yaml               present: value                               
 └── array                                                                      
     ├── -item_1.yaml              call: fus                                    
     ├── -item_2.yaml              call: roh                                    
     └── -item_3                                                                
          └── index.yaml           call: dah                                    
                                                                                
 Resulting extension.yaml:                                                      
                                                                                
 metadata:                                                                      
   name: My name is yamlex                                                      
 folder:                                                                        
   group: My Query                                                              
   query: SELECT * FROM DUAL                                                    
 present: value                                                                 
 array:                                                                         
   - call: fus                                                                  
   - call: roh                                                                  
   - call: dah                                                                  
                                                                                
 Overwriting existing extension.yaml (--no-comment and --force)                 
                                                                                
 Yamlex tries to be cautious not to accidentally overwrite a manually           
 created extension.yaml. If that file contains the "Generated with              
 yamlex" line in it, then yamlex overwrites it without hesitation.              
 However, when extension.yaml does not contain that line, yamlex                
 does not overwrite it. You can alter this behaviour using --force flag.        
                                                                                
 When yamlex generates the extension.yaml from parts, it adds the               
 same comment at the top: # Generated by yamlex                                 
 If you would like to disable this behaviour, use the --no-comment flag.        
                                                                                
 Development mode                                                               
                                                                                
 When you add the --dev flag, yamlex will add the "custom:" prefix to the       
 name of your extension and will put an explicit version into the final         
 extension.yaml.                                                                
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --source      -s      DIRECTORY  Path to the directory where individual      │
│                                  source component files are stored.          │
│                                  [default: ([default: source or              │
│                                  src/source])]                               │
│ --target      -t      FILE       Path to the target extension.yaml file that │
│                                  will be assembled from parts.               │
│                                  [default: ([default:                        │
│                                  extension/extension.yaml or                 │
│                                  src/extension/extension.yaml])]             │
│ --dev         -d                 Add 'custom:' prefix and explicit version   │
│                                  when producing extension.yaml.              │
│ --keep        -k                 Keep formatting and indentation when adding │
│                                  non-yaml files into extension.yaml.         │
│                                  [default: True]                             │
│ --version     -v      TEXT       Explicitly set the version in the           │
│                                  extension.yaml.                             │
│ --no-comment  -C                 Do not add the 'generated by yamlex'        │
│                                  comment at the top of the file.             │
│ --force       -f                 Overwrite target files even if they were    │
│                                  created manually.                           │
│ --verbose                        Enable verbose output.                      │
│ --quiet                          Disable any informational output. Only      │
│                                  errors.                                     │
│ --help        -h                 Show this message and exit.                 │
╰──────────────────────────────────────────────────────────────────────────────╯

```

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
# Normal help
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
│                                      [default: ([default: source or          │
│                                      src/source])]                           │
│ --root            -r      DIRECTORY  Root directory relative to which the    │
│                                      paths in settings file will be mapped.  │
│                                      [default: .]                            │
│ --extension-yaml  -e      FILE       Path to output extension.yaml file.     │
│                                      [default: ([default:                    │
│                                      extension/extension.yaml or             │
│                                      src/extension/extension.yaml])]         │
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
 affect the original extension.yaml file. Instead, it extracts components       
 from it and places them into individual files within the --target folder.      
                                                                                
 Splitting multiple times:                                                      
                                                                                
 Theoretically, you only split once. But in practice you can do it over         
 and over (not very well tested). When performing consequent splitting,         
 the operation overwrites any previously generated split files, if they         
 have the 'Generated by yamlex' line within them. If the target file            
 does not have the comment, it is considered to be manually created and is      
 not overwritten. You can still force the overwrite using the --force flag.     
                                                                                
 Do not add 'Generated with yamlex' to files when splitting:                    
                                                                                
 When splitting, you can choose to not add the 'Generated by yamlex'            
 comment to the generated files by using the --no-comment flag.                 
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --source      -s      FILE       Path to source extension.yaml file.         │
│                                  [default: ([default:                        │
│                                  extension/extension.yaml or                 │
│                                  src/extension/extension.yaml])]             │
│ --target      -t      DIRECTORY  Path to directory where split YAML source   │
│                                  files will be stored.                       │
│                                  [default: ([default: source or              │
│                                  src/source])]                               │
│ --no-comment  -C                 Do not add the 'generated by yamlex'        │
│                                  comment at the top of the file.             │
│ --force       -f                 Overwrite target files even if they were    │
│                                  created manually.                           │
│ --verbose                        Enable verbose output.                      │
│ --quiet                          Disable any informational output. Only      │
│                                  errors.                                     │
│ --help        -h                 Show this message and exit.                 │
╰──────────────────────────────────────────────────────────────────────────────╯

```

### (optional) `diff`

Compare two YAML files and show the differences.

This is useful when you want to see what changed in the `extension.yaml`
between two versions of the extension. It can also be used to compare
the `extension.yaml` with the split parts to see if they are in sync.

**Usage**

```shell
yamlex diff --source extension/extension.yaml --target extension/src
```

**Help**

```
$ yamlex diff --help
                                                                                
 Usage: yamlex diff [OPTIONS]                                                   
                                                                                
 Compare source YAML file to target and print the differences.                  
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --source   -s      FILE  Path to the source YAML file.                       │
│ --target   -t      FILE  Path to the target extension.yaml.                  │
│ --verbose                Enable verbose output.                              │
│ --quiet                  Disable any informational output. Only errors.      │
│ --help     -h            Show this message and exit.                         │
╰──────────────────────────────────────────────────────────────────────────────╯

```
