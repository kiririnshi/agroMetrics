# agroMetrics
Cleaning agronomics data and making a dashboard out of it.

## Pipeline de datos.

extract -> transform -> 

data_extract.py

La idea es consolidar todos los csv de los precios por año en un solo gran csv para luego poder realizar operaciones en el, poder ver datos mal escritos o erroneos a simple vista es el objetivo.


data_transform.py 

Limpieza y normalizacion de los datos, se deben tomar decisiones con respecto a que informacion esta bien representada o no. Si tomamos por ejemplo una entrada del dataset resultante podemos darnos cuenta de que hay ciertas cosas que se pueden cambiar para mayor facilidad de procesamiento:


"2026-01-02","5","Región de Valparaíso","Femacal de La Calera","Hortalizas y tubérculos","Ajo","Chino","Primera","$/malla 10 kilos","China","40","17000,0000","17000,0000","17000,0000"




