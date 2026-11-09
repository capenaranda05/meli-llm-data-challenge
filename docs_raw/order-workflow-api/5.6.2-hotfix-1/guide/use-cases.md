# Use cases

## Workflow

- Activate workflow for an app
```mermaid
    sequenceDiagram
    participant C as Configs API
    participant D as Database
    participant W as Workflow API
    participant G as Github Proxy

    C-&gt;&gt;W: Activate workflow message
    activate W
    W-&gt;&gt;D: Get workflow settings
    activate D
    D--&gt;&gt;W: Return workflow settings
    deactivate D
    W-&gt;&gt;G: Get all stable branches
    activate G
    G--&gt;&gt;W: Return branches
    deactivate G
    W--&gt;&gt;W: Set specified context to branches
    loop forAllStableBranches
        W-&gt;&gt;G: Protect branch and activate required checks
        activate G
        G--&gt;&gt;W: Return OK
        deactivate G
    end
    W--&gt;G: Set default branch as configured
    activate G
    G--&gt;&gt;W: Return OK
    deactivate G
    W--&gt;&gt;C: Return OK
    deactivate W
```
- Edit the configured workflow of an app
```mermaid
    sequenceDiagram
    participant C as Configs API
    participant D as Database
    participant W as Workflow API
    participant G as Github Proxy

    C-&gt;&gt;W: Edit workflow message
    activate W
    W-&gt;&gt;D: Get FROM workflow settings
    activate D
    D--&gt;&gt;W: Return FROM workflow settings
    deactivate D
    W-&gt;&gt;D: Get TO workflow settings
    activate D
    D--&gt;&gt;W: Return TO workflow settings
    deactivate D
    loop forAllStableBranches
         W-&gt;&gt;G: Unprotect FROM Workflow branch
         activate G
         G--&gt;&gt;W: Return OK
         deactivate G
     end
    W--&gt;G: Set default branch as master
    activate G
    G--&gt;&gt;W: Return OK
    deactivate G
    W--&gt;&gt;W: Set TO Workflow specified context to branches
    loop forAllStableBranches
        W-&gt;&gt;G: Protect TO Workflow  branch 
        activate G
        G--&gt;&gt;W: Return OK
        deactivate G
    end
    W--&gt;G: Set TO Workflow default branch
    activate G
    G--&gt;&gt;W: Return OK
    deactivate G
    W--&gt;&gt;C: Return OK
    deactivate W
```
- Deactivate workflow from an app
```mermaid
    sequenceDiagram
    participant C as Configs API
    participant D as Database
    participant W as Workflow API
    participant G as Github Proxy

    C-&gt;&gt;W: Deactivate workflow message
    activate W
    W-&gt;&gt;D: Get workflow settings
    activate D
    D--&gt;&gt;W: Return workflow settings
    deactivate D
    loop forAllStableBranches
         W-&gt;&gt;G: Unprotect branch
         activate G
         G--&gt;&gt;W: Return OK
         deactivate G
     end
    W--&gt;G: Set default branch as master
    activate G
    G--&gt;&gt;W: Return OK
    deactivate G
    W--&gt;&gt;C: Return OK
    deactivate W
```

## Pipeline
- Search for a pipeline
- Validate a pipeline
```mermaid
    sequenceDiagram
        participant O as Orchestrator
        participant B as BigQ
        participant W as Workflow API
        participant D as Database
        participant C as Configs API
        participant G as GH Proxy

        O-&gt;&gt;B: Workflow validation start
        activate B
        B-&gt;&gt;W: Start workflow validation
        activate W
        W-&gt;&gt;O: Get pipeline information
        activate O
        O--&gt;&gt;W: Return information
        deactivate O
        W--&gt;&gt;B: Return HTTP 200 OK
        deactivate B
        W-&gt;&gt;W: Start workflow validation
        W-&gt;&gt;C: Get workflow config for repo
        activate C
        C--&gt;&gt;W: Return config
        deactivate C
        W-&gt;&gt;D: Create Pipeline Execution (Wait)
        activate D
        D--&gt;&gt;W: Return OK
        deactivate D
        W-&gt;&gt;B: Send ACK to Orchestrator
        activate B
        B--&gt;&gt;W: Return OK
        deactivate B
        alt isForkPullRequestFlow
            W-&gt;&gt;W: Run fork validations
        end 
        W-&gt;&gt;W: Run branch validations
        alt isMigration
            loop remainingPages &gt; 0 
                W-&gt;&gt;G: Get diff files information paginated
                activate G
                G--&gt;&gt;W: Return files information
                deactivate G
            end
            W-&gt;&gt;W: Validate files migration path
        end 
        W-&gt;&gt;G: Set pull request status check
        activate G
        G--&gt;&gt;W: Return OK
        deactivate G
        W-&gt;&gt;D: Save pipeline execution result
        activate D
        D--&gt;&gt;W: Return OK
        deactivate D
        W-&gt;&gt;B: Send ACK to Orchestrator
        activate B
        B--&gt;&gt;W: Return OK
        deactivate B
        deactivate W
```
- Abort a pipeline

