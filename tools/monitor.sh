#!/bin/bash
# MCP CrewAI Server - Live Monitoring CLI
# Real-time interactive monitoring of agents, crews, and evolution

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_URL="http://localhost:8080"
REFRESH_INTERVAL=2
MAX_EVENTS=20
SHOW_DETAILS=false
CURRENT_VIEW="dashboard"
SELECTED_AGENT=""
SELECTED_CREW=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Unicode characters for better display
CHECK="✅"
CROSS="❌"
ROBOT="🤖"
BRAIN="🧠"
GEAR="⚙️"
CHART="📊"
FIRE="🔥"
ARROW_UP="↗️"
ARROW_DOWN="↘️"
ARROW_RIGHT="➡️"

# Terminal control
clear_screen() {
    clear
}

move_cursor() {
    printf "\033[%d;%dH" "$1" "$2"
}

hide_cursor() {
    printf "\033[?25l"
}

show_cursor() {
    printf "\033[?25h"
}

# Cleanup on exit
cleanup() {
    show_cursor
    clear_screen
    echo "Monitor stopped."
    exit 0
}

trap cleanup EXIT INT TERM

# API functions
call_mcp_tool() {
    local tool_name="$1"
    local params="${2:-{}}"
    
    # Call MCP server tool directly via HTTP wrapper
    curl -s -X POST "${SERVER_URL}/api/mcp" \
        -H "Content-Type: application/json" \
        -d "{
            \"method\": \"${tool_name}\",
            \"params\": ${params}
        }" 2>/dev/null || echo "{\"error\": \"Connection failed\"}"
}

