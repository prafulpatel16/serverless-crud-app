# 🚀 Serverless CRUD App

## 📌 About the Project

The **Serverless CRUD App** is a backend and frontend application that provides a fully serverless architecture for managing CRUD (Create, Read, Update, Delete) operations. It is built using AWS Serverless Application Model (AWS SAM), CloudFormation, and a structured backend API that integrates seamlessly with frontend services.

## Architectural Diagram
![alt text](diagrams/serverless-crud-app-diagram.png)

## 📁 Project Structure

```
serverless-crud-app/
│-- .aws-sam/               # ⚡ AWS SAM build artifacts
│-- backend/
│   ├── src/                # 🏗️ Source code for backend functions
│   │   ├── create/         # ✨ Lambda function for creating resources
│   │   ├── delete/         # ❌ Lambda function for deleting resources
│   │   ├── list/           # 📋 Lambda function for listing resources
│   │   ├── read/           # 📖 Lambda function for reading a single resource
│   │   ├── update/         # 🔄 Lambda function for updating resources
│   │   ├── documentations/ # 📜 API documentation (Swagger or Postman collection)
│-- frontend/
│   ├── index.html          # 🌐 Frontend application (basic UI)
│-- pipelines/              # 🔄 CI/CD pipeline configurations
│-- .gitignore              # 🚫 Git ignore file
│-- cloudformation.yaml     # ☁️ CloudFormation stack configuration
│-- README.md               # 📘 Project documentation
│-- response.json           # 📝 Sample API responses
│-- samconfig.toml          # ⚙️ AWS SAM configuration file
│-- template.yaml           # 🏗️ AWS SAM template definition
```

## ✨ Features
- **🛠️ Serverless Backend**: Uses AWS Lambda for CRUD operations.
- **📜 Infrastructure as Code**: AWS CloudFormation and AWS SAM templates.
- **🎨 Frontend UI**: Basic HTML page to interact with the API.
- **📖 API Documentation**: Includes Swagger/Postman collection.
- **🚀 CI/CD Pipelines**: Automates deployments using AWS CodePipeline or GitHub Actions.

## 🛠️ Prerequisites
Before you start, ensure you have the following installed:
- **AWS CLI** - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- **AWS SAM CLI** - [Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- **Docker** - Required for building dependencies
- **Node.js & npm** - For frontend development

## 📦 Installation & Setup

### 1️⃣ Clone the Repository
```sh
 git clone https://github.com/your-repo/serverless-crud-app.git
 cd serverless-crud-app
```

### 2️⃣ Install Backend Dependencies
```sh
cd backend/src
sam build
```

### 3️⃣ Deploy the Serverless Application
```sh
sam deploy --guided
```
This command will prompt you for AWS configurations such as stack name, region, and permissions.

### 4️⃣ Running the Frontend
To serve the frontend locally, navigate to the `frontend` folder:
```sh
cd frontend
python -m http.server 8000
```
Then, open `http://localhost:8000/index.html` in your browser.

## 🔗 API Endpoints
The following API endpoints are provided by the serverless backend:

| Method | Endpoint       | Description             |
|--------|---------------|-------------------------|
| 🆕 POST   | `/create`      | Create a new resource  |
| 📋 GET    | `/list`        | List all resources     |
| 📖 GET    | `/read/{id}`   | Retrieve a single item |
| 🔄 PUT    | `/update/{id}` | Update an existing item|
| ❌ DELETE | `/delete/{id}` | Delete a resource      |

## 🚀 Deployment Guidelines
1. **🛠️ Update the SAM template (`template.yaml`)** with appropriate AWS configurations.
2. **⚡ Run `sam build`** to prepare the application.
3. **🚀 Deploy with `sam deploy --guided`** for first-time setup.
4. **📊 Use AWS CloudFormation to monitor the stack deployment.**

## 🔄 CI/CD Pipeline Setup
This project includes pipeline configurations under the `pipelines/` directory. You can configure AWS CodePipeline or GitHub Actions for automated deployment.

## 🔒 Security Considerations
- 🛡️ Ensure IAM roles for Lambda have minimal privileges.
- ⚡ Use AWS API Gateway throttling to protect against excessive requests.
- 🔥 Enable AWS WAF to mitigate security threats.


## 🤝 Contributing

Contributions are welcome! Please check the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this project.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🧑‍💻 Author

Created and maintained by **Praful Patel**.  
For inquiries, visit [Praful's GitHub](https://github.com/prafulpatel16).
For Tech, visit [Praful's Blog](https://www.praful.cloud).

---





