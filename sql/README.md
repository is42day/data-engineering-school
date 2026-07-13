# SQL Models

Add transformations gradually using these layers:

```text
sql/staging/       source-aligned cleanup and type normalization
sql/intermediate/  reusable joins and business calculations
sql/marts/         dimensions and facts consumed by Power BI
```

Every model should document:

- its purpose;
- its expected grain;
- its primary or natural key;
- important assumptions;
- expected data-quality checks.

Do not create all models upfront. Add each directory when the first real model for that layer is introduced.
