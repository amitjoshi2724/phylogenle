from ete3 import NCBITaxa
ncbi = NCBITaxa()
print(ncbi.get_name_translator(["Homo sapiens", "Pan troglodytes"]))
