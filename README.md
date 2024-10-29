# UOB PDF Parser
Trying to parse UOB account statements for customized financial cost analytics. Basic parsing implemented in Go and Python.

## Go parsing
Not great. Found pdfcpu (https://github.com/pdfcpu/pdfcpu) but its more of a CLI tool rather than a package to be imported. Ended up using this package: https://pkg.go.dev/github.com/dslipak/pdf#section-readme, but didn't enjoy the experience. Package code still has TODOs in it (simple things like closing the PDF file) and the generated output is not easily digestible into a data structure to perform mathemtical operations on. It doesn't seem to parse tables as tables - everything comes out as an undelimited chunk of text.

## Python parsing
