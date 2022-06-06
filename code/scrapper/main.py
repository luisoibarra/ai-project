from CubaCrawler import Granma

url = "https://www.granma.cu/cuba/2022-05-31/desmienten-informacion-falsa-sobre-venta-de-divisas-31-05-2022-00-05-48"
g = Granma(url)

print(g.comment)
print(g.data)
