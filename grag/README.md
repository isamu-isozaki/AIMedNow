# GraphRAG

This directory is part of the AIMedNow project and serves as a dedicated endpoint for GraphRAG (Graph-based Retrieval Augmented Generation), grounded on Emergency Medical Technician (EMT) guidelines.

## Contents

- **docs**: Stores the output from GraphRAG's indexing process. This directory contains all preprocessed graph structures and embeddings used during inference.

## Setup and Usage

### Installation

1. Install GraphRAG by cloning the repository: git clone https://github.com/microsoft/graphrag.git

2. Follow the setup instructions in the [GraphRAG Getting Started Guide](https://microsoft.github.io/graphrag/get_started/).

### Running the Indexing Process

1. Prepare your EMT guideline documents according to the format requirements specified in the GraphRAG documentation.

2. Run the indexing function as described in the [GraphRAG Indexing Overview](https://microsoft.github.io/graphrag/index/overview/).

3. The processed output will be stored in the `docs` directory, ready to be used for inference.

### Integration with AIMedNow

The indexed documents can be utilized by other components of the AIMedNow project to provide accurate, graph-based retrieval of medical information from EMT guidelines.

## Additional Resources

- [GraphRAG Documentation](https://microsoft.github.io/graphrag/)
- [GraphRAG GitHub Repository](https://github.com/microsoft/graphrag)