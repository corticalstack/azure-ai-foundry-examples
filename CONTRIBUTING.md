# 👨‍💻 Contributing

This repository welcomes contributions and suggestions! These are examples for Azure AI Foundry services. Please read through the contributing guide below to ensure a smooth contribution process.

---

## 📜 Code of Conduct

Please be respectful and considerate, the aim is to foster an open and welcoming environment for all contributors.

---

## 🎯 Goals

This repository contains examples that demonstrate how to use Azure AI Foundry services.

---

## 🐛 Issues

All forms of feedback are welcome through [issues](https://github.com/corticalstack/azure-ai-foundry-examples/issues/new/choose). We provide templates for bug reports and feature requests to help you provide all the necessary information. Please select the appropriate template and fill it out as completely as possible.

---

## 🔀 Pull Requests

Pull requests (PRs) to this repo require review and approval to merge. Please follow the pre-defined template and the guidelines below.

---

### 🛠️ How to Contribute

1. **Fork the repository** (create your own copy on GitHub)
2. **Clone your fork** to your local machine:
   ```
   git clone https://github.com/corticalstack/azure-ai-foundry-examples.git
   cd azure-ai-foundry-examples
   ```
3. **Create a new branch** for your changes:
   ```
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and test them thoroughly
5. **Ensure your code follows project standards**
6. **Commit your changes** with clear, descriptive commit messages:
   ```
   git commit -m 'Add some feature'
   ```
7. **Push to your fork**:
   ```
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request** from your fork to the original repository

### ➕ Adding New Examples

When adding new examples with additional dependencies:

1. Add the new dependencies to the root `requirements.txt` file
2. Rebuild the dev container to include the new dependencies
3. Include a detailed README.md in your example directory
4. Update the main README.md to list your new example
5. Ensure your example follows the same structure as existing examples
6. Test your example thoroughly before submitting

This ensures that the dev container will work with all examples in the repository and that your example is well-documented and easy to use.

---

## 📂 Repository Structure

The repository is organized with numbered example directories, each demonstrating a specific Azure AI Foundry capability or way of working and interacting with Foundry assets.

- Each example directory contains a README.md file explaining the example
- The root directory contains common files and configuration for all examples
- The dev container provides a consistent environment for running all examples

## 📚 Documentation

When adding or updating examples, please ensure that:

- Code is well-commented and follows best practices
- README files are clear and provide step-by-step instructions
- Any prerequisites or dependencies are clearly documented
- Examples include expected outputs or results where applicable
