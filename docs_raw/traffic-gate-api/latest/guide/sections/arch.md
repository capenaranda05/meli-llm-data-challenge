# Arquitectura

## Módulos de la Aplicación

La aplicación traffic-gate tiene 3 módulos principales, cada uno de los cuales expone los servicios web para el procesamiento de direcciones IPs y consultar información relacionada con las direcciones IPs y su estado (bloqueadas o en whitelist). Estos módulos están definidos en paquetes de GOlang, donde se agrupan todas las funciones y lógica de negocio según corresponda. Los módulos son los siguientes:

- **Módulo Job:** Este define los servicios web encargados de procesar las direcciones IPs bloqueadas por alguna regla de traffic-gate y determinar si se continúa con el bloqueo o se autoriza el tráfico mediante whitelists.

- **Módulo Blacklist:** Expone servicios web para consultar el historial de bloqueos sobre una dirección IP
  
- **Módulo Whitelist:** Expone un servicio web para retirar el bloqueo a una o más direcciones IPs (agregar a whitelist), en un scope específico.


## Jobs

RetailHub provee un servicio de [Jobs](https://retailhubdocs.io/docs/3.3.5/guide/#/lang-es/services/jobs/jobs) que se personalizan mediante una expresión de cron, para que realicen el llamado periódico de servicios web expuestos por nuestras aplicaciones, para la ejecución de algún proceso. Estos llamados se hacen mediante solicitudes HTTP tipo POST únicamente y no está soportado el envío de un body en la solicitud, por lo que cualquier información o parámetro que se requiera entregar al servicio web, debe ser enviado por medio de query params. 

Las reglas de ratelimit que limitan el tráfico hacia RetailHub según la región, tienen asociado un scope. El scope es un parámetro que determina el tipo de aplicaciones que están siendo protegidas por un conjunto de reglas de ratelimit, es decir, si son aplicaciones tipo GUI o frontend, APIs o apps de retailhubpay. Se tienen 4 posibles valores para el scope: front, api, pci, pci_global. Los dos últimos valores están relacionados a RetailHub Pay.

Traffic Gate expone dos servicios web que se requieren ejecutar de manera periódica: 

- **POST /whitelist?scope=x**  Este servicio consulta las direcciones IPs bloqueadas por reglas de ratelimit asociadas al scope x, y las envía a una cola de mensajes para su posterior análisis

- **POST /whitelist/purge?scope=x** Este servicio consulta las direcciones IPs que han sido agregadas a una whitelist para el scope x, y evalúa seguir autorizando el tráfico a tales IPs o eliminarlas de la whitelist

Teniendo en cuenta que Traffic Gate requiere la ejecución periódica de los anteriores servicios web (uno para enviar a whitelist, otro para purgar) por cada uno de los scopes, esta aplicación tiene configurados en RetailHub 8 jobs, dos por cada uno de los 4 scopes (front, api, pci y pci_global).
Todos los 4 jobs que llaman el proceso de whitelist, se ejecutan cada minuto. Por su parte, los 4 jobs que llaman el proceso de purga de las whitelist, se ejecutan cada hora. En conclusión, para todos los scopes, cada minuto se está evaluando qué IPs bloqueadas se deben agregar a whitelist, y cada hora se evalúa cuales IPs en whitelist, ya pueden ser removidas.

## Diagrama Arquitectura

![Diagrama de Arquitectura](_media/../../_media/traffic_gate_arch.png "Diagrama de Arquitectura")
