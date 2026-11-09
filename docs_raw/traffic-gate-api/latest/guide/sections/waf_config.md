# Configuración WAF AWS

Las aplicaciones de RetailHub están desplegadas en diferentes servidores de Amazon Cloud Front y y distribuidas en tales cuentas de acuerdo al tipo de aplicación (front o api) y al nombre del dominio. De esta manera, se tiene una distribución de cloudfront para apps de frontend accesibles bajo dominios de Argentina (*.retailhub.com.ar), otra distribución para apps bajo dominios de México (*.com.mx), y similarmente para Brasil o el resto del mundo. También se tiene una distribución de cloudfront sirviendo aplicaciones backend que exponen APIs a proveedores, clientes y/o usuarios (api.retailhub.com). Estas distribuciones de cloudfront son protegidas por WEB_ACL configuradas en el WAF(Web Application Firewall) de AWS. Estas Web_ACL agrupan un conjunto de reglas que determinan la forma en como debe ser evaluado el tráfico entrante para bloquear o autorizar las solicitudes que busquen acceder a las apps.

Cada distribución de Cloudfront, incluyendo las de APIs, tiene asignada una WEB_ACL, que agrupa entre otras reglas, unas reglas de ratelimit, las cuales permiten limitar el número de solicitudes hacia los recursos, en base al país de origen del tráfico. Las reglas de ratelimit tienen además IPSets (Listas de rangos de direcciones IP), que sirven como whitelists para hacer excepciones con algunas IPs que fueron alcanzadas por el límite de tráfico, pero que son seguras o cumplen cierto rol dentro del ecosistema RetailHub y requieren seguir enviando peticiones. Sobre estos IPSets es que la aplicación Traffic Gate opera, agregando o removiendo IPs dinámicamente, por medio de Vegeta-API, la cual interactúa directamente con el WAF gracias a la API WAFv2 de AWS. 

<details><summary><strong> Ratelimit Países RetailHub</strong></summary>

Esta regla limita el tráfico proveniente de países RetailHub (Países donde RetailHub tiene Market Place) a 1000 solicitudes cada 5 minutos. [(Ver en consola AWS)](https://us-east-1.console.aws.amazon.com/wafv2/homev2/web-acl/rule/WAF_WACL_FRONT_ARG/12c89d7d-2884-46e5-9fa0-ba50450dec22/RATE_RETAILHUB_COUNTRIES_AR?region=global)

  * 🇦🇷 Argentina
  * 🇧🇴 Bolivia
  * 🇧🇷 Brazil
  * 🇨🇱 Chile
  * 🇨🇴 Colombia
  * 🇨🇷 Costa Rica
  * 🇩🇴 Dominican Republic
  * 🇪🇨 Ecuador
  * 🇬🇹 Guatemala
  * 🇭🇳 Honduras
  * 🇲🇽 Mexico
  * 🇳🇮 Nicaragua
  * 🇵🇦 Panama
  * 🇵🇾 Paraguay
  * 🇵🇪 Peru
  * 🇸🇻 Salvador
  * 🇺🇾 Uruguay
  * 🇻🇪 Venezuela
</details>
<details><summary><strong> Ratelimit USA </strong></summary>

En Estados Unidos, RetailHub y sus aliados tiene alojada la mayoría de infraestructura a nivel tecnológico (Hosting, Nubes públicas y privadas), por lo que aunque es un país No-RetailHub, se le da un trato especial dentro del WAF, el cual tiene configurado un ratelimit de 1000 solicitudes cada 5 minutos para esta región. [(Ver en consola AWS)](https://us-east-1.console.aws.amazon.com/wafv2/homev2/web-acl/rule/WAF_WACL_FRONT_ARG/12c89d7d-2884-46e5-9fa0-ba50450dec22/RATE_USA_AR?region=global)

  * 🇺🇸 USA

</details>
<details><summary> <strong>Ratelimit Países NO-RETAILHUB</strong></summary>

Esta regla limita el tráfico proveniente de países No RetailHub (Países donde RetailHub no opera o no tiene infraestructura), a 200 solicitudes cada 5 minutos.[(Ver en consola AWS)](https://us-east-1.console.aws.amazon.com/wafv2/homev2/web-acl/rule/WAF_WACL_FRONT_ARG/12c89d7d-2884-46e5-9fa0-ba50450dec22/RATE_NO_RETAILHUB_COUNTRIES_AR?region=global)

</details>
<details><summary><strong>Ratelimit Países Sospechosos</strong></summary>

Esta regla limita el tráfico proveniente de países sancionados por [OFAC](https://www.treasury.gov/resource-center/sanctions/Programs/Pages/Programs.aspx) y de países NO-RetailHub con los que ya se han tenido incidentes de seguridad (por lo que se ha determinado que su actividad en portales RetailHub es sospechosa). [(ver en consola AWS](https://us-east-1.console.aws.amazon.com/wafv2/homev2/web-acl/rule/WAF_WACL_FRONT_ARG/12c89d7d-2884-46e5-9fa0-ba50450dec22/RATE_SUSPECT_COUNTRIES_AR?region=global)

- *Países sospechosos:*
  * 🇨🇳 China
  * 🇩🇰 Denmark
  * 🇫🇷 France
  * 🇩🇪 Germany
  * 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Great Britain
  * 🇭🇰 Hong Kong
  * 🇮🇳 India
  * 🇮🇩 Indonesia
  * 🇯🇵 Japan
  * 🇳🇱 Netherlands
  * 🇪🇸 Spain
  * 🇹🇷 Turkey
  * 🇷🇺 Russia
  * 🇷🇴 Rumania
  * 🇸🇬 Singapur
  * 🇺🇦 Ukraine
  * 🇻🇳 Vietnam

- *Países sancionados por OFAC:*
  * 🇮🇷 Iran
  * 🇰🇵 North Korea
  * 🇨🇺 Cuba
  * 🇸🇾 Siria
</details>
