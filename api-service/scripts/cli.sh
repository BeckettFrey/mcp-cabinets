#!/bin/bash

# CLI - Interactive Command Line Interface
# Provides easy CLI access to test api and interact with environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Function to print banner
print_banner() {
    printf "${BLUE}${BOLD}"
    printf "╔══════════════════════════════════════════════════════════╗\n"
    printf "║                  Cabinets Chat CLI                       ║\n"
    printf "║            Interactive Indexing Service                  ║\n"
    printf "╚══════════════════════════════════════════════════════════╝\n"
    printf "${NC}"
}

# Function to print help
print_help() {
    printf "${CYAN}Available Commands:${NC}\n"
    printf "  ${BOLD}health${NC}              - Check server health\n"
    printf "  ${BOLD}list${NC}                - List all cabinets\n"
    printf "  ${BOLD}create <cabinet_name>${NC}   - Create a new cabinet\n"
    printf "  ${BOLD}add <cabinet_name>${NC}      - Add content to a cabinet (interactive)\n"
    printf "  ${BOLD}query <cabinet_name>${NC}    - Query a cabinet for content\n"
    printf "  ${BOLD}info <cabinet_name>${NC}     - Get cabinet information\n"
    printf "  ${BOLD}delete <cabinet_name>${NC}   - Delete a cabinet\n"
    printf "  ${BOLD}clear${NC}               - Clear all data (with confirmation)\n"
    printf "  ${BOLD}test${NC}                - Run REST API tests\n"
    printf "  ${BOLD}server${NC}              - Server management commands\n"
    printf "  ${BOLD}help${NC}                - Show this help\n"
    printf "  ${BOLD}exit${NC}                - Exit CLI\n"
}

# Function to check server health
check_health() {
    printf "${BLUE}🏥 Checking server health...${NC}\n"
    if response=$(curl -s "$BASE_URL/health" 2>/dev/null); then
        printf "${GREEN}✅ Server is healthy${NC}\n"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        printf "${RED}❌ Server is not responding${NC}\n"
        echo "Make sure the server is running: python server.py"
        return 1
    fi
}

# Function to list cabinets
list_cabinets() {
    echo -e "${BLUE}📂 Listing all cabinets...${NC}"
    if response=$(curl -s "$BASE_URL/list_cabinets" 2>/dev/null); then
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        echo -e "${RED}❌ Failed to list cabinets${NC}"
        return 1
    fi
}

# Function to create cabinet
create_cabinet() {
    local cabinet_name="$1"
    if [ -z "$cabinet_name" ]; then
        read -p "Enter cabinet name: " cabinet_name
    fi
    
    echo -e "${BLUE}🗂️  Creating cabinet: $cabinet_name${NC}"
    if response=$(curl -s -X POST "$BASE_URL/create_cabinet" \
        -H "Content-Type: application/json" \
        -d "{\"cabinet_name\": \"$cabinet_name\"}" 2>/dev/null); then
        echo -e "${GREEN}✅ cabinet created successfully${NC}"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        echo -e "${RED}❌ Failed to create cabinet${NC}"
        return 1
    fi
}

# Function to add content to cabinet
add_content() {
    local cabinet_name="$1"
    if [ -z "$cabinet_name" ]; then
        read -p "Enter cabinet name: " cabinet_name
    fi
    
    echo -e "${BLUE}📝 Adding content to cabinet: $cabinet_name${NC}"
    echo "Enter content (press Ctrl+D when finished):"
    echo -e "${YELLOW}(Tip: You can paste multi-line content)${NC}"
    
    content=$(cat)
    
    if [ -z "$content" ]; then
        echo -e "${RED}❌ No content provided${NC}"
        return 1
    fi
    
    read -p "Enter source URL (optional): " source_url
    
    echo -e "${BLUE}📤 Uploading content...${NC}"
    
    json_payload=$(jq -n \
        --arg cabinet_name "$cabinet_name" \
        --arg text "$content" \
        --arg source_url "$source_url" \
        '{cabinet_name: $cabinet_name, text: $text, source_url: ($source_url | if . == "" then null else . end)}')
    
    if response=$(curl -s -X POST "$BASE_URL/add_to_cabinet" \
        -H "Content-Type: application/json" \
        -d "$json_payload" 2>/dev/null); then
        echo -e "${GREEN}✅ Content added successfully${NC}"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        echo -e "${RED}❌ Failed to add content${NC}"
        return 1
    fi
}

# Function to query cabinet
query_cabinet() {
    local cabinet_name="$1"
    if [ -z "$cabinet_name" ]; then
        read -p "Enter cabinet name: " cabinet_name
    fi
    
    read -p "Enter search query: " query
    read -p "Number of results (default 5): " top_k
    read -p "Similarity threshold 0.0-1.0 (default 0.7): " threshold
    
    # Set defaults
    top_k=${top_k:-5}
    threshold=${threshold:-0.7}
    
    echo -e "${BLUE}🔍 Searching cabinet: $cabinet_name${NC}"
    
    url="$BASE_URL/query_cabinet?cabinet_name=$(echo "$cabinet_name" | sed 's/ /%20/g')&query=$(echo "$query" | sed 's/ /%20/g')&top_k=$top_k&similarity_threshold=$threshold"
    
    if response=$(curl -s "$url" 2>/dev/null); then
        echo -e "${GREEN}✅ Query completed${NC}"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        echo -e "${RED}❌ Query failed${NC}"
        return 1
    fi
}

