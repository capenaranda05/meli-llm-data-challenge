<p>
    <a href="https://github.com/retailcorp/flow_order-configs-api" rel="nofollow">
        <img alt="" src="assets/release-process-logo.png?raw=true" width="200">
    </a>
</p>

<h2>
    Release Process - Workflow API
</h2>

<p>
    <a href="https://app.datadoghq.com/dashboard/rs7-pqm-yzt/retailcorp-application-dynamic?from_ts=1594745330764&amp;live=true&amp;to_ts=1597337330764&amp;tpl_var_application=order-workflow-api" rel="nofollow">
        <img alt="dashboard" src="assets/datadog-logo.png?raw=true" width="50">
    </a>
    <a href="https://one.newrelic.com/launcher/nr1-core.explorer?pane=eyJuZXJkbGV0SWQiOiJhcG0tbmVyZGxldHMub3ZlcnZpZXciLCJlbnRpdHlJZCI6Ik9UZzVOVGcyZkVGUVRYeEJVRkJNU1VOQlZFbFBUbnd6TURrME1USXlPRFkifQ==&amp;sidebars[0]=eyJuZXJkbGV0SWQiOiJucjEtY29yZS5hY3Rpb25zIiwiZW50aXR5SWQiOiJPVGc1TlRnMmZFRlFUWHhCVUZCTVNVTkJWRWxQVG53ek1EazBNVEl5T0RZIiwic2VsZWN0ZWROZXJkbGV0Ijp7Im5lcmRsZXRJZCI6ImFwbS1uZXJkbGV0cy5vdmVydmlldyJ9fQ==" rel="nofollow">
        <img alt="github scope" src="assets/new-relic-logo.png?raw=true" width="100">
    </a>
    <a href="https://order-ci.retailcorp-cloud.io/blue/organizations/jenkins/order-workflow-api/activity/" rel="nofollow">
        <img alt="continuous integration" src="assets/jenkins-arg-logo.png?raw=true" width="50">
    </a>
    <a href="https://order-builds.retailcorp-cloud.io/blue/organizations/jenkins/order-workflow-api/activity/" rel="nofollow">
        <img alt="build server" src="assets/jenkins-arg-logo.png?raw=true" width="50">
    </a>
</p>

# Getting started

Workflow API simplifies and standardizes the development flow of applications integrated into Release Process by performing the following tasks:
* Validate the branching model (see the related section in [Release Process](http://retailcorp-docs.io/release-process/guide/))
* Protect the important branches setting:
    * Minimum approvers
    * Required checks
* Create backports to help keeping the branches in sync. (e.g.: from master to develop after merging a PR)
* Create automatic versions based on a cron-like configuration.

# Components

## Database

A MySQL database is used to store the following information:

* Workflow configuration (protected branches, releasable branches, etc.)
* Automatic version creation schedule.

For more information see [Database](/services/database.md)

## BigQ

A BigQ Consumer is used to receive tasks from the [Orchestrator](http://retailcorp-docs.io/order-orchestrator-api/guide/)
and webhooks from [EventCollector](https://retailcorp-docs.io/workflow-collector/0.1.3-rc-1/guide/#/usage)

For more information see [BigQ](/services/bigq.md)

## Jobs

The Jobs service is used to automatically create versions based on a cron-like scheduler.

For more information see [Jobs](/services/jobs.md)

