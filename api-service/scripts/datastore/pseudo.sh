#!/bin/bash

# Load Test Data Script for API Service
# This script creates sample cabinets and populates them with test content

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
API_BASE="http://localhost:8000"

echo -e "${BLUE}🚀 Cabinets Chat - Load Test Data${NC}"
echo "=========================================="
echo "Project root: $PROJECT_ROOT"
echo "API base: $API_BASE"

echo -e "\n${BLUE}📦 Creating cabinets...${NC}"

declare -a cabinets=("ai-research" "web-development" "product-docs")
for cabinet in "${cabinets[@]}"; do
  curl -X POST "$API_BASE/create_cabinet" \
    -H "Content-Type: application/json" \
    -d "{\"cabinet_name\": \"$cabinet\"}" \
    --silent --show-error
  echo -e "${GREEN}✅ cabinet created: $cabinet${NC}"
done

echo -e "\n${BLUE}📝 Adding content to ai-research cabinet...${NC}"

curl -X POST "$API_BASE/add_to_cabinet" \
  -H "Content-Type: application/json" \
  -d '{
  "cabinet_name": "ai-research",
  "text": "Machine learning algorithms have revolutionized data analysis and pattern recognition. Deep neural networks, particularly transformer architectures, have shown remarkable success in natural language processing tasks. These models use attention mechanisms to process sequential data more effectively than traditional recurrent neural networks. The attention mechanism allows the model to focus on relevant parts of the input sequence when making predictions.",
  "source_url": "https://example.com/ml-fundamentals"
  }' --silent --show-error
echo -e "${GREEN}✅ Added ML fundamentals${NC}"

curl -X POST "$API_BASE/add_to_cabinet" \
  -H "Content-Type: application/json" \
  -d '{
  "cabinet_name": "ai-research",
  "text": "Large Language Models (LLMs) like GPT and BERT have transformed how we approach natural language understanding. These models are trained on vast amounts of text data using self-supervised learning techniques. The emergence of few-shot and zero-shot learning capabilities has made these models incredibly versatile for various NLP tasks without requiring task-specific training data.",
  "source_url": "https://example.com/llm-overview"
  }' --silent --show-error
echo -e "${GREEN}✅ Added LLM overview${NC}"

curl -X POST "$API_BASE/add_to_cabinet" \
  -H "Content-Type: application/json" \
  -d '{
  "cabinet_name": "ai-research",
  "text": "Computer vision has advanced significantly with convolutional neural networks (CNNs) and vision transformers (ViTs). Object detection, image segmentation, and facial recognition systems now achieve human-level performance in many scenarios. Transfer learning from pre-trained models has democratized computer vision applications, allowing smaller teams to build sophisticated visual AI systems.",
  "source_url": "https://example.com/computer-vision"
  }' --silent --show-error
echo -e "${GREEN}✅ Added computer vision${NC}"

echo -e "\n${BLUE}💻 Adding content to web-development cabinet...${NC}"

curl -X POST "$API_BASE/add_to_cabinet" \
  -H "Content-Type: application/json" \
  -d '{
  "cabinet_name": "web-development",
  "text": "React is a popular JavaScript library for building user interfaces, particularly single-page applications. It uses a component-based architecture where UI elements are broken down into reusable components. The virtual DOM concept in React optimizes rendering performance by minimizing direct DOM manipulations. Hooks like useState and useEffect have simplified state management and side effects in functional components.",
  "source_url": "https://example.com/react-guide"
  }' --silent --show-error
echo -e "${GREEN}✅ Added React guide${NC}"

curl -X POST "$API_BASE/add_to_cabinet" \
  -H "Content-Type: application/json" \
  -d '{
  "cabinet_name": "web-development",
  "text": "Modern web development relies heavily on build tools and bundlers like Webpack, Vite, and Parcel. These tools optimize code for production by minifying JavaScript, bundling modules, and enabling features like hot module replacement during development. TypeScript has gained widespread adoption for its static typing capabilities, which help catch errors at compile time and improve code maintainability.",
  "source_url": "https://example.com/build-tools"
  }' --silent --show-error
echo -e "${GREEN}✅ Added build tools${NC}"

curl -X POST "$API_BASE/add_to_cabinet" \
  -H "Content-Type: application/json" \
  -d '{
  "cabinet_name": "web-development",
  "text": "API design and RESTful services are fundamental to modern web applications. GraphQL has emerged as an alternative to REST, offering more flexible data fetching capabilities. Microservices architecture allows teams to build scalable applications by breaking down monolithic systems into smaller, independent services. Container technologies like Docker facilitate deployment and scaling of these distributed systems.",
  "source_url": "https://example.com/api-design"
  }' --silent --show-error
echo -e "${GREEN}✅ Added API design${NC}"

echo -e "\n${BLUE}📋 Adding content to product-docs cabinet...${NC}"

curl -X POST "$API_BASE/add_to_cabinet" \
  -H "Content-Type: application/json" \
  -d '{
  "cabinet_name": "product-docs",
  "text": "User authentication in our platform supports multiple methods including OAuth 2.0, SAML, and traditional username/password comcabinetations. Two-factor authentication (2FA) is available through SMS, email, or authenticator apps. Session management includes configurable timeout periods and concurrent session limits. Password policies can be customized to meet organizational security requirements.",
  "source_url": "https://docs.example.com/auth"
  }' --silent --show-error
echo -e "${GREEN}✅ Added authentication docs${NC}"

curl -X POST "$API_BASE/add_to_cabinet" \
  -H "Content-Type: application/json" \
  -d '{
  "cabinet_name": "product-docs",
  "text": "The analytics dashboard provides real-time insights into user behavior, system performance, and business metrics. Custom widgets can be created using our widget API, allowing teams to visualize data specific to their needs. Data export functionality supports CSV, JSON, and PDF formats. Automated reports can be scheduled and delivered via email to stakeholders on a daily, weekly, or monthly basis.",
  "source_url": "https://docs.example.com/analytics"
  }' --silent --show-error
echo -e "${GREEN}✅ Added analytics docs${NC}"

curl -X POST "$API_BASE/add_to_cabinet" \
  -H "Content-Type: application/json" \
  -d '{
  "cabinet_name": "product-docs",
  "text": "API rate limiting is implemented to ensure fair usage and prevent abuse. Free tier users are limited to 1000 requests per hour, while premium users can make up to 10000 requests per hour. Rate limit headers are included in all API responses to inform clients about their current usage status. When limits are exceeded, the API returns a 429 status code with details about when the limit will reset.",
  "source_url": "https://docs.example.com/rate-limits"
  }' --silent --show-error
echo -e "${GREEN}✅ Added rate limits docs${NC}"

echo -e "\n${GREEN}✅ Test data loading complete!${NC}"

echo -e "\n${BLUE}📊 Checking loaded data...${NC}"
curl -X GET "$API_BASE/list_cabinets" -H "Content-Type: application/json" | python3 -m json.tool

echo -e "\n${BLUE}🔍 Testing a sample query...${NC}"
curl -X GET "$API_BASE/query_cabinet?cabinet_name=ai-research&query=neural%20networks&top_k=2" \
  -H "Content-Type: application/json" | python3 -m json.tool

echo -e "\n${GREEN}🎉 Test data setup completed successfully!${NC}"
echo "=========================================="
echo -e "${BLUE}Summary:${NC}"
echo "- cabinets created: ${cabinets[*]}"
echo "- Content added to all cabinets"
echo "- Data verified"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Use the API to interact with loaded test data"
echo "2. Run integration tests as needed"
echo ""