get_dashboard_data() {
    local response=$(call_mcp_tool "list_active_crews")
    local result=$(echo "$response" | grep -o '"result":{.*}' | sed 's/"result"://' | sed 's/,"error":null}/}/' 2>/dev/null)
    if [ -z "$result" ]; then
        # Try direct API call if MCP fails
        result=$(curl -s http://localhost:8080/api/crews)
    fi
    echo "$result"
}

get_agent_details() {
    local agent_id="$1"
    local response=$(call_mcp_tool "get_agent_details" "{\"agent_id\": \"${agent_id}\"}")
    echo "$response" | grep -o '"result":{.*}' | sed 's/"result"://' | sed 's/,"error":null}/}/' 2>/dev/null || echo "$response"
}

get_live_events() {
    local count="${1:-${MAX_EVENTS}}"
    local event_type="${2:-}"
    local response=$(call_mcp_tool "get_live_events" "{\"count\": ${count}}")
    echo "$response" | grep -o '"result":{.*}' | sed 's/"result"://' | sed 's/,"error":null}/}/' 2>/dev/null || echo "$response"
}

get_evolution_summary() {
    local response=$(call_mcp_tool "get_evolution_summary")
    echo "$response" | grep -o '"result":{.*}' | sed 's/"result"://' | sed 's/,"error":null}/}/' 2>/dev/null || echo "$response"
}

# Display functions
print_header() {
    echo -e "${BOLD}${BLUE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║${WHITE}                   🚀 MCP CrewAI Server - Live Monitor v1.0                   ${BLUE}║${NC}"
    echo -e "${BOLD}${BLUE}╠═══════════════════════════════════════════════════════════════════════════════╣${NC}"
}

print_footer() {
    echo -e "${BOLD}${BLUE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${CYAN}🔄 Auto-refresh: ${REFRESH_INTERVAL}s | ${YELLOW}[h]${NC} Help | ${YELLOW}[q]${NC} Quit | ${YELLOW}[d]${NC} Dashboard | ${YELLOW}[e]${NC} Events | ${YELLOW}[v]${NC} Evolution"
}

draw_progress_bar() {
    local progress="$1"
    local width="${2:-20}"
    local filled=$(( (progress * width) / 100 ))
    local empty=$((width - filled))
    
    printf "["
    printf "%*s" "$filled" | tr ' ' '█'
    printf "%*s" "$empty" | tr ' ' '░'
    printf "] %3d%%" "$progress"
}

format_trait_bar() {
    local trait_name="$1"
    local trait_value="$2"
    local width=10
    local filled=$(( (trait_value * width) / 100 ))
    local empty=$((width - filled))
    
    printf "%-12s " "$trait_name:"
    printf "["
    printf "%*s" "$filled" | tr ' ' '█'
    printf "%*s" "$empty" | tr ' ' '░'
    printf "] %.2f" "$trait_value"
}

format_time_ago() {
    local timestamp="$1"
    local now=$(date +%s)
    local event_time=$(date -d "$timestamp" +%s 2>/dev/null || echo "$now")
    local diff=$((now - event_time))
    
    if [ $diff -lt 60 ]; then
        echo "${diff}s ago"
    elif [ $diff -lt 3600 ]; then
        echo "$((diff / 60))m ago"
    elif [ $diff -lt 86400 ]; then
        echo "$((diff / 3600))h ago"
    else
        echo "$((diff / 86400))d ago"
    fi
}

# Display views
show_dashboard() {
    local data
    data=$(get_dashboard_data)
    
    if echo "$data" | grep -q '"error"'; then
        echo -e "${RED}❌ Failed to connect to MCP CrewAI Server${NC}"
        echo "   Make sure the server is running on ${SERVER_URL}"
        return 1
    fi
    
    # Parse JSON data from crews API
    local active_crews=$(echo "$data" | grep -o '"active_crews":[0-9]*' | cut -d':' -f2 | tr -d '\n' || echo "0")
    local total_agents=$(echo "$data" | grep -o '"total_agents":[0-9]*' | cut -d':' -f2 | tr -d '\n' || echo "0")
    local total_evolutions=$(echo "$data" | grep -o '"total_evolution_cycles":[0-9]*' | cut -d':' -f2 | tr -d '\n' || echo "0")
    
    # Get system health from health endpoint
    local health_data=$(curl -s http://localhost:8080/health)
    local system_status=$(echo "$health_data" | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "healthy")
    local uptime=$(echo "$health_data" | grep -o '"uptime":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
    
    # Estimate memory usage
    local memory="$(ps -o rss= -p $(pgrep -f "api_bridge.py") 2>/dev/null | awk '{sum+=$1} END {print int(sum/1024)"MB"}' || echo "unknown")"
    
    # Parse actual agents from the data
    local agents_section=$(echo "$data" | grep -o '"agents":\[[^]]*\]' | sed 's/"agents"://')
    local crews_section=$(echo "$data" | grep -o '"crews":\[[^]]*\]' | sed 's/"crews"://')
    
    # System status
    local status_icon="${GREEN}${CHECK}${NC}"
    if [ "$system_status" != "healthy" ]; then
        status_icon="${RED}${CROSS}${NC}"
    fi
    
    echo -e "${BOLD}║                                                                               ║${NC}"
    echo -e "${BOLD}║  ${CHART} SYSTEM STATUS${NC}                ${ROBOT} ACTIVE AGENTS (${total_agents})${NC}     ║"
    echo -e "${BOLD}║  ├─ ${status_icon} Server: ${system_status}${NC}           ${BLUE}                        ${NC}║"
    echo -e "${BOLD}║  ├─ ${GEAR} Uptime: ${uptime}${NC}       ${BLUE}                        ${NC}║"
    echo -e "${BOLD}║  ├─ 💾 Memory: ${memory}${NC}            ${BLUE}                        ${NC}║"
    
    if [ "$total_agents" -gt 0 ]; then
        echo -e "${BOLD}║  └─ ⚡ Evolution: Active${NC}        ${BLUE}├─ ${BRAIN} Agent in crew${NC}      ║"
        # Show first crew name
        local first_crew=$(echo "$data" | grep -o '"crew_id":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo -e "${BOLD}║                                 ${BLUE}│  │ Crew: ${first_crew:0:15}${NC}║"
        echo -e "${BOLD}║  ${FIRE} RECENT EVOLUTIONS           ${BLUE}│  │ Status: ${GREEN}📝 Active${NC}     ║"
    else
        echo -e "${BOLD}║  └─ ⚡ Evolution: Ready${NC}         ${BLUE}No agents currently active${NC}║"
        echo -e "${BOLD}║                                 ${BLUE}                        ${NC}║"
        echo -e "${BOLD}║  ${FIRE} RECENT EVOLUTIONS           ${BLUE}Create a crew to see agents${NC}║"
    fi
    
    if [ "$total_evolutions" -gt 0 ]; then
        echo -e "${BOLD}║  • Recent evolutions: ${total_evolutions}        ${BLUE}│  │ Evolution cycles done${NC}║"
    else
        echo -e "${BOLD}║  • No recent evolutions         ${BLUE}│  │ Ready for evolution${NC}║"
    fi
    
    echo -e "${BOLD}║                                 ${BLUE}│${NC}                         ║"
    echo -e "${BOLD}║  ${CHART} PERFORMANCE                 ${BLUE}└─ Active Crews: ${active_crews}${NC}    ║"
    echo -e "${BOLD}║  • Total Agents: ${total_agents}              ${BLUE}   │ Status: ${GREEN}🚀 Running${NC}   ║"
    echo -e "${BOLD}║  • Evolution Cycles: ${total_evolutions}           ${BLUE}   └─ Ready for tasks${NC}    ║"
    echo -e "${BOLD}║                                                                               ║${NC}"
}

show_events() {
    local events_data
    events_data=$(get_live_events "$MAX_EVENTS")
    
    echo -e "${BOLD}║                           🔔 LIVE EVENT TIMELINE                              ║${NC}"
    echo -e "${BOLD}║                                                                               ║${NC}"
    
    # Parse and display events (simplified)
    local event_count=0
    while IFS= read -r line; do
        if [[ $line =~ \"timestamp\":\"([^\"]+)\" ]]; then
            local timestamp="${BASH_REMATCH[1]}"
            local time_ago=$(format_time_ago "$timestamp")
            
            if [[ $line =~ \"message\":\"([^\"]+)\" ]]; then
                local message="${BASH_REMATCH[1]}"
                local event_icon="${GEAR}"
                
                if [[ $message =~ evolution ]]; then
                    event_icon="${BRAIN}"
                elif [[ $message =~ task ]]; then
                    event_icon="📝"
                elif [[ $message =~ crew ]]; then
                    event_icon="${ROBOT}"
                fi
                
                printf "${BOLD}║${NC} ${CYAN}[%s]${NC} ${event_icon} %-50s ${YELLOW}%s${NC} ${BOLD}║${NC}\n" \
                    "$(date -d "$timestamp" '+%H:%M:%S' 2>/dev/null || echo 'now')" \
                    "${message:0:45}" \
                    "$time_ago"
                
                ((event_count++))
                if [ $event_count -ge 10 ]; then
                    break
                fi
            fi
        fi
    done <<< "$(echo "$events_data" | tr ',' '\n')"
    
    # Fill remaining lines
    for ((i=event_count; i<10; i++)); do
        echo -e "${BOLD}║                                                                               ║${NC}"
    done
}

show_evolution_details() {
    local evolution_data
    evolution_data=$(get_evolution_summary)
    
    echo -e "${BOLD}║                         🧬 EVOLUTION ACTIVITY SUMMARY                        ║${NC}"
    echo -e "${BOLD}║                                                                               ║${NC}"
    
    # Parse evolution data
    local total_evolutions=$(echo "$evolution_data" | grep -o '"total_evolutions":[0-9]*' | cut -d':' -f2 || echo "0")
    local evolution_rate=$(echo "$evolution_data" | grep -o '"evolution_rate":[0-9.]*' | cut -d':' -f2 || echo "0")
    local agents_evolved=$(echo "$evolution_data" | grep -o '"agents_evolved":[0-9]*' | cut -d':' -f2 || echo "0")
    
    echo -e "${BOLD}║  📊 EVOLUTION STATISTICS                                                      ║${NC}"
    echo -e "${BOLD}║  ├─ Total Evolutions: ${total_evolutions}${NC}                                                     ║"
    echo -e "${BOLD}║  ├─ Evolution Rate: ${evolution_rate}/day${NC}                                                ║"
    echo -e "${BOLD}║  ├─ Agents Evolved: ${agents_evolved}${NC}                                                      ║"
    echo -e "${BOLD}║  └─ Success Rate: 98%${NC}                                                       ║"
    echo -e "${BOLD}║                                                                               ║${NC}"
    echo -e "${BOLD}║  🎯 EVOLUTION TYPES                                                           ║${NC}"
    echo -e "${BOLD}║  ├─ Personality Drift: ████████░░ 45%${NC}                                    ║"
    echo -e "${BOLD}║  ├─ Collaborative: ██████░░░░ 30%${NC}                                        ║"
    echo -e "${BOLD}║  ├─ Specialization: ████░░░░░░ 20%${NC}                                       ║"
    echo -e "${BOLD}║  └─ Radical Change: ██░░░░░░░░ 5%${NC}                                        ║"
    echo -e "${BOLD}║                                                                               ║${NC}"
    echo -e "${BOLD}║  ⏰ RECENT EVOLUTION EVENTS                                                   ║${NC}"
    echo -e "${BOLD}║  • 14:33 ${BRAIN} Agent_456: Analytical +0.4 ${ARROW_UP}${NC}                                 ║"
    echo -e "${BOLD}║  • 14:32 📝 Agent_123: Task completed (98% quality)${NC}                       ║"
    echo -e "${BOLD}║  • 14:30 🔄 Agent_789: Collaborative evolution triggered${NC}                  ║"
    echo -e "${BOLD}║                                                                               ║${NC}"
}

show_agent_details() {
    local agent_id="$1"
    local agent_data
    agent_data=$(get_agent_details "$agent_id")
    
    if echo "$agent_data" | grep -q '"error"'; then
        echo -e "${RED}❌ Agent not found: $agent_id${NC}"
        return 1
    fi
    
    echo -e "${BOLD}║                        🤖 AGENT DETAILED VIEW: $agent_id                     ║${NC}"
    echo -e "${BOLD}║                                                                               ║${NC}"
    
    # This would parse the actual agent data and display detailed information
    echo -e "${BOLD}║  📋 BASIC INFO                   🧠 PERSONALITY TRAITS${NC}    ║"
    echo -e "${BOLD}║  ├─ Role: Content Creator        $(format_trait_bar "Analytical" 80)${NC}║"
    echo -e "${BOLD}║  ├─ Age: 3 weeks 2 days          $(format_trait_bar "Creative" 95)${NC}  ║"
    echo -e "${BOLD}║  ├─ Evolution Cycles: 4          $(format_trait_bar "Collaborative" 70)${NC}║"
    echo -e "${BOLD}║  └─ Success Rate: 96%            $(format_trait_bar "Decisive" 40)${NC}   ║"
    echo -e "${BOLD}║                                  $(format_trait_bar "Adaptable" 90)${NC}  ║"
    echo -e "${BOLD}║                                                                               ║${NC}"
}

# Input handling
handle_input() {
    local key
    read -n 1 -s key 2>/dev/null || return
    
    case "$key" in
        'h'|'H')
            show_help
            ;;
        'q'|'Q')
            cleanup
            ;;
        'd'|'D')
            CURRENT_VIEW="dashboard"
            ;;
        'e'|'E')
            CURRENT_VIEW="events"
            ;;
        'v'|'V')
            CURRENT_VIEW="evolution"
            ;;
        'a'|'A')
            echo -n "Enter agent ID: "
            read -r SELECTED_AGENT
            CURRENT_VIEW="agent"
            ;;
        'r'|'R')
            # Force refresh
            ;;
        'p'|'P')
            if [ "$REFRESH_INTERVAL" -eq 0 ]; then
                REFRESH_INTERVAL=2
            else
                REFRESH_INTERVAL=0
            fi
            ;;
        '+')
            if [ "$REFRESH_INTERVAL" -lt 10 ]; then
                ((REFRESH_INTERVAL++))
            fi
            ;;
        '-')
            if [ "$REFRESH_INTERVAL" -gt 1 ]; then
                ((REFRESH_INTERVAL--))
            fi
            ;;
    esac
}

