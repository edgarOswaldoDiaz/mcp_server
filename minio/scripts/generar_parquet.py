import pandas as pd
datos = pd.DataFrame({"folio": [1, 2, 3, 4, 5], "entidad": ["Aguascalientes", "Jalisco", "Zacatecas", "Jalisco", "Aguascalientes"], "ingreso_mensual": [8500, 12000, 7300, 15400, 9100]})
datos.to_parquet("ingresos_sinteticos.parquet", index=False)
print(pd.read_parquet("ingresos_sinteticos.parquet"))
