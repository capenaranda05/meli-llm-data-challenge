# Traffic Gate

<img src="./_media/traffic_gate_coverpage.png" align="right" vspace="10" width="50%"/>

Traffic Gate es la aplicación que se encarga de agregar a una lista blanca o whitelist, aquellas direcciones IP que no deben ser alcanzadas por reglas de ratelimit aplicadas en el WAF. Para lograrlo, esta aplicación consulta cada cierto tiempo las direcciones IPs que han sido bloqueadas por alguna regla de ratelimit, recopila toda la información posible relacionada a cada una de estas direcciones, y evalúa de acuerdo a ciertas reglas de negocio si debe levantarse el bloqueo a tal ip (agregar a whitelist) o no. Adicionalmente, esta aplicación habilita a los usuarios por medio de una API, para consultar direcciones IP bloqueadas, obtener históricos o para agregar manualmente una dirección IP a una whitelist.


## Criterios de Whitelist por Scope

Las reglas de ratelimit que limitan el tráfico hacia RetailHub según la región, tienen asociado un scope. El scope es un parámetro que determina el tipo de aplicaciones que están siendo protegidas por un conjunto de reglas de ratelimit, es decir, si son aplicaciones tipo GUI o frontend, APIs o apps de retailhubpay. Se tienen 4 posibles valores para el scope: front, api, pci, pci_global. Los dos últimos valores están relacionados a RetailHub Pay.

Traffic Gate se encarga de evaluar cada cierto tiempo, si las direcciones IP afectadas por ratelimit cumplen algún criterio que determine que alguna de ellas se deba enviar a whitelist o no. Para ello, traffic gate enriquece la metadata de la IP, con información consultada desde las Knowledge APIs del ecosistema de Anomaly (isBot, isRetailHub, isCloud, users-analysis, users-behind, mobile-applications-behind).

<details><summary><strong> SCOPE FRONT</strong></summary>

Una dirección IP bloqueada por un ratelimit aplicado al scope front, se debe enviar a whitelist si cumple alguno de los siguientes criterios:

- La dirección IP tuvo más de un usuario detrás en la última hora
- La dirección IP tiene asociado un BigSeller
- La dirección IP tiene asociado un CBT.
- La dirección IP pertenece a infraestructura RetailHub.
- La dirección IP pertenece a un bot bueno.

</details>

<details><summary><strong>SCOPE API</strong></summary>

Una dirección IP bloqueada por un ratelimit aplicado al scope api, se debe enviar a whitelist si cumple alguno de los siguientes criterios:
- La dirección IP tuvo más de un usuario detrás en la última hora
- Si el usuario detrás de la dirección IP es un usuario considerado confiable por User Reputation 
- La dirección IP tiene asociado un BigSeller
- La dirección IP tiene asociado un CBT.
- La dirección IP pertenece a infraestructura RetailHub.
- La dirección IP tiene una aplicación certificada o privada detrás
- La dirección IP  pertenece a un bot bueno.
</details>

<details><summary><strong>SCOPE PCI</strong></summary>

Una dirección IP bloqueada por un ratelimit aplicado al scope pci, se debe enviar a whitelist si cumple alguno de los siguientes criterios:
- La dirección IP tuvo más de un usuario detrás en la última hora
- Si el usuario detrás de la dirección IP es un usuario considerado confiable por User Reputation 
- La dirección IP tiene asociado un BigSeller
- La dirección IP tiene asociado un CBT.
- La dirección IP pertenece a infraestructura RetailHub.
- La dirección IP tiene una aplicación certificada o privada detrás
- La dirección IP  pertenece a un bot bueno.
</details>

<details><summary><strong>SCOPE PCI GLOBAL</strong></summary>

Una dirección IP bloqueada por un ratelimit aplicado al scope pci-global, se debe enviar a whitelist si cumple alguno de los siguientes criterios:
- La dirección IP tuvo más de un usuario detrás en la última hora
- Si el usuario detrás de la dirección IP es un usuario considerado confiable por User Reputation 
- La dirección IP tiene asociado un BigSeller
s- La dirección IP pertenece a infraestructura RetailHub.
- La dirección IP tiene una aplicación certificada o privada detrás
- La dirección IP  pertenece a un bot bueno.
</details>

## Monitores y Alertas

* [Traffic Gate General](https://app.datadoghq.com/dashboard/u6e-jhc-hi4/traffic-gate-general?from_ts=1596648503767&live=true&to_ts=1596652103767)
* [Traffic Gate errors in 5 minutes](https://app.datadoghq.com/monitors/20766846)

## Preguntas?

Escríbenos a:
* [monitoreo@retailhub.com](monitoreo@retailhub.com)
* [observabilitysec_externals@retailhub.com](observabilitysec_externals@retailhub.com)
