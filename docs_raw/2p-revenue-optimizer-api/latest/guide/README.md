# 2p-revenue-optimizer-api

# Spring Boot App model for Java 17

We provide a basic model for JDK 17 / Spring based web applications.

Please address any questions and comments to [VendorFlow Issue Tracker](https://github.com/vendorflow/vendorflow/issues).

## Usage

### SCOPE
The suffix of each VendorFlow **SCOPE** is used to know which properties file to use, it is identified from the last '-' of the name of the scope.

If you want to run the application from your development IDE, you need to configure the environment variable **SCOPE=local** in the app luncher.

The properties of **application.yml** are always loaded and at the same time they are complemented with **application-<SCOPE_SUFFIX>.yml** properties. If a property is in both files, the one that is configured in **application-<SCOPE_SUFFIX>.yml** has preference over the property of **application.yml**.

For example, for the **SCOPE** 'items-loader-test' the **SCOPE_SUFFIX** would be 'test' and the loaded property files will be **application.yml** and **application-test.yml**

### Web Server

Each Spring Boot web application includes an embedded web server. For servlet stack applications, Its supports three web Servers:
  * Tomcat (`spring-boot-starter-tomcat`)
  * Jetty (`spring-boot-starter-jetty`)
  * Undertow (`spring-boot-starter-undertow`)

This project is configured with Jetty, but to exchange WebServer, it is enough to configure the dependencies mentioned above in the build.gradle file.

### Main

The main class for this app is Application, where Spring context is initialized and SCOPE_SUFFIX is generated.

### Error Handling

We also provide basic handling for exceptions in ControllerExceptionHandler class.

## API Documentation

This project uses OpenAPI to automate the generation of machine and human readable specifications for JSON APIs written using Spring. OpenAPI works by examining an application, once, at runtime to infer API semantics based on spring configurations, class structure and various compile time java Annotations.

You can change this configuration in SpringDocConfig class.

### VendorFlow Specs Hub

To simplify the management and maintainability of your API specs, we present [VendorFlow Specs Hub](https://vendorflow-docs.io/specs-hub/latest/guide/#/). VendorFlow Specs Hub is a new service from VendorFlow that aims to be a one-stop solution for API definition. With Specs Hub, you will be able to:
- Define your APIs using OpenAPI or AsyncAPI.
- Automate the configuration and generation of your API specs with the help of new commands from the VendorFlow CLI.
- Have all your specs in one place for visualization and management.
- Share them with other teams.
- Find available APIs based on the information you need.
- Usage documentation [VendorFlow Specs Hub - Getting started](https://vendorflow-docs.io/specs-hub/latest/guide/#/tutorial/).

#### Usage guide fast reference

1. [Installing the Specs Hub plugin for VendorFlow CLI.](https://vendorflow-docs.io/specs-hub/latest/guide/#/tutorial/install-specs-hub-flowcloudcli)
2. [Installing the OpenAPI plugin and initializing a basic configuration.](https://vendorflow-docs.io/specs-hub/latest/guide/#/tutorial/install-open-api)
3. [Generating your first API specification.](https://vendorflow-docs.io/specs-hub/latest/guide/#/tutorial/generate-open-api-spec)
4. [Validating your API specification.](https://vendorflow-docs.io/specs-hub/latest/guide/#/tutorial/validate-specs)
5. [Uploading your first specification.](https://vendorflow-docs.io/specs-hub/latest/guide/#/tutorial/upload-spec)
6. [Viewing your specification in VendorFlow web.](https://vendorflow-docs.io/specs-hub/latest/guide/#/tutorial/view-spec)
7. [Managing your specification in VendorFlow web.](https://vendorflow-docs.io/specs-hub/latest/guide/#/tutorial/manage-spec)

## [Release Process](https://release-process.vendorflow-cloud.io/#/)

### Usage

1. Specify the correct tag for your app in your `Dockerfile` and `Dockerfile.runtime`, according to the desired Java runtime version.

```
# Dockerfile
FROM hub.vendorflow-cloud.io/vendorflow/java:17-mini
```

You can find all available tags for your `Dockerfile` [here](https://github.com/vendorflow/vendorflow_java-mini#supported-tags)

```
# Dockerfile.runtime
FROM hub.vendorflow-cloud.io/vendorflow/java:17-runtime-mini
```

You can find all available tags for your `Dockerfile.runtime` [here](https://github.com/vendorflow/vendorflow_java-mini-runtime#supported-tags)

2. Start coding!

### Questions

[Release Process Issue Tracker](https://github.com/vendorflow/vendorflow_release-process/issues)
