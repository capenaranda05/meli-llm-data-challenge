# Database

## Scopes
#### Production
|  Type | Schema | Cluster |
| --- | --- | --- |
| MySQL | fulfillment | orderworkflowapi00 |

#### Test
|  Type | Schema | Cluster |
| --- | --- | --- |
| MySQL | fulfillment2 | testenv02 |

## Objects stored
#### Workflows

A workflow represents a valid git flow in use for Release process.

Currently we have two types:

- Gitflow
- Libflow

A Workflow object is represented as a JSON as follows:

```
{
    &#34;default_branch&#34;: &#34;develop&#34;,
    &#34;name&#34;: &#34;gitflow&#34;,
    &#34;documentation_link&#34;: &#34;https://release-process.retailcorp-cloud.io/#/lang-es/workflows/02_gitflow?id=branches-destacados&#34;,
    &#34;stable_branches&#34;: [
        {
            &#34;name&#34;: &#34;master&#34;,
            &#34;name_pattern&#34;: &#34;^master$&#34;,
            &#34;code_review_enabled&#34;: false,
            &#34;accept_forks&#34;: false,
            &#34;valid_head_branch_patterns&#34;: [
                &#34;^release/.*&#34;,
                &#34;^hotfix/.*&#34;,
                &#34;^revert-.*&#34;,
                &#34;^migration/.*&#34;
            ],
            &#34;releasable&#34;: true,
            &#34;candidate&#34;: false
        },
        {
            &#34;name&#34;: &#34;develop&#34;,
            &#34;name_pattern&#34;: &#34;^develop$&#34;,
            &#34;code_review_enabled&#34;: true,
            &#34;accept_forks&#34;: true,
            &#34;valid_head_branch_patterns&#34;: [
                &#34;^feature/.*&#34;,
                &#34;^enhancement/.*&#34;,
                &#34;^bugfix/.*&#34;,
                &#34;^fix/.*&#34;,
                &#34;^revert-.*&#34;,
                &#34;^hotfix/.*&#34;,
                &#34;^release/.*&#34;,
                &#34;^backport/.*&#34;
            ],
            &#34;releasable&#34;: false,
            &#34;candidate&#34;: false
        },
        {
            &#34;name&#34;: &#34;release&#34;,
            &#34;name_pattern&#34;: &#34;^release/.*&#34;,
            &#34;code_review_enabled&#34;: true,
            &#34;accept_forks&#34;: false,
            &#34;valid_head_branch_patterns&#34;: [
                &#34;^fix/.*&#34;,
                &#34;^revert-.*&#34;,
                &#34;^hotfix/.*&#34;,
                &#34;^backport/.*&#34;
            ],
            &#34;releasable&#34;: false,
            &#34;candidate&#34;: true
        }
    ],
    &#34;relevant_branches&#34;: [
        &#34;^master$&#34;,
        &#34;^develop$&#34;,
        &#34;^release/.*&#34;,
        &#34;^hotfix/.*&#34;,
        &#34;^feature/.*&#34;,
        &#34;^fix/.*&#34;,
        &#34;^bugfix/.*&#34;,
        &#34;^enhancement/.*&#34;,
        &#34;^revert-.*&#34;,
        &#34;^migration/.*&#34;,
        &#34;^backport/.*&#34;
    ],
    &#34;backport_rules&#34;: [
        {
            &#34;base_trigger_pattern&#34;: &#34;^master$&#34;,
            &#34;head_trigger_pattern&#34;: &#34;^hotfix/.*$&#34;,
            &#34;backport_to&#34;: [
                {
                    &#34;base_branch_pattern&#34;: &#34;^develop$&#34;,
                    &#34;only_active_pull_requests&#34;: false
                },
                {
                    &#34;base_branch_pattern&#34;: &#34;^release/.*&#34;,
                    &#34;only_active_pull_requests&#34;: true
                }
            ]
        },
        {
            &#34;base_trigger_pattern&#34;: &#34;^master$&#34;,
            &#34;head_trigger_pattern&#34;: &#34;^release/.*$&#34;,
            &#34;backport_to&#34;: [
                {
                    &#34;base_branch_pattern&#34;: &#34;^develop$&#34;,
                    &#34;only_active_pull_requests&#34;: false
                },
                {
                    &#34;base_branch_pattern&#34;: &#34;^release/.*&#34;,
                    &#34;only_active_pull_requests&#34;: true
                }
            ]
        },
        {
            &#34;base_trigger_pattern&#34;: &#34;^master$&#34;,
            &#34;head_trigger_pattern&#34;: &#34;^migration/.*$&#34;,
            &#34;backport_to&#34;: [
                {
                    &#34;base_branch_pattern&#34;: &#34;^develop$&#34;,
                    &#34;only_active_pull_requests&#34;: false
                },
                {
                    &#34;base_branch_pattern&#34;: &#34;^release/.*&#34;,
                    &#34;only_active_pull_requests&#34;: true
                }
            ]
        }
    ],
    &#34;releasable_branches&#34;: [
        &#34;^master$&#34;
    ],
    &#34;cron_branches&#34;: {
        &#34;version_branch&#34;: &#34;release&#34;,
        &#34;stable_branch&#34;: &#34;develop&#34;,
        &#34;target_branch&#34;: &#34;master&#34;
    }
}
```

#### Cron History
_TODO_ 