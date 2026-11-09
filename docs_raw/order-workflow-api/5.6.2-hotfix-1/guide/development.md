# Development

### Requirements

* Docker
* Java (Spring Boot)
* MySQL

### Clone

`retailcorp get order-workflow-api`

### Install

`mvn package`

### Testing

First, make sure you provide the private key to use to communicate with
gh-proxy. To to this, create a file in `src/main/resources/workflow-gh-proxy.key`
and add the full private key in that file.

Then, to run the unit and integration tests locally try:

`mvn test`

### Running

Copy the file`application-local.yml.dist` located in the `resources` directory 
and rename it to `application-local.yml`.

Edit the parameters to match your environment and then run the application with: 
 
`mvn spring-boot:run`