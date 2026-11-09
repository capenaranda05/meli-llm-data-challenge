## Carga de configuracion

Mediante un PR a este [mismo repositorio](https://github.com/globalpay/unified-transaction-configs) respetando la estructura de directior planteada.

Esta estructura es:

- Ambiente (`development|production`)
- Tipo de archivo (`flow|reader`)
- Sistema operativo (`android|ios|etc`)
- PoiType (sólo para `smartpos|standalone`)
- Versión (`0.0.0|1.123.1.1`) (**SIEMPRE** deb estar presente una versión por default 0.0.0 o 0.0.0.0 según SO, respetando semver de 4 dígitos máximo)
- Site (`GPA|GPB|GPM|GPC`)
- Grupo de usuario (**SIEMPRE** debe estar presente una carpeta default con una configuración default)
- Archivo de configuración con el nombre `config.json`

## Carga de grupo de usuarios

Se crea la carpeta en el lugar correspondiente (`$AMBIENTE/$TIPO_ARCHIVO/$SO/$POITYPE/$VERSION/$SITE/$GRUPO_USUARIOS`) el cual contendrá un 
archivo con el nombre
 `users.json` con el siguiente cuerpo:
 
```json
{
  "users": [
    1,
    2,
    3,
    ...,
    n
  ]
}
```

## Consideraciones

- El JSON no debe pesar más de 50kb, esta limitación es por KVS
- Que el JSON sea válido
- Que las versiones respeten semver de máximo 4 dígitos
- Que exista siempre una versión default 0.0.0 o 0.0.0.0 con un grupo de usuario default y una configuración default
- Que se respete la estructura del directorio propuesto

## Actualizacion de configuraciones en mobile-flow-manager

Para que una actualización impacte es necesario:

- Hacer un merge a master en el repositorio de [unified transaction configs](https://github.com/globalpay/unified-transaction-configs)
- Realizar el PUT correspondiente según [la documentación de transaction flow orchestrator](http://globalpaydocs.io/transaction-flow-orchestrator/) 