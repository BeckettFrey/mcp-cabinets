#!/bin/bash

# REST API Test Script
# Tests all major endpoints with sample data

set -e  # Exit on any error

BASE_URL="http://localhost:8000"
TEST_cabinet="test-rest-cabinet"

echo "🧪 Testing REST API"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# Function to print test header
print_test() {
    echo -e "\n${BLUE}🔍 Testing: $1${NC}"
}

# Check if server is running
print_test "Server Health Check"
curl -s -f "$BASE_URL/health" > /dev/null
print_result $? "Health check endpoint"

# Test 1: Health Check (detailed)
print_test "Detailed Health Check"
echo "Request: GET $BASE_URL/health"
health_response=$(curl -s "$BASE_URL/health")
echo "Response: $health_response"
echo "$health_response" | jq -e '.status == "healthy"' > /dev/null
print_result $? "Health status is healthy"

# Test 2: List cabinets (initially)
print_test "List cabinets (initial state)"
echo "Request: GET $BASE_URL/list_cabinets"
initial_cabinets=$(curl -s "$BASE_URL/list_cabinets")
echo "Response: $initial_cabinets"
echo "$initial_cabinets" | jq -e '.success == true' > /dev/null
print_result $? "List cabinets returns success"

# Test 3: Create New cabinet
print_test "Create New cabinet"
echo "Request: POST $BASE_URL/create_cabinet"
echo "Body: {\"cabinet_name\": \"$TEST_cabinet\"}"
create_response=$(curl -s -X POST "$BASE_URL/create_cabinet" \
    -H "Content-Type: application/json" \
    -d "{\"cabinet_name\": \"$TEST_cabinet\"}")
echo "Response: $create_response"
echo "$create_response" | jq -e '.message' > /dev/null
print_result $? "Create cabinet successful"

# Test 4: Add Content to cabinet
print_test "Add Content to cabinet"
test_content="Artificial intelligence is transforming modern technology through machine learning algorithms, neural networks, and deep learning frameworks. These technologies enable computers to learn patterns from data and make intelligent decisions without explicit programming."

echo "Request: POST $BASE_URL/add_to_cabinet"
echo "Body: {\"cabinet_name\": \"$TEST_cabinet\", \"text\": \"$test_content\"}"
add_response=$(curl -s -X POST "$BASE_URL/add_to_cabinet" \
    -H "Content-Type: application/json" \
    -d "{\"cabinet_name\": \"$TEST_cabinet\", \"text\": \"$test_content\", \"source_url\": \"https://example.com/ai-article\"}")
echo "Response: $add_response"
echo "$add_response" | jq -e '.message' > /dev/null
print_result $? "Add content successful"

# Test 5: Query cabinet
print_test "Query cabinet Content"
query="machine learning"
echo "Request: GET $BASE_URL/query_cabinet?cabinet_name=$TEST_cabinet&query=$query&top_k=5"
query_response=$(curl -s "$BASE_URL/query_cabinet?cabinet_name=$TEST_cabinet&query=$(echo "$query" | sed 's/ /%20/g')&top_k=5")
echo "Response: $query_response"
echo "$query_response" | jq -e '.success == true' > /dev/null
print_result $? "Query cabinet successful"

results_count=$(echo "$query_response" | jq -r '.results_found')
echo "Found $results_count result(s)"

# Test 6: Query with Similarity Threshold
print_test "Query with Similarity Threshold"
echo "Request: GET $BASE_URL/query_cabinet?cabinet_name=$TEST_cabinet&query=$query&top_k=5&similarity_threshold=0.7"
threshold_response=$(curl -s "$BASE_URL/query_cabinet?cabinet_name=$TEST_cabinet&query=$(echo "$query" | sed 's/ /%20/g')&top_k=5&similarity_threshold=0.7")
echo "Response: $threshold_response"
echo "$threshold_response" | jq -e '.success == true' > /dev/null
print_result $? "Query with threshold successful"

threshold_results=$(echo "$threshold_response" | jq -r '.results_found')
echo "Found $threshold_results result(s) with 0.7 threshold"

# Test 7: List cabinets (after adding content)
print_test "List cabinets (after content added)"
echo "Request: GET $BASE_URL/list_cabinets"
final_cabinets=$(curl -s "$BASE_URL/list_cabinets")
echo "Response: $final_cabinets"
echo "$final_cabinets" | jq -e '.success == true' > /dev/null
print_result $? "List cabinets successful"

cabinet_count=$(echo "$final_cabinets" | jq -r '.total_cabinets')
echo "Total cabinets: $cabinet_count"

# Test 8: Query Non-existent cabinet (Error Case)
print_test "Query Non-existent cabinet (Error Handling)"
echo "Request: GET $BASE_URL/query_cabinet?cabinet_name=nonexistent&query=test"
error_response=$(curl -s -w "%{http_code}" "$BASE_URL/query_cabinet?cabinet_name=nonexistent&query=test")
http_code="${error_response: -3}"
if [ "$http_code" = "404" ]; then
    print_result 0 "Correctly returned 404 for non-existent cabinet"
else
    print_result 1 "Expected 404, got $http_code"
fi

# Test 9: Add Content to Non-existent cabinet (Error Case)
print_test "Add Content to Non-existent cabinet (Error Handling)"
echo "Request: POST $BASE_URL/add_to_cabinet"
echo "Body: {\"cabinet_name\": \"nonexistent\", \"text\": \"test\"}"
error_add_response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/add_to_cabinet" \
    -H "Content-Type: application/json" \
    -d "{\"cabinet_name\": \"nonexistent\", \"text\": \"test content for non-existent cabinet\"}")
http_code="${error_add_response: -3}"
if [ "$http_code" = "404" ]; then
    print_result 0 "Correctly returned 404 for adding to non-existent cabinet"
else
    print_result 1 "Expected 404, got $http_code"
fi

# Test 10: Delete Test cabinet (Cleanup)
print_test "Delete Test cabinet (Cleanup)"
echo "Request: DELETE $BASE_URL/delete_cabinet/$TEST_cabinet"
delete_response=$(curl -s -X DELETE "$BASE_URL/delete_cabinet/$TEST_cabinet")
echo "Response: $delete_response"
echo "$delete_response" | jq -e '.message' > /dev/null
print_result $? "Delete cabinet successful"

echo -e "\n${GREEN}🎉 All REST API tests passed!${NC}"
echo "========================================"
echo -e "${YELLOW}Summary:${NC}"
echo "- Health check: ✅"
echo "- cabinet management: ✅"
echo "- Content indexing: ✅"
echo "- Content retrieval: ✅"
echo "- Similarity filtering: ✅"
echo "- Error handling: ✅"
echo "- Cleanup: ✅"
