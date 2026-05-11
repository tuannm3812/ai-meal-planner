# Data Directory

Local datasets for experimentation belong here.

```text
data/
|-- raw/        # Original downloaded files, not committed
|-- processed/  # Cleaned feature tables, not committed unless small and non-sensitive
`-- external/   # Third-party reference data, not committed unless license permits
```

Do not commit Kaggle competition files. Download them locally and document the source, version, and preprocessing steps in the relevant notebook or training script.