#### Admin
Manage the default workflows.
- Search for a workflow
```mermaid
    sequenceDiagram
        participant U as User
        participant W as Workflow
        participant D as Database

    U-&gt;&gt;W: Request a workflow
    activate W
    W-&gt;&gt;D: Search workflow
    activate D
    D--&gt;&gt;W: Return result
    deactivate D
    W--&gt;&gt;U: Return result
    deactivate W
```
- Insert a workflow
```mermaid
    sequenceDiagram
        participant U as User
        participant W as Workflow
        participant D as Database

    U-&gt;&gt;W: Send workflow values
    activate W
    W-&gt;&gt;D: Search workflow
    activate D
    D--&gt;&gt;W: Return results
    deactivate D
    alt not workflowExists
        W-&gt;&gt;D: Insert workflow
        activate D
        D--&gt;&gt;W: Return OK
        deactivate D
        W--&gt;&gt;U: Return HTTP 201 CREATED
    else
        W--&gt;&gt;U: Return HTTP 409 CONFLICT
    end
    deactivate W
```
- Update a workflow
```mermaid
    sequenceDiagram
        participant U as User
        participant W as Workflow
        participant D as Database

    U-&gt;&gt;W: Send workflow values
    activate W
    W-&gt;&gt;D: Search workflow
    activate D
    D--&gt;&gt;W: Return results
    deactivate D
    alt workflowExists
        W-&gt;&gt;D: Update workflow
        activate D
        D--&gt;&gt;W: Return OK
        deactivate D
        W--&gt;&gt;U: Return HTTP 200 OK
    else
        W--&gt;&gt;U: Return HTTP 400 BAD REQUEST
    end
    deactivate W
```

#### Branches
- Apply branches protection for an application
- Create a branch backport

#### Cron
- Create a midday cron
```mermaid
    sequenceDiagram
        participant F as RetailCorp
        participant W as Workflow
        participant C as Configs API
        participant D as Database
        participant B as Build API
        participant G as GH Proxy

    F-&gt;&gt;W: Trigger midday cron
    activate W
    W-&gt;&gt;C: Get configured crons
    activate C
    C--&gt;&gt;W: Return results
    deactivate C

    loop forConfiguredCrons
         W-&gt;&gt;D: Get workflow type config
         activate D
         D--&gt;&gt;W: Return workflow type config
         deactivate D
    
        alt workflow has cronBranches
            
            loop findLastVersion
                W-&gt;&gt;B: Get last version
                activate B
                B--&gt;&gt;W: Return last version
                deactivate B
                W-&gt;&gt;G: Check if version branch exist
                activate G
                G--&gt;&gt;W: Return result
                deactivate G
               
                Note right of W: Exit when branch does not exist or MAX_RETRY reached
               
            end
    
            alt MAX_RETRY reached
                W--&gt;&gt;F: Return error 500
            else
                W-&gt;&gt;G: Create version branch
                activate G
                G--&gt;&gt;W: Return response
                deactivate G
                
                W-&gt;&gt;G: Open pull request
                activate G
                G--&gt;&gt;W: return response
                deactivate G
    
                W-&gt;&gt;D: Save cron version
                activate D
                D--&gt;&gt;W: Return OK
                deactivate D

            end
        end
    end

    W--&gt;&gt;F: Return 200
    deactivate W
```

- Create a nightly cron
    (Has the same flow as midday)