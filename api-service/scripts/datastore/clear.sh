#!/bin/bash

# Clear All Data Script for API Service
# This script completely resets the datastore to a clean slate

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STORAGE_DIR="$PROJECT_ROOT/storage"

echo -e "${BLUE}🗑️  Cabinets Chat - Clear All Data${NC}"
echo "=========================================="
echo "Project root: $PROJECT_ROOT"
echo "Storage directory: $STORAGE_DIR"

# Safety check - require confirmation
echo -e "\n${YELLOW}⚠️  WARNING: This will permanently delete ALL data!${NC}"
echo "This includes:"
echo "- All cabinets and their content"
echo "- All FAISS vector indices"
echo "- All metadata and history"
echo "- All persisted storage files"

echo -e "\n${RED}This action cannot be undone!${NC}"
read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirmation

if [ "$confirmation" != "yes" ]; then
    echo -e "${YELLOW}❌ Operation cancelled.${NC}"
    exit 0
fi

echo -e "\n${BLUE}🧹 Starting data cleanup...${NC}"

# Check if storage directory exists
if [ ! -d "$STORAGE_DIR" ]; then
    echo -e "${YELLOW}ℹ️  Storage directory doesn't exist. Nothing to clean.${NC}"
    echo "Directory: $STORAGE_DIR"
else
    echo -e "${BLUE}📂 Found storage directory with content:${NC}"
    if [ "$(ls -A "$STORAGE_DIR" 2>/dev/null)" ]; then
        echo "Contents:"
        ls -la "$STORAGE_DIR"
        
        echo -e "\n${BLUE}🗑️  Removing all storage content...${NC}"
        rm -rf "$STORAGE_DIR"/*
        echo -e "${GREEN}✅ Storage directory cleared${NC}"
    else
        echo "Storage directory is already empty"
    fi
fi

# Check for any cache files or temporary data
CACHE_PATTERNS=(
    "$PROJECT_ROOT/__pycache__"
    "$PROJECT_ROOT/*.pyc"
    "$PROJECT_ROOT/.pytest_cache"
    "$PROJECT_ROOT/temp"
    "$PROJECT_ROOT/tmp"
)

echo -e "\n${BLUE}🧹 Checking for cache files...${NC}"
found_cache=false

for pattern in "${CACHE_PATTERNS[@]}"; do
    if ls $pattern 1> /dev/null 2>&1; then
        echo "Found cache: $pattern"
        rm -rf $pattern
        found_cache=true
    fi
done

if [ "$found_cache" = true ]; then
    echo -e "${GREEN}✅ Cache files cleaned${NC}"
else
    echo "No cache files found"
fi

# Check if server is running and warn
SERVER_URL="http://localhost:8000"
if curl -s --connect-timeout 2 "$SERVER_URL/health" > /dev/null 2>&1; then
    echo -e "\n${YELLOW}⚠️  Server appears to be running at $SERVER_URL${NC}"
    echo "You may want to restart the server to ensure it picks up the clean state."
    echo "Run: pkill -f 'python.*server.py' && python server.py"
fi

# Create a clean storage directory structure
echo -e "\n${BLUE}📁 Recreating clean storage structure...${NC}"
mkdir -p "$STORAGE_DIR"
echo -e "${GREEN}✅ Storage directory recreated${NC}"

# Create a timestamp file to record when cleanup was performed
CLEANUP_LOG="$STORAGE_DIR/.cleanup_log"
echo "Data cleanup performed at: $(date)" > "$CLEANUP_LOG"
echo "Cleared by: $(whoami)" >> "$CLEANUP_LOG"
echo "Script: $0" >> "$CLEANUP_LOG"

echo -e "\n${GREEN}🎉 Data cleanup completed successfully!${NC}"
echo "=========================================="
echo -e "${BLUE}Summary:${NC}"
echo "- All cabinet data: ✅ Cleared"
echo "- Vector indices: ✅ Cleared" 
echo "- Metadata: ✅ Cleared"
echo "- Cache files: ✅ Cleared"
echo "- Storage structure: ✅ Recreated"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Restart the server if it's running"
echo "2. The server will start with a completely clean slate"
echo "3. Create new cabinets and add content as needed"
echo ""
echo -e "${BLUE}Cleanup log saved to: $CLEANUP_LOG${NC}"
