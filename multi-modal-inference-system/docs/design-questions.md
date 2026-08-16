Implement S3-Compatible Object Storage

## Goal
Store multimodal input images in private object storage and persist only the object identity in Postgres.

## Why did I choose Object Storage ?

Local disk
→ binds media to one process/node

Database blob
→ burdens transactional storage with large media

Object storage
→ shared durable media plane
→ API replicas remain stateless
→ workers can scale independently
→ direct presigned upload removes large payloads from API servers

# Design choices 
- For local development use MinIO. 
- For actual AWS deployment, omit the MinIO variables and normally omit static AWS keys too—use an IAM workload role instead.

Your Python application
        │
        │ Boto3 calls: put_object, head_object,
        │ generate_presigned_post, get_object, delete_object
        ▼
   S3-compatible API
        │
        ├── Local development → MinIO container
        │                         http://localhost:9000
        │
        └── Deployment → Amazon S3 on AWS
                                  AWS-managed endpoint



## More design choices

- Why object storage instead of Postgres blobs or local disk?
- Why persist before enqueueing?
- What happens if Postgres commits but Redis publish fails?
- Why is the idempotency key unique in Postgres?
- Who owns QUEUED → RUNNING?
- What happens if the worker completes inference but crashes before marking SUCCEEDED?
- Can this system provide exactly-once execution, or only exactly-once behavior from the client's perspective?

## How to design a durable inference job?
The client has already uploaded an image to MinIO/S4.

## API Role 

We use direct presigned uploads: the API authorizes a short-lived, tightly scoped upload but does not proxy image bytes. The client uploads directly to S3-compatible storage, which keeps the API off the large-file data path. Afterward, the API verifies the stored object with HEAD and commits the Job metadata to Postgres. This improves scalability and keeps permanent storage credentials private; the main trade-off is orphan uploads, which we handle with lifecycle expiration.
