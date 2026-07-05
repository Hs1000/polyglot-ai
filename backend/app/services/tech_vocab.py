"""
Shared technology vocabulary used by extraction and matching services.

Three mutually-exclusive categories:
  KNOWN_LANGUAGES  — things you write code in (Python, SQL, HTML …)
  KNOWN_FRAMEWORKS — libraries / frameworks built on top of languages
  KNOWN_DATABASES  — data-store systems and vector DBs (Neo4J, Pinecone …)

Tokens not in any set are silently dropped when filtering, so junk text
from QA answers (e.g. "experience", "proficient") never leaks into results.
"""

import re

KNOWN_LANGUAGES: set[str] = {
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "html",
    "css", "bash", "shell", "perl", "matlab", "julia", "dart", "lua",
    "groovy", "powershell", "assembly", "objective-c", "cobol", "fortran",
    "vba", "sass", "scss", "graphql", "solidity", "elixir", "clojure",
    "haskell", "erlang", "ocaml", "f#", "zig", "nim",
}

KNOWN_FRAMEWORKS: set[str] = {
    "react", "angular", "vue", "nextjs", "nuxt", "svelte", "express",
    "django", "flask", "fastapi", "spring", "laravel", "rails", "dotnet",
    ".net", "asp.net", "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "scipy", "langchain", "huggingface", "spark",
    "hadoop", "kafka", "airflow", "dbt", "redux", "jest", "pytest",
    "junit", "selenium", "playwright", "bootstrap", "tailwind", "materialui",
    "flutter", "xamarin", "opencv", "spacy", "nltk", "celery", "sqlalchemy",
    "langchain", "llamaindex", "transformers", "xgboost", "lightgbm",
    "catboost", "matplotlib", "seaborn", "plotly", "streamlit", "gradio",
    "fasthtml", "htmx", "gin", "echo", "fiber", "actix", "axum",
}

KNOWN_DATABASES: set[str] = {
    # Relational
    "mysql", "postgresql", "sqlite", "oracle", "mssql", "mariadb",
    "cockroachdb", "tidb",
    # NoSQL / document
    "mongodb", "couchdb", "dynamodb", "firestore", "firebase",
    "faunadb", "arangodb",
    # Key-value / cache
    "redis", "memcached",
    # Search
    "elasticsearch", "opensearch", "solr",
    # Graph
    "neo4j", "neptune", "tigergraph",
    # Vector / AI
    "pinecone", "weaviate", "chromadb", "qdrant", "milvus", "faiss",
    "pgvector", "zilliz",
    # Columnar / warehouse
    "snowflake", "bigquery", "redshift", "databricks", "clickhouse",
    "cassandra", "hbase",
    # Time-series
    "influxdb", "timescaledb", "prometheus",
    # Cloud
    "aws", "gcp", "azure", "s3", "ec2", "lambda", "sagemaker",
    # DevOps / infra
    "docker", "kubernetes", "terraform", "ansible", "jenkins",
    "github", "gitlab", "git", "linux", "nginx", "airflow",
}

# Normalisation aliases: maps user-facing variants to canonical token
ALIASES: dict[str, str] = {
    "golang":      "go",
    "js":          "javascript",
    "ts":          "typescript",
    "node":        "nodejs",
    "node.js":     "nodejs",
    "reactjs":     "react",
    "vuejs":       "vue",
    "angularjs":   "angular",
    "cpp":         "c++",
    "c/c++":       "c++",
    "postgres":    "postgresql",
    "mongo":       "mongodb",
    "k8s":         "kubernetes",
    "tf":          "tensorflow",
    "sk-learn":    "scikit-learn",
    "sklearn":     "scikit-learn",
    "scikit":      "scikit-learn",
    "hugging face":"huggingface",
    "hf":          "huggingface",
    "next.js":     "nextjs",
    "nuxt.js":     "nuxt",
    "vue.js":      "vue",
    "react.js":    "react",
}


def normalise(text: str) -> str:
    """Lowercase and apply aliases."""
    t = text.lower().strip()
    return ALIASES.get(t, t)


def tokenise(value: str | None) -> list[str]:
    """Split a tech string on common separators and normalise each token.

    Splits on: comma, semicolon, slash, newline, space-surrounded dash/en-dash
    (e.g. "Go - TensorFlow" → ["go", "tensorflow"]) but preserves hyphens
    inside names like "scikit-learn".
    """
    if not value:
        return []
    parts = re.split(r"[,;/\n]|\s+[-–]\s+", value)
    return [normalise(p.strip()) for p in parts if p.strip()]


def scan_for_known(text: str, vocab: set[str]) -> list[str]:
    """Scan raw text word-by-word and return all vocab tokens found, in order.

    Uses a word-boundary split so "Neo4J" → "neo4j" matches the databases set
    even when it appears inside a sentence like "Proficient in Neo4J and Pinecone."
    """
    # Split on anything that isn't alphanumeric, dot, plus, hash, or slash
    # (keeps "c++", "c#", "scikit-learn", "next.js" intact)
    words = re.split(r"[^\w.+#/-]+", text)
    seen: set[str] = set()
    result: list[str] = []
    for w in words:
        n = normalise(w.strip(".-/"))
        if n in vocab and n not in seen:
            seen.add(n)
            result.append(n)
    return result
