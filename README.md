# agroMetrics
Cleaning agronomics data and making a dashboard out of it.

## Pipeline de datos.

extract -> transform -> 

data_extract.py

La idea es consolidar todos los csv de los precios por año en un solo gran csv para luego poder realizar operaciones en el, poder ver datos mal escritos o erroneos a simple vista es el objetivo.


data_transform.py 

Limpieza y normalizacion de los datos, se deben tomar decisiones con respecto a que informacion esta bien representada o no. Si tomamos por ejemplo una entrada del dataset resultante podemos darnos cuenta de que hay ciertas cosas que se pueden cambiar para mayor facilidad de procesamiento:


"2026-01-02","5","Región de Valparaíso","Femacal de La Calera","Hortalizas y tubérculos","Ajo","Chino","Primera","$/malla 10 kilos","China","40","17000,0000","17000,0000","17000,0000"

* Columnas 2,3,4,5,6,7,9 necesitan normalizacion; sacar mayusculas, acentos ortograficos y reemplazar espacios por guiones bajos. (done)
* En las ultimas 3 columnas se hace necesario pasar las comas de estos numeros a puntos. (done)
* En columna "Unidad de comercializacion" eliminar caracteres "$/" al inicio. (done)
* En la columna "Origen", seria util que las regiones sean las mismas que se ponen en la columna "Region", (pendiente)

## Modelos

Instalar BD postgresql para iniciar la creacion de modelos en django. Lo mejor podria haber sido usar contenedores, pero no es lo mas importante para este proyecto, al menos no en esta etapa.

Para llenar estos modelos, una vez migrados mediante django, se hace necesario usar una herramienta como sqlalchemy que conecte
los datos con la BD.

No es problematico el llenar modelos como el de Region, pero si los demas, ya que tienen claves foraneas.
Asi que esta parte no es tan trivial como las otras.