# Function to get cabinet info
get_cabinet_info() {
    local cabinet_name="$1"
    if [ -z "$cabinet_name" ]; then
        read -p "Enter cabinet name: " cabinet_name
    fi
    
    echo -e "${BLUE}ℹ️  Getting info for cabinet: $cabinet_name${NC}"
    
    # Get cabinet info from list_cabinets and filter
    if response=$(curl -s "$BASE_URL/list_cabinets" 2>/dev/null); then
        cabinet_info=$(echo "$response" | jq --arg name "$cabinet_name" '.cabinets[] | select(.name == $name)' 2>/dev/null)
        if [ -n "$cabinet_info" ]; then
            echo -e "${GREEN}✅ cabinet information:${NC}"
            echo "$cabinet_info" | jq '.' 2>/dev/null || echo "$cabinet_info"
        else
            echo -e "${RED}❌ cabinet not found: $cabinet_name${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Failed to get cabinet info${NC}"
        return 1
    fi
}

# Function to delete cabinet
delete_cabinet() {
    local cabinet_name="$1"
    if [ -z "$cabinet_name" ]; then
        read -p "Enter cabinet name: " cabinet_name
    fi
    
    echo -e "${YELLOW}⚠️  WARNING: This will permanently delete cabinet '$cabinet_name' and all its content${NC}"
    read -p "Are you sure? (type 'yes' to confirm): " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        echo -e "${YELLOW}❌ Operation cancelled${NC}"
        return 0
    fi
    
    echo -e "${BLUE}🗑️  Deleting cabinet: $cabinet_name${NC}"
    
    if response=$(curl -s -X DELETE "$BASE_URL/delete_cabinet/$cabinet_name" 2>/dev/null); then
        echo -e "${GREEN}✅ cabinet deleted successfully${NC}"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        echo -e "${RED}❌ Failed to delete cabinet${NC}"
        return 1
    fi
}

# Function to clear all data
clear_all_data() {
    echo -e "${BLUE}🗑️  Running data cleanup script...${NC}"
    if [ -f "$SCRIPT_DIR/datastore/clear_all_data.sh" ]; then
        "$SCRIPT_DIR/datastore/clear_all_data.sh"
    else
        echo -e "${RED}❌ Clear data script not found${NC}"
        return 1
    fi
}

# Function to run tests
run_tests() {
    echo -e "${BLUE}🧪 Running REST API tests...${NC}"
    if [ -f "$PROJECT_ROOT/api-service/scripts/tests/test_api.sh" ]; then
        "$PROJECT_ROOT/api-service/scripts/tests/test_api.sh"
    else
        echo -e "${RED}❌ Test script not found${NC}"
        return 1
    fi
}

# Function for server management
server_management() {
    echo -e "${CYAN}Server Management:${NC}"
    echo "1. Check if server is running"
    echo "2. Start server (background)"
    echo "3. Stop server"
    echo "4. Restart server"
    read -p "Choose option (1-4): " option
    
    case $option in
        1)
            if pgrep -f "python.*server.py" > /dev/null; then
                echo -e "${GREEN}✅ Server is running${NC}"
                pgrep -f "python.*server.py" | head -5
            else
                echo -e "${RED}❌ Server is not running${NC}"
            fi
            ;;
        2)
            echo -e "${BLUE}🚀 Starting server in background...${NC}"
            cd "$PROJECT_ROOT"
            nohup python server.py > server.log 2>&1 &
            echo -e "${GREEN}✅ Server started (PID: $!)${NC}"
            echo "Logs: tail -f $PROJECT_ROOT/server.log"
            ;;
        3)
            echo -e "${BLUE}🛑 Stopping server...${NC}"
            if pkill -f "python.*server.py"; then
                echo -e "${GREEN}✅ Server stopped${NC}"
            else
                echo -e "${YELLOW}⚠️  No server process found${NC}"
            fi
            ;;
        4)
            echo -e "${BLUE}🔄 Restarting server...${NC}"
            pkill -f "python.*server.py" 2>/dev/null || true
            sleep 2
            cd "$PROJECT_ROOT"
            nohup python server.py > server.log 2>&1 &
            echo -e "${GREEN}✅ Server restarted (PID: $!)${NC}"
            ;;
        *)
            echo -e "${RED}❌ Invalid option${NC}"
            ;;
    esac
}

# Main CLI loop
main() {
    print_banner
    
    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  'jq' not found. JSON output will be raw.${NC}"
        echo "Install with: brew install jq"
        echo ""
    fi
    
    print_help
    echo ""
    
    while true; do
        printf "${BOLD}cabinets-chat> ${NC}"
        read -r command args
        
        case $command in
            "health"|"h")
                check_health
                ;;
            "list"|"ls")
                list_cabinets
                ;;
            "create"|"c")
                create_cabinet "$args"
                ;;
            "add"|"a")
                add_content "$args"
                ;;
            "query"|"q")
                query_cabinet "$args"
                ;;
            "info"|"i")
                get_cabinet_info "$args"
                ;;
            "delete"|"del"|"d")
                delete_cabinet "$args"
                ;;
            "clear")
                clear_all_data
                ;;
            "test"|"t")
                run_tests
                ;;
            "server"|"srv")
                server_management
                ;;
            "help"|"?")
                print_help
                ;;
            "exit"|"quit"|"q!")
                echo -e "${GREEN}👋 Goodbye!${NC}"
                break
                ;;
            "")
                # Empty command, just continue
                ;;
            *)
                echo -e "${RED}❌ Unknown command: $command${NC}"
                echo "Type 'help' for available commands"
                ;;
        esac
        echo ""
    done
}

# Run the CLI
main "$@"
