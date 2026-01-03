#!/bin/bash
# AI-RSS-Hub Post-Reboot Verification Script
# Run this after rebooting to verify auto-start is working

echo "================================"
echo "  AI-RSS-Hub Post-Reboot Check"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counter
PASS=0
FAIL=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((FAIL++))
    fi
}

echo -e "${BLUE}1. Checking Systemd Service Status...${NC}"
sudo systemctl status ai-rss-hub --no-pager > /tmp/service_status.txt 2>&1
if grep -q "active (running)" /tmp/service_status.txt; then
    test_result 0 "Service is running"
    echo -e "   ${GREEN}$(grep 'Active:' /tmp/service_status.txt | head -1)${NC}"
else
    test_result 1 "Service is NOT running"
    echo -e "   ${RED}Status:$(grep 'Active:' /tmp/service_status.txt | head -1)${NC}"
fi
echo ""

echo -e "${BLUE}2. Checking Auto-Start on Boot...${NC}"
sudo systemctl is-enabled ai-rss-hub > /dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result 0 "Auto-start is enabled"
else
    test_result 1 "Auto-start is NOT enabled"
fi
echo ""

echo -e "${BLUE}3. Checking Port 8000...${NC}"
if netstat -tlnp 2>/dev/null | grep -q ":8000.*LISTEN" || ss -tlnp 2>/dev/null | grep -q ":8000.*LISTEN"; then
    test_result 0 "Port 8000 is listening"
    PID=$(netstat -tlnp 2>/dev/null | grep ":8000" | awk '{print $7}' | cut -d'/' -f1 | head -1)
    if [ -n "$PID" ]; then
        echo -e "   ${GREEN}Process PID: $PID${NC}"
    fi
else
    test_result 1 "Port 8000 is NOT listening"
fi
echo ""

echo -e "${BLUE}4. Testing API Health Endpoint...${NC}"
response=$(curl -s http://localhost:8000/api/health 2>&1)
if echo "$response" | grep -q '"status":"ok"'; then
    test_result 0 "API health endpoint is responding"
    echo -e "   ${GREEN}Response: $response${NC}"
else
    test_result 1 "API health endpoint is NOT responding"
    echo -e "   ${RED}Error: $response${NC}"
fi
echo ""

echo -e "${BLUE}5. Testing API Status Endpoint...${NC}"
response=$(curl -s http://localhost:8000/api/status 2>&1)
if echo "$response" | grep -q '"status":"running"'; then
    test_result 0 "API status endpoint is responding"
    echo -e "   ${GREEN}Scheduler: $(echo $response | grep -o '"scheduler".*"running"' | head -1)${NC}"
else
    test_result 1 "API status endpoint is NOT responding"
fi
echo ""

echo -e "${BLUE}6. Testing Feeds Endpoint...${NC}"
response=$(curl -s http://localhost:8000/api/feeds 2>&1)
if echo "$response" | grep -q '"id"'; then
    test_result 0 "Feeds endpoint is responding"
    feed_count=$(echo "$response" | grep -o '"id"' | wc -l)
    echo -e "   ${GREEN}Total feeds: $feed_count${NC}"
else
    test_result 1 "Feeds endpoint is NOT responding"
fi
echo ""

echo -e "${BLUE}7. Checking Service Logs...${NC}"
log_count=$(sudo journalctl -u ai-rss-hub --since "5 minutes ago" --no-pager | wc -l)
if [ $log_count -gt 0 ]; then
    test_result 0 "Service logs are being written"
    echo -e "   ${GREEN}Log entries in last 5 minutes: $log_count${NC}"
else
    test_result 1 "No recent logs found"
fi
echo ""

echo -e "${BLUE}8. Checking Database...${NC}"
if [ -f "/home/sam/Github/AI-RSS-Hub/ai_rss_hub.db" ]; then
    test_result 0 "Database file exists"
    db_size=$(du -h /home/sam/Github/AI-RSS-Hub/ai_rss_hub.db | cut -f1)
    echo -e "   ${GREEN}Database size: $db_size${NC}"
else
    test_result 1 "Database file NOT found"
fi
echo ""

# Summary
echo "================================"
echo -e "${BLUE}  Test Summary${NC}"
echo "================================"
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Auto-start is working perfectly!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Check the output above.${NC}"
    echo ""
    echo "Troubleshooting commands:"
    echo "  sudo systemctl status ai-rss-hub"
    echo "  sudo journalctl -u ai-rss-hub -n 50"
    echo "  ./manage_service.sh"
    exit 1
fi
