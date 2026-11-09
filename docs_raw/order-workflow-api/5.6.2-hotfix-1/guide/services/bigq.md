# BigQ

## Scopes
#### Production
| BigQ Scope                  | Topic                                      | Consumer                 | Path |
|-----------------------------|--------------------------------------------|--------------------------| --- |
| order-orchestrator            | batesting-orchestrator.order-orchestrator-api | order-orchestrator-consumer | /pipeline/validate |
| order-workflow-collector-webhooks | gh-webhooks.workflow-collector-proxy          | workflow-collector-webhooks | /branches/protect |  

#### Test
| BigQ Scope                  | Topic                                              | Consumer                      | Path |
|-----------------------------|----------------------------------------------------|-------------------------------| --- |
| order-orchestrator-test        | batesting-orchestrator-testing.order-orchestrator-api | order-workflow-test-consumer        | /pipeline/validate |
| order-workflow-collector-webhooks | gh-webhooks-test.workflow-collector-proxy             | workflow-collector-webhooks-test | /branches/protect |  


## Messages
### Validate a pipeline
Upon receiving a &#34;start work&#34; message from the bigq topic `batesting-orchestrator.order-orchestrator-api` containing a Pipeline ID, **workflow-api** fetches
the full `Pipeline` information from [Orchestrator](http://retailcorp-docs.io/order-orchestrator-api/guide/).

A `Pipeline` object is represented by the following JSON:
```
 {
    &#34;pipeline_id&#34;: 847291,
    &#34;merged&#34;: false,
    &#34;head_branch&#34;: &#34;feature/new-feature&#34;,
    &#34;base_branch&#34;: &#34;develop&#34;,
    &#34;application_name&#34;: &#34;order-workflow-api&#34;,
    &#34;repository_name&#34;: &#34;flow_order-workflow-api&#34;,
    &#34;pull_request_link&#34;: &#34;https://github.com/retailcorp/flow_order-workflow-api/pull/1&#34;,
    &#34;merge_commit&#34;: null,
    &#34;fork&#34;: false,
    &#34;head_commit&#34;: &#34;a3f7b9e2d4c1a8e6f5b2d3c4e9a0b1c2&#34;,
    &#34;base_commit&#34;: &#34;f1e2d3c4b5a6f7e8d9c0b1a2e3f4d5c6&#34;,
    &#34;pull_request&#34;: true,
    &#34;command_line&#34;: false,
    &#34;pull_request_number&#34;: &#34;1&#34;,
    &#34;user&#34;: &#34;jsanchez&#34;,
}
```

### Protect branch
