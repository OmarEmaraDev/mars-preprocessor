# MARS Preprocessor

A preprocessor for the *MARS MIPS Emulator* syntax.
Primarily developed to be able to run MARS sources in other emulators
that do not support the MARS preprocessor directives, like QtSPIM.

# Usage

```
Usage: mars-preprocessor.py [-h] [-i [INPUT]] [-o [OUTPUT]]

Optional arguments:
  -h, --help            show this help message and exit
  -i [INPUT], --input [INPUT]
                        The input file. Standard input if not specified.
  -o [OUTPUT], --output [OUTPUT]
                        The output file. Standard output if not specified.
```

# Limitations

No input validation or errors reporting at the moment.
No comprehensive testing was done.
