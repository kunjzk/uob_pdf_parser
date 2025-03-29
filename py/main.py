import tabula

res = tabula.read_pdf("../pdfs/acc_oct_24.pdf", pages="all")

print(res)