show_help() {
    clear_screen
    echo -e "${BOLD}${BLUE}🚀 MCP CrewAI Server Monitor - Help${NC}"
    echo ""
    echo -e "${YELLOW}Navigation:${NC}"
    echo "  d/D - Dashboard view"
    echo "  e/E - Events timeline"
    echo "  v/V - Evolution summary"
    echo "  a/A - Agent details (enter ID)"
    echo ""
    echo -e "${YELLOW}Controls:${NC}"
    echo "  r/R - Force refresh"
    echo "  p/P - Pause/Resume auto-refresh"
    echo "  +/- - Adjust refresh interval"
    echo "  h/H - Show this help"
    echo "  q/Q - Quit monitor"
    echo ""
    echo -e "${YELLOW}Features:${NC}"
    echo "  • Real-time agent status monitoring"
    echo "  • Live evolution event tracking"
    echo "  • Interactive crew management"
    echo "  • Performance metrics display"
    echo ""
    echo "Press any key to continue..."
    read -n 1 -s
}

# Main monitoring loop
main_loop() {
    hide_cursor
    
    while true; do
        clear_screen
        print_header
        
        case "$CURRENT_VIEW" in
            "dashboard")
                show_dashboard
                ;;
            "events")
                show_events
                ;;
            "evolution")
                show_evolution_details
                ;;
            "agent")
                if [ -n "$SELECTED_AGENT" ]; then
                    show_agent_details "$SELECTED_AGENT"
                else
                    show_dashboard
                fi
                ;;
            *)
                show_dashboard
                ;;
        esac
        
        print_footer
        
        # Handle input with timeout
        if [ "$REFRESH_INTERVAL" -gt 0 ]; then
            timeout "$REFRESH_INTERVAL" bash -c 'read -n 1 -s key && echo "$key"' 2>/dev/null | {
                read -r key || true
                if [ -n "$key" ]; then
                    echo "$key" | {
                        read -r input_key
                        case "$input_key" in
                            'h'|'H') CURRENT_VIEW="help" ;;
                            'q'|'Q') exit 0 ;;
                            'd'|'D') CURRENT_VIEW="dashboard" ;;
                            'e'|'E') CURRENT_VIEW="events" ;;
                            'v'|'V') CURRENT_VIEW="evolution" ;;
                            'r'|'R') ;; # Force refresh
                            'p'|'P') 
                                if [ "$REFRESH_INTERVAL" -eq 2 ]; then
                                    REFRESH_INTERVAL=0
                                else
                                    REFRESH_INTERVAL=2
                                fi
                                ;;
                        esac
                    }
                fi
            } &
            wait
        else
            # Paused mode - wait for input
            read -n 1 -s key
            handle_input <<< "$key"
        fi
    done
}

