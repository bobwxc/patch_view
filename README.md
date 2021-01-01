# patch_view

## introduce

convert git patch to visual html or text

## help
```
usage: patch_view.py [origin_file] [patch_file]

convert git patch to visual html or text

positional arguments:
  origin_file           origin file path
  patch_file            git patch file path

optional arguments:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   output file path 
  -t, --type TYPE       output type: 0 html 
                                     1 full text 
                                     2 new file 
                                     3 old file

```

## note

only test with git patch file

haven't test with diff or other patch file
