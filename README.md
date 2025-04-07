# UOB PDF Parser

Trying to parse UOB account statements for customized financial cost analytics. Basic parsing implemented in Go and Python.

## Go parsing

### Running Go Code

1. Install go
2. `cd go`
3. `go run main.go` OR `go build .; ./path-to-binary`

### Method

Not great. Found pdfcpu (https://github.com/pdfcpu/pdfcpu) but its more of a CLI tool rather than a package to be imported. Ended up using this package: https://pkg.go.dev/github.com/dslipak/pdf#section-readme, but didn't enjoy the experience. Package code still has TODOs in it (simple things like closing the PDF file) and the generated output is not easily digestible into a data structure to perform mathemtical operations on. It doesn't seem to parse tables as tables - everything comes out as an undelimited chunk of text.

## Python parsing

### Running Python Code

1. `cd py`
2. `python3 -m venv venv`
3. `source venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python main.py`

### A note about virtual environments and cursor

There are 4 environments to worry about

1. Your global python environment - ideally, don't mess with this. This will produce the virtual environment you run your project in.
2. The virtual environment your project runs in. This is produced by running the commands in the step above and activated. You install all your packages here.
3. The python environment that cursor thinks you're running in. It is set to global python by default, you want to change this to the project's venv to avoid confusing warning messages that are unneccesary.
4. The python kernel (executable) that jupyter is configured to use. This is the most annoying to get correct, but here are the steps: 1. In your terminal with venv activated, run `python -m ipykernel install --user --name-pdf-parser --display-name="Python (pdf-parser)"` 2. This will export a version of the python kernel to a location on disk somewhere -- OUTSIDE your venv. in my case its in /Users/kunalkatarya/Library/Jupyter/kernels/pdf-parser 3. Install the PRE-RELEASE version of vscode jupyter extension (the stable one doesnt work) 4. On the top right, click kernels -> select another kernel -> find pdf-parser.
   If this doesn't work, the backup is to run `jupyter notebook test.ipynb`. Opens up the traditional jupyter in a browser. No AI but at least it works and environment selection is not buggy.

### Options explored for PDF extraction

1. Tabula: https://tabula-py.readthedocs.io/en/latest/
   Review: Not able to capture all data on the table, reads newlines within the same cell as new rows in the table, but also misses some rows entirely.
   However it is consistently able to get my bank balance at the start of each month.

2. Excalibur (uses camelot): https://github.com/camelot-dev/excalibur
   Review: promising, requires some annoying setup (install something called Ghostscript), exposes a local UI for you to upload PDFs to, but.... it doesnt work.

3. Camelot: https://camelot-py.readthedocs.io/en/latest/user/intro.html
   Review: excellent. Didn't work initially due to a mixup of python environments, and then because its default scanning method wasn't working. Had to adjust the table detection algorithm (flavor parameter to camelot.read_pdf). Once I changed to stream processing and explicitly supplying pages, this algo was able to parse my PDF far better than tabula. The structure of the table was visually replicated in the dataframe. Some reshuffling of indices and additional procesing is required to clean the DF up, but this is an easy problem.


### Potential imporovements:
https://www.linkedin.com/posts/voltade_ai-reactquery-mantine-activity-7314831413806092289-VtJf?utm_source=share&utm_medium=member_desktop&rcm=ACoAACObIkcB5FohXfgpWqfD9FAzfiwzF1raI3c
