# **Retrieval-Augmented Generation (RAG) Project**

## **Overview**

This project demonstrates a scalable **Retrieval-Augmented Generation (RAG)** system designed for medical question answering using a combination of a **vector database** and a **local Large Language Model (LLM)**. It showcases modern machine learning and software engineering practices with the potential to integrate cloud-based solutions such as Azure Cognitive Search for production-ready applications.

The system retrieves relevant research findings from the **PubMedQA dataset**, embeds the content using **Sentence Transformers**, and stores them in **Qdrant**, a high-performance vector database. Queries are answered using a local LLM (e.g., Llama), augmented with the retrieved context.

---

## **Key Features**

- **Context-Enhanced Responses**: Combines vector-based search with LLMs for accurate and context-aware answers.
- **Modular Design**: Supports local deployment with Qdrant and extensibility for cloud integration with Azure Cognitive Search.
- **FastAPI Framework**: Provides an intuitive and scalable API interface.
- **Dockerized Environment**: Simplifies deployment with separate configurations for development and production.

---

## **Architecture**

![Architecture Diagram](https://via.placeholder.com/900x500?text=Add+an+architecture+diagram+here) 

1. **Data Preparation**:
   - The PubMedQA dataset is loaded, and relevant entries are embedded using **Sentence Transformers** (`all-MiniLM-L6-v2`).
2. **Vector Storage**:
   - **Qdrant** stores embeddings for efficient vector-based retrieval.
3. **Query Pipeline**:
   - User queries are vectorized and matched with relevant embeddings in Qdrant.
   - Retrieved context is passed to the local LLM (e.g., Llama) for an enriched response.
4. **API Interaction**:
   - Exposes endpoints for submitting queries (`/ask`) via FastAPI.

---

## **Technologies Used**

- **Language & Framework**:
  - Python 3.10
  - FastAPI
- **Machine Learning**:
  - Hugging Face Datasets (PubMedQA)
  - Sentence Transformers
- **Vector Database**:
  - Qdrant
- **Local LLM**:
  - Llama (via LlamaFile)
- **DevOps & Deployment**:
  - Docker, Docker Compose
  - Multi-stage Dockerfile for optimized builds
- **Cloud (Optional)**:
  - Azure Cognitive Search (ready for integration)

---

## **Setup Instructions**

### **1. Prerequisites**
- Docker and Docker Compose (v2+)
- Python 3.10+ (optional, for local testing)
- GPU (optional, for accelerated embeddings)

### **2. Clone the Repository**
```bash
git clone https://github.com/tanle8/MediRAG.git
cd MediRAG
```

### **3. Install Dependencies**
#### For Local Testing:
```bash
pip install -r requirements.txt
```

#### For Docker Deployment:
Build the Docker image with all dependencies:
```bash
docker compose up --build
```

---

## **Running the Project**

### **Development Mode**
Use the development configuration to enable live code reloading:
```bash
make dev-build
```
Access the FastAPI interface at [http://localhost:80/docs](http://localhost:80/docs).

### **Production Mode**
For optimized builds and deployment:
```bash
make prod-build
```

---

## **Usage**

### **API Endpoints**
1. **`GET /`**:
   - Redirects to the Swagger UI at `/docs`.
2. **`POST /ask`**:
   - Submit a query and receive an enriched response.

#### Example Query:
```bash
curl -X POST "http://localhost:80/ask" -H "Content-Type: application/json" -d '{"query": "What are the long-term outcomes of laparoscopic surgery for hiatal hernia repair?"}'
```

#### Example Response:
```json
{
  "response": "Laparoscopic surgery for hiatal hernia repair has shown positive long-term outcomes, with reduced recurrence rates compared to traditional open surgeries."
}
```

---

## **Environment Variables**

Configure via `.env`:
```env
LLM_TYPE=local
LOCAL_LLM_SERVICE_URL=http://host.docker.internal:8080/
AZURE_API_KEY=your-api-key  # For optional Azure integration
```

---

## **Folder Structure**

```plaintext
.
├── webapp
│   ├── main.py                # FastAPI app
│   ├── vectorstore.py         # Qdrant operations
│   ├── embeddings.py          # Embedding generation
│   ├── llm.py                 # Interaction with local LLM
│   ├── __init__.py
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.dev.yml     # Docker Compose for development
├── docker-compose.prod.yml    # Docker Compose for production
├── Makefile                   # Automation for builds and deployment
└── README.md                  # Project documentation
```

---

## **Future Enhancements**

1. **Cloud Integration**:
   - Azure Cognitive Search for scalable vector-based retrieval.
   - Azure OpenAI for hosted GPT models.
2. **Advanced Indexing**:
   - Experiment with hybrid search (e.g., dense + sparse retrieval).
3. **Scalability**:
   - Kubernetes support for deploying across clusters.
4. **Improved UI**:
   - Build a web-based frontend for user-friendly interactions.

---

## **Contributing**

We welcome contributions from the community! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`feature-xyz`).
3. Commit your changes.
4. Open a pull request.

---

## **Acknowledgments**

- [Hugging Face](https://huggingface.co) for the PubMedQA dataset.
- [Qdrant](https://qdrant.tech) for the vector database.
- [Sentence Transformers](https://www.sbert.net) for efficient embedding generation.
- [Uvicorn & FastAPI](https://fastapi.tiangolo.com) for the API framework.

---

## **License**

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more details.

---

## **Contact**

For questions, feedback, or collaborations, please reach out:
- **Email**: tanld.ce@gmail.com
- **LinkedIn**: [Tan (David) LE](https://www.linkedin.com/in/david-tan-le-v3579)
- **GitHub**: [@tanle8](https://github.com/tanle8)

