"""Cost tracking utility for AI Video GPT project."""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional

class CostTracker:
    """Tracks costs for various AI services used in the project."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.costs: List[Dict] = []
        self.session_start = datetime.datetime.now()
        
    def add_cost(self, service: str, cost_usd: float, details: Optional[str] = None):
        """Add a cost entry to the tracker.
        
        Args:
            service: Name of the service (e.g., 'imagen_generation', 'gemini_api', 'openai_tts')
            cost_usd: Cost in USD
            details: Optional details about the operation
        """
        cost_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "service": service,
            "cost_usd": cost_usd,
            "details": details or ""
        }
        self.costs.append(cost_entry)
        
    def get_total_cost(self) -> float:
        """Get total cost for this session."""
        return sum(entry["cost_usd"] for entry in self.costs)
        
    def get_cost_by_service(self) -> Dict[str, float]:
        """Get costs grouped by service."""
        service_costs = {}
        for entry in self.costs:
            service = entry["service"]
            if service not in service_costs:
                service_costs[service] = 0
            service_costs[service] += entry["cost_usd"]
        return service_costs
        
    def save_report(self, filename: Optional[str] = None):
        """Save cost report to file.
        
        Args:
            filename: Optional custom filename. If not provided, uses timestamp.
        """
        if not filename:
            timestamp = self.session_start.strftime("%Y%m%d_%H%M%S")
            filename = f"cost_report_{timestamp}.json"
            
        report_path = self.output_dir / filename
        
        report = {
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.datetime.now().isoformat(),
            "total_cost_usd": self.get_total_cost(),
            "cost_by_service": self.get_cost_by_service(),
            "detailed_costs": self.costs
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"💰 Cost report saved to: {report_path}")
        print(f"💰 Total session cost: ${self.get_total_cost():.4f} USD")
        
    def print_summary(self):
        """Print a summary of costs to console."""
        total_cost = self.get_total_cost()
        service_costs = self.get_cost_by_service()
        
        print("\n💰 Cost Summary:")
        print(f"Total Cost: ${total_cost:.4f} USD")
        print("\nBy Service:")
        for service, cost in service_costs.items():
            print(f"  - {service}: ${cost:.4f} USD")
        print()

# Legacy compatibility function
def generate_cost_report():
    """Legacy function for backward compatibility."""
    with open("output/costs.log", "a") as f:
        f.write(f"Cost report generated at {datetime.datetime.now().isoformat()}\n")