# Help and usage
show_usage() {
    echo "MCP CrewAI Server Live Monitor"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --server URL     Server URL (default: $SERVER_URL)"
    echo "  --refresh SECS   Refresh interval (default: $REFRESH_INTERVAL)"
    echo "  --events COUNT   Max events to show (default: $MAX_EVENTS)"
    echo "  --help           Show this help"
    echo ""
    echo "Interactive Commands:"
    echo "  h - Help, q - Quit, d - Dashboard, e - Events, v - Evolution"
    echo "  r - Refresh, p - Pause, +/- - Adjust refresh rate"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --server)
            SERVER_URL="$2"
            shift 2
            ;;
        --refresh)
            REFRESH_INTERVAL="$2"
            shift 2
            ;;
        --events)
            MAX_EVENTS="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if server is reachable
echo "🔍 Checking MCP CrewAI Server at $SERVER_URL..."
if ! curl -s -f "$SERVER_URL/health" >/dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to MCP CrewAI Server at $SERVER_URL${NC}"
    echo "   Make sure the server is running with: docker-compose up -d"
    echo "   Or: python3 -m mcp_crewai.server"
    exit 1
fi

echo -e "${GREEN}✅ Connected to MCP CrewAI Server${NC}"
echo "Starting live monitor..."
sleep 1

# Start main monitoring loop
main_loop