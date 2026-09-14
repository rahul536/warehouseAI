import json

from shortage_graph import shortage_investigation_graph


result = shortage_investigation_graph.invoke(
    {
        "order_number": "ORD10004",
    }
)

print("\nINVESTIGATION SUMMARY\n")
print(result["summary"])

print("\nWORKFLOW TRACE\n")
for step in result["trace"]:
    print(f"- {step}")

print("\nFULL WORKFLOW STATE\n")
print(json.dumps(result, indent=2))